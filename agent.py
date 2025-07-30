import json
import yaml
from openai import OpenAI
from tools import discover_tools
from config_manager import ConfigurationManager, ConfigurationError
from provider_factory import ProviderClientFactory, ProviderError, DeepSeekAPIError, OpenRouterAPIError

class UniversalAgent:
    """Universal agent that works with any OpenAI-compatible provider (OpenRouter, DeepSeek, etc.)"""
    
    def __init__(self, config_path="config.yaml", silent=False):
        # Silent mode for orchestrator (suppresses debug output)
        self.silent = silent
        
        try:
            # Load configuration using ConfigurationManager
            self.config_manager = ConfigurationManager()
            self.config = self.config_manager.load_config(config_path)
            
            # Get provider configuration
            self.provider_config = self.config_manager.get_provider_config()
            self.provider_type = self.provider_config.provider_type
            
            # Create provider-specific client
            self.client = ProviderClientFactory.create_client(self.provider_config)
            
            # Get provider and model information
            self.provider_info = ProviderClientFactory.get_provider_info(self.provider_type)
            self.model_info = ProviderClientFactory.get_model_info(self.provider_type, self.provider_config.model)
            
            if not self.silent:
                print(f"🤖 Initialized {self.provider_info.get('name', self.provider_type)} Agent")
                print(f"📡 Provider: {self.provider_type}")
                print(f"🧠 Model: {self.provider_config.model}")
                if self.model_info.get('name'):
                    print(f"📋 Model Name: {self.model_info['name']}")
            
        except (ConfigurationError, ProviderError) as e:
            raise Exception(f"Agent initialization failed: {str(e)}")
        
        # Discover tools dynamically
        self.discovered_tools = discover_tools(self.config, silent=self.silent)
        
        # Build tools array (compatible with OpenAI format)
        self.tools = [tool.to_openrouter_schema() for tool in self.discovered_tools.values()]
        
        # Build tool mapping
        self.tool_mapping = {name: tool.execute for name, tool in self.discovered_tools.items()}
    
    
    def call_llm(self, messages):
        """Make API call with tools (works with any OpenAI-compatible provider)"""
        try:
            # Prepare API call parameters
            api_params = {
                "model": self.provider_config.model,
                "messages": messages
            }
            
            # For DeepSeek, ensure tools array is never empty by adding a dummy tool if needed
            if self.provider_type == "deepseek":
                if self.tools:
                    api_params["tools"] = self.tools
                else:
                    # Add a dummy tool for DeepSeek when no real tools are available
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
                    api_params["tools"] = [dummy_tool]
            elif self.tools:
                api_params["tools"] = self.tools
            
            response = self.client.chat.completions.create(**api_params)
            return response
        except Exception as e:
            # Provide provider-specific error messages
            if self.provider_type == "deepseek":
                error_msg = f"DeepSeek API call failed: {str(e)}"
                if "api_key" in str(e).lower():
                    error_msg += "\n💡 Check your DeepSeek API key in the configuration file"
                elif "rate" in str(e).lower():
                    error_msg += "\n💡 DeepSeek rate limit reached. Try again later or during off-peak hours (16:30-00:30 UTC)"
                raise DeepSeekAPIError(error_msg)
            elif self.provider_type == "openrouter":
                error_msg = f"OpenRouter API call failed: {str(e)}"
                if "api_key" in str(e).lower():
                    error_msg += "\n💡 Check your OpenRouter API key in the configuration file"
                raise OpenRouterAPIError(error_msg)
            else:
                raise Exception(f"LLM call failed: {str(e)}")
    
    def handle_tool_call(self, tool_call):
        """Handle a tool call and return the result message"""
        try:
            # Extract tool name and arguments
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # Call appropriate tool from tool_mapping
            if tool_name in self.tool_mapping:
                tool_result = self.tool_mapping[tool_name](**tool_args)
            else:
                tool_result = {"error": f"Unknown tool: {tool_name}"}
            
            # Return tool result message
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps(tool_result)
            }
        
        except Exception as e:
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps({"error": f"Tool execution failed: {str(e)}"})
            }
    
    def get_provider_info(self) -> dict:
        """Get information about the current provider and model"""
        return {
            "provider_type": self.provider_type,
            "provider_name": self.provider_info.get('name', self.provider_type),
            "model": self.provider_config.model,
            "model_name": self.model_info.get('name', self.provider_config.model),
            "base_url": self.provider_config.base_url,
            "supports_function_calling": self.model_info.get('supports_function_calling', True),
            "context_window": self.model_info.get('context_window', 'Unknown')
        }
    
    def run(self, user_input: str):
        """Run the agent with user input and return FULL conversation content"""
        # Initialize messages with system prompt and user input
        system_prompt = self.config_manager.get_system_prompt()
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
        
        # Track all assistant responses for full content capture
        full_response_content = []
        
        # Get agent configuration
        agent_config = self.config_manager.get_agent_config()
        max_iterations = agent_config.get('max_iterations', 10)
        iteration = 0
        
        # Remove dummy tool addition - handle empty tools at API call level instead
        # The dummy tool was interfering with normal agent operation
        
        while iteration < max_iterations:
            iteration += 1
            if not self.silent:
                print(f"🔄 Agent iteration {iteration}/{max_iterations}")
            
            # Call LLM
            response = self.call_llm(messages)
            
            # Add the response to messages
            assistant_message = response.choices[0].message
            message_dict = {
                "role": "assistant",
                "content": assistant_message.content
            }
            
            # Only add tool_calls if they exist
            if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                message_dict["tool_calls"] = assistant_message.tool_calls
                
            messages.append(message_dict)
            
            # Capture assistant content for full response
            # If content is empty but there are tool calls, use the tool call arguments as content
            if assistant_message.content:
                full_response_content.append(assistant_message.content)
            elif hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                # Extract content from tool calls, particularly the mark_task_complete tool
                for tool_call in assistant_message.tool_calls:
                    if tool_call.function.name == "mark_task_complete":
                        try:
                            args = json.loads(tool_call.function.arguments)
                            if 'completion_message' in args:
                                full_response_content.append(args['completion_message'])
                            elif 'task_summary' in args:
                                full_response_content.append(args['task_summary'])
                        except:
                            pass
            
            # Check if there are tool calls
            if assistant_message.tool_calls:
                if not self.silent:
                    print(f"🔧 Agent making {len(assistant_message.tool_calls)} tool call(s)")
                # Handle each tool call
                task_completed = False
                for tool_call in assistant_message.tool_calls:
                    if not self.silent:
                        print(f"   📞 Calling tool: {tool_call.function.name}")
                    tool_result = self.handle_tool_call(tool_call)
                    messages.append(tool_result)
                    
                    # Check if this was the task completion tool
                    if tool_call.function.name == "mark_task_complete":
                        task_completed = True
                        if not self.silent:
                            print("✅ Task completion tool called - exiting loop")
                        # Extract final message from tool arguments
                        try:
                            args = json.loads(tool_call.function.arguments)
                            if 'completion_message' in args:
                                full_response_content.append(args['completion_message'])
                            elif 'task_summary' in args:
                                full_response_content.append(args['task_summary'])
                        except:
                            pass
                        # Return FULL conversation content
                        return "\n\n".join(full_response_content)
                
                # If task was completed, we already returned above
                if task_completed:
                    return "\n\n".join(full_response_content)
            else:
                if not self.silent:
                    print("💭 Agent responded without tool calls - continuing loop")
            
            # Continue the loop regardless of whether there were tool calls or not
        
        # If max iterations reached, return whatever content we gathered
        return "\n\n".join(full_response_content) if full_response_content else "Maximum iterations reached. The agent may be stuck in a loop."

# Backward compatibility: OpenRouterAgent is now an alias for UniversalAgent
class OpenRouterAgent(UniversalAgent):
    """
    Backward compatibility class. 
    OpenRouterAgent is now an alias for UniversalAgent.
    """
    
    def __init__(self, config_path="config.yaml", silent=False):
        # Check if this is a legacy config file (has 'openrouter' key but no 'provider' key)
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # If it's a legacy config, we need to handle it specially
            if 'openrouter' in config and 'provider' not in config:
                if not silent:
                    print("⚠️  Using legacy OpenRouter configuration format")
                    print("💡 Consider updating to the new universal configuration format")
        except Exception:
            pass  # If we can't read the config, let UniversalAgent handle the error
        
        # Initialize as UniversalAgent
        super().__init__(config_path, silent)


# For convenience, create an alias
Agent = UniversalAgent