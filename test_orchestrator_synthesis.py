import unittest
import yaml
import os
import tempfile
from unittest.mock import patch, MagicMock
from orchestrator import TaskOrchestrator

class TestOrchestratorSynthesis(unittest.TestCase):
    """Test suite for verifying the orchestrator's synthesis process with DeepSeek API"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
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
        self.config_path = os.path.join(self.temp_dir, 'config.yaml')
        with open(self.config_path, 'w') as f:
            yaml.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary directory and all its contents
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_synthesis_process_with_deepseek(self):
        """Test that the synthesis process works correctly with DeepSeek configuration."""
        # Initialize orchestrator with DeepSeek config
        orchestrator = TaskOrchestrator(config_path=self.config_path, silent=True)
        
        # Mock the UniversalAgent class
        with patch('agent.UniversalAgent') as mock_agent_class:
            # Create mock instances for different agent types
            mock_question_agent = MagicMock()
            mock_question_agent.run.return_value = '["Subtask 1", "Subtask 2"]'
            
            mock_agent_1 = MagicMock()
            mock_agent_1.run.return_value = "Response from agent 1"
            
            mock_agent_2 = MagicMock()
            mock_agent_2.run.return_value = "Response from agent 2"
            
            mock_synthesis_agent = MagicMock()
            mock_synthesis_agent.run.return_value = "Final synthesized answer"
            
            # Set up side effect to return different agents based on call count
            side_effects = [
                mock_question_agent,  # First call: question agent
                mock_agent_1,         # Second call: agent 1
                mock_agent_2,         # Third call: agent 2
                mock_synthesis_agent  # Fourth call: synthesis agent
            ]
            
            mock_agent_class.side_effect = side_effects
            
            # Mock the decompose_task method to avoid API calls
            with patch.object(orchestrator, 'decompose_task') as mock_decompose:
                mock_decompose.return_value = ["Subtask 1", "Subtask 2"]
                
                # Execute orchestration
                result = orchestrator.orchestrate("Test query")
                
                # Verify all agents were created
                self.assertEqual(mock_agent_class.call_count, 4)
                
                # Verify agent execution
                mock_agent_1.run.assert_called_with("Subtask 1")
                mock_agent_2.run.assert_called_with("Subtask 2")
                
                # Verify synthesis was called with the correct prompt
                mock_synthesis_agent.run.assert_called_once()
                synthesis_call_args = mock_synthesis_agent.run.call_args[0][0]
                self.assertIn("2", synthesis_call_args)  # num_responses
                self.assertIn("Response from agent 1", synthesis_call_args)  # agent_responses
                self.assertIn("Response from agent 2", synthesis_call_args)  # agent_responses
                
                # Verify final result
                self.assertEqual(result, "Final synthesized answer")
    
    def test_synthesis_fallback_with_deepseek(self):
        """Test that fallback mechanism works when synthesis fails with DeepSeek."""
        # Initialize orchestrator
        orchestrator = TaskOrchestrator(config_path=self.config_path, silent=True)
        
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
            mock_synthesis_agent.run.side_effect = Exception("Synthesis failed")
            
            # Set up side effect to return different agents
            side_effects = [
                mock_question_agent,  # First call: question agent
                mock_agent_1,         # Second call: agent 1
                mock_agent_2,         # Third call: agent 2
                mock_synthesis_agent  # Fourth call: synthesis agent
            ]
            
            mock_agent_class.side_effect = side_effects
            
            # Mock the decompose_task method to avoid API calls
            with patch.object(orchestrator, 'decompose_task') as mock_decompose:
                mock_decompose.return_value = ["Subtask 1", "Subtask 2"]
                
                # Execute orchestration
                result = orchestrator.orchestrate("Test query")
                
                # Verify all agents were created
                self.assertEqual(mock_agent_class.call_count, 4)
                
                # Verify agent execution
                mock_agent_1.run.assert_called_with("Subtask 1")
                mock_agent_2.run.assert_called_with("Subtask 2")
                
                # Verify synthesis was attempted
                mock_synthesis_agent.run.assert_called_once()
                
                # Verify fallback was triggered
                self.assertIn("=== Agent 1 Response ===", result)
                self.assertIn("=== Agent 2 Response ===", result)
                self.assertIn("Response from agent 1", result)
                self.assertIn("Response from agent 2", result)
                self.assertNotIn("Final synthesized answer", result)
    
    def test_empty_tools_handling_with_deepseek(self):
        """Test that dummy tool is added when tools list is empty for DeepSeek."""
        # Initialize orchestrator
        orchestrator = TaskOrchestrator(config_path=self.config_path, silent=True)
        
        # Mock the UniversalAgent class
        with patch('agent.UniversalAgent') as mock_agent_class:
            # Create a mock agent instance
            mock_agent_instance = MagicMock()
            # Start with empty tools to trigger the dummy tool logic
            mock_agent_instance.tools = []
            mock_agent_instance.tool_mapping = {}
            mock_agent_instance.provider_type = "deepseek"
            mock_agent_instance.run.return_value = "Synthesized response"
            
            # Make the mock class return our instance
            mock_agent_class.return_value = mock_agent_instance
            
            # Mock the call_llm method to avoid API calls
            with patch.object(mock_agent_instance, 'call_llm') as mock_call_llm:
                mock_call_llm.return_value = MagicMock(
                    choices=[MagicMock(message=MagicMock(content="Test response", tool_calls=None))]
                )
                
                # Call the _aggregate_consensus method directly
                responses = ["Test response"]
                result = orchestrator._aggregate_consensus(responses, [])
                
                # Verify that the dummy tool was added
                # The dummy tool should be added in the run method of UniversalAgent
                # when provider is deepseek and tools is empty
                self.assertTrue(len(mock_agent_instance.tools) > 0, "Dummy tool should be added when tools list is empty")
                self.assertEqual(mock_agent_instance.tools[0]['function']['name'], 'dummy_tool', "First tool should be dummy_tool")
                mock_agent_instance.run.assert_called_once()

if __name__ == '__main__':
    unittest.main()