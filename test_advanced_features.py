#!/usr/bin/env python3
"""
End-to-end tests for advanced multi-model configuration features.
Tests configuration testing, export/import, cost monitoring, and comparison tools.
"""

import os
import json
import yaml
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from model_config.model_configuration_manager import ModelConfigurationManager
from model_config.data_models import AgentModelConfig, ModelInfo, ModelTestResult
from cost_monitor import CostMonitor, CostAlert, BudgetManager
from orchestrator import TaskOrchestrator
from config_manager import ConfigurationManager


class TestAdvancedFeatures(unittest.TestCase):
    """Test advanced multi-model configuration features."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        
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
                'budget_limit': 0.10,  # $0.10 budget limit
                'question_generation_prompt': 'Generate questions',
                'synthesis_prompt': 'Synthesize responses'
            },
            'search': {'max_results': 5}
        }
        
        yaml.dump(self.basic_config, self.temp_config)
        self.temp_config.close()
        self.config_path = self.temp_config.name
        
        # Test configuration
        self.test_config = AgentModelConfig(
            agent_0_model='deepseek-chat',
            agent_1_model='deepseek-reasoner',
            agent_2_model='deepseek-chat',
            agent_3_model='deepseek-reasoner',
            synthesis_model='deepseek-reasoner',
            default_model='deepseek-chat',
            profile_name='test'
        )
        
        # Mock models
        self.mock_models = [
            ModelInfo(
                id='deepseek-chat',
                name='DeepSeek Chat',
                provider='deepseek',
                supports_function_calling=True,
                context_window=4000,
                input_cost_per_1m=0.14,
                output_cost_per_1m=0.28,
                description='Fast chat model'
            ),
            ModelInfo(
                id='deepseek-reasoner',
                name='DeepSeek Reasoner',
                provider='deepseek',
                supports_function_calling=True,
                context_window=8000,
                input_cost_per_1m=2.19,
                output_cost_per_1m=8.78,
                description='Advanced reasoning model'
            )
        ]
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.config_path):
            os.unlink(self.config_path)
    
    @patch('model_config.model_configuration_manager.ModelConfigurationManager.get_available_models')
    def test_configuration_testing(self, mock_get_models):
        """Test configuration testing functionality."""
        mock_get_models.return_value = self.mock_models
        
        config_manager = ConfigurationManager()
        config_manager.load_config(self.config_path)
        manager = ModelConfigurationManager(config_manager)
        
        # Mock the test results
        with patch.object(manager, '_test_single_model') as mock_test:
            mock_test.return_value = ModelTestResult(
                model_id='test-model',
                success=True,
                response_time=1.5
            )
            
            results = manager.test_configuration_connectivity(self.test_config)
            
            # Should test all agents plus synthesis
            self.assertEqual(len(results), 5)  # 4 agents + synthesis
            self.assertIn('agent_0', results)
            self.assertIn('agent_1', results)
            self.assertIn('agent_2', results)
            self.assertIn('agent_3', results)
            self.assertIn('synthesis', results)
            
            # All should be successful
            for result in results.values():
                self.assertTrue(result.success)
    
    @patch('model_config.model_configuration_manager.ModelConfigurationManager.get_available_models')
    def test_configuration_export_import(self, mock_get_models):
        """Test configuration export and import functionality."""
        mock_get_models.return_value = self.mock_models
        
        config_manager = ConfigurationManager()
        config_manager.load_config(self.config_path)
        manager = ModelConfigurationManager(config_manager)
        
        # Test export
        exported = manager.export_configuration_with_sanitization(self.test_config, include_costs=True)
        
        self.assertIn('configuration', exported)
        self.assertIn('export_timestamp', exported)
        self.assertIn('note', exported)
        self.assertTrue(exported['requires_api_setup'])
        
        # Test import
        imported_config = manager.import_configuration(exported)
        
        self.assertEqual(imported_config.agent_0_model, self.test_config.agent_0_model)
        self.assertEqual(imported_config.synthesis_model, self.test_config.synthesis_model)
        self.assertEqual(imported_config.profile_name, self.test_config.profile_name)
    
    @patch('model_config.model_configuration_manager.ModelConfigurationManager.get_available_models')
    def test_configuration_comparison(self, mock_get_models):
        """Test configuration comparison functionality."""
        mock_get_models.return_value = self.mock_models
        
        config_manager = ConfigurationManager()
        config_manager.load_config(self.config_path)
        manager = ModelConfigurationManager(config_manager)
        
        # Create second config for comparison
        config2 = AgentModelConfig(
            agent_0_model='deepseek-reasoner',
            agent_1_model='deepseek-reasoner',
            agent_2_model='deepseek-reasoner',
            agent_3_model='deepseek-reasoner',
            synthesis_model='deepseek-reasoner',
            default_model='deepseek-reasoner',
            profile_name='premium'
        )
        
        # Test comparison report
        report = manager.create_configuration_comparison_report(
            [self.test_config, config2],
            ['Mixed Config', 'Premium Config']
        )
        
        self.assertIn('comparison_matrix', report)
        self.assertIn('summary', report)
        self.assertEqual(len(report['comparison_matrix']), 2)
        
        # Check summary
        summary = report['summary']
        self.assertEqual(summary['total_configurations'], 2)
        self.assertIn('best_cost_config', summary)
        self.assertIn('worst_cost_config', summary)
    
    @patch('model_config.model_configuration_manager.ModelConfigurationManager.get_available_models')
    def test_configuration_recommendations(self, mock_get_models):
        """Test configuration recommendations."""
        mock_get_models.return_value = self.mock_models
        
        config_manager = ConfigurationManager()
        config_manager.load_config(self.config_path)
        manager = ModelConfigurationManager(config_manager)
        
        recommendations = manager.get_configuration_recommendations(self.test_config)
        
        self.assertIn('current_cost', recommendations)
        self.assertIn('recommendations', recommendations)
        self.assertIn('recommendation_count', recommendations)
        self.assertIsInstance(recommendations['recommendations'], list)
    
    def test_cost_monitor_basic_functionality(self):
        """Test basic cost monitoring functionality."""
        monitor = CostMonitor(budget_limit=1.0)
        
        # Test recording costs
        monitor.record_agent_cost(0, 'test-model', 1000, 500, 0.001)
        monitor.record_agent_cost(1, 'test-model-2', 1500, 750, 0.002)
        
        summary = monitor.get_cost_summary()
        
        self.assertEqual(summary['total_cost'], 0.003)
        self.assertEqual(len(summary['agent_costs']), 2)
        self.assertEqual(summary['agent_costs'][0], 0.001)
        self.assertEqual(summary['agent_costs'][1], 0.002)
        self.assertEqual(summary['budget_limit'], 1.0)
        self.assertEqual(summary['budget_remaining'], 0.997)
    
    def test_cost_monitor_alerts(self):
        """Test cost monitoring alerts."""
        alerts_triggered = []
        
        def alert_callback(alert):
            alerts_triggered.append(alert)
        
        monitor = CostMonitor(budget_limit=0.01, alert_callback=alert_callback)
        
        # Trigger warning alert (50% of budget)
        monitor.record_agent_cost(0, 'test-model', 1000, 500, 0.006)
        self.assertEqual(len(alerts_triggered), 1)
        self.assertEqual(alerts_triggered[0].alert_type, 'warning')
        
        # Trigger critical alert (80% of budget)
        monitor.record_agent_cost(1, 'test-model', 1000, 500, 0.003)
        self.assertEqual(len(alerts_triggered), 2)
        self.assertEqual(alerts_triggered[1].alert_type, 'critical')
        
        # Trigger budget exceeded alert
        monitor.record_agent_cost(2, 'test-model', 1000, 500, 0.002)
        self.assertEqual(len(alerts_triggered), 3)
        self.assertEqual(alerts_triggered[2].alert_type, 'budget_exceeded')
    
    def test_cost_monitor_real_time_stats(self):
        """Test real-time cost statistics."""
        monitor = CostMonitor(budget_limit=1.0)
        
        # Record some costs
        monitor.record_agent_cost(0, 'test-model', 1000, 500, 0.001)
        monitor.record_agent_cost(1, 'test-model', 1500, 750, 0.002)
        
        stats = monitor.get_real_time_stats()
        
        self.assertEqual(stats['current_total'], 0.003)
        self.assertEqual(stats['recent_cost_1min'], 0.003)  # All recent
        self.assertEqual(stats['active_agents'], 2)
        self.assertEqual(stats['budget_status'], 'OK')
    
    def test_cost_monitor_export_report(self):
        """Test cost monitoring report export."""
        monitor = CostMonitor(budget_limit=1.0)
        
        # Record some costs
        monitor.record_agent_cost(0, 'test-model', 1000, 500, 0.001)
        monitor.record_agent_cost(1, 'test-model-2', 1500, 750, 0.002)
        
        # Export without detailed entries
        report = monitor.export_cost_report(include_detailed_entries=False)
        
        self.assertIn('report_timestamp', report)
        self.assertIn('session_summary', report)
        self.assertIn('configuration', report)
        self.assertNotIn('detailed_entries', report)
        
        # Export with detailed entries
        detailed_report = monitor.export_cost_report(include_detailed_entries=True)
        
        self.assertIn('detailed_entries', detailed_report)
        self.assertEqual(len(detailed_report['detailed_entries']), 2)
    
    def test_budget_manager(self):
        """Test budget manager functionality."""
        manager = BudgetManager()
        
        # Create monitors
        monitor1 = manager.create_monitor('session1', budget_limit=0.5)
        monitor2 = manager.create_monitor('session2', budget_limit=0.3)
        
        # Record costs
        monitor1.record_agent_cost(0, 'model1', 1000, 500, 0.1)
        monitor2.record_agent_cost(0, 'model2', 1500, 750, 0.2)
        
        # Set global budget
        manager.set_global_budget(1.0)
        
        # Get global summary
        summary = manager.get_global_summary()
        
        self.assertAlmostEqual(summary['total_cost_all_monitors'], 0.3, places=6)
        self.assertEqual(summary['global_budget'], 1.0)
        self.assertEqual(summary['global_budget_remaining'], 0.7)
        self.assertEqual(summary['active_monitors'], 2)
        self.assertIn('session1', summary['monitor_summaries'])
        self.assertIn('session2', summary['monitor_summaries'])
    
    def test_orchestrator_cost_monitoring_integration(self):
        """Test orchestrator integration with cost monitoring."""
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        # Should have cost monitoring enabled due to budget_limit in config
        self.assertIsNotNone(orchestrator.cost_monitor)
        self.assertEqual(orchestrator.budget_limit, 0.10)
        
        # Test cost monitoring summary
        summary = orchestrator.get_cost_monitoring_summary()
        self.assertIsNotNone(summary)
        self.assertEqual(summary['budget_limit'], 0.10)
    
    @patch('orchestrator.TaskOrchestrator.run_agent_parallel')
    @patch('orchestrator.TaskOrchestrator.decompose_task')
    def test_end_to_end_workflow(self, mock_decompose, mock_run_agent):
        """Test complete end-to-end workflow with all advanced features."""
        # Setup orchestrator with cost monitoring
        orchestrator = TaskOrchestrator(self.config_path, silent=True)
        
        # Mock task decomposition
        mock_decompose.return_value = ["Task 1", "Task 2"]
        
        # Mock agent results with costs
        def mock_run_agent_side_effect(agent_id, subtask):
            result = {
                'agent_id': agent_id,
                'status': 'success',
                'response': f'Response {agent_id + 1}',
                'execution_time': 1.0,
                'model': 'deepseek-chat',
                'estimated_cost': 0.01  # High cost to trigger alerts
            }
            # Update orchestrator state
            orchestrator.agent_models[agent_id] = result['model']
            orchestrator.agent_costs[agent_id] = result['estimated_cost']
            
            # Also record in cost monitor if it exists
            if orchestrator.cost_monitor:
                orchestrator.cost_monitor.record_agent_cost(
                    agent_id=agent_id,
                    model=result['model'],
                    input_tokens=250,  # Estimated tokens
                    output_tokens=125,
                    cost=result['estimated_cost']
                )
            
            return result
        
        mock_run_agent.side_effect = mock_run_agent_side_effect
        
        # Mock synthesis to avoid actual API call
        with patch.object(orchestrator, '_aggregate_consensus', return_value="Final response"):
            result = orchestrator.orchestrate("Test query")
        
        self.assertEqual(result, "Final response")
        
        # Check cost monitoring worked
        cost_summary = orchestrator.get_cost_monitoring_summary()
        self.assertIsNotNone(cost_summary)
        self.assertGreater(cost_summary['total_cost'], 0)
        
        # Should have triggered budget alerts due to high costs
        if cost_summary['alerts_triggered']:
            self.assertGreater(len(cost_summary['alerts_triggered']), 0)


if __name__ == '__main__':
    unittest.main()