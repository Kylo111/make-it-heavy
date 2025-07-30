"""
Unit tests for configuration management and provider factory.
"""

import pytest
import tempfile
import os
import yaml
from unittest.mock import patch, MagicMock

from config_manager import (
    ConfigurationManager, 
    ProviderConfig, 
    ConfigurationError,
    validate_deepseek_config,
    validate_openrouter_config
)
from provider_factory import (
    ProviderClientFactory,
    ProviderError,
    DeepSeekAPIError,
    OpenRouterAPIError,
    create_client_from_config
)


class TestProviderConfig:
    """Test ProviderConfig data class"""
    
    def test_provider_config_creation(self):
        """Test creating a ProviderConfig instance"""
        config = ProviderConfig(
            provider_type="deepseek",
            api_key="test-key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat"
        )
        
        assert config.provider_type == "deepseek"
        assert config.api_key == "test-key"
        assert config.base_url == "https://api.deepseek.com"
        assert config.model == "deepseek-chat"
    
    def test_provider_config_validation_success(self):
        """Test successful validation"""
        config = ProviderConfig(
            provider_type="deepseek",
            api_key="test-key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat"
        )
        
        assert config.validate() is True
    
    def test_provider_config_validation_missing_api_key(self):
        """Test validation failure with missing API key"""
        config = ProviderConfig(
            provider_type="deepseek",
            api_key="",
            base_url="https://api.deepseek.com",
            model="deepseek-chat"
        )
        
        with pytest.raises(ConfigurationError, match="API key is required"):
            config.validate()
    
    def test_to_openai_config(self):
        """Test conversion to OpenAI config format"""
        config = ProviderConfig(
            provider_type="deepseek",
            api_key="test-key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat"
        )
        
        openai_config = config.to_openai_config()
        expected = {
            "api_key": "test-key",
            "base_url": "https://api.deepseek.com"
        }
        
        assert openai_config == expected


class TestConfigurationManager:
    """Test ConfigurationManager class"""
    
    def create_temp_config(self, config_data):
        """Helper to create temporary config file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(config_data, temp_file)
        temp_file.close()
        return temp_file.name
    
    def test_load_config_success(self):
        """Test successful config loading"""
        config_data = {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'test-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            }
        }
        
        config_path = self.create_temp_config(config_data)
        
        try:
            manager = ConfigurationManager()
            loaded_config = manager.load_config(config_path)
            
            assert loaded_config == config_data
            assert manager.config == config_data
        finally:
            os.unlink(config_path)
    
    def test_load_config_file_not_found(self):
        """Test config loading with non-existent file"""
        manager = ConfigurationManager()
        
        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            manager.load_config("non_existent_file.yaml")
    
    def test_get_provider_config_new_format(self):
        """Test getting provider config with new format"""
        config_data = {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'test-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            }
        }
        
        manager = ConfigurationManager()
        manager.config = config_data
        
        provider_config = manager.get_provider_config()
        
        assert provider_config.provider_type == 'deepseek'
        assert provider_config.api_key == 'test-key'
        assert provider_config.base_url == 'https://api.deepseek.com'
        assert provider_config.model == 'deepseek-chat'
    
    def test_get_provider_config_legacy_format(self):
        """Test getting provider config with legacy OpenRouter format"""
        config_data = {
            'openrouter': {
                'api_key': 'test-key',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'openai/gpt-4.1-mini'
            }
        }
        
        manager = ConfigurationManager()
        manager.config = config_data
        
        provider_config = manager.get_provider_config()
        
        assert provider_config.provider_type == 'openrouter'
        assert provider_config.api_key == 'test-key'
        assert provider_config.base_url == 'https://openrouter.ai/api/v1'
        assert provider_config.model == 'openai/gpt-4.1-mini'
    
    def test_get_active_provider(self):
        """Test getting active provider"""
        config_data = {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'test-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            }
        }
        
        manager = ConfigurationManager()
        manager.config = config_data
        
        assert manager.get_active_provider() == 'deepseek'


class TestProviderValidation:
    """Test provider-specific validation functions"""
    
    def test_validate_deepseek_config_success(self):
        """Test successful DeepSeek config validation"""
        config = {
            'api_key': 'test-key',
            'base_url': 'https://api.deepseek.com',
            'model': 'deepseek-chat'
        }
        
        assert validate_deepseek_config(config) is True
    
    def test_validate_deepseek_config_invalid_model(self):
        """Test DeepSeek config validation with invalid model"""
        config = {
            'api_key': 'test-key',
            'base_url': 'https://api.deepseek.com',
            'model': 'invalid-model'
        }
        
        with pytest.raises(ConfigurationError, match="DeepSeek model must be one of"):
            validate_deepseek_config(config)
    
    def test_validate_openrouter_config_success(self):
        """Test successful OpenRouter config validation"""
        config = {
            'api_key': 'test-key',
            'base_url': 'https://openrouter.ai/api/v1',
            'model': 'openai/gpt-4.1-mini'
        }
        
        assert validate_openrouter_config(config) is True


class TestProviderClientFactory:
    """Test ProviderClientFactory class"""
    
    @patch('provider_factory.OpenAI')
    def test_create_client_deepseek(self, mock_openai):
        """Test creating DeepSeek client"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        config = ProviderConfig(
            provider_type="deepseek",
            api_key="test-key",
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
            additional_params={
                'api_key': 'test-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            }
        )
        
        client = ProviderClientFactory.create_client(config)
        
        mock_openai.assert_called_once_with(
            api_key="test-key",
            base_url="https://api.deepseek.com"
        )
        assert client == mock_client
    
    def test_get_supported_providers(self):
        """Test getting supported providers"""
        providers = ProviderClientFactory.get_supported_providers()
        
        assert "deepseek" in providers
        assert "openrouter" in providers
        assert len(providers) == 2
    
    def test_get_provider_info(self):
        """Test getting provider information"""
        deepseek_info = ProviderClientFactory.get_provider_info("deepseek")
        
        assert deepseek_info["name"] == "DeepSeek"
        assert deepseek_info["base_url"] == "https://api.deepseek.com"
        assert "deepseek-chat" in deepseek_info["models"]
    
    def test_get_model_info(self):
        """Test getting model information"""
        model_info = ProviderClientFactory.get_model_info("deepseek", "deepseek-chat")
        
        assert model_info["name"] == "DeepSeek-V3"
        assert model_info["context_window"] == 64000
        assert model_info["supports_function_calling"] is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])