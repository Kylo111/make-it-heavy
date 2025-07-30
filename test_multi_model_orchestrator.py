#!/usr/bin/env python3
"""
Integration tests for multi-model orchestrator functionality.
Tests the enhanced TaskOrchestrator with multi-model support.
"""

import os
import yaml
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from orchestrator import TaskOrchestrator
from model_config.data_models import AgentModelConfig


class TestMultiModelOrchestrator(unittest.TestCase):
    """Test multi-model orchestrator functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        
        # Basic config without multi-model
        self.basic_config = {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'test-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            },
            'system_prompt': 'Test prompt',
            'agent': {'max_iterations': 3},
            'orchestrator': {
                'parallel_agents': 2,
                'task_timeout': 30,
                'aggregation_strategy': 'consensus',
                'question_generation_prompt': 'Generate {num_agents} questions about: {user_input}',
                'synthesis_prompt': 'Synthesize {num_responses} responses: {agent_responses}'
            },
            'search': {'max_results': 5}
        }
        
        # Multi-model config
        self.multi_model_config = {
            'agent_0_model': 'deepseek-chat',
            'agent_1_model': 'deepseek-reasoner',
            'agent_2_model': 'deepseek-chat',
            'agent_3_model': 'deepseek-reasoner',
            'synthesis_model': 'deepseek-reasoner',
            'default_model': 'deepseek-chat',
            'profile_name': 'test'
        }
        
        yaml.dump(self.basic_config, self.temp_config)
        self.temp_config.close()
        self.config_path = self.temp_config.name
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.config_path):
            os.unlink(self.config_path)
    
    def test_orchestrator_initialization_without_multi_model(self):
        """Test orchestrator initialization without multi-model config."""
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        self.assertIsNone(orchestrator.multi_model_config)
        self.assertEqual(orchestrator.num_agents, 2)
        self.assertIsNotNone(orchestrator.config_manager)
        self.assertIsNotNone(orchestrator.model_config_manager)
    
    def test_orchestrator_initialization_with_multi_model(self):
        """Test orchestrator initialization with multi-model config."""
        # Add multi-model config to the file
        config_with_multi_model = self.basic_config.copy()
        config_with_multi_model['multi_model'] = self.multi_model_config
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_with_multi_model, f)
        
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        self.assertIsNotNone(orchestrator.multi_model_config)
        self.assertEqual(orchestrator.multi_model_config.agent_0_model, 'deepseek-chat')
        self.assertEqual(orchestrator.multi_model_config.synthesis_model, 'deepseek-reasoner')
    
    def test_get_agent_model_with_multi_model_config(self):
        """Test getting agent model with multi-model configuration."""
        config_with_multi_model = self.basic_config.copy()
        config_with_multi_model['multi_model'] = self.multi_model_config
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_with_multi_model, f)
        
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        self.assertEqual(orchestrator._get_agent_model(0), 'deepseek-chat')
        self.assertEqual(orchestrator._get_agent_model(1), 'deepseek-reasoner')
        self.assertEqual(orchestrator._get_synthesis_model(), 'deepseek-reasoner')
    
    def test_get_agent_model_without_multi_model_config(self):
        """Test getting agent model without multi-model configuration."""
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        # Should fallback to default model
        self.assertEqual(orchestrator._get_agent_model(0), 'deepseek-chat')
        self.assertEqual(orchestrator._get_agent_model(1), 'deepseek-chat')
        self.assertEqual(orchestrator._get_synthesis_model(), 'deepseek-chat')
    
    @patch('orchestrator.UniversalAgent')
    def test_create_agent_with_model(self, mock_agent_class):
        """Test creating agent with specific model."""
        mock_agent = MagicMock()
        mock_agent.provider_config = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        agent = orchestrator._create_agent_with_model(0, 'test-model')
        
        self.assertIsNotNone(agent)
        self.assertEqual(agent.provider_config.model, 'test-model')
        self.assertIn(0, orchestrator.agent_models)
        self.assertEqual(orchestrator.agent_models[0], 'test-model')
    
    @patch('orchestrator.UniversalAgent')
    def test_create_agent_with_model_fallback(self, mock_agent_class):
        """Test creating agent with model fallback on error."""
        # First call fails, second succeeds
        mock_agent = MagicMock()
        mock_agent.provider_config = MagicMock()
        mock_agent.provider_config.model = 'fallback-model'
        
        mock_agent_class.side_effect = [Exception("Test error"), mock_agent]
        
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        agent = orchestrator._create_agent_with_model(0, 'test-model')
        
        self.assertIsNotNone(agent)
        self.assertIn(0, orchestrator.agent_models)
        self.assertEqual(orchestrator.agent_models[0], 'fallback-model')
    
    @patch('model_config.model_configuration_manager.ModelConfigurationManager.get_available_models')
    def test_estimate_agent_cost(self, mock_get_models):
        """Test agent cost estimation."""
        from model_config.data_models import ModelInfo
        
        # Mock model with cost information
        mock_model = ModelInfo(
            id='test-model',
            name='Test Model',
            provider='test',
            supports_function_calling=True,
            context_window=4000,
            input_cost_per_1m=1.0,
            output_cost_per_1m=2.0,
            description='Test model'
        )
        mock_get_models.return_value = [mock_model]
        
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        # Test cost estimation
        cost = orchestrator._estimate_agent_cost(0, 'test-model', 1000, 500)
        
        # Should calculate cost based on token estimation
        # 1000 chars input / 4 = 250 tokens, 500 chars output / 4 = 125 tokens
        # Cost = (250/1M * 1.0) + (125/1M * 2.0) = 0.00025 + 0.00025 = 0.0005
        expected_cost = (250 / 1_000_000 * 1.0) + (125 / 1_000_000 * 2.0)
        self.assertAlmostEqual(cost, expected_cost, places=8)
        
        # Check that cost is tracked
        self.assertIn(0, orchestrator.agent_costs)
        self.assertAlmostEqual(orchestrator.agent_costs[0], expected_cost, places=8)
    
    @patch('model_config.model_configuration_manager.ModelConfigurationManager.get_available_models')
    def test_estimate_agent_cost_no_model_info(self, mock_get_models):
        """Test agent cost estimation when model info is not available."""
        mock_get_models.return_value = []
        
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        cost = orchestrator._estimate_agent_cost(0, 'unknown-model', 1000, 500)
        
        self.assertEqual(cost, 0.0)
    
    def test_get_execution_summary_without_multi_model(self):
        """Test execution summary without multi-model configuration."""
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        summary = orchestrator.get_execution_summary()
        
        self.assertFalse(summary['multi_model_enabled'])
        self.assertIsNone(summary['synthesis_model'])
        self.assertEqual(summary['total_estimated_cost'], 0.0)
    
    def test_get_execution_summary_with_multi_model(self):
        """Test execution summary with multi-model configuration."""
        config_with_multi_model = self.basic_config.copy()
        config_with_multi_model['multi_model'] = self.multi_model_config
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_with_multi_model, f)
        
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        # Simulate some agent execution
        orchestrator.agent_models[0] = 'deepseek-chat'
        orchestrator.agent_models[1] = 'deepseek-reasoner'
        orchestrator.agent_costs[0] = 0.001
        orchestrator.agent_costs[1] = 0.002
        
        summary = orchestrator.get_execution_summary()
        
        self.assertTrue(summary['multi_model_enabled'])
        self.assertEqual(summary['synthesis_model'], 'deepseek-reasoner')
        self.assertEqual(summary['total_estimated_cost'], 0.003)
        self.assertEqual(len(summary['agent_models']), 2)
    
    @patch('orchestrator.TaskOrchestrator._create_agent_with_model')
    @patch('orchestrator.TaskOrchestrator._estimate_agent_cost')
    def test_run_agent_parallel_success(self, mock_estimate_cost, mock_create_agent):
        """Test successful parallel agent execution."""
        # Mock agent
        mock_agent = MagicMock()
        mock_agent.run.return_value = "Test response"
        mock_create_agent.return_value = mock_agent
        mock_estimate_cost.return_value = 0.001
        
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        result = orchestrator.run_agent_parallel(0, "Test task")
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['agent_id'], 0)
        self.assertEqual(result['response'], 'Test response')
        self.assertEqual(result['estimated_cost'], 0.001)
        self.assertIn('model', result)
        self.assertIn('execution_time', result)
    
    @patch('orchestrator.TaskOrchestrator._create_agent_with_model')
    def test_run_agent_parallel_error(self, mock_create_agent):
        """Test parallel agent execution with error."""
        # Mock agent that raises exception
        mock_agent = MagicMock()
        mock_agent.run.side_effect = Exception("Test error")
        mock_create_agent.return_value = mock_agent
        
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        result = orchestrator.run_agent_parallel(0, "Test task")
        
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['agent_id'], 0)
        self.assertIn('Test error', result['response'])
        self.assertEqual(result['estimated_cost'], 0.0)
    
    @patch('orchestrator.TaskOrchestrator.run_agent_parallel')
    @patch('orchestrator.TaskOrchestrator.decompose_task')
    def test_orchestrate_with_multi_model_logging(self, mock_decompose, mock_run_agent):
        """Test orchestration with multi-model logging."""
        config_with_multi_model = self.basic_config.copy()
        config_with_multi_model['multi_model'] = self.multi_model_config
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_with_multi_model, f)
        
        # Mock task decomposition
        mock_decompose.return_value = ["Task 1", "Task 2"]
        
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        # Mock agent results with side effect that updates orchestrator state
        def mock_run_agent_side_effect(agent_id, subtask):
            result = {
                'agent_id': agent_id,
                'status': 'success',
                'response': f'Response {agent_id + 1}',
                'execution_time': 1.0 + agent_id * 0.5,
                'model': 'deepseek-chat' if agent_id == 0 else 'deepseek-reasoner',
                'estimated_cost': 0.001 + agent_id * 0.001
            }
            # Update orchestrator state to simulate real execution
            orchestrator.agent_models[agent_id] = result['model']
            orchestrator.agent_costs[agent_id] = result['estimated_cost']
            return result
        
        mock_run_agent.side_effect = mock_run_agent_side_effect
        
        # Mock synthesis to avoid actual API call
        with patch.object(orchestrator, '_aggregate_consensus', return_value="Final response"):
            result = orchestrator.orchestrate("Test query")
        
        self.assertEqual(result, "Final response")
        
        # Check execution summary
        summary = orchestrator.get_execution_summary()
        self.assertTrue(summary['multi_model_enabled'])
        self.assertEqual(summary['total_estimated_cost'], 0.003)


if __name__ == '__main__':
    unittest.main()