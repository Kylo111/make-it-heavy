import unittest
import yaml
import os
from unittest.mock import patch, MagicMock
from orchestrator import TaskOrchestrator
from agent import UniversalAgent

class TestTaskOrchestratorDeepSeek(unittest.TestCase):
    """Test suite for TaskOrchestrator with DeepSeek API integration"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a test configuration for DeepSeek
        self.test_config = {
            'provider': {
                'type': 'deepseek'
            },
            'deepseek': {
                'api_key': 'test-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            },
            'orchestrator': {
                'parallel_agents': 2,
                'task_timeout': 30,
                'aggregation_strategy': 'consensus',
                'question_generation_prompt': 'Generate {num_agents} questions for: {user_input}',
                'synthesis_prompt': 'Synthesize these {num_responses} responses: {agent_responses}'
            },
            'system_prompt': 'You are a helpful assistant',
            'agent': {
                'max_iterations': 5
            }
        }
        
        # Save test config to temporary file
        self.config_path = 'test_config_deepseek.yaml'
        with open(self.config_path, 'w') as f:
            yaml.dump(self.test_config, f)
    
    
    def test_task_decomposition_with_deepseek(self):
        """Test that task decomposition works correctly with DeepSeek configuration."""
        # Initialize orchestrator with DeepSeek config
        orchestrator = TaskOrchestrator(config_path=self.config_path, silent=True)
        
        # Mock the agent.run method to avoid API calls
        with patch.object(UniversalAgent, 'run') as mock_run:
            # Setup mock to return valid JSON
            mock_run.return_value = '["Question 1", "Question 2"]'
            
            # Test task decomposition
            user_input = "Test query"
            subtasks = orchestrator.decompose_task(user_input, 2)
            
            # Assertions
            self.assertEqual(len(subtasks), 2)
            self.assertEqual(subtasks, ["Question 1", "Question 2"])
            mock_run.assert_called_once()
            # Verify the prompt was formatted correctly
            call_args = mock_run.call_args[0][0]
            self.assertIn(user_input, call_args)
            self.assertIn("2", call_args)
    
    def test_parallel_agent_execution_with_deepseek(self):
        """Test that parallel agent execution works with DeepSeek configuration."""
        # Create a temporary config file
        test_config = {
            'provider': {
                'type': 'deepseek'
            },
            'deepseek': {
                'api_key': 'test-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            },
            'orchestrator': {
                'parallel_agents': 2,
                'task_timeout': 30,
                'aggregation_strategy': 'consensus',
                'question_generation_prompt': 'Generate {num_agents} questions for: {user_input}',
                'synthesis_prompt': 'Synthesize these {num_responses} responses: {agent_responses}'
            },
            'system_prompt': 'You are a helpful assistant',
            'agent': {
                'max_iterations': 5
            }
        }
        
        config_path = 'test_config_deepseek.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        try:
            # Initialize orchestrator with our test config
            orchestrator = TaskOrchestrator(config_path=config_path, silent=True)
            
            # Mock the UniversalAgent class
            with patch('agent.UniversalAgent') as mock_agent_class:
                # Create mock instances
                mock_question_agent = MagicMock()
                mock_question_agent.run.return_value = '["Subtask 1", "Subtask 2"]'
                
                mock_agent_1 = MagicMock()
                mock_agent_1.run.return_value = "Response from agent 1"
                
                mock_agent_2 = MagicMock()
                mock_agent_2.run.return_value = "Response from agent 2"
                
                mock_synthesis_agent = MagicMock()
                mock_synthesis_agent.run.return_value = "Final synthesized answer"
                
                # Set up side effect to return different agents
                side_effects = [
                    mock_question_agent,  # First call: question agent
                    mock_agent_1,         # Second call: agent 1
                    mock_agent_2,         # Third call: agent 2
                    mock_synthesis_agent  # Fourth call: synthesis agent
                ]
                
                mock_agent_class.side_effect = side_effects
                
                # Mock decompose_task to avoid API calls
                with patch.object(orchestrator, 'decompose_task') as mock_decompose:
                    mock_decompose.return_value = ["Subtask 1", "Subtask 2"]
                    
                    # Execute orchestration
                    result = orchestrator.orchestrate("Test query")
                    
                    # Verify all agents were created
                    self.assertEqual(mock_agent_class.call_count, 4)
                    
                    # Verify agent execution
                    mock_agent_1.run.assert_called_with("Subtask 1")
                    mock_agent_2.run.assert_called_with("Subtask 2")
                    
                    # Verify synthesis was called
                    mock_synthesis_agent.run.assert_called_once()
                    synthesis_call_args = mock_synthesis_agent.run.call_args[0][0]
                    self.assertIn("2", synthesis_call_args)  # num_responses
                    self.assertIn("Response from agent 1", synthesis_call_args)  # agent_responses
                    self.assertIn("Response from agent 2", synthesis_call_args)  # agent_responses
        finally:
            # Clean up
            if os.path.exists(config_path):
                os.remove(config_path)
    
    def test_synthesis_process_with_deepseek(self):
        """Test the synthesis process with DeepSeek configuration."""
        # Initialize orchestrator
        orchestrator = TaskOrchestrator(config_path=self.config_path, silent=True)
        
        # Mock the agent.run method to avoid API calls
        with patch.object(UniversalAgent, 'run') as mock_run:
            # Setup mock to return agent responses and final synthesis
            mock_run.side_effect = [
                "Response from agent 1",  # Agent 1 response
                "Response from agent 2",  # Agent 2 response
                "Final synthesized answer"  # Synthesis agent response
            ]
            
            # Mock the decompose_task method
            with patch.object(orchestrator, 'decompose_task') as mock_decompose:
                mock_decompose.return_value = ["Subtask 1", "Subtask 2"]
                
                # Execute orchestration
                result = orchestrator.orchestrate("Test query")
                
                # Verify all calls were made
                self.assertEqual(mock_run.call_count, 3)
                # First two calls are for agents
                mock_run.assert_any_call("Subtask 1")
                mock_run.assert_any_call("Subtask 2")
                # Third call is for synthesis
                synthesis_call_args = mock_run.call_args_list[2][0][0]
                self.assertIn("2", synthesis_call_args)  # num_responses
                self.assertIn("Response from agent 1", synthesis_call_args)  # agent_responses
                self.assertIn("Response from agent 2", synthesis_call_args)  # agent_responses
                
                # Verify final result
                self.assertEqual(result, "Final synthesized answer")
    
    def test_synthesis_fallback_with_deepseek(self):
        """Test that fallback mechanism works when synthesis fails with DeepSeek."""
        # Initialize orchestrator
        orchestrator = TaskOrchestrator(config_path=self.config_path, silent=True)
        
        # Mock the agent.run method to avoid API calls
        with patch.object(UniversalAgent, 'run') as mock_run:
            # Setup mock to return agent responses and fail on synthesis
            mock_run.side_effect = [
                "Response from agent 1",  # Agent 1 response
                "Response from agent 2",  # Agent 2 response
                Exception("Synthesis failed")  # Synthesis agent fails
            ]
            
            # Mock the decompose_task method
            with patch.object(orchestrator, 'decompose_task') as mock_decompose:
                mock_decompose.return_value = ["Subtask 1", "Subtask 2"]
                
                # Execute orchestration
                result = orchestrator.orchestrate("Test query")
                
                # Verify all calls were made
                self.assertEqual(mock_run.call_count, 3)
                # First two calls are for agents
                mock_run.assert_any_call("Subtask 1")
                mock_run.assert_any_call("Subtask 2")
                # Third call is for synthesis (which fails)
                
                # Verify fallback was triggered
                self.assertIn("=== Agent 1 Response ===", result)
                self.assertIn("=== Agent 2 Response ===", result)
                self.assertIn("Response from agent 1", result)
                self.assertIn("Response from agent 2", result)
                self.assertNotIn("Final synthesized answer", result)
    
    def test_empty_tools_handling_with_deepseek(self):
        """Test that dummy tool is added when tools list is empty for DeepSeek."""
        # Create a temporary config file with deepseek provider
        test_config = {
            'provider': {
                'type': 'deepseek'
            },
            'deepseek': {
                'api_key': 'test-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            },
            'orchestrator': {
                'parallel_agents': 1,
                'task_timeout': 30,
                'aggregation_strategy': 'consensus',
                'question_generation_prompt': 'Generate {num_agents} questions for: {user_input}',
                'synthesis_prompt': 'Synthesize these {num_responses} responses: {agent_responses}'
            },
            'system_prompt': 'You are a helpful assistant',
            'agent': {
                'max_iterations': 5
            }
        }
        
        config_path = 'test_config_deepseek.yaml'
        with open(config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        try:
            # Initialize orchestrator with our test config
            orchestrator = TaskOrchestrator(config_path=config_path, silent=True)
            
            # We need to test the actual _aggregate_consensus method
            # First, let's verify the provider type is correctly read
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.assertEqual(config['provider']['type'], 'deepseek')
            
            # Now test the _aggregate_consensus method
            # We'll need to patch the UniversalAgent to control its tools
            with patch('agent.UniversalAgent') as mock_agent_class:
                # Create a mock agent instance
                mock_agent_instance = MagicMock()
                # Start with empty tools to trigger the dummy tool logic
                mock_agent_instance.tools = []
                mock_agent_instance.tool_mapping = {}
                mock_agent_instance.run.return_value = "Synthesized response"
                
                # Make the mock class return our instance
                mock_agent_class.return_value = mock_agent_instance
                
                # Call the _aggregate_consensus method
                responses = ["Test response"]
                result = orchestrator._aggregate_consensus(responses, [])
                
                # Verify that the dummy tool was added
                # The dummy tool should be added in the _aggregate_consensus method
                # when provider is deepseek and tools is empty
                self.assertTrue(len(mock_agent_instance.tools) > 0, "Dummy tool should be added when tools list is empty")
                self.assertEqual(mock_agent_instance.tools[0]['function']['name'], 'dummy_tool', "First tool should be dummy_tool")
                mock_agent_instance.run.assert_called_once()
        finally:
            # Clean up
            if os.path.exists(config_path):
                os.remove(config_path)
    
    def test_partial_agent_failure_with_deepseek(self):
        """Test orchestration handles partial agent failures with DeepSeek."""
        # Initialize orchestrator
        orchestrator = TaskOrchestrator(config_path=self.config_path, silent=True)
        
        # Mock the agent.run method to avoid API calls
        with patch.object(UniversalAgent, 'run') as mock_run:
            # Setup mock to simulate one success and one failure
            mock_run.side_effect = [
                "Successful response",
                Exception("Agent failed")
            ]
            
            # Mock the decompose_task method
            with patch.object(orchestrator, 'decompose_task') as mock_decompose:
                mock_decompose.return_value = ["Subtask 1", "Subtask 2"]
                
                # Execute orchestration
                result = orchestrator.orchestrate("Test query")
                
                # Verify result includes successful response
                self.assertIn("Successful response", result)
                # Verify error message is not in final result (should be handled internally)
                self.assertNotIn("Agent failed", result)

if __name__ == '__main__':
    unittest.main()