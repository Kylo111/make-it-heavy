"""
Service for calculating model costs and estimates.
"""

from typing import Dict, List, Optional
from .data_models import ModelInfo, AgentModelConfig, CostEstimate, CostInfo
from .provider_model_service import ProviderModelService


class CostCalculationServiceError(Exception):
    """Exception for cost calculation errors."""
    pass


class CostCalculationService:
    """Service for calculating model costs and providing estimates."""
    
    def __init__(self, provider_service: ProviderModelService):
        self.provider_service = provider_service
        
        # Typical token usage estimates for different agent roles
        self.agent_token_estimates = {
            0: {'input': 2000, 'output': 800},   # Research agent - more input processing
            1: {'input': 1500, 'output': 1000},  # Analysis agent - balanced
            2: {'input': 1200, 'output': 600},   # Verification agent - focused output
            3: {'input': 1800, 'output': 900},   # Alternatives agent - comprehensive
            'synthesis': {'input': 3000, 'output': 1200}  # Synthesis - processes all responses
        }
    
    def calculate_configuration_cost(
        self, 
        config: AgentModelConfig, 
        available_models: List[ModelInfo]
    ) -> CostEstimate:
        """Calculate estimated cost for a complete agent configuration."""
        model_map = {model.id: model for model in available_models}
        
        total_input_tokens = 0
        total_output_tokens = 0
        total_cost = 0.0
        per_agent_costs = {}
        breakdown = {}
        
        # Calculate cost for each agent
        for agent_id in range(4):
            model_id = config.get_agent_model(agent_id)
            model_info = model_map.get(model_id)
            
            if not model_info:
                raise CostCalculationServiceError(f"Model {model_id} not found for agent {agent_id}")
            
            # Get token estimates for this agent
            token_est = self.agent_token_estimates[agent_id]
            input_tokens = token_est['input']
            output_tokens = token_est['output']
            
            # Calculate cost for this agent
            agent_cost = self._calculate_model_cost(
                model_info, input_tokens, output_tokens
            )
            
            per_agent_costs[agent_id] = agent_cost
            breakdown[f"Agent {agent_id} ({model_id})"] = agent_cost
            
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_cost += agent_cost
        
        # Calculate synthesis cost
        synthesis_model_id = config.synthesis_model
        synthesis_model = model_map.get(synthesis_model_id)
        
        if synthesis_model:
            synthesis_tokens = self.agent_token_estimates['synthesis']
            synthesis_cost = self._calculate_model_cost(
                synthesis_model, 
                synthesis_tokens['input'], 
                synthesis_tokens['output']
            )
            
            breakdown[f"Synthesis ({synthesis_model_id})"] = synthesis_cost
            total_input_tokens += synthesis_tokens['input']
            total_output_tokens += synthesis_tokens['output']
            total_cost += synthesis_cost
        
        return CostEstimate(
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_cost=total_cost,
            per_agent_costs=per_agent_costs,
            breakdown=breakdown
        )
    
    def calculate_model_cost_per_query(
        self, 
        model_info: ModelInfo, 
        estimated_input_tokens: int = 2000, 
        estimated_output_tokens: int = 800
    ) -> float:
        """Calculate estimated cost per query for a specific model."""
        return self._calculate_model_cost(model_info, estimated_input_tokens, estimated_output_tokens)
    
    def compare_configurations(
        self, 
        config1: AgentModelConfig, 
        config2: AgentModelConfig, 
        available_models: List[ModelInfo]
    ) -> Dict[str, float]:
        """Compare costs between two configurations."""
        cost1 = self.calculate_configuration_cost(config1, available_models)
        cost2 = self.calculate_configuration_cost(config2, available_models)
        
        return {
            'config1_cost': cost1.total_cost,
            'config2_cost': cost2.total_cost,
            'difference': cost2.total_cost - cost1.total_cost,
            'percentage_change': ((cost2.total_cost - cost1.total_cost) / cost1.total_cost) * 100 if cost1.total_cost > 0 else 0
        }
    
    def get_cheapest_configuration(self, available_models: List[ModelInfo]) -> AgentModelConfig:
        """Generate the cheapest possible configuration."""
        function_calling_models = [m for m in available_models if m.supports_function_calling]
        
        if not function_calling_models:
            raise CostCalculationServiceError("No models with function calling support available")
        
        # Find cheapest model with cost data
        models_with_cost = [m for m in function_calling_models if m.input_cost_per_1m is not None]
        
        if models_with_cost:
            cheapest_model = min(models_with_cost, key=lambda x: x.input_cost_per_1m or float('inf'))
        else:
            # Fallback to first available model
            cheapest_model = function_calling_models[0]
        
        return AgentModelConfig(
            agent_0_model=cheapest_model.id,
            agent_1_model=cheapest_model.id,
            agent_2_model=cheapest_model.id,
            agent_3_model=cheapest_model.id,
            synthesis_model=cheapest_model.id,
            default_model=cheapest_model.id,
            profile_name="budget"
        )
    
    def get_premium_configuration(self, available_models: List[ModelInfo]) -> AgentModelConfig:
        """Generate the most capable (expensive) configuration."""
        function_calling_models = [m for m in available_models if m.supports_function_calling]
        
        if not function_calling_models:
            raise CostCalculationServiceError("No models with function calling support available")
        
        # Find most expensive model with cost data
        models_with_cost = [m for m in function_calling_models if m.input_cost_per_1m is not None]
        
        if models_with_cost:
            premium_model = max(models_with_cost, key=lambda x: x.input_cost_per_1m or 0)
        else:
            # Fallback to first available model
            premium_model = function_calling_models[0]
        
        return AgentModelConfig(
            agent_0_model=premium_model.id,
            agent_1_model=premium_model.id,
            agent_2_model=premium_model.id,
            agent_3_model=premium_model.id,
            synthesis_model=premium_model.id,
            default_model=premium_model.id,
            profile_name="premium"
        )
    
    def get_balanced_configuration(self, available_models: List[ModelInfo]) -> AgentModelConfig:
        """Generate a balanced cost/performance configuration."""
        function_calling_models = [m for m in available_models if m.supports_function_calling]
        
        if not function_calling_models:
            raise CostCalculationServiceError("No models with function calling support available")
        
        # Find middle-range model
        models_with_cost = [m for m in function_calling_models if m.input_cost_per_1m is not None]
        
        if models_with_cost:
            # Sort by cost and pick middle
            models_with_cost.sort(key=lambda x: x.input_cost_per_1m or 0)
            mid_index = len(models_with_cost) // 2
            balanced_model = models_with_cost[mid_index]
        else:
            # Fallback to first available model
            balanced_model = function_calling_models[0]
        
        return AgentModelConfig(
            agent_0_model=balanced_model.id,
            agent_1_model=balanced_model.id,
            agent_2_model=balanced_model.id,
            agent_3_model=balanced_model.id,
            synthesis_model=balanced_model.id,
            default_model=balanced_model.id,
            profile_name="balanced"
        )
    
    def estimate_monthly_cost(
        self, 
        config: AgentModelConfig, 
        available_models: List[ModelInfo], 
        queries_per_day: int = 10
    ) -> Dict[str, float]:
        """Estimate monthly cost based on usage patterns."""
        daily_cost = self.calculate_configuration_cost(config, available_models)
        
        return {
            'cost_per_query': daily_cost.total_cost,
            'daily_cost': daily_cost.total_cost * queries_per_day,
            'weekly_cost': daily_cost.total_cost * queries_per_day * 7,
            'monthly_cost': daily_cost.total_cost * queries_per_day * 30
        }
    
    def _calculate_model_cost(
        self, 
        model_info: ModelInfo, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """Calculate cost for a specific model and token usage."""
        if model_info.input_cost_per_1m is None or model_info.output_cost_per_1m is None:
            return 0.0
        
        # Convert tokens to millions for cost calculation
        input_cost = (input_tokens / 1_000_000) * model_info.input_cost_per_1m
        output_cost = (output_tokens / 1_000_000) * model_info.output_cost_per_1m
        
        return input_cost + output_cost
    
    def get_cost_breakdown_by_agent(
        self, 
        config: AgentModelConfig, 
        available_models: List[ModelInfo]
    ) -> Dict[str, Dict[str, float]]:
        """Get detailed cost breakdown by agent."""
        model_map = {model.id: model for model in available_models}
        breakdown = {}
        
        # Agent costs
        for agent_id in range(4):
            model_id = config.get_agent_model(agent_id)
            model_info = model_map.get(model_id)
            
            if model_info:
                token_est = self.agent_token_estimates[agent_id]
                cost = self._calculate_model_cost(
                    model_info, token_est['input'], token_est['output']
                )
                
                breakdown[f"Agent {agent_id}"] = {
                    'model': model_id,
                    'input_tokens': token_est['input'],
                    'output_tokens': token_est['output'],
                    'cost': cost,
                    'input_cost': (token_est['input'] / 1_000_000) * (model_info.input_cost_per_1m or 0),
                    'output_cost': (token_est['output'] / 1_000_000) * (model_info.output_cost_per_1m or 0)
                }
        
        # Synthesis cost
        synthesis_model = model_map.get(config.synthesis_model)
        if synthesis_model:
            synthesis_tokens = self.agent_token_estimates['synthesis']
            synthesis_cost = self._calculate_model_cost(
                synthesis_model, synthesis_tokens['input'], synthesis_tokens['output']
            )
            
            breakdown['Synthesis'] = {
                'model': config.synthesis_model,
                'input_tokens': synthesis_tokens['input'],
                'output_tokens': synthesis_tokens['output'],
                'cost': synthesis_cost,
                'input_cost': (synthesis_tokens['input'] / 1_000_000) * (synthesis_model.input_cost_per_1m or 0),
                'output_cost': (synthesis_tokens['output'] / 1_000_000) * (synthesis_model.output_cost_per_1m or 0)
            }
        
        return breakdown