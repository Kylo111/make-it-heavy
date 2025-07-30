"""
Unit tests for UniversalAgent class.
"""

import pytest
import tempfile
import os
import yaml
from unittest.mock import patch, MagicMock, mock_open

from agent import UniversalAgent, OpenRouterAgent
from config_manager import ConfigurationError
from provider_factory import ProviderError, DeepSeekAPIError, OpenRouterAPIError


class TestUniversalAgent:
    """Test UniversalAgent class"""
    
    def create_temp_config(self, config_data):
        """Helper to create temporary config file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(config_data, temp_file)
        temp_file.close()
        return temp_file.name
    
    def create_deepseek_config(self):
        """Create a valid DeepSeek configuration"""
        return {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'test-deepseek-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            },
            'system_prompt': 'You are a helpful assistant.',
            'agent': {'max_iterations': 10},
            'orchestrator': {'parallel_agents': 4},
            'search': {'max_results': 5}
        }
    
    def create_openrouter_config(self):
        """Create a valid OpenRouter configuration"""
        return {
            'provider': {'type': 'openrouter'},
            'openrouter': {
                'api_key': 'test-openrouter-key',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'openai/gpt-4.1-mini'
            },
            'system_prompt': 'You are a helpful assistant.',
            'agent': {'max_iterations': 10},
            'orchestrator': {'parallel_agents': 4},
            'search': {'max_results': 5}
        }
    
    def create_legacy_config(self):
        """Create a legacy OpenRouter configuration"""
        return {
            'openrouter': {
                'api_key': 'test-openrouter-key',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'openai/gpt-4.1-mini'
            },
            'system_prompt': 'You are a helpful assistant.',
            'agent': {'max_iterations': 10},
            'orchestrator': {'parallel_agents': 4},
            'search': {'max_results': 5}
        }
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_universal_agent_deepseek_initialization(self, mock_openai, mock_discover_tools):
        """Test UniversalAgent initialization with DeepSeek"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = self.create_deepseek_config()
        config_path = self.create_temp_config(config_data)
        
        try:
            agent = UniversalAgent(config_path, silent=True)
            
            # Verify initialization
            assert agent.provider_type == 'deepseek'
            assert agent.provider_config.api_key == 'test-deepseek-key'
            assert agent.provider_config.model == 'deepseek-chat'
            
            # Verify client creation
            mock_openai.assert_called_once_with(
                api_key='test-deepseek-key',
                base_url='https://api.deepseek.com'
            )
            
        finally:
            os.unlink(config_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_universal_agent_openrouter_initialization(self, mock_openai, mock_discover_tools):
        """Test UniversalAgent initialization with OpenRouter"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = self.create_openrouter_config()
        config_path = self.create_temp_config(config_data)
        
        try:
            agent = UniversalAgent(config_path, silent=True)
            
            # Verify initialization
            assert agent.provider_type == 'openrouter'
            assert agent.provider_config.api_key == 'test-openrouter-key'
            assert agent.provider_config.model == 'openai/gpt-4.1-mini'
            
            # Verify client creation
            mock_openai.assert_called_once_with(
                api_key='test-openrouter-key',
                base_url='https://openrouter.ai/api/v1'
            )
            
        finally:
            os.unlink(config_path)
    
    def test_universal_agent_invalid_config(self):
        """Test UniversalAgent with invalid configuration"""
        with pytest.raises(Exception, match="Agent initialization failed"):
            UniversalAgent("non_existent_config.yaml", silent=True)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_get_provider_info(self, mock_openai, mock_discover_tools):
        """Test getting provider information"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = self.create_deepseek_config()
        config_path = self.create_temp_config(config_data)
        
        try:
            agent = UniversalAgent(config_path, silent=True)
            provider_info = agent.get_provider_info()
            
            assert provider_info['provider_type'] == 'deepseek'
            assert provider_info['model'] == 'deepseek-chat'
            assert provider_info['base_url'] == 'https://api.deepseek.com'
            assert 'supports_function_calling' in provider_info
            
        finally:
            os.unlink(config_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_call_llm_success(self, mock_openai, mock_discover_tools):
        """Test successful LLM call"""
        # Setup mocks
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = self.create_deepseek_config()
        config_path = self.create_temp_config(config_data)
        
        try:
            agent = UniversalAgent(config_path, silent=True)
            messages = [{"role": "user", "content": "Hello"}]
            
            response = agent.call_llm(messages)
            
            assert response == mock_response
            mock_client.chat.completions.create.assert_called_once_with(
                model='deepseek-chat',
                messages=messages,
                tools=[]
            )
            
        finally:
            os.unlink(config_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_call_llm_deepseek_error(self, mock_openai, mock_discover_tools):
        """Test LLM call with DeepSeek API error"""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API key invalid")
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = self.create_deepseek_config()
        config_path = self.create_temp_config(config_data)
        
        try:
            agent = UniversalAgent(config_path, silent=True)
            messages = [{"role": "user", "content": "Hello"}]
            
            with pytest.raises(DeepSeekAPIError, match="DeepSeek API call failed"):
                agent.call_llm(messages)
            
        finally:
            os.unlink(config_path)


class TestOpenRouterAgentBackwardCompatibility:
    """Test OpenRouterAgent backward compatibility"""
    
    def create_temp_config(self, config_data):
        """Helper to create temporary config file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(config_data, temp_file)
        temp_file.close()
        return temp_file.name
    
    def create_legacy_config(self):
        """Create a legacy OpenRouter configuration"""
        return {
            'openrouter': {
                'api_key': 'test-openrouter-key',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'openai/gpt-4.1-mini'
            },
            'system_prompt': 'You are a helpful assistant.',
            'agent': {'max_iterations': 10},
            'orchestrator': {'parallel_agents': 4},
            'search': {'max_results': 5}
        }
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_openrouter_agent_legacy_config(self, mock_openai, mock_discover_tools):
        """Test OpenRouterAgent with legacy configuration"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = self.create_legacy_config()
        config_path = self.create_temp_config(config_data)
        
        try:
            agent = OpenRouterAgent(config_path, silent=True)
            
            # Should work as UniversalAgent
            assert agent.provider_type == 'openrouter'
            assert agent.provider_config.api_key == 'test-openrouter-key'
            
        finally:
            os.unlink(config_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_openrouter_agent_is_universal_agent(self, mock_openai, mock_discover_tools):
        """Test that OpenRouterAgent is instance of UniversalAgent"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = self.create_legacy_config()
        config_path = self.create_temp_config(config_data)
        
        try:
            agent = OpenRouterAgent(config_path, silent=True)
            
            # Should be instance of UniversalAgent
            assert isinstance(agent, UniversalAgent)
            
        finally:
            os.unlink(config_path)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])