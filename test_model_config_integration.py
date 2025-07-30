"""
Integration tests for the multi-model configuration system.
"""

import unittest
import tempfile
import os
import yaml
from unittest.mock import patch, Mock

from model_config import ModelConfigurationManager
from model_config.data_models import ModelInfo, AgentModelConfig
from config_manager import ConfigurationManager


class TestModelConfigIntegration(unittest.TestCase):
    """Integration tests for the complete model configuration system."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_config_file = None
        
    def tearDown(self):
        """Clean up test environment."""
        if self.temp_config_file and os.path.exists(self.temp_config_file):
            os.unlink(self.temp_config_file)
    
    def test_complete_configuration_workflow(self):
        """Test the complete workflow from getting models to saving configuration."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            initial_config = {
                'provider': {'type': 'deepseek'},
                'deepseek': {
                    'api_key': 'test-key',
                    'base_url': 'https://api.deepseek.com',
                    'model': 'deepseek-chat'
                }
            }
            yaml.dump(initial_config, f)
            self.temp_config_file = f.name
        
        # Initialize configuration manager
        config_manager = ConfigurationManager()
        config_manager.load_config(self.temp_config_file)
        
        # Initialize model configuration manager
        model_manager = ModelConfigurationManager(config_manager)
        
        # Mock the provider service to return test models
        test_models = [
            ModelInfo(
                id="deepseek-chat",
                name="DeepSeek Chat",
                provider="deepseek",
                supports_function_calling=True,
                context_window=64000,
                input_cost_per_1m=0.27,
                output_cost_per_1m=1.10,
                description="DeepSeek chat model"
            ),
            ModelInfo(
                id="deepseek-reasoner",
                name="DeepSeek Reasoner",
                provider="deepseek",
                supports_function_calling=True,
                context_window=64000,
                input_cost_per_1m=0.55,
                output_cost_per_1m=2.19,
                description="DeepSeek reasoning model"
            )
        ]
        
        with patch.object(model_manager, 'get_available_models', return_value=test_models):
                
                # 1. Get available models
                available_models = model_manager.get_available_models()
                self.assertEqual(len(available_models), 2)
                self.assertTrue(all(model.supports_function_calling for model in available_models))
                
                # 2. Create a configuration
                config = AgentModelConfig(
                    agent_0_model="deepseek-chat",
                    agent_1_model="deepseek-reasoner",
                    agent_2_model="deepseek-chat",
                    agent_3_model="deepseek-reasoner",
                    synthesis_model="deepseek-reasoner",
                    default_model="deepseek-chat",
                    profile_name="mixed"
                )
                
                # 3. Validate the configuration
                validation_result = model_manager.validate_configuration(config)
                self.assertTrue(validation_result['valid'])
                self.assertEqual(len(validation_result['errors']), 0)
                
                # 4. Calculate cost estimate
                cost_estimate = model_manager.calculate_configuration_cost(config)
                self.assertGreater(cost_estimate.total_cost, 0)
                self.assertEqual(len(cost_estimate.per_agent_costs), 4)
                
                # 5. Save the configuration
                success = model_manager.save_agent_configuration(config, self.temp_config_file)
                self.assertTrue(success)
                
                # 6. Load the configuration back
                loaded_config = model_manager.load_agent_configuration(self.temp_config_file)
                self.assertIsNotNone(loaded_config)
                self.assertEqual(loaded_config.agent_0_model, "deepseek-chat")
                self.assertEqual(loaded_config.agent_1_model, "deepseek-reasoner")
                
                # 7. Test configuration manager extensions (reload config first)
                config_manager.load_config(self.temp_config_file)
                self.assertTrue(config_manager.has_multi_model_config())
                agent_0_model = config_manager.get_agent_model(0)
                self.assertEqual(agent_0_model, "deepseek-chat")
                
                synthesis_model = config_manager.get_synthesis_model()
                self.assertEqual(synthesis_model, "deepseek-reasoner")
    
    def test_predefined_profiles(self):
        """Test predefined configuration profiles."""
        config_manager = ConfigurationManager()
        model_manager = ModelConfigurationManager(config_manager)
        
        # Mock models with different costs
        test_models = [
            ModelInfo(
                id="cheap-model",
                name="Cheap Model",
                provider="test",
                supports_function_calling=True,
                context_window=4000,
                input_cost_per_1m=0.1,
                output_cost_per_1m=0.2,
                description="Cheap model"
            ),
            ModelInfo(
                id="expensive-model",
                name="Expensive Model",
                provider="test",
                supports_function_calling=True,
                context_window=8000,
                input_cost_per_1m=5.0,
                output_cost_per_1m=10.0,
                description="Expensive model"
            ),
            ModelInfo(
                id="medium-model",
                name="Medium Model",
                provider="test",
                supports_function_calling=True,
                context_window=6000,
                input_cost_per_1m=1.0,
                output_cost_per_1m=2.0,
                description="Medium model"
            )
        ]
        
        with patch.object(model_manager, 'get_available_models', return_value=test_models):
                
                profiles = model_manager.get_predefined_profiles()
                
                # Should have budget, balanced, and premium profiles
                profile_names = [p.name for p in profiles]
                self.assertIn("Budget", profile_names)
                self.assertIn("Balanced", profile_names)
                self.assertIn("Premium", profile_names)
                
                # Budget profile should use cheapest model
                budget_profile = next(p for p in profiles if p.name == "Budget")
                self.assertEqual(budget_profile.config.agent_0_model, "cheap-model")
                
                # Premium profile should use most expensive model
                premium_profile = next(p for p in profiles if p.name == "Premium")
                self.assertEqual(premium_profile.config.agent_0_model, "expensive-model")
    
    def test_configuration_export_import(self):
        """Test configuration export and import functionality."""
        config_manager = ConfigurationManager()
        model_manager = ModelConfigurationManager(config_manager)
        
        # Create a test configuration
        config = AgentModelConfig(
            agent_0_model="model-1",
            agent_1_model="model-2",
            agent_2_model="model-3",
            agent_3_model="model-4",
            synthesis_model="synthesis-model",
            default_model="default-model",
            profile_name="test"
        )
        
        # Mock validation to pass
        with patch.object(model_manager, 'validate_configuration') as mock_validate:
            mock_validate.return_value = {'valid': True, 'errors': []}
            
            # Export configuration
            export_data = model_manager.export_configuration(config, include_costs=False)
            
            self.assertIn('configuration', export_data)
            self.assertIn('export_timestamp', export_data)
            self.assertIn('version', export_data)
            
            # Import configuration
            imported_config = model_manager.import_configuration(export_data)
            
            self.assertEqual(imported_config.agent_0_model, config.agent_0_model)
            self.assertEqual(imported_config.synthesis_model, config.synthesis_model)
            self.assertEqual(imported_config.profile_name, config.profile_name)
    
    def test_configuration_validation_errors(self):
        """Test configuration validation with errors."""
        config_manager = ConfigurationManager()
        model_manager = ModelConfigurationManager(config_manager)
        
        # Mock models
        test_models = [
            ModelInfo(
                id="valid-model",
                name="Valid Model",
                provider="test",
                supports_function_calling=True,
                context_window=8000,
                input_cost_per_1m=1.0,
                output_cost_per_1m=2.0,
                description="Valid model"
            )
        ]
        
        # Create invalid configuration
        invalid_config = AgentModelConfig(
            agent_0_model="nonexistent-model",
            agent_1_model="valid-model",
            agent_2_model="",
            agent_3_model="valid-model",
            synthesis_model="valid-model",
            default_model="valid-model"
        )
        
        with patch.object(model_manager, 'get_available_models', return_value=test_models):
                
                validation_result = model_manager.validate_configuration(invalid_config)
                
                self.assertFalse(validation_result['valid'])
                self.assertGreater(len(validation_result['errors']), 0)
                self.assertIn('suggestions', validation_result)
                
                # Should suggest fixes
                suggestions = validation_result['suggestions']
                self.assertIn('agent_0', suggestions)


if __name__ == '__main__':
    unittest.main()