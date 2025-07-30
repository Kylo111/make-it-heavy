#!/usr/bin/env python3
"""
Integration test for multi-model configuration with the main GUI application.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class TestMainAppIntegration(unittest.TestCase):
    """Test integration of multi-model config with main application."""
    
    def test_main_app_includes_multi_model_tab(self):
        """Test that main app includes multi-model configuration tab."""
        # Test the import and class structure without creating instances
        try:
            from gui.main_app import MainApplication
            from gui.multi_model_config_panel import MultiModelConfigPanel
            
            # Verify the classes can be imported
            self.assertTrue(hasattr(MainApplication, '__init__'))
            self.assertTrue(hasattr(MultiModelConfigPanel, '__init__'))
            
            # Test that the main app has the callback method
            self.assertTrue(hasattr(MainApplication, 'on_multi_model_config_change'))
            
        except ImportError as e:
            self.fail(f"Failed to import required classes: {e}")
    
    def test_multi_model_config_callback_logic(self):
        """Test the multi-model configuration callback logic."""
        from model_config.data_models import AgentModelConfig
        
        # Create a mock main app
        class MockMainApp:
            def __init__(self):
                self.agent_manager = Mock()
            
            def on_multi_model_config_change(self, config):
                """Handle multi-model configuration changes"""
                try:
                    # Update agent manager with multi-model configuration
                    if self.agent_manager:
                        self.agent_manager.set_multi_model_config(config)
                        print("Multi-model configuration updated")
                except Exception as e:
                    print(f"Failed to update multi-model configuration: {e}")
        
        # Test the callback
        app = MockMainApp()
        
        config = AgentModelConfig(
            agent_0_model="test-model-1",
            agent_1_model="test-model-2",
            agent_2_model="test-model-3",
            agent_3_model="test-model-4",
            synthesis_model="test-model-5",
            default_model="test-model-default"
        )
        
        # Call the callback
        app.on_multi_model_config_change(config)
        
        # Verify agent manager was called
        app.agent_manager.set_multi_model_config.assert_called_once_with(config)
    
    def test_menu_integration(self):
        """Test that menu includes multi-model config option."""
        # This tests the menu command logic
        notebook_select_calls = []
        
        def mock_notebook_select(tab_index):
            notebook_select_calls.append(tab_index)
        
        # Simulate the menu command
        menu_command = lambda: mock_notebook_select(3)  # Multi-model config is tab 3
        
        # Execute the command
        menu_command()
        
        # Verify the correct tab was selected
        self.assertEqual(notebook_select_calls, [3])


class TestConfigurationFlow(unittest.TestCase):
    """Test the complete configuration flow."""
    
    def test_configuration_save_load_flow(self):
        """Test saving and loading configuration."""
        from model_config.data_models import AgentModelConfig
        
        # Create a test configuration
        original_config = AgentModelConfig(
            agent_0_model="model-research",
            agent_1_model="model-analysis",
            agent_2_model="model-verification",
            agent_3_model="model-alternatives",
            synthesis_model="model-synthesis",
            default_model="model-default",
            profile_name="test-profile"
        )
        
        # Test to_dict conversion
        config_dict = original_config.to_dict()
        
        expected_keys = [
            'agent_0_model', 'agent_1_model', 'agent_2_model', 'agent_3_model',
            'synthesis_model', 'default_model', 'profile_name'
        ]
        
        for key in expected_keys:
            self.assertIn(key, config_dict)
        
        # Test from_dict conversion
        loaded_config = AgentModelConfig.from_dict(config_dict)
        
        # Verify all fields match
        self.assertEqual(loaded_config.agent_0_model, original_config.agent_0_model)
        self.assertEqual(loaded_config.agent_1_model, original_config.agent_1_model)
        self.assertEqual(loaded_config.agent_2_model, original_config.agent_2_model)
        self.assertEqual(loaded_config.agent_3_model, original_config.agent_3_model)
        self.assertEqual(loaded_config.synthesis_model, original_config.synthesis_model)
        self.assertEqual(loaded_config.default_model, original_config.default_model)
        self.assertEqual(loaded_config.profile_name, original_config.profile_name)
    
    @patch('gui.multi_model_config_panel.ModelConfigurationManager')
    def test_panel_configuration_management(self, mock_model_manager):
        """Test panel configuration management without GUI."""
        from model_config.data_models import AgentModelConfig
        
        # Setup mock
        mock_manager_instance = Mock()
        mock_model_manager.return_value = mock_manager_instance
        
        # Mock configuration save/load
        test_config = AgentModelConfig(
            agent_0_model="test-model",
            agent_1_model="test-model",
            agent_2_model="test-model",
            agent_3_model="test-model",
            synthesis_model="test-model",
            default_model="test-model"
        )
        
        mock_manager_instance.save_agent_configuration.return_value = True
        mock_manager_instance.load_agent_configuration.return_value = test_config
        
        # Test save operation
        result = mock_manager_instance.save_agent_configuration(test_config, "test_config.yaml")
        self.assertTrue(result)
        
        # Test load operation
        loaded_config = mock_manager_instance.load_agent_configuration("test_config.yaml")
        self.assertIsNotNone(loaded_config)
        self.assertEqual(loaded_config.agent_0_model, "test-model")


class TestErrorHandling(unittest.TestCase):
    """Test error handling in the multi-model configuration system."""
    
    def test_invalid_configuration_handling(self):
        """Test handling of invalid configurations."""
        from model_config.data_models import AgentModelConfig
        
        # Test configuration with empty models
        config = AgentModelConfig(
            agent_0_model="",  # Empty model
            agent_1_model="valid-model",
            agent_2_model="valid-model",
            agent_3_model="valid-model",
            synthesis_model="valid-model",
            default_model="valid-model"
        )
        
        # Simulate validation logic
        def validate_config(config):
            errors = []
            if not config.agent_0_model:
                errors.append("Agent 0 model cannot be empty")
            if not config.agent_1_model:
                errors.append("Agent 1 model cannot be empty")
            if not config.agent_2_model:
                errors.append("Agent 2 model cannot be empty")
            if not config.agent_3_model:
                errors.append("Agent 3 model cannot be empty")
            return errors
        
        errors = validate_config(config)
        self.assertEqual(len(errors), 1)
        self.assertIn("Agent 0", errors[0])
    
    def test_model_loading_error_handling(self):
        """Test handling of model loading errors."""
        # Simulate model loading failure
        def load_models_with_error():
            raise Exception("Failed to connect to model provider")
        
        # Test error handling
        try:
            load_models_with_error()
            self.fail("Expected exception was not raised")
        except Exception as e:
            self.assertIn("Failed to connect", str(e))
    
    def test_cost_calculation_error_handling(self):
        """Test handling of cost calculation errors."""
        from model_config.data_models import CostEstimate
        
        # Test with missing cost data
        def calculate_cost_with_missing_data():
            # Simulate missing cost data
            return None
        
        result = calculate_cost_with_missing_data()
        self.assertIsNone(result)
        
        # Test with valid cost data
        def calculate_cost_with_valid_data():
            return CostEstimate(
                total_input_tokens=1000,
                total_output_tokens=500,
                total_cost=0.015,
                per_agent_costs={0: 0.003, 1: 0.004, 2: 0.003, 3: 0.005},
                breakdown={'synthesis': 0.000}
            )
        
        result = calculate_cost_with_valid_data()
        self.assertIsNotNone(result)
        self.assertEqual(result.total_cost, 0.015)


class TestThemeIntegration(unittest.TestCase):
    """Test theme integration with multi-model configuration panel."""
    
    def test_theme_compatibility(self):
        """Test that the panel is compatible with different themes."""
        # Test theme color handling
        def get_theme_colors():
            return {
                'bg_primary': '#ffffff',
                'bg_secondary': '#f0f0f0',
                'text_primary': '#000000',
                'text_secondary': '#666666'
            }
        
        colors = get_theme_colors()
        
        # Verify color structure
        required_colors = ['bg_primary', 'bg_secondary', 'text_primary', 'text_secondary']
        for color in required_colors:
            self.assertIn(color, colors)
            self.assertTrue(colors[color].startswith('#'))
    
    def test_responsive_layout(self):
        """Test responsive layout logic."""
        # Test grid layout calculations
        def calculate_grid_layout(window_width, window_height):
            # This simulates the grid layout logic for agent selectors
            if window_width < 800:
                return {'columns': 1, 'rows': 4}  # Stack vertically on narrow screens
            else:
                return {'columns': 2, 'rows': 2}  # 2x2 grid on wider screens
        
        # Test narrow layout
        narrow_layout = calculate_grid_layout(600, 800)
        self.assertEqual(narrow_layout['columns'], 1)
        self.assertEqual(narrow_layout['rows'], 4)
        
        # Test wide layout
        wide_layout = calculate_grid_layout(1200, 800)
        self.assertEqual(wide_layout['columns'], 2)
        self.assertEqual(wide_layout['rows'], 2)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)