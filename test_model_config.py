"""
Unit tests for the multi-model configuration system.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import tempfile
import os
import yaml

from model_config.data_models import ModelInfo, AgentModelConfig, CostInfo, ModelTestResult
from model_config.provider_model_service import ProviderModelService, ProviderModelServiceError
from model_config.cost_calculation_service import CostCalculationService, CostCalculationServiceError
from model_config.model_validation_service import ModelValidationService, ModelValidationServiceError
from model_config.model_configuration_manager import ModelConfigurationManager, ModelConfigurationManagerError
from config_manager import ConfigurationManager, ProviderConfig


class TestDataModels(unittest.TestCase):
    """Test data models."""
    
    def test_model_info_creation(self):
        """Test ModelInfo creation and validation."""
        model = ModelInfo(
            id="test-model",
            name="Test Model",
            provider="test",
            supports_function_calling=True,
            context_window=4000,
            input_cost_per_1m=1.0,
            output_cost_per_1m=2.0,
            description="Test model"
        )
        
        self.assertEqual(model.id, "test-model")
        self.assertEqual(model.name, "Test Model")
        self.assertTrue(model.supports_function_calling)
    
    def test_model_info_validation(self):
        """Test ModelInfo validation."""
        with self.assertRaises(ValueError):
            ModelInfo(
                id="",  # Empty ID should raise error
                name="Test",
                provider="test",
                supports_function_calling=True,
                context_window=4000,
                input_cost_per_1m=1.0,
                output_cost_per_1m=2.0,
                description="Test"
            )
    
    def test_agent_model_config(self):
        """Test AgentModelConfig functionality."""
        config = AgentModelConfig(
            agent_0_model="model-1",
            agent_1_model="model-2",
            agent_2_model="model-3",
            agent_3_model="model-4",
            synthesis_model="model-synthesis",
            default_model="model-default"
        )
        
        self.assertEqual(config.get_agent_model(0), "model-1")
        self.assertEqual(config.get_agent_model(1), "model-2")
        self.assertEqual(config.get_agent_model(99), "model-default")  # Fallback
        
        # Test dict conversion
        config_dict = config.to_dict()
        self.assertEqual(config_dict['agent_0_model'], "model-1")
        
        # Test from dict
        config2 = AgentModelConfig.from_dict(config_dict)
        self.assertEqual(config2.agent_0_model, "model-1")
    
    def test_cost_info(self):
        """Test CostInfo functionality."""
        cost_info = CostInfo(
            model_id="test-model",
            input_cost_per_1m=1.0,
            output_cost_per_1m=2.0
        )
        
        self.assertTrue(cost_info.has_cost_data)
        
        cost_info_no_data = CostInfo(
            model_id="test-model",
            input_cost_per_1m=None,
            output_cost_per_1m=None
        )
        
        self.assertFalse(cost_info_no_data.has_cost_data)


class TestProviderModelService(unittest.TestCase):
    """Test ProviderModelService."""
    
    def setUp(self):
        self.service = ProviderModelService()
    
    def test_cache_functionality(self):
        """Test caching mechanism."""
        # Initially no cache
        self.assertFalse(self.service._is_model_cache_valid("test"))
        
        # Add to cache
        test_models = [
            ModelInfo(
                id="test-1", name="Test 1", provider="test",
                supports_function_calling=True, context_window=4000,
                input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
            )
        ]
        self.service.model_cache["test"] = test_models
        self.service.last_model_fetch["test"] = datetime.now()
        
        # Should be valid now
        self.assertTrue(self.service._is_model_cache_valid("test"))
        
        # Should be invalid after TTL
        self.service.last_model_fetch["test"] = datetime.now() - timedelta(hours=2)
        self.assertFalse(self.service._is_model_cache_valid("test"))
    
    def test_filter_function_calling_models(self):
        """Test filtering models by function calling support."""
        models = [
            ModelInfo(
                id="model-1", name="Model 1", provider="test",
                supports_function_calling=True, context_window=4000,
                input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
            ),
            ModelInfo(
                id="model-2", name="Model 2", provider="test",
                supports_function_calling=False, context_window=4000,
                input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
            )
        ]
        
        filtered = self.service.filter_function_calling_models(models)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].id, "model-1")
    
    def test_get_known_deepseek_models(self):
        """Test getting known DeepSeek models."""
        models = self.service._get_known_deepseek_models()
        
        self.assertGreater(len(models), 0)
        self.assertTrue(all(model.provider == "deepseek" for model in models))
        self.assertTrue(all(model.supports_function_calling for model in models))
    
    def test_parse_cost(self):
        """Test cost parsing."""
        self.assertEqual(self.service._parse_cost("$1.50"), 1500.0)  # Converted to per 1M
        self.assertEqual(self.service._parse_cost("0.001"), 1.0)  # Converted to per 1M
        self.assertEqual(self.service._parse_cost("15.0"), 15.0)  # Already per 1M (high value)
        self.assertIsNone(self.service._parse_cost("invalid"))
        self.assertIsNone(self.service._parse_cost(None))
    
    @patch('requests.get')
    def test_fetch_openrouter_models_success(self, mock_get):
        """Test successful OpenRouter model fetching."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'data': [
                {
                    'id': 'test/model',
                    'name': 'Test Model',
                    'context_length': 4000,
                    'pricing': {
                        'prompt': '0.001',
                        'completion': '0.002'
                    },
                    'description': 'Test model'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        models = self.service._fetch_openrouter_models("test-key")
        
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].id, 'test/model')
        self.assertEqual(models[0].provider, 'openrouter')
    
    @patch('requests.get')
    def test_fetch_openrouter_models_failure(self, mock_get):
        """Test OpenRouter model fetching failure."""
        mock_get.side_effect = Exception("Network error")
        
        with self.assertRaises(ProviderModelServiceError):
            self.service._fetch_openrouter_models("test-key")


