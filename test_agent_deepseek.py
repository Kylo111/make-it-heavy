import unittest
import yaml
import os
import tempfile
from unittest.mock import patch, MagicMock
from agent import UniversalAgent

class TestAgentDeepSeek(unittest.TestCase):
    """Test suite for UniversalAgent with DeepSeek API integration"""
    
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
    
    def test_dummy_tool_added_with_empty_tools(self):
        """Test that dummy tool is added when tools list is empty for DeepSeek."""
        # Mock the discover_tools function to return empty tools
        with patch('agent.discover_tools') as mock_discover_tools:
            mock_discover_tools.return_value = {}
            
            # Initialize agent with DeepSeek config
            agent = UniversalAgent(config_path=self.config_path, silent=True)
            
            # Verify provider type
            self.assertEqual(agent.provider_type, 'deepseek', "Provider type should be deepseek")
            
            # Verify initial tools are empty
            self.assertEqual(len(agent.tools), 0, "Initial tools should be empty")
            
            # Mock the call_llm method to avoid API calls
            with patch.object(agent, 'call_llm') as mock_call_llm:
                mock_call_llm.return_value = MagicMock(
                    choices=[MagicMock(message=MagicMock(content="Test response", tool_calls=None))]
                )
                
                # Call the run method which should add the dummy tool
                agent.run("Test input")
                
                # Verify that a dummy tool was added
                self.assertTrue(len(agent.tools) > 0, "Dummy tool should be added when tools list is empty")
                self.assertEqual(agent.tools[0]['function']['name'], 'dummy_tool', "First tool should be dummy_tool")

if __name__ == '__main__':
    unittest.main()