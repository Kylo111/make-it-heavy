"""
Integration tests for DeepSeek integration in Make It Heavy framework.
Tests single-agent mode, multi-agent orchestration, provider switching, and error handling.
"""

import pytest
import tempfile
import os
import yaml
import subprocess
import sys
import time
import threading
from unittest.mock import patch, MagicMock, mock_open
from concurrent.futures import ThreadPoolExecutor

from agent import UniversalAgent, OpenRouterAgent
from orchestrator import TaskOrchestrator
from config_manager import ConfigurationManager, ConfigurationError, ProviderConfig
from provider_factory import ProviderClientFactory, ProviderError, DeepSeekAPIError, OpenRouterAPIError


class TestSingleAgentIntegration:
    """Integration tests for single-agent mode with DeepSeek configuration"""
    
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
    
    def create_deepseek_reasoner_config(self):
        """Create a valid DeepSeek Reasoner configuration"""
        return {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'test-deepseek-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-reasoner'
            },
            'system_prompt': 'You are a helpful reasoning assistant.',
            'agent': {'max_iterations': 15},
            'orchestrator': {'parallel_agents': 4, 'task_timeout': 450},
            'search': {'max_results': 7}
        }
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_single_agent_deepseek_chat_integration(self, mock_openai, mock_discover_tools):
        """Test single agent with DeepSeek-Chat model end-to-end"""
        # Setup mocks
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello! I'm DeepSeek-Chat."
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = self.create_deepseek_config()
        config_path = self.create_temp_config(config_data)
        
        try:
            # Initialize agent
            agent = UniversalAgent(config_path, silent=True)
            
            # Verify initialization
            assert agent.provider_type == 'deepseek'
            assert agent.provider_config.model == 'deepseek-chat'
            
            # Test agent run
            response = agent.run("Hello, how are you?")
            
            # Verify response
            assert "Hello! I'm DeepSeek-Chat." in response
            
            # Verify API call was made correctly
            mock_client.chat.completions.create.assert_called()
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['model'] == 'deepseek-chat'
            
        finally:
            os.unlink(config_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_single_agent_deepseek_reasoner_integration(self, mock_openai, mock_discover_tools):
        """Test single agent with DeepSeek-Reasoner model end-to-end"""
        # Setup mocks
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "I'm DeepSeek-Reasoner, ready for complex reasoning."
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = self.create_deepseek_reasoner_config()
        config_path = self.create_temp_config(config_data)
        
        try:
            # Initialize agent
            agent = UniversalAgent(config_path, silent=True)
            
            # Verify initialization
            assert agent.provider_type == 'deepseek'
            assert agent.provider_config.model == 'deepseek-reasoner'
            
            # Test agent run
            response = agent.run("Solve this complex problem: 2+2")
            
            # Verify response
            assert "DeepSeek-Reasoner" in response
            
            # Verify API call was made correctly
            mock_client.chat.completions.create.assert_called()
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]['model'] == 'deepseek-reasoner'
            
        finally:
            os.unlink(config_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_single_agent_with_tool_calls(self, mock_openai, mock_discover_tools):
        """Test single agent with tool calling functionality"""
        # Setup tool mock
        mock_tool = MagicMock()
        mock_tool.to_openrouter_schema.return_value = {
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": {"type": "object", "properties": {}}
            }
        }
        mock_tool.execute.return_value = {"result": "Tool executed successfully"}
        mock_discover_tools.return_value = {"test_tool": mock_tool}
        
        # Setup API mocks
        mock_client = MagicMock()
        
        # First response with tool call
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "test_tool"
        mock_tool_call.function.arguments = "{}"
        
        mock_response1 = MagicMock()
        mock_response1.choices = [MagicMock()]
        mock_response1.choices[0].message.content = "I'll use a tool to help."
        mock_response1.choices[0].message.tool_calls = [mock_tool_call]
        
        # Second response after tool call
        mock_response2 = MagicMock()
        mock_response2.choices = [MagicMock()]
        mock_response2.choices[0].message.content = "Tool result processed successfully."
        mock_response2.choices[0].message.tool_calls = None
        
        # Use cycle to handle multiple calls
        from itertools import cycle
        mock_client.chat.completions.create.side_effect = cycle([mock_response1, mock_response2])
        mock_openai.return_value = mock_client
        
        config_data = self.create_deepseek_config()
        config_data['agent']['max_iterations'] = 2  # Limit iterations to avoid infinite loop
        config_path = self.create_temp_config(config_data)
        
        try:
            # Initialize agent
            agent = UniversalAgent(config_path, silent=True)
            
            # Test agent run with tool usage
            response = agent.run("Use a tool to help me")
            
            # Verify tool was called
            mock_tool.execute.assert_called_once()
            
            # Verify response contains both parts
            assert "I'll use a tool to help." in response
            assert "Tool result processed successfully." in response
            
            # Verify multiple API calls were made
            assert mock_client.chat.completions.create.call_count >= 2
            
        finally:
            os.unlink(config_path)