class TestCostCalculationService(unittest.TestCase):
    """Test CostCalculationService."""
    
    def setUp(self):
        self.provider_service = Mock()
        self.service = CostCalculationService(self.provider_service)
    
    def test_calculate_model_cost(self):
        """Test model cost calculation."""
        model = ModelInfo(
            id="test-model", name="Test", provider="test",
            supports_function_calling=True, context_window=4000,
            input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
        )
        
        cost = self.service._calculate_model_cost(model, 1000, 500)
        expected = (1000 / 1_000_000) * 1.0 + (500 / 1_000_000) * 2.0
        self.assertEqual(cost, expected)
    
    def test_calculate_model_cost_no_pricing(self):
        """Test model cost calculation with no pricing data."""
        model = ModelInfo(
            id="test-model", name="Test", provider="test",
            supports_function_calling=True, context_window=4000,
            input_cost_per_1m=None, output_cost_per_1m=None, description="Test"
        )
        
        cost = self.service._calculate_model_cost(model, 1000, 500)
        self.assertEqual(cost, 0.0)
    
    def test_calculate_configuration_cost(self):
        """Test configuration cost calculation."""
        models = [
            ModelInfo(
                id="model-1", name="Model 1", provider="test",
                supports_function_calling=True, context_window=4000,
                input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
            ),
            ModelInfo(
                id="model-2", name="Model 2", provider="test",
                supports_function_calling=True, context_window=4000,
                input_cost_per_1m=0.5, output_cost_per_1m=1.0, description="Test"
            )
        ]
        
        config = AgentModelConfig(
            agent_0_model="model-1",
            agent_1_model="model-1",
            agent_2_model="model-2",
            agent_3_model="model-2",
            synthesis_model="model-1",
            default_model="model-1"
        )
        
        estimate = self.service.calculate_configuration_cost(config, models)
        
        self.assertGreater(estimate.total_cost, 0)
        self.assertEqual(len(estimate.per_agent_costs), 4)
        self.assertTrue(any("Synthesis" in key for key in estimate.breakdown.keys()))
    
    def test_get_cheapest_configuration(self):
        """Test getting cheapest configuration."""
        models = [
            ModelInfo(
                id="expensive", name="Expensive", provider="test",
                supports_function_calling=True, context_window=4000,
                input_cost_per_1m=10.0, output_cost_per_1m=20.0, description="Test"
            ),
            ModelInfo(
                id="cheap", name="Cheap", provider="test",
                supports_function_calling=True, context_window=4000,
                input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
            )
        ]
        
        config = self.service.get_cheapest_configuration(models)
        
        self.assertEqual(config.agent_0_model, "cheap")
        self.assertEqual(config.synthesis_model, "cheap")
        self.assertEqual(config.profile_name, "budget")
    
    def test_get_cheapest_configuration_no_models(self):
        """Test getting cheapest configuration with no models."""
        with self.assertRaises(CostCalculationServiceError):
            self.service.get_cheapest_configuration([])


