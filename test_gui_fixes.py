#!/usr/bin/env python3
"""
Test script to verify GUI fixes
"""

import sys
import os
sys.path.append('gui')

def test_api_key_validation():
    """Test API key validation fixes"""
    print("🧪 Testing API key validation...")
    
    try:
        from settings_panel import SettingsPanel
        import tkinter as tk
        
        # Create minimal test environment
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        # Create settings panel
        settings = SettingsPanel(root)
        
        # Test DeepSeek key validation
        try:
            result = settings.validate_single_api_key("deepseek", "sk-test123456789012345")
            print("✅ DeepSeek validation: PASS")
        except Exception as e:
            print(f"❌ DeepSeek validation: {e}")
        
        # Test OpenRouter key validation
        try:
            result = settings.validate_single_api_key("openrouter", "sk-or-test123456789012345678901234567890")
            print("✅ OpenRouter validation: PASS")
        except Exception as e:
            print(f"❌ OpenRouter validation: {e}")
        
        # Test invalid keys
        try:
            settings.validate_single_api_key("deepseek", "invalid")
            print("❌ Invalid key test: Should have failed")
        except Exception:
            print("✅ Invalid key rejection: PASS")
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ API key validation test failed: {e}")

def test_openrouter_models():
    """Test OpenRouter model list"""
    print("\n🧪 Testing OpenRouter model list...")
    
    try:
        from settings_panel import SettingsPanel
        import tkinter as tk
        
        # Create minimal test environment
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        # Create settings panel
        settings = SettingsPanel(root)
        
        # Check OpenRouter models
        openrouter_models = settings.providers["openrouter"]["models"]
        print(f"✅ OpenRouter models count: {len(openrouter_models)}")
        
        if len(openrouter_models) > 50:
            print("✅ Model list expansion: PASS")
        else:
            print("❌ Model list expansion: FAIL (too few models)")
        
        # Show first few models
        print("📋 First 5 models:")
        for i, model in enumerate(openrouter_models[:5]):
            print(f"   {i+1}. {model}")
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ OpenRouter models test failed: {e}")

def test_agent_manager():
    """Test agent manager callback handling"""
    print("\n🧪 Testing agent manager callback handling...")
    
    try:
        from agent_manager import AgentManager
        
        # Create agent manager
        agent_manager = AgentManager()
        
        # Test callback setting
        callback_called = []
        
        def test_callback(result):
            callback_called.append(result)
        
        agent_manager.set_completion_callback(test_callback)
        
        if agent_manager.completion_callback == test_callback:
            print("✅ Callback setting: PASS")
        else:
            print("❌ Callback setting: FAIL")
        
        # Test callback clearing
        agent_manager.set_completion_callback(None)
        
        if agent_manager.completion_callback is None:
            print("✅ Callback clearing: PASS")
        else:
            print("❌ Callback clearing: FAIL")
        
    except Exception as e:
        print(f"❌ Agent manager test failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Testing GUI fixes...")
    print("=" * 50)
    
    # Test 1: API key validation
    test_api_key_validation()
    
    # Test 2: OpenRouter models
    test_openrouter_models()
    
    # Test 3: Agent manager
    test_agent_manager()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")
    print("\nIf all tests pass, the GUI fixes should work correctly.")
    print("You can now run the GUI with: python gui/main_app.py")

if __name__ == "__main__":
    main()