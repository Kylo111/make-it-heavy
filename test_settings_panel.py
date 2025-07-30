#!/usr/bin/env python3
"""
Test script for the SettingsPanel functionality.
"""

import sys
import os
import tempfile
import yaml
from unittest.mock import patch

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.settings_panel import SettingsPanel, AppConfig


def test_config_loading():
    """Test configuration loading functionality"""
    print("Testing configuration loading...")
    
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        test_config = {
            'provider': {'type': 'deepseek'},
            'deepseek': {
                'api_key': 'test-deepseek-key',
                'base_url': 'https://api.deepseek.com',
                'model': 'deepseek-chat'
            },
            'openrouter': {
                'api_key': 'test-openrouter-key',
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'anthropic/claude-3.5-sonnet'
            }
        }
        yaml.dump(test_config, f)
        temp_config_path = f.name
    
    try:
        # Test loading configuration without GUI
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create settings panel
        settings_panel = SettingsPanel(root, config_path=temp_config_path)
        
        # Verify configuration was loaded correctly
        config = settings_panel.current_config
        assert config.provider == 'deepseek', f"Expected provider 'deepseek', got '{config.provider}'"
        assert config.model == 'deepseek-chat', f"Expected model 'deepseek-chat', got '{config.model}'"
        assert 'deepseek' in config.api_keys, "DeepSeek API key not loaded"
        assert config.api_keys['deepseek'] == 'test-deepseek-key', "DeepSeek API key mismatch"
        
        print("✓ Configuration loading test passed")
        
        root.destroy()
        
    finally:
        # Clean up temporary file
        os.unlink(temp_config_path)


def test_provider_models():
    """Test provider model loading"""
    print("Testing provider model loading...")
    
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    
    # Create settings panel with default config
    settings_panel = SettingsPanel(root)
    
    # Test DeepSeek models
    deepseek_models = settings_panel.providers['deepseek']['models']
    assert 'deepseek-chat' in deepseek_models, "DeepSeek chat model not found"
    assert 'deepseek-reasoner' in deepseek_models, "DeepSeek reasoner model not found"
    
    # Test OpenRouter models
    openrouter_models = settings_panel.providers['openrouter']['models']
    assert 'anthropic/claude-3.5-sonnet' in openrouter_models, "Claude model not found"
    assert 'openai/gpt-4-turbo' in openrouter_models, "GPT-4 model not found"
    
    print("✓ Provider model loading test passed")
    
    root.destroy()


def test_api_key_validation():
    """Test API key validation (mock test)"""
    print("Testing API key validation...")
    
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    
    settings_panel = SettingsPanel(root)
    
    # Test empty key validation
    try:
        settings_panel.validate_single_api_key("deepseek", "")
        assert False, "Should have raised ValueError for empty key"
    except ValueError as e:
        assert "empty" in str(e).lower(), f"Unexpected error message: {e}"
    
    # Test invalid key format (this would normally make an API call)
    try:
        with patch('gui.settings_panel.ProviderClientFactory.create_client') as mock_create:
            mock_create.side_effect = Exception("Invalid API key")
            settings_panel.validate_single_api_key("deepseek", "invalid-key")
            assert False, "Should have raised ValueError for invalid key"
    except ValueError as e:
        assert "Invalid API key" in str(e), f"Unexpected error message: {e}"
    
    print("✓ API key validation test passed")
    
    root.destroy()


def test_configuration_save():
    """Test configuration saving"""
    print("Testing configuration saving...")
    
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_config_path = f.name
    
    try:
        settings_panel = SettingsPanel(root, config_path=temp_config_path)
        
        # Set some test values
        settings_panel.provider_var.set("openrouter (OpenRouter)")
        settings_panel.model_var.set("anthropic/claude-3.5-sonnet")
        settings_panel.openrouter_key_var.set("test-openrouter-key")
        settings_panel.mode_var.set("heavy")
        
        # Save configuration
        settings_panel.save_configuration()
        
        # Verify file was created and contains expected data
        assert os.path.exists(temp_config_path), "Configuration file was not created"
        
        with open(temp_config_path, 'r') as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config['provider']['type'] == 'openrouter', "Provider not saved correctly"
        assert saved_config['openrouter']['model'] == 'anthropic/claude-3.5-sonnet', "Model not saved correctly"
        assert saved_config['openrouter']['api_key'] == 'test-openrouter-key', "API key not saved correctly"
        
        print("✓ Configuration saving test passed")
        
    finally:
        root.destroy()
        if os.path.exists(temp_config_path):
            os.unlink(temp_config_path)


def main():
    """Run all tests"""
    print("Running SettingsPanel tests...\n")
    
    try:
        test_config_loading()
        test_provider_models()
        test_api_key_validation()
        test_configuration_save()
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()