class TestModelValidationService(unittest.TestCase):
    """Test ModelValidationService."""
    
    def setUp(self):
        self.service = ModelValidationService()
    
    def test_validate_model_compatibility(self):
        """Test model compatibility validation."""
        # Valid model
        valid_model = ModelInfo(
            id="valid", name="Valid", provider="test",
            supports_function_calling=True, context_window=8000,
            input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
        )
        self.assertTrue(self.service.validate_model_compatibility(valid_model))
        
        # Invalid - no function calling
        invalid_model1 = ModelInfo(
            id="invalid1", name="Invalid", provider="test",
            supports_function_calling=False, context_window=8000,
            input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
        )
        self.assertFalse(self.service.validate_model_compatibility(invalid_model1))
        
        # Invalid - small context window
        invalid_model2 = ModelInfo(
            id="invalid2", name="Invalid", provider="test",
            supports_function_calling=True, context_window=2000,
            input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
        )
        self.assertFalse(self.service.validate_model_compatibility(invalid_model2))
    
    def test_validate_configuration(self):
        """Test configuration validation."""
        models = [
            ModelInfo(
                id="valid", name="Valid", provider="test",
                supports_function_calling=True, context_window=8000,
                input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
            ),
            ModelInfo(
                id="invalid", name="Invalid", provider="test",
                supports_function_calling=False, context_window=8000,
                input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
            )
        ]
        
        # Valid configuration
        valid_config = AgentModelConfig(
            agent_0_model="valid",
            agent_1_model="valid",
            agent_2_model="valid",
            agent_3_model="valid",
            synthesis_model="valid",
            default_model="valid"
        )
        
        results = self.service.validate_configuration(valid_config, models)
        self.assertTrue(all(results.values()))
        
        # Invalid configuration
        invalid_config = AgentModelConfig(
            agent_0_model="invalid",
            agent_1_model="valid",
            agent_2_model="nonexistent",
            agent_3_model="valid",
            synthesis_model="valid",
            default_model="valid"
        )
        
        results = self.service.validate_configuration(invalid_config, models)
        self.assertFalse(results["agent_0"])  # Invalid model
        self.assertTrue(results["agent_1"])   # Valid model
        self.assertFalse(results["agent_2"])  # Nonexistent model
    
    def test_get_validation_errors(self):
        """Test getting validation errors."""
        models = [
            ModelInfo(
                id="valid", name="Valid", provider="test",
                supports_function_calling=True, context_window=8000,
                input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
            )
        ]
        
        invalid_config = AgentModelConfig(
            agent_0_model="nonexistent",
            agent_1_model="valid",
            agent_2_model="",
            agent_3_model="valid",
            synthesis_model="valid",
            default_model="valid"
        )
        
        errors = self.service.get_validation_errors(invalid_config, models)
        
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("nonexistent" in error for error in errors))
        self.assertTrue(any("Agent 2 has no model" in error for error in errors))
    
    def test_suggest_fixes(self):
        """Test getting fix suggestions."""
        models = [
            ModelInfo(
                id="valid", name="Valid", provider="test",
                supports_function_calling=True, context_window=8000,
                input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
            )
        ]
        
        invalid_config = AgentModelConfig(
            agent_0_model="nonexistent",
            agent_1_model="valid",
            agent_2_model="valid",
            agent_3_model="valid",
            synthesis_model="valid",
            default_model="valid"
        )
        
        suggestions = self.service.suggest_fixes(invalid_config, models)
        
        self.assertIn("agent_0", suggestions)
        self.assertIn("valid", suggestions["agent_0"])


