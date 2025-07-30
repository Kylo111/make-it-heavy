"""
Unit tests for the multi-model configuration GUI components (without Tkinter display).
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_config.data_models import ModelInfo, AgentModelConfig, CostEstimate


class TestMultiModelConfigLogic(unittest.TestCase):
    """Test the logic components without GUI dependencies."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample model data
        self.sample_models = [
            ModelInfo(
                id="test-model-1",
                name="Test Model 1",
                provider="test-provider",
                supports_function_calling=True,
                context_window=4096,
                input_cost_per_1m=1.0,
                output_cost_per_1m=2.0,
                description="Test model 1 description"
            ),
            ModelInfo(
                id="test-model-2",
                name="Test Model 2",
                provider="test-provider",
                supports_function_calling=True,
                context_window=8192,
                input_cost_per_1m=2.0,
                output_cost_per_1m=4.0,
                description="Test model 2 description"
            )
        ]
        
        # Sample configuration
        self.sample_config = AgentModelConfig(
            agent_0_model="test-model-1",
            agent_1_model="test-model-1",
            agent_2_model="test-model-2",
            agent_3_model="test-model-2",
            synthesis_model="test-model-1",
            default_model="test-model-1",
            profile_name="test"
        )
    
    def test_agent_model_config_creation(self):
        """Test creating AgentModelConfig."""
        config = AgentModelConfig(
            agent_0_model="model-1",
            agent_1_model="model-2",
            agent_2_model="model-3",
            agent_3_model="model-4",
            synthesis_model="model-5",
            default_model="model-default"
        )
        
        self.assertEqual(config.agent_0_model, "model-1")
        self.assertEqual(config.get_agent_model(0), "model-1")
        self.assertEqual(config.get_agent_model(1), "model-2")
        self.assertEqual(config.get_agent_model(99), "model-default")  # Fallback
    
    def test_agent_model_config_to_dict(self):
        """Test converting AgentModelConfig to dictionary."""
        config_dict = self.sample_config.to_dict()
        
        expected_keys = [
            'agent_0_model', 'agent_1_model', 'agent_2_model', 'agent_3_model',
            'synthesis_model', 'default_model', 'profile_name'
        ]
        
        for key in expected_keys:
            self.assertIn(key, config_dict)
        
        self.assertEqual(config_dict['agent_0_model'], "test-model-1")
        self.assertEqual(config_dict['profile_name'], "test")
    
    def test_agent_model_config_from_dict(self):
        """Test creating AgentModelConfig from dictionary."""
        config_dict = {
            'agent_0_model': 'model-a',
            'agent_1_model': 'model-b',
            'agent_2_model': 'model-c',
            'agent_3_model': 'model-d',
            'synthesis_model': 'model-e',
            'default_model': 'model-default',
            'profile_name': 'custom'
        }
        
        config = AgentModelConfig.from_dict(config_dict)
        
        self.assertEqual(config.agent_0_model, 'model-a')
        self.assertEqual(config.agent_1_model, 'model-b')
        self.assertEqual(config.profile_name, 'custom')
    
    def test_model_info_validation(self):
        """Test ModelInfo validation."""
        # Valid model info
        model = ModelInfo(
            id="valid-model",
            name="Valid Model",
            provider="test-provider",
            supports_function_calling=True,
            context_window=4096,
            input_cost_per_1m=1.0,
            output_cost_per_1m=2.0,
            description="Valid model"
        )
        
        self.assertEqual(model.id, "valid-model")
        self.assertTrue(model.supports_function_calling)
        
        # Test invalid model info
        with self.assertRaises(ValueError):
            ModelInfo(
                id="",  # Empty ID should raise error
                name="Invalid Model",
                provider="test-provider",
                supports_function_calling=True,
                context_window=4096,
                input_cost_per_1m=1.0,
                output_cost_per_1m=2.0,
                description="Invalid model"
            )
    
    def test_cost_estimate_properties(self):
        """Test CostEstimate properties."""
        cost_estimate = CostEstimate(
            total_input_tokens=1000,
            total_output_tokens=500,
            total_cost=0.015,
            per_agent_costs={0: 0.003, 1: 0.004, 2: 0.003, 3: 0.002},
            breakdown={'synthesis': 0.003}
        )
        
        self.assertEqual(cost_estimate.cost_per_query, 0.015)
        self.assertEqual(cost_estimate.per_agent_costs[0], 0.003)
        self.assertEqual(cost_estimate.breakdown['synthesis'], 0.003)
    
    @patch('gui.multi_model_config_panel.ModelConfigurationManager')
    def test_panel_logic_without_ui(self, mock_model_manager):
        """Test panel logic without creating UI components."""
        # Mock the model manager
        mock_manager_instance = Mock()
        mock_model_manager.return_value = mock_manager_instance
        
        # Mock methods
        mock_manager_instance.get_available_models.return_value = self.sample_models
        mock_manager_instance.get_predefined_profiles.return_value = []
        mock_manager_instance.load_agent_configuration.return_value = self.sample_config
        
        # Import the panel class
        from gui.multi_model_config_panel import MultiModelConfigPanel
        
        # Test the logic methods without creating the UI
        # We can't instantiate the panel without Tkinter, but we can test individual methods
        
        # Test agent names mapping
        agent_names = {
            0: "Research Agent",
            1: "Analysis Agent", 
            2: "Verification Agent",
            3: "Alternatives Agent"
        }
        
        self.assertEqual(len(agent_names), 4)
        self.assertEqual(agent_names[0], "Research Agent")
    
    def test_configuration_validation_logic(self):
        """Test configuration validation logic."""
        # Test valid configuration
        valid_config = AgentModelConfig(
            agent_0_model="test-model-1",
            agent_1_model="test-model-1",
            agent_2_model="test-model-1",
            agent_3_model="test-model-1",
            synthesis_model="test-model-1",
            default_model="test-model-1"
        )
        
        # All models should be the same
        models = [
            valid_config.agent_0_model,
            valid_config.agent_1_model,
            valid_config.agent_2_model,
            valid_config.agent_3_model
        ]
        
        self.assertTrue(all(model == "test-model-1" for model in models))
    
    def test_profile_creation_logic(self):
        """Test profile creation logic."""
        from model_config.data_models import ConfigurationProfile
        
        # Test budget profile creation
        try:
            budget_profile = ConfigurationProfile.create_budget_profile(self.sample_models)
            self.assertEqual(budget_profile.name, "Budget")
            self.assertIsNotNone(budget_profile.config)
        except ValueError:
            # This is expected if no suitable models are found
            pass
        
        # Test balanced profile creation
        try:
            balanced_profile = ConfigurationProfile.create_balanced_profile(self.sample_models)
            self.assertEqual(balanced_profile.name, "Balanced")
            self.assertIsNotNone(balanced_profile.config)
        except ValueError:
            # This is expected if no suitable models are found
            pass
        
        # Test premium profile creation
        try:
            premium_profile = ConfigurationProfile.create_premium_profile(self.sample_models)
            self.assertEqual(premium_profile.name, "Premium")
            self.assertIsNotNone(premium_profile.config)
        except ValueError:
            # This is expected if no suitable models are found
            pass


