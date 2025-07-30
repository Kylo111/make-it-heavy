"""
Integration tests for the multi-model configuration GUI components.
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.multi_model_config_panel import (
    MultiModelConfigPanel, 
    AgentModelSelector, 
    ModelInfoWidget, 
    CostCalculatorWidget,
    ConfigurationTestDialog
)
from model_config.data_models import ModelInfo, AgentModelConfig, CostEstimate


class TestMultiModelConfigPanel(unittest.TestCase):
    """Test cases for MultiModelConfigPanel."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
        # Mock the model manager
        self.mock_model_manager = Mock()
        self.mock_config_manager = Mock()
        
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
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    @patch('gui.multi_model_config_panel.ModelConfigurationManager')
    @patch('gui.multi_model_config_panel.ConfigurationManager')
    def test_panel_initialization(self, mock_config_manager, mock_model_manager):
        """Test that the panel initializes correctly."""
        # Setup mocks
        mock_model_manager.return_value = self.mock_model_manager
        mock_config_manager.return_value = self.mock_config_manager
        
        # Create panel
        panel = MultiModelConfigPanel(self.root)
        
        # Verify initialization
        self.assertIsNotNone(panel.main_frame)
        self.assertEqual(len(panel.agent_selectors), 4)
        self.assertIsNotNone(panel.model_info_widget)
        self.assertIsNotNone(panel.cost_calculator_widget)
    
    @patch('gui.multi_model_config_panel.ModelConfigurationManager')
    @patch('gui.multi_model_config_panel.ConfigurationManager')
    def test_load_configuration_to_ui(self, mock_config_manager, mock_model_manager):
        """Test loading configuration into UI components."""
        # Setup mocks
        mock_model_manager.return_value = self.mock_model_manager
        mock_config_manager.return_value = self.mock_config_manager
        
        # Create panel
        panel = MultiModelConfigPanel(self.root)
        
        # Mock agent selectors
        for i in range(4):
            panel.agent_selectors[i] = Mock()
        
        # Load configuration
        panel.load_configuration_to_ui(self.sample_config)
        
        # Verify agent selectors were updated
        panel.agent_selectors[0].set_selected_model.assert_called_with("test-model-1")
        panel.agent_selectors[1].set_selected_model.assert_called_with("test-model-1")
        panel.agent_selectors[2].set_selected_model.assert_called_with("test-model-2")
        panel.agent_selectors[3].set_selected_model.assert_called_with("test-model-2")
    
    @patch('gui.multi_model_config_panel.ModelConfigurationManager')
    @patch('gui.multi_model_config_panel.ConfigurationManager')
    def test_on_agent_model_change(self, mock_config_manager, mock_model_manager):
        """Test handling agent model changes."""
        # Setup mocks
        mock_model_manager.return_value = self.mock_model_manager
        mock_config_manager.return_value = self.mock_config_manager
        
        # Create panel
        panel = MultiModelConfigPanel(self.root)
        panel.current_config = self.sample_config
        panel.available_models = self.sample_models
        
        # Mock UI components
        panel.model_info_widget = Mock()
        panel.cost_calculator_widget = Mock()
        panel.profile_var = Mock()
        
        # Test agent model change
        panel.on_agent_model_change(0, "test-model-2")
        
        # Verify configuration was updated
        self.assertEqual(panel.current_config.agent_0_model, "test-model-2")
        self.assertEqual(panel.current_config.profile_name, "custom")


