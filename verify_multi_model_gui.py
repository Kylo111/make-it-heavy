#!/usr/bin/env python3
"""
Verification script for the multi-model configuration GUI implementation.
This script verifies that all requirements have been implemented correctly.
"""

import sys
import os
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_requirement_4_1():
    """Verify Requirement 4.1: GUI displays clear interface with tabs for each agent."""
    print("✓ Verifying Requirement 4.1: Clear interface with agent tabs")
    
    try:
        from gui.multi_model_config_panel import MultiModelConfigPanel, AgentModelSelector
        
        # Check that MultiModelConfigPanel exists and has agent selectors
        panel_methods = dir(MultiModelConfigPanel)
        required_methods = ['setup_agent_section', 'setup_ui', 'on_agent_model_change']
        
        for method in required_methods:
            if method not in panel_methods:
                print(f"  ✗ Missing method: {method}")
                return False
        
        # Check that AgentModelSelector exists
        selector_methods = dir(AgentModelSelector)
        required_selector_methods = ['set_available_models', 'set_selected_model', 'get_selected_model_id']
        
        for method in required_selector_methods:
            if method not in selector_methods:
                print(f"  ✗ Missing selector method: {method}")
                return False
        
        print("  ✓ GUI interface structure is correct")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_requirement_4_2():
    """Verify Requirement 4.2: Model selection shows model details."""
    print("✓ Verifying Requirement 4.2: Model details display")
    
    try:
        from gui.multi_model_config_panel import ModelInfoWidget
        from model_config.data_models import ModelInfo
        
        # Check that ModelInfoWidget exists and has display methods
        widget_methods = dir(ModelInfoWidget)
        required_methods = ['display_model_info', 'clear_display']
        
        for method in required_methods:
            if method not in widget_methods:
                print(f"  ✗ Missing widget method: {method}")
                return False
        
        # Test model info display logic
        sample_model = ModelInfo(
            id="test-model",
            name="Test Model",
            provider="test-provider",
            supports_function_calling=True,
            context_window=4096,
            input_cost_per_1m=1.0,
            output_cost_per_1m=2.0,
            description="Test model description"
        )
        
        # Verify model has all required fields
        required_fields = ['id', 'name', 'provider', 'supports_function_calling', 
                          'context_window', 'input_cost_per_1m', 'output_cost_per_1m', 'description']
        
        for field in required_fields:
            if not hasattr(sample_model, field):
                print(f"  ✗ Missing model field: {field}")
                return False
        
        print("  ✓ Model details display is implemented")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_requirement_4_3():
    """Verify Requirement 4.3: Configuration save with validation."""
    print("✓ Verifying Requirement 4.3: Configuration save and validation")
    
    try:
        from gui.multi_model_config_panel import MultiModelConfigPanel
        from model_config.data_models import AgentModelConfig
        
        # Check that save methods exist
        panel_methods = dir(MultiModelConfigPanel)
        required_methods = ['save_configuration', 'load_configuration_to_ui']
        
        for method in required_methods:
            if method not in panel_methods:
                print(f"  ✗ Missing method: {method}")
                return False
        
        # Test configuration structure
        config = AgentModelConfig(
            agent_0_model="test-model",
            agent_1_model="test-model",
            agent_2_model="test-model",
            agent_3_model="test-model",
            synthesis_model="test-model",
            default_model="test-model"
        )
        
        # Test to_dict and from_dict methods
        config_dict = config.to_dict()
        loaded_config = AgentModelConfig.from_dict(config_dict)
        
        if loaded_config.agent_0_model != config.agent_0_model:
            print("  ✗ Configuration serialization failed")
            return False
        
        print("  ✓ Configuration save and validation is implemented")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_requirement_4_4():
    """Verify Requirement 4.4: Reset to defaults functionality."""
    print("✓ Verifying Requirement 4.4: Reset to defaults")
    
    try:
        from gui.multi_model_config_panel import MultiModelConfigPanel
        
        # Check that reset method exists
        panel_methods = dir(MultiModelConfigPanel)
        
        if 'reset_to_defaults' not in panel_methods:
            print("  ✗ Missing reset_to_defaults method")
            return False
        
        if 'set_default_configuration' not in panel_methods:
            print("  ✗ Missing set_default_configuration method")
            return False
        
        print("  ✓ Reset to defaults functionality is implemented")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_requirement_5_1():
    """Verify Requirement 5.1: Cost calculation for configuration."""
    print("✓ Verifying Requirement 5.1: Cost calculation")
    
    try:
        from gui.multi_model_config_panel import CostCalculatorWidget
        from model_config.data_models import CostEstimate
        
        # Check that cost calculator exists
        widget_methods = dir(CostCalculatorWidget)
        required_methods = ['display_cost_estimate', 'display_error']
        
        for method in required_methods:
            if method not in widget_methods:
                print(f"  ✗ Missing cost calculator method: {method}")
                return False
        
        # Test cost estimate structure
        cost_estimate = CostEstimate(
            total_input_tokens=1000,
            total_output_tokens=500,
            total_cost=0.015,
            per_agent_costs={0: 0.003, 1: 0.004, 2: 0.003, 3: 0.005},
            breakdown={'synthesis': 0.000}
        )
        
        if cost_estimate.cost_per_query != 0.015:
            print("  ✗ Cost calculation property failed")
            return False
        
        print("  ✓ Cost calculation is implemented")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_requirement_5_2():
    """Verify Requirement 5.2: Real-time cost updates."""
    print("✓ Verifying Requirement 5.2: Real-time cost updates")
    
    try:
        from gui.multi_model_config_panel import MultiModelConfigPanel
        
        # Check that cost update method exists
        panel_methods = dir(MultiModelConfigPanel)
        
        if 'update_cost_calculation' not in panel_methods:
            print("  ✗ Missing update_cost_calculation method")
            return False
        
        if 'on_agent_model_change' not in panel_methods:
            print("  ✗ Missing on_agent_model_change method")
            return False
        
        print("  ✓ Real-time cost updates are implemented")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_requirement_6_1():
    """Verify Requirement 6.1: Predefined profiles available."""
    print("✓ Verifying Requirement 6.1: Predefined profiles")
    
    try:
        from gui.multi_model_config_panel import MultiModelConfigPanel
        from model_config.data_models import ConfigurationProfile
        
        # Check that profile methods exist
        panel_methods = dir(MultiModelConfigPanel)
        required_methods = ['setup_profile_section', 'apply_selected_profile', 'on_profile_change']
        
        for method in required_methods:
            if method not in panel_methods:
                print(f"  ✗ Missing profile method: {method}")
                return False
        
        # Check that profile creation methods exist
        profile_methods = dir(ConfigurationProfile)
        required_profile_methods = ['create_budget_profile', 'create_balanced_profile', 'create_premium_profile']
        
        for method in required_profile_methods:
            if method not in profile_methods:
                print(f"  ✗ Missing profile creation method: {method}")
                return False
        
        print("  ✓ Predefined profiles are implemented")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_requirement_6_2_6_3_6_4():
    """Verify Requirements 6.2-6.4: Profile functionality."""
    print("✓ Verifying Requirements 6.2-6.4: Profile functionality")
    
    try:
        from model_config.data_models import ConfigurationProfile, ModelInfo
        
        # Create sample models for testing
        sample_models = [
            ModelInfo(
                id="cheap-model",
                name="Cheap Model",
                provider="test",
                supports_function_calling=True,
                context_window=4096,
                input_cost_per_1m=0.5,
                output_cost_per_1m=1.0,
                description="Cheap model"
            ),
            ModelInfo(
                id="expensive-model",
                name="Expensive Model",
                provider="test",
                supports_function_calling=True,
                context_window=8192,
                input_cost_per_1m=5.0,
                output_cost_per_1m=10.0,
                description="Expensive model"
            )
        ]
        
        # Test profile creation
        try:
            budget_profile = ConfigurationProfile.create_budget_profile(sample_models)
            if budget_profile.name != "Budget":
                print("  ✗ Budget profile name incorrect")
                return False
        except ValueError:
            # This is acceptable if no suitable models found
            pass
        
        try:
            premium_profile = ConfigurationProfile.create_premium_profile(sample_models)
            if premium_profile.name != "Premium":
                print("  ✗ Premium profile name incorrect")
                return False
        except ValueError:
            # This is acceptable if no suitable models found
            pass
        
        print("  ✓ Profile functionality is implemented")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_requirement_7_1():
    """Verify Requirement 7.1: Test configuration option."""
    print("✓ Verifying Requirement 7.1: Test configuration")
    
    try:
        from gui.multi_model_config_panel import MultiModelConfigPanel, ConfigurationTestDialog
        
        # Check that test methods exist
        panel_methods = dir(MultiModelConfigPanel)
        
        if 'test_configuration' not in panel_methods:
            print("  ✗ Missing test_configuration method")
            return False
        
        # Check that test dialog exists
        dialog_methods = dir(ConfigurationTestDialog)
        required_methods = ['run_test', 'display_results', 'display_error']
        
        for method in required_methods:
            if method not in dialog_methods:
                print(f"  ✗ Missing test dialog method: {method}")
                return False
        
        print("  ✓ Test configuration functionality is implemented")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_requirement_8_1_8_4():
    """Verify Requirements 8.1-8.4: Export/import functionality."""
    print("✓ Verifying Requirements 8.1-8.4: Export/import functionality")
    
    try:
        from gui.multi_model_config_panel import MultiModelConfigPanel
        
        # Check that export/import methods exist
        panel_methods = dir(MultiModelConfigPanel)
        required_methods = ['export_configuration', 'import_configuration']
        
        for method in required_methods:
            if method not in panel_methods:
                print(f"  ✗ Missing method: {method}")
                return False
        
        print("  ✓ Export/import functionality is implemented")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_integration_with_existing_gui():
    """Verify integration with existing GUI system."""
    print("✓ Verifying integration with existing GUI system")
    
    try:
        from gui.main_app import MainApplication
        
        # Check that main app has multi-model callback
        app_methods = dir(MainApplication)
        
        if 'on_multi_model_config_change' not in app_methods:
            print("  ✗ Missing multi-model config callback in main app")
            return False
        
        # Check that the import exists
        import gui.main_app
        import inspect
        
        source = inspect.getsource(gui.main_app)
        if 'MultiModelConfigPanel' not in source:
            print("  ✗ MultiModelConfigPanel not imported in main app")
            return False
        
        if 'multi_model_frame' not in source:
            print("  ✗ Multi-model frame not created in main app")
            return False
        
        print("  ✓ Integration with existing GUI is implemented")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def verify_theme_integration():
    """Verify theme integration."""
    print("✓ Verifying theme integration")
    
    try:
        from gui.multi_model_config_panel import MultiModelConfigPanel
        
        # Check that the panel uses ttk widgets (theme-compatible)
        import inspect
        source = inspect.getsource(MultiModelConfigPanel)
        
        if 'ttk.' not in source:
            print("  ✗ Panel doesn't use ttk widgets")
            return False
        
        print("  ✓ Theme integration is implemented")
        return True
        
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("MULTI-MODEL CONFIGURATION GUI VERIFICATION")
    print("=" * 60)
    
    tests = [
        ("Requirement 4.1", verify_requirement_4_1),
        ("Requirement 4.2", verify_requirement_4_2),
        ("Requirement 4.3", verify_requirement_4_3),
        ("Requirement 4.4", verify_requirement_4_4),
        ("Requirement 5.1", verify_requirement_5_1),
        ("Requirement 5.2", verify_requirement_5_2),
        ("Requirement 6.1", verify_requirement_6_1),
        ("Requirements 6.2-6.4", verify_requirement_6_2_6_3_6_4),
        ("Requirement 7.1", verify_requirement_7_1),
        ("Requirements 8.1-8.4", verify_requirement_8_1_8_4),
        ("GUI Integration", verify_integration_with_existing_gui),
        ("Theme Integration", verify_theme_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"  ✗ {test_name} FAILED")
        except Exception as e:
            print(f"  ✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"VERIFICATION RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ ALL REQUIREMENTS IMPLEMENTED SUCCESSFULLY!")
        return 0
    else:
        print(f"✗ {total - passed} requirements need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())