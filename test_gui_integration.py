#!/usr/bin/env python3
"""
Test script for GUI integration with AgentManager.
Tests the complete integration without actually opening the GUI.
"""

import sys
import os
import time
import threading
from unittest.mock import Mock, patch

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.agent_manager import AgentManager, AgentProgress
from gui.chat_interface import ChatInterface
from gui.main_app import MainApplication
from gui.settings_panel import AppConfig


def test_chat_interface_agent_integration():
    """Test ChatInterface integration with AgentManager"""
    print("Testing ChatInterface-AgentManager integration...")
    
    try:
        # Create mock parent
        mock_parent = Mock()
        
        # Create agent manager
        agent_manager = AgentManager(config_path="config.yaml")
        
        # Create chat interface
        chat_interface = ChatInterface(mock_parent, agent_manager)
        
        # Test mode switching
        chat_interface.set_mode("single")
        assert chat_interface.current_mode == "single"
        print("✓ Single mode set in chat interface")
        
        chat_interface.set_mode("heavy")
        assert chat_interface.current_mode == "heavy"
        print("✓ Heavy mode set in chat interface")
        
        # Test agent manager connection
        assert chat_interface.agent_manager is not None
        print("✓ Agent manager connected to chat interface")
        
        return True
        
    except Exception as e:
        print(f"✗ ChatInterface integration test failed: {e}")
        return False


def test_progress_callback_integration():
    """Test progress callback integration"""
    print("\nTesting progress callback integration...")
    
    try:
        # Create mock parent
        mock_parent = Mock()
        
        # Create agent manager
        agent_manager = AgentManager(config_path="config.yaml")
        agent_manager.set_mode("heavy")
        
        # Create chat interface
        chat_interface = ChatInterface(mock_parent, agent_manager)
        chat_interface.set_mode("heavy")
        
        # Mock the chat display to avoid GUI operations
        chat_interface.chat_display = Mock()
        chat_interface.chat_display.config = Mock()
        chat_interface.chat_display.insert = Mock()
        chat_interface.chat_display.delete = Mock()
        chat_interface.chat_display.index = Mock(return_value="1.0")
        chat_interface.chat_display.mark_set = Mock()
        chat_interface.chat_display.see = Mock()
        
        # Test progress callback
        progress_data = {
            0: AgentProgress(0, "PROCESSING...", "● " + ":" * 10 + "·" * 60),
            1: AgentProgress(1, "QUEUED", "○ " + "·" * 70),
            2: AgentProgress(2, "COMPLETED", "● " + ":" * 70),
            3: AgentProgress(3, "PROCESSING...", "● " + ":" * 10 + "·" * 60)
        }
        
        # Set progress start position to simulate heavy mode display
        chat_interface.progress_start_pos = "5.0"
        
        # Call progress update
        chat_interface.on_progress_update(progress_data)
        
        print("✓ Progress callback executed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Progress callback test failed: {e}")
        return False


def test_config_integration():
    """Test configuration integration between components"""
    print("\nTesting configuration integration...")
    
    try:
        # Create test configuration
        test_config = AppConfig(
            provider="deepseek",
            model="deepseek-chat",
            api_keys={"deepseek": "test-key", "openrouter": ""},
            mode="heavy"
        )
        
        # Create agent manager
        agent_manager = AgentManager(config_path="config.yaml")
        
        # Test configuration update
        # Note: We won't actually update with test key to avoid API issues
        # Just test that the method exists and can be called
        assert hasattr(agent_manager, 'update_config')
        print("✓ Agent manager has update_config method")
        
        # Test mode setting
        agent_manager.set_mode(test_config.mode)
        assert agent_manager.get_current_mode() == test_config.mode
        print("✓ Configuration mode applied successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration integration test failed: {e}")
        return False


def test_main_app_initialization():
    """Test MainApplication initialization without GUI"""
    print("\nTesting MainApplication initialization...")
    
    try:
        # Mock tkinter to avoid GUI creation
        with patch('tkinter.Tk') as mock_tk:
            mock_root = Mock()
            mock_tk.return_value = mock_root
            
            # Mock other GUI components
            with patch('gui.main_app.ttk') as mock_ttk:
                mock_ttk.Frame.return_value = Mock()
                mock_ttk.Notebook.return_value = Mock()
                mock_ttk.LabelFrame.return_value = Mock()
                mock_ttk.Radiobutton.return_value = Mock()
                mock_ttk.Label.return_value = Mock()
                mock_ttk.Style.return_value = Mock()
                
                # Mock the chat interface and settings panel
                with patch('gui.main_app.ChatInterface') as mock_chat:
                    with patch('gui.main_app.SettingsPanel') as mock_settings:
                        mock_chat.return_value = Mock()
                        mock_settings.return_value = Mock()
                        
                        # Create main application
                        app = MainApplication()
                        
                        # Test that components were initialized
                        assert hasattr(app, 'agent_manager')
                        assert hasattr(app, 'mode_var')
                        print("✓ MainApplication initialized successfully")
                        
                        # Test mode change
                        app.mode_var = Mock()
                        app.mode_var.get.return_value = "heavy"
                        app.mode_status_var = Mock()
                        app.on_mode_change()
                        print("✓ Mode change handling works")
        
        return True
        
    except Exception as e:
        print(f"✗ MainApplication initialization test failed: {e}")
        return False


def test_end_to_end_flow():
    """Test end-to-end flow simulation"""
    print("\nTesting end-to-end flow simulation...")
    
    try:
        # Create agent manager
        agent_manager = AgentManager(config_path="config.yaml")
        
        # Create mock chat interface
        mock_parent = Mock()
        chat_interface = ChatInterface(mock_parent, agent_manager)
        
        # Mock GUI components
        chat_interface.chat_display = Mock()
        chat_interface.chat_display.config = Mock()
        chat_interface.chat_display.insert = Mock()
        chat_interface.chat_display.delete = Mock()
        chat_interface.chat_display.index = Mock(return_value="1.0")
        chat_interface.chat_display.mark_set = Mock()
        chat_interface.chat_display.see = Mock()
        
        chat_interface.send_button = Mock()
        chat_interface.message_input = Mock()
        chat_interface.message_input.get.return_value = "Test message"
        chat_interface.message_input.delete = Mock()
        
        # Test single mode flow
        chat_interface.set_mode("single")
        
        # Simulate completion callback
        test_result = "Test response from agent"
        chat_interface.on_agent_completion(test_result)
        
        print("✓ Single mode flow simulation completed")
        
        # Test heavy mode flow
        chat_interface.set_mode("heavy")
        
        # Simulate progress updates
        progress_data = {
            0: AgentProgress(0, "COMPLETED", "● " + ":" * 70),
            1: AgentProgress(1, "COMPLETED", "● " + ":" * 70),
            2: AgentProgress(2, "COMPLETED", "● " + ":" * 70),
            3: AgentProgress(3, "COMPLETED", "● " + ":" * 70)
        }
        
        chat_interface.progress_start_pos = "5.0"
        chat_interface.on_progress_update(progress_data)
        chat_interface.on_agent_completion("Heavy mode test response")
        
        print("✓ Heavy mode flow simulation completed")
        
        return True
        
    except Exception as e:
        print(f"✗ End-to-end flow test failed: {e}")
        return False


def main():
    """Run all GUI integration tests"""
    print("=" * 60)
    print("GUI Integration Tests")
    print("=" * 60)
    
    tests = [
        test_chat_interface_agent_integration,
        test_progress_callback_integration,
        test_config_integration,
        test_main_app_initialization,
        test_end_to_end_flow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)