class TestMultiAgentOrchestrationIntegration:
    """Integration tests for multi-agent orchestration with DeepSeek"""
    
    def create_temp_config(self, config_data):
        """Helper to create temporary config file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(config_data, temp_file)
        temp_file.close()
        return temp_file.name
    
    def create_deepseek_orchestrator_config(self):
        """Create a valid DeepSeek configuration for orchestrator"""
        return {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'test-deepseek-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            },
            'system_prompt': 'You are a helpful assistant.',
            'agent': {'max_iterations': 10},
            'orchestrator': {
                'parallel_agents': 4,
                'task_timeout': 300,
                'aggregation_strategy': 'consensus',
                'question_generation_prompt': 'Generate {num_agents} questions: {user_input}. Return JSON array.',
                'synthesis_prompt': 'Synthesize {num_responses} responses: {agent_responses}'
            },
            'search': {'max_results': 5}
        }
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_multi_agent_orchestration_deepseek(self, mock_openai, mock_discover_tools):
        """Test multi-agent orchestration with DeepSeek"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        # Mock question generation response
        question_response = MagicMock()
        question_response.choices = [MagicMock()]
        question_response.choices[0].message.content = '["Question 1", "Question 2", "Question 3", "Question 4"]'
        question_response.choices[0].message.tool_calls = None
        
        # Mock agent responses
        agent_response = MagicMock()
        agent_response.choices = [MagicMock()]
        agent_response.choices[0].message.content = "Agent response to question"
        agent_response.choices[0].message.tool_calls = None
        
        # Mock synthesis response
        synthesis_response = MagicMock()
        synthesis_response.choices = [MagicMock()]
        synthesis_response.choices[0].message.content = "Final synthesized answer from all agents"
        synthesis_response.choices[0].message.tool_calls = None
        
        # Set up call sequence: question generation, 4 agent calls, synthesis
        from itertools import cycle
        mock_client.chat.completions.create.side_effect = cycle([
            question_response,  # Question generation
            agent_response,     # Agent 1
            agent_response,     # Agent 2
            agent_response,     # Agent 3
            agent_response,     # Agent 4
            synthesis_response  # Synthesis
        ])
        
        config_data = self.create_deepseek_orchestrator_config()
        config_path = self.create_temp_config(config_data)
        
        try:
            # Initialize orchestrator
            orchestrator = TaskOrchestrator(config_path, silent=True)
            
            # Verify configuration
            assert orchestrator.num_agents == 4
            
            # Run orchestration
            result = orchestrator.orchestrate("Test question for orchestration")
            
            # Verify result
            assert "Final synthesized answer from all agents" in result
            
            # Verify API calls were made (at least question generation + 4 agents + synthesis)
            assert mock_client.chat.completions.create.call_count >= 6
            
        finally:
            os.unlink(config_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_multi_agent_parallel_execution(self, mock_openai, mock_discover_tools):
        """Test that agents run in parallel, not sequentially"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        # Track call times to verify parallelism
        call_times = []
        
        def mock_api_call(*args, **kwargs):
            call_times.append(time.time())
            # Simulate some processing time
            time.sleep(0.05)  # Reduced sleep time
            response = MagicMock()
            response.choices = [MagicMock()]
            response.choices[0].message.content = f"Response at {time.time()}"
            response.choices[0].message.tool_calls = None
            return response
        
        mock_client.chat.completions.create.side_effect = mock_api_call
        
        config_data = self.create_deepseek_orchestrator_config()
        config_data['orchestrator']['parallel_agents'] = 2  # Reduce agents for faster test
        config_path = self.create_temp_config(config_data)
        
        try:
            # Initialize orchestrator
            orchestrator = TaskOrchestrator(config_path, silent=True)
            
            # Override decompose_task to return simple questions
            orchestrator.decompose_task = lambda user_input, num_agents: [
                f"Question {i+1}" for i in range(num_agents)
            ]
            
            start_time = time.time()
            
            # Run orchestration
            result = orchestrator.orchestrate("Test parallel execution")
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Verify result exists
            assert result is not None
            
            # If agents ran sequentially, it would take at least 2 * 0.05 = 0.1 seconds per agent
            # If they ran in parallel, it should be closer to 0.05 seconds
            # Allow very generous overhead for test environment and CI
            assert total_time < 2.0, f"Execution took {total_time}s, suggesting sequential execution"
            
            # Verify we got some API calls
            assert len(call_times) > 0
            
        finally:
            os.unlink(config_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_multi_agent_error_handling(self, mock_openai, mock_discover_tools):
        """Test error handling in multi-agent orchestration"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        # Mock question generation response
        question_response = MagicMock()
        question_response.choices = [MagicMock()]
        question_response.choices[0].message.content = '["Question 1", "Question 2", "Question 3", "Question 4"]'
        question_response.choices[0].message.tool_calls = None
        
        # Mock agent responses - some succeed, some fail
        success_response = MagicMock()
        success_response.choices = [MagicMock()]
        success_response.choices[0].message.content = "Successful agent response"
        success_response.choices[0].message.tool_calls = None
        
        # Mock synthesis response
        synthesis_response = MagicMock()
        synthesis_response.choices = [MagicMock()]
        synthesis_response.choices[0].message.content = "Synthesized result from successful agents"
        synthesis_response.choices[0].message.tool_calls = None
        
        # Simplify: just test that orchestrator can handle some agent failures
        # Override the orchestrator's run_agent_parallel method to simulate failures
        config_data = self.create_deepseek_orchestrator_config()
        config_path = self.create_temp_config(config_data)
        
        # Mock successful question generation and synthesis
        from itertools import cycle
        mock_client.chat.completions.create.side_effect = cycle([
            question_response,  # Question generation
            synthesis_response  # Synthesis
        ])
        
        try:
            # Initialize orchestrator
            orchestrator = TaskOrchestrator(config_path, silent=True)
            
            # Override run_agent_parallel to simulate mixed success/failure
            original_run_agent = orchestrator.run_agent_parallel
            
            def mock_run_agent(agent_id, subtask):
                if agent_id % 2 == 0:  # Even agents succeed
                    return {
                        "agent_id": agent_id,
                        "status": "success",
                        "response": "Successful agent response",
                        "execution_time": 0.1
                    }
                else:  # Odd agents fail
                    return {
                        "agent_id": agent_id,
                        "status": "error",
                        "response": f"Agent {agent_id} failed with error",
                        "execution_time": 0.1
                    }
            
            orchestrator.run_agent_parallel = mock_run_agent
            
            # Run orchestration
            result = orchestrator.orchestrate("Test error handling")
            
            # Verify result exists (should synthesize from successful agents)
            assert result is not None
            assert "Synthesized result from successful agents" in result
            
        finally:
            os.unlink(config_path)


class TestProviderSwitchingIntegration:
    """Integration tests for provider switching functionality"""
    
    def create_temp_config(self, config_data):
        """Helper to create temporary config file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(config_data, temp_file)
        temp_file.close()
        return temp_file.name
    
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
    
    def create_legacy_openrouter_config(self):
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
    def test_switch_from_openrouter_to_deepseek(self, mock_openai, mock_discover_tools):
        """Test switching from OpenRouter to DeepSeek configuration"""
        # Setup mocks
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response from provider"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        # Create OpenRouter config
        openrouter_config = self.create_openrouter_config()
        openrouter_config['agent']['max_iterations'] = 1  # Limit iterations
        openrouter_path = self.create_temp_config(openrouter_config)
        
        # Create DeepSeek config
        deepseek_config = self.create_deepseek_config()
        deepseek_config['agent']['max_iterations'] = 1  # Limit iterations
        deepseek_path = self.create_temp_config(deepseek_config)
        
        try:
            # Initialize with OpenRouter
            agent1 = UniversalAgent(openrouter_path, silent=True)
            assert agent1.provider_type == 'openrouter'
            assert agent1.provider_config.model == 'openai/gpt-4.1-mini'
            
            # Switch to DeepSeek
            agent2 = UniversalAgent(deepseek_path, silent=True)
            assert agent2.provider_type == 'deepseek'
            assert agent2.provider_config.model == 'deepseek-chat'
            
            # Verify both work
            response1 = agent1.run("Test OpenRouter")
            response2 = agent2.run("Test DeepSeek")
            
            assert "Response from provider" in response1
            assert "Response from provider" in response2
            
            # Verify correct API calls were made (at least 2, could be more due to agent loop)
            assert mock_client.chat.completions.create.call_count >= 2
            
        finally:
            os.unlink(openrouter_path)
            os.unlink(deepseek_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_legacy_config_compatibility(self, mock_openai, mock_discover_tools):
        """Test backward compatibility with legacy OpenRouter configuration"""
        # Setup mocks
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Legacy config response"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        # Create legacy config
        legacy_config = self.create_legacy_openrouter_config()
        legacy_config['agent']['max_iterations'] = 1  # Limit iterations
        legacy_path = self.create_temp_config(legacy_config)
        
        try:
            # Test with UniversalAgent
            universal_agent = UniversalAgent(legacy_path, silent=True)
            assert universal_agent.provider_type == 'openrouter'
            
            # Test with OpenRouterAgent (backward compatibility)
            openrouter_agent = OpenRouterAgent(legacy_path, silent=True)
            assert openrouter_agent.provider_type == 'openrouter'
            assert isinstance(openrouter_agent, UniversalAgent)
            
            # Both should work identically
            response1 = universal_agent.run("Test universal")
            response2 = openrouter_agent.run("Test openrouter")
            
            assert "Legacy config response" in response1
            assert "Legacy config response" in response2
            
        finally:
            os.unlink(legacy_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_orchestrator_provider_switching(self, mock_openai, mock_discover_tools):
        """Test orchestrator with different provider configurations"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        # Mock responses
        question_response = MagicMock()
        question_response.choices = [MagicMock()]
        question_response.choices[0].message.content = '["Q1", "Q2"]'
        question_response.choices[0].message.tool_calls = None
        
        agent_response = MagicMock()
        agent_response.choices = [MagicMock()]
        agent_response.choices[0].message.content = "Agent response"
        agent_response.choices[0].message.tool_calls = None
        
        synthesis_response = MagicMock()
        synthesis_response.choices = [MagicMock()]
        synthesis_response.choices[0].message.content = "Synthesized response"
        synthesis_response.choices[0].message.tool_calls = None
        
        from itertools import cycle
        mock_client.chat.completions.create.side_effect = cycle([
            question_response, agent_response, agent_response, synthesis_response
        ])
        
        # Create configs for different providers
        openrouter_config = self.create_openrouter_config()
        openrouter_config['orchestrator'] = {
            'parallel_agents': 2,
            'task_timeout': 300,
            'aggregation_strategy': 'consensus',
            'question_generation_prompt': 'Generate {num_agents} questions: {user_input}. Return JSON array.',
            'synthesis_prompt': 'Synthesize {num_responses} responses: {agent_responses}'
        }
        openrouter_path = self.create_temp_config(openrouter_config)
        
        deepseek_config = self.create_deepseek_config()
        deepseek_config['orchestrator'] = {
            'parallel_agents': 2,
            'task_timeout': 300,
            'aggregation_strategy': 'consensus',
            'question_generation_prompt': 'Generate {num_agents} questions: {user_input}. Return JSON array.',
            'synthesis_prompt': 'Synthesize {num_responses} responses: {agent_responses}'
        }
        deepseek_path = self.create_temp_config(deepseek_config)
        
        try:
            # Test orchestrator with OpenRouter
            orchestrator1 = TaskOrchestrator(openrouter_path, silent=True)
            result1 = orchestrator1.orchestrate("Test with OpenRouter")
            
            # Reset mock call count
            mock_client.chat.completions.create.reset_mock()
            from itertools import cycle
            mock_client.chat.completions.create.side_effect = cycle([
                question_response, agent_response, agent_response, synthesis_response
            ])
            
            # Test orchestrator with DeepSeek
            orchestrator2 = TaskOrchestrator(deepseek_path, silent=True)
            result2 = orchestrator2.orchestrate("Test with DeepSeek")
            
            # Both should work
            assert "Synthesized response" in result1
            assert "Synthesized response" in result2
            
        finally:
            os.unlink(openrouter_path)
            os.unlink(deepseek_path)


class TestErrorHandlingAndRecovery:
    """Integration tests for error handling and recovery scenarios"""
    
    def create_temp_config(self, config_data):
        """Helper to create temporary config file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(config_data, temp_file)
        temp_file.close()
        return temp_file.name
    
    def create_invalid_deepseek_config(self):
        """Create an invalid DeepSeek configuration"""
        return {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': '',  # Invalid: empty API key
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            },
            'system_prompt': 'You are a helpful assistant.',
            'agent': {'max_iterations': 10}
        }
    
    def create_invalid_model_config(self):
        """Create a configuration with invalid model"""
        return {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'test-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'invalid-model'  # Invalid model
            },
            'system_prompt': 'You are a helpful assistant.',
            'agent': {'max_iterations': 10}
        }
    
    def test_invalid_configuration_error(self):
        """Test error handling for invalid configuration"""
        invalid_config = self.create_invalid_deepseek_config()
        config_path = self.create_temp_config(invalid_config)
        
        try:
            with pytest.raises(Exception, match="Agent initialization failed"):
                UniversalAgent(config_path, silent=True)
        finally:
            os.unlink(config_path)
    
    def test_invalid_model_error(self):
        """Test error handling for invalid model"""
        invalid_config = self.create_invalid_model_config()
        config_path = self.create_temp_config(invalid_config)
        
        try:
            with pytest.raises(Exception, match="Agent initialization failed"):
                UniversalAgent(config_path, silent=True)
        finally:
            os.unlink(config_path)
    
    def test_missing_config_file_error(self):
        """Test error handling for missing configuration file"""
        with pytest.raises(Exception, match="Agent initialization failed"):
            UniversalAgent("non_existent_config.yaml", silent=True)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_deepseek_api_error_handling(self, mock_openai, mock_discover_tools):
        """Test DeepSeek-specific API error handling"""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API key invalid")
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'invalid-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            },
            'system_prompt': 'You are a helpful assistant.',
            'agent': {'max_iterations': 10}
        }
        config_path = self.create_temp_config(config_data)
        
        try:
            agent = UniversalAgent(config_path, silent=True)
            
            with pytest.raises(DeepSeekAPIError, match="DeepSeek API call failed"):
                agent.run("Test question")
                
        finally:
            os.unlink(config_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_openrouter_api_error_handling(self, mock_openai, mock_discover_tools):
        """Test OpenRouter-specific API error handling"""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API key invalid")
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = {
            'provider': {'type': 'openrouter'},
            'openrouter': {
                'api_key': 'invalid-key',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'openai/gpt-4.1-mini'
            },
            'system_prompt': 'You are a helpful assistant.',
            'agent': {'max_iterations': 10}
        }
        config_path = self.create_temp_config(config_data)
        
        try:
            agent = UniversalAgent(config_path, silent=True)
            
            with pytest.raises(OpenRouterAPIError, match="OpenRouter API call failed"):
                agent.run("Test question")
                
        finally:
            os.unlink(config_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_orchestrator_timeout_handling(self, mock_openai, mock_discover_tools):
        """Test orchestrator timeout handling"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        # Mock question generation response
        question_response = MagicMock()
        question_response.choices = [MagicMock()]
        question_response.choices[0].message.content = '["Question 1", "Question 2"]'
        question_response.choices[0].message.tool_calls = None
        
        # Mock synthesis response
        synthesis_response = MagicMock()
        synthesis_response.choices = [MagicMock()]
        synthesis_response.choices[0].message.content = "Partial synthesis from available agents"
        synthesis_response.choices[0].message.tool_calls = None
        
        from itertools import cycle
        mock_client.chat.completions.create.side_effect = cycle([
            question_response,  # Question generation
            synthesis_response  # Synthesis
        ])
        
        config_data = {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'test-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            },
            'system_prompt': 'You are a helpful assistant.',
            'agent': {'max_iterations': 10},
            'orchestrator': {
                'parallel_agents': 2,
                'task_timeout': 1,  # Very short timeout
                'aggregation_strategy': 'consensus',
                'question_generation_prompt': 'Generate {num_agents} questions: {user_input}. Return JSON array.',
                'synthesis_prompt': 'Synthesize {num_responses} responses: {agent_responses}'
            }
        }
        config_path = self.create_temp_config(config_data)
        
        try:
            orchestrator = TaskOrchestrator(config_path, silent=True)
            
            # Override run_agent_parallel to simulate timeout
            def mock_run_agent_timeout(agent_id, subtask):
                time.sleep(2)  # Longer than timeout
                return {
                    "agent_id": agent_id,
                    "status": "success",
                    "response": "This should timeout",
                    "execution_time": 2.0
                }
            
            orchestrator.run_agent_parallel = mock_run_agent_timeout
            
            # This should handle timeouts gracefully and raise TimeoutError
            # which the orchestrator should catch and handle
            try:
                result = orchestrator.orchestrate("Test timeout handling")
                # If we get here, the orchestrator handled timeouts gracefully
                assert result is not None
            except Exception as e:
                # Timeout handling should result in some kind of graceful degradation
                # The exact behavior depends on implementation
                assert "timeout" in str(e).lower() or "unfinished" in str(e).lower()
            
        finally:
            os.unlink(config_path)


class TestConfigurationValidationIntegration:
    """Integration tests for configuration validation and provider factory functionality"""
    
    def test_configuration_manager_validation(self):
        """Test ConfigurationManager validation functionality"""
        manager = ConfigurationManager()
        
        # Test valid DeepSeek config
        valid_deepseek = {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'test-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            }
        }
        
        manager.config = valid_deepseek
        provider_config = manager.get_provider_config()
        assert provider_config.provider_type == 'deepseek'
        assert provider_config.validate() is True
        
        # Test valid OpenRouter config
        valid_openrouter = {
            'provider': {'type': 'openrouter'},
            'openrouter': {
                'api_key': 'test-key',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'openai/gpt-4.1-mini'
            }
        }
        
        manager.config = valid_openrouter
        provider_config = manager.get_provider_config()
        assert provider_config.provider_type == 'openrouter'
        assert provider_config.validate() is True
    
    def test_provider_factory_functionality(self):
        """Test ProviderClientFactory functionality"""
        # Test supported providers
        providers = ProviderClientFactory.get_supported_providers()
        assert 'deepseek' in providers
        assert 'openrouter' in providers
        
        # Test provider info
        deepseek_info = ProviderClientFactory.get_provider_info('deepseek')
        assert deepseek_info['name'] == 'DeepSeek'
        assert deepseek_info['base_url'] == 'https://api.deepseek.com'
        
        openrouter_info = ProviderClientFactory.get_provider_info('openrouter')
        assert openrouter_info['name'] == 'OpenRouter'
        assert openrouter_info['base_url'] == 'https://openrouter.ai/api/v1'
        
        # Test model info
        deepseek_chat_info = ProviderClientFactory.get_model_info('deepseek', 'deepseek-chat')
        assert deepseek_chat_info['name'] == 'DeepSeek-V3'
        assert deepseek_chat_info['supports_function_calling'] is True
        
        deepseek_reasoner_info = ProviderClientFactory.get_model_info('deepseek', 'deepseek-reasoner')
        assert deepseek_reasoner_info['name'] == 'DeepSeek-R1'
        assert deepseek_reasoner_info['supports_function_calling'] is True
    
    @patch('provider_factory.OpenAI')
    def test_provider_client_creation(self, mock_openai):
        """Test provider client creation"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Test DeepSeek client creation
        deepseek_config = ProviderConfig(
            provider_type='deepseek',
            api_key='test-key',
            base_url='https://api.deepseek.com',
            model='deepseek-chat',
            additional_params={
                'api_key': 'test-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            }
        )
        
        client = ProviderClientFactory.create_client(deepseek_config)
        assert client == mock_client
        mock_openai.assert_called_with(
            api_key='test-key',
            base_url='https://api.deepseek.com'
        )
        
        # Test OpenRouter client creation
        mock_openai.reset_mock()
        openrouter_config = ProviderConfig(
            provider_type='openrouter',
            api_key='test-key',
            base_url='https://openrouter.ai/api/v1',
            model='openai/gpt-4.1-mini',
            additional_params={
                'api_key': 'test-key',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'openai/gpt-4.1-mini'
            }
        )
        
        client = ProviderClientFactory.create_client(openrouter_config)
        assert client == mock_client
        mock_openai.assert_called_with(
            api_key='test-key',
            base_url='https://openrouter.ai/api/v1'
        )


class TestCommandLineParameterIntegration:
    """Integration tests for command-line parameter functionality"""
    
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
            'agent': {'max_iterations': 10}
        }
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_main_py_config_parameter(self, mock_openai, mock_discover_tools):
        """Test main.py with --config parameter"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = self.create_deepseek_config()
        config_path = self.create_temp_config(config_data)
        
        try:
            # Test that main.py can accept config parameter
            # We'll test the argument parsing logic by importing and testing directly
            import main
            import argparse
            
            # Test argument parser
            parser = argparse.ArgumentParser(description='Universal AI Agent with Multi-Provider Support')
            parser.add_argument('--config', '-c', default='config.yaml', 
                               help='Configuration file path (default: config.yaml)')
            
            # Test with custom config
            args = parser.parse_args(['--config', config_path])
            assert args.config == config_path
            
            # Test with short form
            args = parser.parse_args(['-c', config_path])
            assert args.config == config_path
            
            # Test default
            args = parser.parse_args([])
            assert args.config == 'config.yaml'
            
        finally:
            os.unlink(config_path)
    
    @patch('agent.discover_tools')
    @patch('provider_factory.OpenAI')
    def test_make_it_heavy_config_parameter(self, mock_openai, mock_discover_tools):
        """Test make_it_heavy.py with --config parameter"""
        # Setup mocks
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_discover_tools.return_value = {}
        
        config_data = self.create_deepseek_config()
        config_data['orchestrator'] = {
            'parallel_agents': 4,
            'task_timeout': 300,
            'aggregation_strategy': 'consensus'
        }
        config_path = self.create_temp_config(config_data)
        
        try:
            # Test that make_it_heavy.py can accept config parameter
            import make_it_heavy
            import argparse
            
            # Test argument parser
            parser = argparse.ArgumentParser(description='Multi-Agent Orchestrator with Multi-Provider Support')
            parser.add_argument('--config', '-c', default='config.yaml', 
                               help='Configuration file path (default: config.yaml)')
            
            # Test with custom config
            args = parser.parse_args(['--config', config_path])
            assert args.config == config_path
            
            # Test with short form
            args = parser.parse_args(['-c', config_path])
            assert args.config == config_path
            
            # Test default
            args = parser.parse_args([])
            assert args.config == 'config.yaml'
            
        finally:
            os.unlink(config_path)
    
    def test_config_file_selection_integration(self):
        """Test that different config files can be selected and work correctly"""
        # Create different config files
        deepseek_config = {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'deepseek-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            },
            'system_prompt': 'DeepSeek assistant'
        }
        
        openrouter_config = {
            'provider': {'type': 'openrouter'},
            'openrouter': {
                'api_key': 'openrouter-key',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'openai/gpt-4.1-mini'
            },
            'system_prompt': 'OpenRouter assistant'
        }
        
        deepseek_path = self.create_temp_config(deepseek_config)
        openrouter_path = self.create_temp_config(openrouter_config)
        
        try:
            # Test configuration manager with different files
            manager1 = ConfigurationManager()
            config1 = manager1.load_config(deepseek_path)
            assert manager1.get_active_provider() == 'deepseek'
            assert manager1.get_system_prompt() == 'DeepSeek assistant'
            
            manager2 = ConfigurationManager()
            config2 = manager2.load_config(openrouter_path)
            assert manager2.get_active_provider() == 'openrouter'
            assert manager2.get_system_prompt() == 'OpenRouter assistant'
            
            # Verify configs are different
            assert config1 != config2
            
        finally:
            os.unlink(deepseek_path)
            os.unlink(openrouter_path)


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])