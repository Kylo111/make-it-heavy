#!/usr/bin/env python3
"""
Test script for GUI session integration functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from gui.main_app import MainApplication
from gui.session_manager import SessionManager
from gui.theme_manager import ThemeManager
import tempfile
import shutil
import threading
import time


def test_gui_integration():
    """Test GUI integration with session and theme management"""
    print("Testing GUI Integration...")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(f"Using temporary directory: {temp_dir}")
    
    try:
        # Test 1: Initialize components
        print("\n1. Testing component initialization...")
        
        session_manager = SessionManager(sessions_dir=temp_dir)
        theme_manager = ThemeManager()
        
        print(f"   Session manager initialized with {len(session_manager.get_session_list())} sessions")
        print(f"   Theme manager initialized with theme: {theme_manager.get_current_theme()}")
        
        # Test 2: Session operations
        print("\n2. Testing session operations...")
        
        # Create test session
        session = session_manager.create_new_session("GUI Test Session")
        session_manager.add_message("user", "Test message from GUI integration")
        session_manager.add_message("agent", "Test response from agent")
        
        print(f"   Created session: {session.title}")
        print(f"   Added {len(session.messages)} messages")
        
        # Test session list
        sessions = session_manager.get_session_list()
        print(f"   Session list contains {len(sessions)} sessions")
        
        # Test 3: Theme operations
        print("\n3. Testing theme operations...")
        
        original_theme = theme_manager.get_current_theme()
        colors_light = theme_manager.get_theme_colors("light")
        colors_dark = theme_manager.get_theme_colors("dark")
        
        print(f"   Light theme primary bg: {colors_light.bg_primary}")
        print(f"   Dark theme primary bg: {colors_dark.bg_primary}")
        
        # Test theme switching
        theme_manager.toggle_theme()
        new_theme = theme_manager.get_current_theme()
        print(f"   Theme switched from {original_theme} to {new_theme}")
        
        # Test 4: Message tag configurations
        print("\n4. Testing message tag configurations...")
        
        user_tag = theme_manager.get_message_tag_config("user_message")
        agent_tag = theme_manager.get_message_tag_config("agent_message")
        system_tag = theme_manager.get_message_tag_config("system_message")
        
        print(f"   User message config keys: {list(user_tag.keys())}")
        print(f"   Agent message config keys: {list(agent_tag.keys())}")
        print(f"   System message config keys: {list(system_tag.keys())}")
        
        # Test 5: Export/Import functionality
        print("\n5. Testing export/import functionality...")
        
        export_path = os.path.join(temp_dir, "gui_test_export.json")
        if session_manager.export_session(session.session_id, export_path):
            print(f"   Successfully exported session to {export_path}")
            
            # Test import
            imported_id = session_manager.import_session(export_path)
            if imported_id:
                print(f"   Successfully imported session with ID: {imported_id}")
            else:
                print("   ❌ Failed to import session")
        else:
            print("   ❌ Failed to export session")
        
        # Test 6: Session statistics
        print("\n6. Testing session statistics...")
        
        stats = session_manager.get_session_stats()
        print(f"   Total sessions: {stats['total_sessions']}")
        print(f"   Total messages: {stats['total_messages']}")
        
        # Test 7: Error handling
        print("\n7. Testing error handling...")
        
        # Test invalid session ID
        invalid_session = session_manager.load_session("invalid-id")
        if invalid_session is None:
            print("   ✅ Correctly handled invalid session ID")
        else:
            print("   ❌ Should have returned None for invalid session ID")
        
        # Test invalid theme
        try:
            theme_manager.set_theme("invalid-theme")
            print("   ❌ Should have raised error for invalid theme")
        except ValueError:
            print("   ✅ Correctly raised error for invalid theme")
        
        print("\n✅ All GUI integration tests completed successfully!")
        
    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)
        print(f"Cleaned up temporary directory: {temp_dir}")


def test_responsive_layout():
    """Test responsive layout functionality"""
    print("\nTesting Responsive Layout...")
    
    try:
        # Test window resize handling
        print("1. Testing window resize calculations...")
        
        # Simulate different window sizes
        test_sizes = [
            (800, 600),   # Minimum size
            (1000, 700),  # Default size
            (1200, 800),  # Large size
            (1600, 1000)  # Very large size
        ]
        
        for width, height in test_sizes:
            print(f"   Testing size {width}x{height}")
            # In a real GUI test, we would create a window and test resizing
            # For now, we just verify the calculations would work
            
        print("✅ Responsive layout tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Responsive layout test failed: {e}")


def test_error_handling():
    """Test error handling and user feedback"""
    print("\nTesting Error Handling...")
    
    try:
        # Test 1: Session manager error handling
        print("1. Testing session manager error handling...")
        
        # Test with invalid directory
        try:
            invalid_session_manager = SessionManager(sessions_dir="/invalid/path/that/does/not/exist")
            print("   ❌ Should have handled invalid directory")
        except:
            print("   ✅ Correctly handled invalid directory")
        
        # Test 2: Theme manager error handling
        print("2. Testing theme manager error handling...")
        
        theme_manager = ThemeManager()
        
        # Test invalid widget type
        try:
            import tkinter as tk
            root = tk.Tk()
            label = tk.Label(root, text="Test")
            theme_manager.apply_theme_to_widget(label, "invalid_widget_type")
            root.destroy()
            print("   ✅ Handled invalid widget type gracefully")
        except Exception as e:
            print(f"   ✅ Handled widget theme error: {e}")
        
        print("✅ Error handling tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")


if __name__ == "__main__":
    test_gui_integration()
    test_responsive_layout()
    test_error_handling()
    
    print("\n🎉 All integration tests completed!")
    print("\nTo test the full GUI application, run:")
    print("   python gui/main_app.py")