class TestAgentModelSelector(unittest.TestCase):
    """Test cases for AgentModelSelector widget."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.mock_callback = Mock()
        
        self.sample_models = [
            ModelInfo(
                id="test-model-1",
                name="Test Model 1",
                provider="test-provider",
                supports_function_calling=True,
                context_window=4096,
                input_cost_per_1m=1.0,
                output_cost_per_1m=2.0,
                description="Test model 1"
            )
        ]
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_selector_initialization(self):
        """Test that the selector initializes correctly."""
        selector = AgentModelSelector(
            self.root,
            agent_id=0,
            agent_name="Test Agent",
            on_model_change=self.mock_callback
        )
        
        self.assertEqual(selector.agent_id, 0)
        self.assertEqual(selector.agent_name, "Test Agent")
        self.assertIsNotNone(selector.model_combo)
    
    def test_set_available_models(self):
        """Test setting available models."""
        selector = AgentModelSelector(
            self.root,
            agent_id=0,
            agent_name="Test Agent",
            on_model_change=self.mock_callback
        )
        
        selector.set_available_models(self.sample_models)
        
        self.assertEqual(len(selector.available_models), 1)
        self.assertEqual(len(selector.model_combo['values']), 1)
    
    def test_set_selected_model(self):
        """Test setting selected model."""
        selector = AgentModelSelector(
            self.root,
            agent_id=0,
            agent_name="Test Agent",
            on_model_change=self.mock_callback
        )
        
        selector.set_available_models(self.sample_models)
        selector.set_selected_model("test-model-1")
        
        self.assertIn("test-model-1", selector.model_var.get())
    
    def test_get_selected_model_id(self):
        """Test getting selected model ID."""
        selector = AgentModelSelector(
            self.root,
            agent_id=0,
            agent_name="Test Agent",
            on_model_change=self.mock_callback
        )
        
        selector.set_available_models(self.sample_models)
        selector.set_selected_model("test-model-1")
        
        model_id = selector.get_selected_model_id()
        self.assertEqual(model_id, "test-model-1")


class TestModelInfoWidget(unittest.TestCase):
    """Test cases for ModelInfoWidget."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.sample_model = ModelInfo(
            id="test-model-1",
            name="Test Model 1",
            provider="test-provider",
            supports_function_calling=True,
            context_window=4096,
            input_cost_per_1m=1.0,
            output_cost_per_1m=2.0,
            description="Test model description"
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_widget_initialization(self):
        """Test that the widget initializes correctly."""
        widget = ModelInfoWidget(self.root)
        
        self.assertIsNotNone(widget.name_var)
        self.assertIsNotNone(widget.provider_var)
        self.assertIsNotNone(widget.description_text)
    
    def test_display_model_info(self):
        """Test displaying model information."""
        widget = ModelInfoWidget(self.root)
        
        widget.display_model_info(self.sample_model)
        
        self.assertEqual(widget.name_var.get(), "Test Model 1")
        self.assertEqual(widget.provider_var.get(), "test-provider")
        self.assertEqual(widget.context_var.get(), "4,096 tokens")
        self.assertEqual(widget.input_cost_var.get(), "$1.000 per 1M tokens")
        self.assertEqual(widget.output_cost_var.get(), "$2.000 per 1M tokens")
        self.assertEqual(widget.function_calling_var.get(), "✓ Supported")
    
    def test_clear_display(self):
        """Test clearing the display."""
        widget = ModelInfoWidget(self.root)
        
        # First display some info
        widget.display_model_info(self.sample_model)
        
        # Then clear it
        widget.clear_display()
        
        self.assertEqual(widget.name_var.get(), "No model selected")
        self.assertEqual(widget.provider_var.get(), "")


