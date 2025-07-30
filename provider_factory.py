"""
Provider client factory for Make It Heavy framework.
Creates appropriate OpenAI clients for different providers.
"""

from typing import Dict, List
from openai import OpenAI
from config_manager import ProviderConfig, ConfigurationError, validate_deepseek_config, validate_openrouter_config


class ProviderError(Exception):
    """Base class for provider-specific errors"""
    pass


class DeepSeekAPIError(ProviderError):
    """DeepSeek-specific API errors"""
    pass


class OpenRouterAPIError(ProviderError):
    """OpenRouter-specific API errors"""
    pass


class ProviderClientFactory:
    """Factory for creating provider-specific OpenAI clients"""
    
    SUPPORTED_PROVIDERS = ["openrouter", "deepseek"]
    
    @staticmethod
    def create_client(provider_config: ProviderConfig) -> OpenAI:
        """Creates appropriate OpenAI client for the specified provider"""
        try:
            # Validate configuration first
            ProviderClientFactory.validate_provider_config(
                provider_config.provider_type, 
                provider_config.additional_params
            )
            
            # Create OpenAI client with provider-specific configuration
            client = OpenAI(
                api_key=provider_config.api_key,
                base_url=provider_config.base_url
            )
            
            return client
            
        except Exception as e:
            provider_type = provider_config.provider_type
            if provider_type == "deepseek":
                raise DeepSeekAPIError(f"Failed to create DeepSeek client: {str(e)}")
            elif provider_type == "openrouter":
                raise OpenRouterAPIError(f"Failed to create OpenRouter client: {str(e)}")
            else:
                raise ProviderError(f"Failed to create client for {provider_type}: {str(e)}")
    
    @staticmethod
    def get_supported_providers() -> List[str]:
        """Returns list of supported providers"""
        return ProviderClientFactory.SUPPORTED_PROVIDERS.copy()
    
    @staticmethod
    def validate_provider_config(provider_type: str, config: Dict) -> bool:
        """Validates provider-specific configuration"""
        if provider_type not in ProviderClientFactory.SUPPORTED_PROVIDERS:
            raise ConfigurationError(f"Unsupported provider: {provider_type}")
        
        if provider_type == "deepseek":
            return validate_deepseek_config(config)
        elif provider_type == "openrouter":
            return validate_openrouter_config(config)
        
        return True
    
    @staticmethod
    def get_provider_info(provider_type: str) -> Dict[str, str]:
        """Get information about a specific provider"""
        provider_info = {
            "deepseek": {
                "name": "DeepSeek",
                "description": "DeepSeek AI API with competitive pricing",
                "base_url": "https://api.deepseek.com",
                "models": "deepseek-chat, deepseek-reasoner",
                "features": "Function calling, JSON output, competitive pricing"
            },
            "openrouter": {
                "name": "OpenRouter",
                "description": "OpenRouter API with access to multiple models",
                "base_url": "https://openrouter.ai/api/v1",
                "models": "Various (GPT-4, Claude, Gemini, etc.)",
                "features": "Multiple model access, function calling"
            }
        }
        
        return provider_info.get(provider_type, {})
    
    @staticmethod
    def get_model_info(provider_type: str, model_name: str) -> Dict[str, any]:
        """Get information about a specific model"""
        model_info = {
            "deepseek": {
                "deepseek-chat": {
                    "name": "DeepSeek-V3",
                    "context_window": 64000,
                    "supports_function_calling": True,
                    "supports_json_output": True,
                    "cost_per_1m_input_tokens": 0.27,
                    "cost_per_1m_output_tokens": 1.10,
                    "special_features": ["Context caching", "Off-peak pricing"]
                },
                "deepseek-reasoner": {
                    "name": "DeepSeek-R1",
                    "context_window": 64000,
                    "supports_function_calling": True,
                    "supports_json_output": True,
                    "cost_per_1m_input_tokens": 0.55,
                    "cost_per_1m_output_tokens": 2.19,
                    "special_features": ["Advanced reasoning", "Context caching", "Off-peak pricing"]
                }
            },
            "openrouter": {
                # OpenRouter models vary, so we provide generic info
                "default": {
                    "name": "Various Models",
                    "context_window": "Varies by model",
                    "supports_function_calling": True,
                    "supports_json_output": True,
                    "cost_per_1m_input_tokens": "Varies by model",
                    "cost_per_1m_output_tokens": "Varies by model",
                    "special_features": ["Multiple model access"]
                }
            }
        }
        
        provider_models = model_info.get(provider_type, {})
        return provider_models.get(model_name, provider_models.get("default", {}))


def create_client_from_config(config_dict: Dict) -> OpenAI:
    """Convenience function to create client directly from config dictionary"""
    from config_manager import ConfigurationManager
    
    # Create temporary config manager
    config_manager = ConfigurationManager()
    config_manager.config = config_dict
    
    # Get provider config and create client
    provider_config = config_manager.get_provider_config()
    return ProviderClientFactory.create_client(provider_config)