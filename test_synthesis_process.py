import unittest
import yaml
import os
import tempfile
from unittest.mock import patch, MagicMock
from orchestrator import TaskOrchestrator

class TestSynthesisProcess(unittest.TestCase):
    """Test suite for verifying the orchestrator's synthesis process"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test configuration
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
    
    def test_synthesis_process(self):
        """Test the complete synthesis process."""
        # Initialize orchestrator
        orchestrator = TaskOrchestrator(config_path=self.config_path, silent=True)
        
        # Mock the UniversalAgent class
        with patch('agent.UniversalAgent') as mock_agent_class:
            # Create mock instances
            mock_question_agent = MagicMock()
            mock_question_agent.run.return_value = '["Question 1", "Question 2"]'
            
            mock_agent_1 = MagicMock()
            mock_agent_1.run.return_value = "Answer 1"
            
            mock_agent_2 = MagicMock()
            mock_agent_2.run.return_value = "Answer 2"
            
            mock_synthesis_agent = MagicMock()
            mock_synthesis_agent.run.side_effect = Exception("Synthesis failed")
            
            # Set up side effect to return different agents
            side_effects = [
                mock_question_agent,  # Question agent
                mock_agent_1,         # Agent 1
                mock_agent_2,         # Agent 2
                mock_synthesis_agent  # Synthesis agent
            ]
            
            mock_agent_class.side_effect = side_effects
            
            # Mock decompose_task to avoid API calls
            with patch.object(orchestrator, 'decompose_task') as mock_decompose:
                mock_decompose.return_value = ["Question 1", "Question 2"]
                
                # Mock the run_agent_parallel method to avoid thread issues
                with patch.object(orchestrator, 'run_agent_parallel') as mock_run_agent:
                    mock_run_agent.side_effect = [
                        {"status": "success", "response": "Answer 1", "agent_id": 0},
                        {"status": "success", "response": "Answer 2", "agent_id": 1}
                    ]
                    
                    # Execute orchestration
                    result = orchestrator.orchestrate("Test query")
                    
                    # Verify fallback result
                    self.assertIn("Answer 1", result)
                    self.assertIn("Answer 2", result)

if __name__ == '__main__':
    unittest.main()