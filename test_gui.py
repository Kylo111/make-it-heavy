#!/usr/bin/env python3
"""
Simple test script to verify GUI components work correctly
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all GUI components can be imported"""
    try:
        from gui.main_app import MainApplication
        from gui.chat_interface import ChatInterface
        print("✓ All GUI imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_gui_creation():
    """Test that GUI components can be created"""
    try:
        import tkinter as tk
        from gui.main_app import MainApplication
        
        # Create a test root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test MainApplication creation
        app = MainApplication()
        app.root.withdraw()  # Hide the window
        
        print("✓ GUI components created successfully")
        
        # Clean up
        app.root.destroy()
        root.destroy()
        
        return True
    except Exception as e:
        print(f"✗ GUI creation error: {e}")
        return False

def test_chat_interface():
    """Test ChatInterface functionality"""
    try:
        import tkinter as tk
        from gui.chat_interface import ChatInterface
        
        # Create test environment
        root = tk.Tk()
        root.withdraw()
        frame = tk.Frame(root)
        
        # Create ChatInterface
        chat = ChatInterface(frame)
        
        # Test adding messages
        chat.add_message("user", "Test user message")
        chat.add_message("agent", "Test agent response")
        chat.add_message("system", "Test system message")
        
        print("✓ ChatInterface functionality works")
        
        # Clean up
        root.destroy()
        
        return True
    except Exception as e:
        print(f"✗ ChatInterface error: {e}")
        return False

if __name__ == "__main__":
    print("Testing GUI components...")
    print()
    
    tests = [
        test_imports,
        test_gui_creation,
        test_chat_interface
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All GUI components are working correctly!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)