class TestCostCalculatorWidget(unittest.TestCase):
    """Test cases for CostCalculatorWidget."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.sample_cost_estimate = CostEstimate(
            total_input_tokens=1000,
            total_output_tokens=500,
            total_cost=0.015,
            per_agent_costs={0: 0.003, 1: 0.004, 2: 0.003, 3: 0.002},
            breakdown={'synthesis': 0.003}
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_widget_initialization(self):
        """Test that the widget initializes correctly."""
        widget = CostCalculatorWidget(self.root)
        
        self.assertIsNotNone(widget.total_cost_var)
        self.assertEqual(len(widget.agent_cost_vars), 4)
        self.assertIsNotNone(widget.synthesis_cost_var)
    
    def test_display_cost_estimate(self):
        """Test displaying cost estimate."""
        widget = CostCalculatorWidget(self.root)
        
        widget.display_cost_estimate(self.sample_cost_estimate)
        
        self.assertEqual(widget.total_cost_var.get(), "Total: $0.015 per query")
        self.assertEqual(widget.agent_cost_vars[0].get(), "Research: $0.003")
        self.assertEqual(widget.agent_cost_vars[1].get(), "Analysis: $0.004")
        self.assertEqual(widget.synthesis_cost_var.get(), "Synthesis: $0.003")
    
    def test_display_error(self):
        """Test displaying error message."""
        widget = CostCalculatorWidget(self.root)
        
        error_message = "Test error message"
        widget.display_error(error_message)
        
        self.assertIn(error_message, widget.total_cost_var.get())


class TestConfigurationTestDialog(unittest.TestCase):
    """Test cases for ConfigurationTestDialog."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.mock_model_manager = Mock()
        self.sample_config = AgentModelConfig(
            agent_0_model="test-model-1",
            agent_1_model="test-model-1",
            agent_2_model="test-model-1",
            agent_3_model="test-model-1",
            synthesis_model="test-model-1",
            default_model="test-model-1"
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    def test_dialog_initialization(self):
        """Test that the dialog initializes correctly."""
        dialog = ConfigurationTestDialog(
            self.root,
            self.mock_model_manager,
            self.sample_config
        )
        
        self.assertIsNotNone(dialog.dialog)
        self.assertIsNotNone(dialog.results_text)
        self.assertIsNotNone(dialog.progress_bar)
    
    def test_display_results(self):
        """Test displaying test results."""
        dialog = ConfigurationTestDialog(
            self.root,
            self.mock_model_manager,
            self.sample_config
        )
        
        # Mock test results
        from model_config.data_models import ModelTestResult
        test_results = {
            'agent_0_model': ModelTestResult(
                model_id="test-model-1",
                success=True,
                response_time=1.5
            ),
            'agent_1_model': ModelTestResult(
                model_id="test-model-1",
                success=False,
                error_message="Test error"
            )
        }
        
        dialog.display_results(test_results)
        
        # Check that results are displayed
        results_text = dialog.results_text.get(1.0, tk.END)
        self.assertIn("Research Agent: ✓ PASSED", results_text)
        self.assertIn("Analysis Agent: ✗ FAILED", results_text)
        self.assertIn("Test error", results_text)


class TestGUIIntegration(unittest.TestCase):
    """Integration tests for GUI components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root = tk.Tk()
        self.root.withdraw()
    
    def tearDown(self):
        """Clean up after tests."""
        self.root.destroy()
    
    @patch('gui.multi_model_config_panel.ModelConfigurationManager')
    @patch('gui.multi_model_config_panel.ConfigurationManager')
    def test_full_workflow(self, mock_config_manager, mock_model_manager):
        """Test a complete workflow through the GUI."""
        # Setup mocks
        mock_model_manager_instance = Mock()
        mock_model_manager.return_value = mock_model_manager_instance
        mock_config_manager.return_value = Mock()
        
        # Mock available models
        sample_models = [
            ModelInfo(
                id="model-1",
                name="Model 1",
                provider="provider-1",
                supports_function_calling=True,
                context_window=4096,
                input_cost_per_1m=1.0,
                output_cost_per_1m=2.0,
                description="Model 1"
            ),
            ModelInfo(
                id="model-2",
                name="Model 2",
                provider="provider-2",
                supports_function_calling=True,
                context_window=8192,
                input_cost_per_1m=2.0,
                output_cost_per_1m=4.0,
                description="Model 2"
            )
        ]
        
        mock_model_manager_instance.get_available_models.return_value = sample_models
        mock_model_manager_instance.get_predefined_profiles.return_value = []
        mock_model_manager_instance.load_agent_configuration.return_value = None
        
        # Create panel
        panel = MultiModelConfigPanel(self.root)
        
        # Simulate data loading completion
        panel.available_models = sample_models
        panel.update_ui_after_load()
        
        # Verify UI was updated
        self.assertEqual(len(panel.available_models), 2)
        
        # Test agent model change
        panel.on_agent_model_change(0, "model-2")
        
        # Verify configuration was updated
        self.assertIsNotNone(panel.current_config)
        self.assertEqual(panel.current_config.agent_0_model, "model-2")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)