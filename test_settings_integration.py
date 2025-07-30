#!/usr/bin/env python3
"""
Integration test for SettingsPanel with MainApplication.
"""

import sys
import os
import tempfile
import yaml
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_app import MainApplication
from gui.settings_panel import AppConfig


def test_main_app_with_settings():
    """Test MainApplication with SettingsPanel integration"""
    print("Testing MainApplication with SettingsPanel integration...")
    
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        test_config = {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'sk-test-deepseek-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            },
            'system_prompt': 'Test system prompt',
            'agent': {'max_iterations': 10},
            'orchestrator': {'parallel_agents': 4},
            'search': {'max_results': 5}
        }
        yaml.dump(test_config, f)
        temp_config_path = f.name
    
    try:
        # Temporarily replace the default config path
        original_cwd = os.getcwd()
        temp_dir = os.path.dirname(temp_config_path)
        temp_config_name = os.path.basename(temp_config_path)
        
        # Copy config to current directory as config.yaml for the test
        import shutil
        test_config_path = os.path.join(original_cwd, 'test_config.yaml')
        shutil.copy2(temp_config_path, test_config_path)
        
        # Create main application (but don't run mainloop)
        app = MainApplication()
        
        # Verify that settings panel was created
        assert hasattr(app, 'settings_panel'), "SettingsPanel not created"
        assert app.settings_panel is not None, "SettingsPanel is None"
        
        # Verify that configuration was loaded
        config = app.settings_panel.current_config
        assert config is not None, "Configuration not loaded"
        assert config.provider == 'deepseek', f"Expected provider 'deepseek', got '{config.provider}'"
        
        # Test configuration change callback
        test_config = AppConfig(
            provider='openrouter',
            model='anthropic/claude-3.5-sonnet',
            api_keys={'openrouter': 'test-key'},
            mode='heavy'
        )
        
        app.on_config_change(test_config)
        assert app.current_config == test_config, "Configuration change callback failed"
        
        # Test utility methods
        models = app.load_models('deepseek')
        assert 'deepseek-chat' in models, "DeepSeek models not loaded correctly"
        
        app.switch_mode('single')
        app.switch_provider('openrouter')
        
        print("✓ MainApplication integration test passed")
        
        # Clean up
        app.root.destroy()
        
    finally:
        # Clean up temporary files
        if os.path.exists(temp_config_path):
            os.unlink(temp_config_path)
        if os.path.exists('test_config.yaml'):
            os.unlink('test_config.yaml')


def test_settings_panel_ui_components():
    """Test that all UI components are created properly"""
    print("Testing SettingsPanel UI components...")
    
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    
    try:
        from gui.settings_panel import SettingsPanel
        
        settings_panel = SettingsPanel(root)
        
        # Verify UI components exist
        assert hasattr(settings_panel, 'provider_combo'), "Provider combo not created"
        assert hasattr(settings_panel, 'model_combo'), "Model combo not created"
        assert hasattr(settings_panel, 'deepseek_key_entry'), "DeepSeek key entry not created"
        assert hasattr(settings_panel, 'openrouter_key_entry'), "OpenRouter key entry not created"
        assert hasattr(settings_panel, 'mode_var'), "Mode variable not created"
        assert hasattr(settings_panel, 'save_button'), "Save button not created"
        assert hasattr(settings_panel, 'validate_button'), "Validate button not created"
        
        # Test that provider combo has values
        provider_values = settings_panel.provider_combo['values']
        assert len(provider_values) > 0, "Provider combo has no values"
        assert any('deepseek' in str(val).lower() for val in provider_values), "DeepSeek not in provider values"
        assert any('openrouter' in str(val).lower() for val in provider_values), "OpenRouter not in provider values"
        
        # Test that model combo gets populated
        settings_panel.load_models_for_provider('deepseek')
        model_values = settings_panel.model_combo['values']
        assert len(model_values) > 0, "Model combo has no values after loading DeepSeek models"
        
        print("✓ SettingsPanel UI components test passed")
        
    finally:
        root.destroy()


def main():
    """Run all integration tests"""
    print("Running SettingsPanel integration tests...\n")
    
    try:
        test_settings_panel_ui_components()
        test_main_app_with_settings()
        
        print("\n✅ All integration tests passed!")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()