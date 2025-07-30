"""
Configuration management system for Make It Heavy framework.
Supports multiple providers (OpenRouter, DeepSeek) with validation.
"""

import yaml
import os
from typing import Dict, Any, List
from dataclasses import dataclass, field


class ConfigurationError(Exception):
    """Configuration-related errors"""
    pass


@dataclass
class ProviderConfig:
    """Provider configuration data model"""
    provider_type: str
    api_key: str
    base_url: str
    model: str
    additional_params: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validates the configuration for the specific provider"""
        if not self.api_key:
            raise ConfigurationError(f"API key is required for {self.provider_type}")
        if not self.base_url:
            raise ConfigurationError(f"Base URL is required for {self.provider_type}")
        if not self.model:
            raise ConfigurationError(f"Model is required for {self.provider_type}")
        return True
    
    def to_openai_config(self) -> Dict[str, str]:
        """Converts to OpenAI client configuration format"""
        return {
            "api_key": self.api_key,
            "base_url": self.base_url
        }


class ConfigurationManager:
    """Manages configuration loading and validation for multiple providers"""
    
    SUPPORTED_PROVIDERS = ["openrouter", "deepseek"]
    
    def __init__(self):
        self.config = None
        self.config_path = None
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not os.path.exists(config_path):
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self.config_path = config_path
            return self.config
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {e}")
    
    def get_provider_config(self) -> ProviderConfig:
        """Get the active provider configuration"""
        if not self.config:
            raise ConfigurationError("Configuration not loaded")
        
        # Check if new format with provider selection
        if 'provider' in self.config:
            provider_type = self.config['provider']['type']
            if provider_type not in self.SUPPORTED_PROVIDERS:
                raise ConfigurationError(f"Unsupported provider: {provider_type}")
            
            provider_config = self.config.get(provider_type, {})
            return ProviderConfig(
                provider_type=provider_type,
                api_key=provider_config.get('api_key', ''),
                base_url=provider_config.get('base_url', ''),
                model=provider_config.get('model', ''),
                additional_params=provider_config
            )
        
        # Fallback to legacy OpenRouter format for backward compatibility
        elif 'openrouter' in self.config:
            openrouter_config = self.config['openrouter']
            return ProviderConfig(
                provider_type='openrouter',
                api_key=openrouter_config.get('api_key', ''),
                base_url=openrouter_config.get('base_url', ''),
                model=openrouter_config.get('model', ''),
                additional_params=openrouter_config
            )
        
        else:
            raise ConfigurationError("No valid provider configuration found")
    
    def validate_provider_config(self, provider_type: str) -> bool:
        """Validates provider-specific configuration"""
        if provider_type not in self.SUPPORTED_PROVIDERS:
            raise ConfigurationError(f"Unsupported provider: {provider_type}")
        
        provider_config = self.get_provider_config()
        if provider_config.provider_type != provider_type:
            raise ConfigurationError(f"Expected {provider_type}, got {provider_config.provider_type}")
        
        return provider_config.validate()
    
    def get_active_provider(self) -> str:
        """Returns the active provider type"""
        provider_config = self.get_provider_config()
        return provider_config.provider_type
    
    def get_system_prompt(self) -> str:
        """Get system prompt from configuration"""
        if not self.config:
            raise ConfigurationError("Configuration not loaded")
        return self.config.get('system_prompt', '')
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent-specific configuration"""
        if not self.config:
            raise ConfigurationError("Configuration not loaded")
        return self.config.get('agent', {})
    
    def get_orchestrator_config(self) -> Dict[str, Any]:
        """Get orchestrator-specific configuration"""
        if not self.config:
            raise ConfigurationError("Configuration not loaded")
        return self.config.get('orchestrator', {})
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search tool configuration"""
        if not self.config:
            raise ConfigurationError("Configuration not loaded")
        return self.config.get('search', {})
    
    def get_multi_model_config(self) -> Dict[str, Any]:
        """Get multi-model configuration for agents"""
        if not self.config:
            raise ConfigurationError("Configuration not loaded")
        return self.config.get('multi_model', {})
    
    def has_multi_model_config(self) -> bool:
        """Check if multi-model configuration exists"""
        if not self.config:
            return False
        return 'multi_model' in self.config and bool(self.config['multi_model'])
    
    def get_agent_model(self, agent_id: int, default_model: str = None) -> str:
        """Get model for specific agent ID from multi-model config"""
        multi_model_config = self.get_multi_model_config()
        
        if not multi_model_config:
            # Fallback to default provider model
            return default_model or self.get_provider_config().model
        
        agent_model_key = f'agent_{agent_id}_model'
        agent_model = multi_model_config.get(agent_model_key)
        
        if agent_model:
            return agent_model
        
        # Fallback to default model from multi-model config or provider config
        return multi_model_config.get('default_model') or default_model or self.get_provider_config().model
    
    def get_synthesis_model(self, default_model: str = None) -> str:
        """Get model for synthesis from multi-model config"""
        multi_model_config = self.get_multi_model_config()
        
        if not multi_model_config:
            return default_model or self.get_provider_config().model
        
        return multi_model_config.get('synthesis_model') or multi_model_config.get('default_model') or default_model or self.get_provider_config().model
    
    def save_multi_model_config(self, multi_model_config: Dict[str, Any]) -> bool:
        """Save multi-model configuration to the config file"""
        if not self.config_path:
            raise ConfigurationError("No config file path available")
        
        try:
            # Update in-memory config
            if not self.config:
                self.config = {}
            self.config['multi_model'] = multi_model_config
            
            # Write to file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            
            return True
        except Exception as e:
            raise ConfigurationError(f"Failed to save multi-model configuration: {e}")
    
    def remove_multi_model_config(self) -> bool:
        """Remove multi-model configuration from config file"""
        if not self.config_path:
            raise ConfigurationError("No config file path available")
        
        try:
            if self.config and 'multi_model' in self.config:
                del self.config['multi_model']
                
                # Write to file
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            
            return True
        except Exception as e:
            raise ConfigurationError(f"Failed to remove multi-model configuration: {e}")


def validate_deepseek_config(config: Dict[str, Any]) -> bool:
    """Validate DeepSeek-specific configuration"""
    required_fields = ['api_key', 'base_url', 'model']
    
    for field in required_fields:
        if not config.get(field):
            raise ConfigurationError(f"DeepSeek configuration missing required field: {field}")
    
    # Validate DeepSeek-specific values
    if config['base_url'] != 'https://api.deepseek.com':
        raise ConfigurationError("DeepSeek base_url should be 'https://api.deepseek.com'")
    
    valid_models = ['deepseek-chat', 'deepseek-reasoner']
    if config['model'] not in valid_models:
        raise ConfigurationError(f"DeepSeek model must be one of: {valid_models}")
    
    return True


def validate_openrouter_config(config: Dict[str, Any]) -> bool:
    """Validate OpenRouter-specific configuration"""
    required_fields = ['api_key', 'base_url', 'model']
    
    for field in required_fields:
        if not config.get(field):
            raise ConfigurationError(f"OpenRouter configuration missing required field: {field}")
    
    # Validate OpenRouter-specific values
    valid_base_urls = ['https://openrouter.ai/api/v1', 'https://openrouter.ai/api/v1/']
    if config['base_url'] not in valid_base_urls:
        raise ConfigurationError("OpenRouter base_url should be 'https://openrouter.ai/api/v1'")
    
    return True