class TestModelConfigurationManager(unittest.TestCase):
    """Test ModelConfigurationManager."""
    
    def setUp(self):
        self.config_manager = Mock()
        self.manager = ModelConfigurationManager(self.config_manager)
    
    def test_save_and_load_configuration(self):
        """Test saving and loading configuration."""
        config = AgentModelConfig(
            agent_0_model="model-1",
            agent_1_model="model-2",
            agent_2_model="model-3",
            agent_3_model="model-4",
            synthesis_model="model-synthesis",
            default_model="model-default"
        )
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'test': 'data'}, f)
            temp_path = f.name
        
        try:
            # Save configuration
            success = self.manager.save_agent_configuration(config, temp_path)
            self.assertTrue(success)
            
            # Load configuration
            loaded_config = self.manager.load_agent_configuration(temp_path)
            self.assertIsNotNone(loaded_config)
            self.assertEqual(loaded_config.agent_0_model, "model-1")
            
        finally:
            os.unlink(temp_path)
    
    def test_load_nonexistent_configuration(self):
        """Test loading from nonexistent file."""
        result = self.manager.load_agent_configuration("nonexistent.yaml")
        self.assertIsNone(result)
    
    @patch.object(ModelConfigurationManager, 'get_available_models')
    def test_validate_model_compatibility(self, mock_get_models):
        """Test model compatibility validation."""
        mock_get_models.return_value = [
            ModelInfo(
                id="valid", name="Valid", provider="test",
                supports_function_calling=True, context_window=8000,
                input_cost_per_1m=1.0, output_cost_per_1m=2.0, description="Test"
            )
        ]
        
        self.assertTrue(self.manager.validate_model_compatibility("valid"))
        self.assertFalse(self.manager.validate_model_compatibility("nonexistent"))
    
    def test_export_import_configuration(self):
        """Test configuration export and import."""
        config = AgentModelConfig(
            agent_0_model="model-1",
            agent_1_model="model-2",
            agent_2_model="model-3",
            agent_3_model="model-4",
            synthesis_model="model-synthesis",
            default_model="model-default"
        )
        
        # Export
        export_data = self.manager.export_configuration(config, include_costs=False)
        
        self.assertIn('configuration', export_data)
        self.assertIn('export_timestamp', export_data)
        self.assertEqual(export_data['configuration']['agent_0_model'], 'model-1')
        
        # Mock validation for import
        with patch.object(self.manager, 'validate_configuration') as mock_validate:
            mock_validate.return_value = {'valid': True, 'errors': []}
            
            # Import
            imported_config = self.manager.import_configuration(export_data)
            self.assertEqual(imported_config.agent_0_model, 'model-1')


class TestConfigurationManagerExtensions(unittest.TestCase):
    """Test extensions to ConfigurationManager."""
    
    def setUp(self):
        self.config_manager = ConfigurationManager()
        # Mock config data
        self.config_manager.config = {
            'multi_model': {
                'agent_0_model': 'model-1',
                'agent_1_model': 'model-2',
                'synthesis_model': 'synthesis-model',
                'default_model': 'default-model'
            },
            'openrouter': {
                'model': 'fallback-model'
            }
        }
    
    def test_get_multi_model_config(self):
        """Test getting multi-model configuration."""
        config = self.config_manager.get_multi_model_config()
        self.assertEqual(config['agent_0_model'], 'model-1')
    
    def test_has_multi_model_config(self):
        """Test checking for multi-model configuration."""
        self.assertTrue(self.config_manager.has_multi_model_config())
        
        # Test without multi-model config
        self.config_manager.config = {}
        self.assertFalse(self.config_manager.has_multi_model_config())
    
    def test_get_agent_model(self):
        """Test getting agent-specific model."""
        # With multi-model config
        model = self.config_manager.get_agent_model(0)
        self.assertEqual(model, 'model-1')
        
        # Fallback to default
        model = self.config_manager.get_agent_model(99)
        self.assertEqual(model, 'default-model')
        
        # Without multi-model config
        self.config_manager.config = {
            'openrouter': {'model': 'fallback-model'}
        }
        with patch.object(self.config_manager, 'get_provider_config') as mock_provider:
            mock_provider.return_value = Mock(model='fallback-model')
            model = self.config_manager.get_agent_model(0)
            self.assertEqual(model, 'fallback-model')
    
    def test_get_synthesis_model(self):
        """Test getting synthesis model."""
        model = self.config_manager.get_synthesis_model()
        self.assertEqual(model, 'synthesis-model')


if __name__ == '__main__':
    unittest.main()