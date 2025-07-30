import json
import yaml
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from agent import UniversalAgent
from config_manager import ConfigurationManager
from model_config.data_models import AgentModelConfig
from model_config.model_configuration_manager import ModelConfigurationManager
from cost_monitor import CostMonitor, CostAlert

class TaskOrchestrator:
    def __init__(self, config_path="config.yaml", silent=False):
        # Store config path for agent creation
        self.config_path = config_path
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.num_agents = self.config['orchestrator']['parallel_agents']
        self.task_timeout = self.config['orchestrator']['task_timeout']
        self.aggregation_strategy = self.config['orchestrator']['aggregation_strategy']
        self.silent = silent
        
        # Initialize configuration managers
        self.config_manager = ConfigurationManager()
        self.config_manager.load_config(config_path)
        self.model_config_manager = ModelConfigurationManager(self.config_manager)
        
        # Load multi-model configuration if available
        self.multi_model_config = self._load_multi_model_config()
        
        # Track agent progress and model usage
        self.agent_progress = {}
        self.agent_results = {}
        self.agent_models = {}  # Track which model each agent uses
        self.agent_costs = {}   # Track costs per agent
        self.progress_lock = threading.Lock()
        
        # Cost monitoring
        self.cost_monitor: Optional[CostMonitor] = None
        self.budget_limit: Optional[float] = None
        
        # Initialize cost monitoring if budget is configured
        orchestrator_config = self.config.get('orchestrator', {})
        if 'budget_limit' in orchestrator_config:
            self.enable_cost_monitoring(orchestrator_config['budget_limit'])
    
    def enable_cost_monitoring(self, budget_limit: float):
        """Enable real-time cost monitoring with budget alerts."""
        self.budget_limit = budget_limit
        self.cost_monitor = CostMonitor(
            budget_limit=budget_limit,
            alert_callback=self._handle_cost_alert
        )
        
        if not self.silent:
            print(f"💰 Cost monitoring enabled with budget limit: ${budget_limit:.4f}")
    
    def _handle_cost_alert(self, alert: CostAlert):
        """Handle cost alerts during execution."""
        if not self.silent:
            if alert.alert_type == 'warning':
                print(f"⚠️  {alert.message}")
            elif alert.alert_type == 'critical':
                print(f"🚨 {alert.message}")
            elif alert.alert_type == 'budget_exceeded':
                print(f"💸 {alert.message}")
                print("🛑 Consider stopping execution to avoid additional costs!")
    
    def get_cost_monitoring_summary(self) -> Optional[Dict[str, Any]]:
        """Get cost monitoring summary if enabled."""
        if self.cost_monitor:
            return self.cost_monitor.get_cost_summary()
        return None
    
    def _load_multi_model_config(self) -> Optional[AgentModelConfig]:
        """Load multi-model configuration from YAML file."""
        try:
            return self.model_config_manager.load_agent_configuration(self.config_path)
        except Exception as e:
            if not self.silent:
                print(f"⚠️  No multi-model configuration found, using default model: {e}")
            return None
    
    def _get_agent_model(self, agent_id: int) -> str:
        """Get the model to use for a specific agent."""
        if self.multi_model_config:
            agent_model = self.multi_model_config.get_agent_model(agent_id)
            if agent_model:
                return agent_model
        
        # Fallback to default model from provider config
        try:
            return self.config_manager.get_provider_config().model
        except Exception:
            # Ultimate fallback
            return "deepseek-chat"
    
    def _get_synthesis_model(self) -> str:
        """Get the model to use for synthesis."""
        if self.multi_model_config:
            return self.multi_model_config.synthesis_model
        
        # Fallback to default model from provider config
        try:
            return self.config_manager.get_provider_config().model
        except Exception:
            # Ultimate fallback
            return "deepseek-chat"
    
    def _create_agent_with_model(self, agent_id: int, model: str) -> UniversalAgent:
        """Create an agent with a specific model configuration."""
        try:
            # Create a temporary config file with the specific model
            temp_config = self.config.copy()
            
            # Update the model in the provider configuration
            provider_type = self.config_manager.get_provider_config().provider_type
            if provider_type in temp_config:
                temp_config[provider_type]['model'] = model
            
            # Create agent with modified config
            # For now, we'll use the existing config file approach
            # In a more advanced implementation, we could pass the config directly
            agent = UniversalAgent(config_path=self.config_path, silent=True)
            
            # Override the model in the agent's provider config
            agent.provider_config.model = model
            
            # Log the model being used
            if not self.silent:
                print(f"🤖 Agent {agent_id} using model: {model}")
            
            # Track the model for this agent
            with self.progress_lock:
                self.agent_models[agent_id] = model
            
            return agent
            
        except Exception as e:
            if not self.silent:
                print(f"⚠️  Failed to create agent {agent_id} with model {model}: {e}")
                print(f"🔄 Falling back to default agent configuration")
            
            # Fallback to default agent
            agent = UniversalAgent(config_path=self.config_path, silent=True)
            
            # Track the fallback model
            with self.progress_lock:
                self.agent_models[agent_id] = agent.provider_config.model
            
            return agent
    
    def decompose_task(self, user_input: str, num_agents: int) -> List[str]:
        """Use AI to dynamically generate different questions based on user input"""
        
        # Create question generation agent
        question_agent = UniversalAgent(config_path=self.config_path, silent=True)
        
        # Get question generation prompt from config
        prompt_template = self.config['orchestrator']['question_generation_prompt']
        generation_prompt = prompt_template.format(
            user_input=user_input,
            num_agents=num_agents
        )
        
        # Remove task completion tool to avoid issues
        question_agent.tools = [tool for tool in question_agent.tools if tool.get('function', {}).get('name') != 'mark_task_complete']
        question_agent.tool_mapping = {name: func for name, func in question_agent.tool_mapping.items() if name != 'mark_task_complete'}
        
        # Note: If tools array becomes empty, the updated call_llm method will handle it properly
        
        try:
            # Get AI-generated questions
            response = question_agent.run(generation_prompt)
            
            # Parse JSON response
            questions = json.loads(response.strip())
            
            # Validate we got the right number of questions
            if len(questions) != num_agents:
                raise ValueError(f"Expected {num_agents} questions, got {len(questions)}")
            
            return questions
            
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: create simple variations if AI fails
            return [
                f"Research comprehensive information about: {user_input}",
                f"Analyze and provide insights about: {user_input}",
                f"Find alternative perspectives on: {user_input}",
                f"Verify and cross-check facts about: {user_input}"
            ][:num_agents]
    
    def update_agent_progress(self, agent_id: int, status: str, result: str = None):
        """Thread-safe progress tracking"""
        with self.progress_lock:
            self.agent_progress[agent_id] = status
            if result is not None:
                self.agent_results[agent_id] = result
    
    def run_agent_parallel(self, agent_id: int, subtask: str) -> Dict[str, Any]:
        """
        Run a single agent with the given subtask.
        Returns result dictionary with agent_id, status, response, model, and cost info.
        """
        agent_model = None
        try:
            if not self.silent:
                print(f"🔄 Agent {agent_id} starting task: {subtask[:50]}...")
            
            self.update_agent_progress(agent_id, "PROCESSING...")
            
            # Get the model for this agent
            agent_model = self._get_agent_model(agent_id)
            
            # Create agent with specific model
            agent = self._create_agent_with_model(agent_id, agent_model)
            
            if not self.silent:
                print(f"⚡ Agent {agent_id} running with model {agent_model}...")
            
            start_time = time.time()
            response = agent.run(subtask)
            execution_time = time.time() - start_time
            
            if not self.silent:
                print(f"✅ Agent {agent_id} completed in {execution_time:.2f}s")
            
            self.update_agent_progress(agent_id, "COMPLETED", response)
            
            # Calculate estimated cost (simplified - in real implementation would track actual tokens)
            estimated_cost = self._estimate_agent_cost(agent_id, agent_model, len(subtask), len(response))
            
            return {
                "agent_id": agent_id,
                "status": "success", 
                "response": response,
                "execution_time": execution_time,
                "model": agent_model,
                "estimated_cost": estimated_cost
            }
            
        except Exception as e:
            # Enhanced error handling with model-specific information
            error_msg = f"Agent {agent_id} error"
            if agent_model:
                error_msg += f" (model: {agent_model})"
            error_msg += f": {str(e)}"
            
            if not self.silent:
                print(f"🚨 {error_msg}")
            
            return {
                "agent_id": agent_id,
                "status": "error",
                "response": error_msg,
                "execution_time": 0,
                "model": agent_model or "unknown",
                "estimated_cost": 0.0
            }
    
    def _estimate_agent_cost(self, agent_id: int, model: str, input_length: int, output_length: int) -> float:
        """Estimate cost for an agent's execution (simplified calculation)."""
        try:
            # Get model cost information
            available_models = self.model_config_manager.get_available_models()
            model_info = next((m for m in available_models if m.id == model), None)
            
            if not model_info or not model_info.input_cost_per_1m or not model_info.output_cost_per_1m:
                return 0.0
            
            # Rough token estimation (4 chars per token average)
            input_tokens = input_length // 4
            output_tokens = output_length // 4
            
            # Calculate cost
            input_cost = (input_tokens / 1_000_000) * model_info.input_cost_per_1m
            output_cost = (output_tokens / 1_000_000) * model_info.output_cost_per_1m
            
            total_cost = input_cost + output_cost
            
            # Track cost for this agent
            with self.progress_lock:
                if agent_id not in self.agent_costs:
                    self.agent_costs[agent_id] = 0.0
                self.agent_costs[agent_id] += total_cost
            
            # Record in cost monitor if enabled
            if self.cost_monitor:
                self.cost_monitor.record_agent_cost(
                    agent_id=agent_id,
                    model=model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=total_cost
                )
            
            return total_cost
            
        except Exception as e:
            if not self.silent:
                print(f"⚠️  Cost estimation failed for agent {agent_id}: {e}")
            return 0.0
    
    def aggregate_results(self, agent_results: List[Dict[str, Any]]) -> str:
        """
        Combine results from all agents into a comprehensive final answer.
        Uses the configured aggregation strategy.
        """
        successful_results = [r for r in agent_results if r["status"] == "success"]
        
        if not successful_results:
            # Log failed agents with their models
            if not self.silent:
                print("🚨 All agents failed:")
                for result in agent_results:
                    model = result.get("model", "unknown")
                    print(f"   Agent {result['agent_id']} ({model}): {result['response']}")
            return "All agents failed to provide results. Please try again."
        
        # Log successful agents
        if not self.silent and len(successful_results) < len(agent_results):
            failed_results = [r for r in agent_results if r["status"] != "success"]
            print(f"⚠️  {len(failed_results)} agent(s) failed:")
            for result in failed_results:
                model = result.get("model", "unknown")
                print(f"   Agent {result['agent_id']} ({model}): {result['response']}")
        
        # Extract responses for aggregation
        responses = [r["response"] for r in successful_results]
        
        if self.aggregation_strategy == "consensus":
            return self._aggregate_consensus(responses, successful_results)
        else:
            # Default to consensus
            return self._aggregate_consensus(responses, successful_results)
    
    def _aggregate_consensus(self, responses: List[str], results: List[Dict[str, Any]]) -> str:
        """
        Use one final AI call to synthesize all agent responses into a coherent answer.
        """
        if len(responses) == 1:
            return responses[0]
        
        # Get synthesis model and create agent
        synthesis_model = self._get_synthesis_model()
        
        try:
            # Create synthesis agent with specific model
            synthesis_agent = self._create_agent_with_model(-1, synthesis_model)  # Use -1 for synthesis agent
            
            if not self.silent:
                print(f"🔄 Synthesis using model: {synthesis_model}")
                
        except Exception as e:
            if not self.silent:
                print(f"⚠️  Failed to create synthesis agent with model {synthesis_model}: {e}")
                print("🔄 Using default synthesis agent")
            # Fallback to default agent
            synthesis_agent = UniversalAgent(config_path=self.config_path, silent=True)
        
        # Build agent responses section
        agent_responses_text = ""
        for i, response in enumerate(responses, 1):
            agent_responses_text += f"=== AGENT {i} RESPONSE ===\n{response}\n\n"
        
        # Get synthesis prompt from config and format it
        synthesis_prompt_template = self.config['orchestrator']['synthesis_prompt']
        synthesis_prompt = synthesis_prompt_template.format(
            num_responses=len(responses),
            agent_responses=agent_responses_text
        )
        
        # Remove task completion tool to avoid premature completion
        synthesis_agent.tools = [tool for tool in synthesis_agent.tools if tool.get('function', {}).get('name') != 'mark_task_complete']
        synthesis_agent.tool_mapping = {name: func for name, func in synthesis_agent.tool_mapping.items() if name != 'mark_task_complete'}
        
        # Ensure we have at least one tool for DeepSeek
        # We need to check if provider is DeepSeek and tools is empty
        # The provider_type should be available from the config
        if not synthesis_agent.tools:
            # Check if we're using DeepSeek provider
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                provider_type = config.get('provider', {}).get('type', '')
            
            if provider_type == "deepseek":
                dummy_tool = {
                    "type": "function",
                    "function": {
                        "name": "dummy_tool",
                        "description": "A dummy tool that does nothing",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                }
                synthesis_agent.tools = [dummy_tool]
        
        # Get the synthesized response
        try:
            print(f"[DEBUG] Calling synthesis_agent.run with {len(synthesis_agent.tools)} tools")
            start_time = time.time()
            final_answer = synthesis_agent.run(synthesis_prompt)
            synthesis_time = time.time() - start_time
            
            # Estimate synthesis cost
            synthesis_cost = self._estimate_agent_cost(-1, synthesis_model, len(synthesis_prompt), len(final_answer))
            
            if not self.silent:
                print(f"[DEBUG] Synthesis successful! Time: {synthesis_time:.2f}s, Cost: ${synthesis_cost:.6f}")
            
            return final_answer
        except Exception as e:
            # Log the error for debugging
            print(f"\n🚨 SYNTHESIS FAILED: {str(e)}")
            print(f"[DEBUG] Tools count at failure: {len(synthesis_agent.tools)}")
            print(f"[DEBUG] Tools at failure: {synthesis_agent.tools}")
            print("📋 Falling back to concatenated responses\n")
            # Fallback: if synthesis fails, concatenate responses
            combined = []
            for i, response in enumerate(responses, 1):
                combined.append(f"=== Agent {i} Response ===")
                combined.append(response)
                combined.append("")
            return "\n".join(combined)
    
    def get_progress_status(self) -> Dict[int, str]:
        """Get current progress status for all agents"""
        with self.progress_lock:
            return self.agent_progress.copy()
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution including models used and costs."""
        with self.progress_lock:
            total_cost = sum(self.agent_costs.values())
            
            return {
                "agent_models": self.agent_models.copy(),
                "agent_costs": self.agent_costs.copy(),
                "total_estimated_cost": total_cost,
                "multi_model_enabled": self.multi_model_config is not None,
                "synthesis_model": self._get_synthesis_model() if self.multi_model_config else None
            }
    
    def log_execution_summary(self):
        """Log a summary of the execution with model and cost information."""
        if self.silent:
            return
            
        summary = self.get_execution_summary()
        
        print("\n" + "="*60)
        print("🎯 EXECUTION SUMMARY")
        print("="*60)
        
        if summary["multi_model_enabled"]:
            print("🔧 Multi-model configuration: ENABLED")
            print(f"🧠 Models used:")
            for agent_id, model in summary["agent_models"].items():
                if agent_id == -1:
                    print(f"   Synthesis: {model}")
                else:
                    print(f"   Agent {agent_id}: {model}")
            
            print(f"💰 Cost breakdown:")
            for agent_id, cost in summary["agent_costs"].items():
                if agent_id == -1:
                    print(f"   Synthesis: ${cost:.6f}")
                else:
                    print(f"   Agent {agent_id}: ${cost:.6f}")
            
            print(f"💵 Total estimated cost: ${summary['total_estimated_cost']:.6f}")
        else:
            print("🔧 Multi-model configuration: DISABLED")
            print("🧠 Using default model for all agents")
        
        # Add cost monitoring summary if enabled
        if self.cost_monitor:
            cost_summary = self.cost_monitor.get_cost_summary()
            print(f"📊 Cost Monitoring:")
            print(f"   Budget limit: ${cost_summary['budget_limit']:.6f}")
            print(f"   Budget remaining: ${cost_summary['budget_remaining']:.6f}")
            print(f"   Budget usage: {cost_summary['budget_usage_percentage']:.1f}%")
            
            if cost_summary['alerts_triggered']:
                print(f"   Alerts triggered: {len(cost_summary['alerts_triggered'])}")
                for alert in cost_summary['alerts_triggered']:
                    print(f"     - {alert.alert_type}: {alert.message}")
        
        print("="*60)
    
    def orchestrate(self, user_input: str):
        """
        Main orchestration method.
        Takes user input, delegates to parallel agents, and returns aggregated result.
        """
        
        # Start cost monitoring if enabled
        if self.cost_monitor:
            self.cost_monitor.start_monitoring()
        
        try:
            # Reset progress tracking
            self.agent_progress = {}
            self.agent_results = {}
            
            # Decompose task into subtasks
            subtasks = self.decompose_task(user_input, self.num_agents)
            
            # Initialize progress tracking
            for i in range(self.num_agents):
                self.agent_progress[i] = "QUEUED"
            
            # Execute agents in parallel
            agent_results = []
            
            with ThreadPoolExecutor(max_workers=self.num_agents) as executor:
                # Submit all agent tasks
                future_to_agent = {
                    executor.submit(self.run_agent_parallel, i, subtasks[i]): i 
                    for i in range(self.num_agents)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_agent, timeout=self.task_timeout):
                    try:
                        result = future.result()
                        agent_results.append(result)
                    except Exception as e:
                        agent_id = future_to_agent[future]
                        agent_results.append({
                            "agent_id": agent_id,
                            "status": "timeout",
                            "response": f"Agent {agent_id + 1} timed out or failed: {str(e)}",
                            "execution_time": self.task_timeout
                        })
            
            # Sort results by agent_id for consistent output
            agent_results.sort(key=lambda x: x["agent_id"])
            
            # Aggregate results
            final_result = self.aggregate_results(agent_results)
            
            # Log execution summary
            self.log_execution_summary()
            
            return final_result
            
        finally:
            # Stop cost monitoring
            if self.cost_monitor:
                self.cost_monitor.stop_monitoring()