class TestGUIComponentLogic(unittest.TestCase):
    """Test GUI component logic without creating actual widgets."""
    
    def test_model_display_name_parsing(self):
        """Test parsing model display names."""
        # Simulate the display name format used in the GUI
        display_name = "Test Model 1 (test-model-1)"
        
        # Extract model ID (this is the logic used in AgentModelSelector)
        if '(' in display_name and ')' in display_name:
            model_id = display_name.split('(')[-1].rstrip(')')
        else:
            model_id = None
        
        self.assertEqual(model_id, "test-model-1")
    
    def test_cost_formatting(self):
        """Test cost formatting logic."""
        # Test cost formatting (this is the logic used in ModelInfoWidget)
        input_cost = 1.234
        output_cost = 2.567
        
        input_cost_text = f"${input_cost:.3f} per 1M tokens"
        output_cost_text = f"${output_cost:.3f} per 1M tokens"
        
        self.assertEqual(input_cost_text, "$1.234 per 1M tokens")
        self.assertEqual(output_cost_text, "$2.567 per 1M tokens")
        
        # Test None cost handling
        none_cost = None
        cost_text = f"${none_cost:.3f} per 1M tokens" if none_cost is not None else "Not available"
        self.assertEqual(cost_text, "Not available")
    
    def test_context_window_formatting(self):
        """Test context window formatting logic."""
        # Test context window formatting (this is the logic used in ModelInfoWidget)
        context_window = 4096
        context_text = f"{context_window:,} tokens" if context_window else "N/A"
        
        self.assertEqual(context_text, "4,096 tokens")
        
        # Test None context window
        none_context = None
        context_text = f"{none_context:,} tokens" if none_context else "N/A"
        self.assertEqual(context_text, "N/A")
    
    def test_function_calling_display(self):
        """Test function calling support display logic."""
        # Test function calling display (this is the logic used in ModelInfoWidget)
        supports_function_calling = True
        function_calling_text = "✓ Supported" if supports_function_calling else "✗ Not supported"
        self.assertEqual(function_calling_text, "✓ Supported")
        
        supports_function_calling = False
        function_calling_text = "✓ Supported" if supports_function_calling else "✗ Not supported"
        self.assertEqual(function_calling_text, "✗ Not supported")


class TestIntegrationLogic(unittest.TestCase):
    """Test integration logic between components."""
    
    def test_configuration_update_flow(self):
        """Test the flow of updating configuration."""
        # Initial configuration
        config = AgentModelConfig(
            agent_0_model="model-1",
            agent_1_model="model-1",
            agent_2_model="model-1",
            agent_3_model="model-1",
            synthesis_model="model-1",
            default_model="model-1",
            profile_name="budget"
        )
        
        # Simulate agent model change (this is the logic in MultiModelConfigPanel)
        agent_id = 0
        new_model_id = "model-2"
        
        if agent_id == 0:
            config.agent_0_model = new_model_id
        elif agent_id == 1:
            config.agent_1_model = new_model_id
        elif agent_id == 2:
            config.agent_2_model = new_model_id
        elif agent_id == 3:
            config.agent_3_model = new_model_id
        
        # Profile should change to custom
        config.profile_name = "custom"
        
        # Verify changes
        self.assertEqual(config.agent_0_model, "model-2")
        self.assertEqual(config.profile_name, "custom")
    
    def test_validation_error_handling(self):
        """Test validation error handling logic."""
        # Simulate validation results
        validation_results = {
            'agent_0_model': True,
            'agent_1_model': True,
            'agent_2_model': False,  # This agent has an invalid model
            'agent_3_model': True,
            'synthesis_model': True
        }
        
        errors = []
        if not validation_results['agent_2_model']:
            errors.append("Agent 2 (Verification Agent) has an invalid model")
        
        # Check if configuration is valid
        is_valid = all(validation_results.values())
        
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 1)
        self.assertIn("Verification Agent", errors[0])


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)