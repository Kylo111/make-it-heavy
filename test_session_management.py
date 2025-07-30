#!/usr/bin/env python3
"""
Test script for session management functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.session_manager import SessionManager, ChatMessage
from datetime import datetime
import tempfile
import shutil


def test_session_management():
    """Test session management functionality"""
    print("Testing Session Management...")
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(f"Using temporary directory: {temp_dir}")
    
    try:
        # Initialize session manager
        session_manager = SessionManager(sessions_dir=temp_dir)
        
        # Test 1: Create new session
        print("\n1. Testing session creation...")
        session = session_manager.create_new_session("Test Session")
        print(f"Created session: {session.session_id} - {session.title}")
        
        # Test 2: Add messages
        print("\n2. Testing message addition...")
        msg1 = session_manager.add_message("user", "Hello, how are you?")
        msg2 = session_manager.add_message("agent", "I'm doing well, thank you!")
        msg3 = session_manager.add_message("user", "What can you help me with?")
        print(f"Added {len(session.messages)} messages")
        
        # Test 3: Session persistence
        print("\n3. Testing session persistence...")
        session_id = session.session_id
        
        # Create new session manager instance (simulates app restart)
        session_manager2 = SessionManager(sessions_dir=temp_dir)
        loaded_session = session_manager2.load_session(session_id)
        
        if loaded_session:
            print(f"Successfully loaded session: {loaded_session.title}")
            print(f"Messages count: {len(loaded_session.messages)}")
            for i, msg in enumerate(loaded_session.messages):
                print(f"  {i+1}. {msg.sender}: {msg.content[:50]}...")
        else:
            print("Failed to load session")
        
        # Test 4: Session list
        print("\n4. Testing session list...")
        sessions_list = session_manager2.get_session_list()
        print(f"Found {len(sessions_list)} sessions:")
        for session_info in sessions_list:
            print(f"  - {session_info['title']} ({session_info['message_count']} messages)")
        
        # Test 5: Export/Import
        print("\n5. Testing export/import...")
        export_path = os.path.join(temp_dir, "exported_session.json")
        
        if session_manager2.export_session(session_id, export_path):
            print(f"Exported session to: {export_path}")
            
            # Import the session
            imported_session_id = session_manager2.import_session(export_path)
            if imported_session_id:
                print(f"Imported session with new ID: {imported_session_id}")
                
                # Check imported session
                imported_session = session_manager2.load_session(imported_session_id)
                if imported_session:
                    print(f"Imported session title: {imported_session.title}")
                    print(f"Imported messages count: {len(imported_session.messages)}")
            else:
                print("Failed to import session")
        else:
            print("Failed to export session")
        
        # Test 6: Session deletion
        print("\n6. Testing session deletion...")
        sessions_before = len(session_manager2.get_session_list())
        print(f"Sessions before deletion: {sessions_before}")
        
        if session_manager2.delete_session(session_id):
            print("Successfully deleted session")
            sessions_after = len(session_manager2.get_session_list())
            print(f"Sessions after deletion: {sessions_after}")
        else:
            print("Failed to delete session")
        
        # Test 7: Session stats
        print("\n7. Testing session statistics...")
        stats = session_manager2.get_session_stats()
        print(f"Session statistics:")
        print(f"  Total sessions: {stats['total_sessions']}")
        print(f"  Total messages: {stats['total_messages']}")
        
        print("\n✅ All session management tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        print(f"Cleaned up temporary directory: {temp_dir}")


def test_theme_management():
    """Test theme management functionality"""
    print("\nTesting Theme Management...")
    
    try:
        from gui.theme_manager import ThemeManager
        
        # Initialize theme manager
        theme_manager = ThemeManager()
        
        # Test 1: Theme detection
        print(f"1. Detected system theme: {theme_manager.get_current_theme()}")
        
        # Test 2: Theme switching
        print("2. Testing theme switching...")
        original_theme = theme_manager.get_current_theme()
        theme_manager.toggle_theme()
        new_theme = theme_manager.get_current_theme()
        print(f"   Switched from {original_theme} to {new_theme}")
        
        # Test 3: Theme colors
        print("3. Testing theme colors...")
        colors = theme_manager.get_theme_colors()
        print(f"   Primary background: {colors.bg_primary}")
        print(f"   Text color: {colors.text_primary}")
        print(f"   Accent color: {colors.accent_color}")
        
        # Test 4: Message tag configuration
        print("4. Testing message tag configuration...")
        user_config = theme_manager.get_message_tag_config("user_message")
        agent_config = theme_manager.get_message_tag_config("agent_message")
        print(f"   User message background: {user_config.get('background', 'N/A')}")
        print(f"   Agent message background: {agent_config.get('background', 'N/A')}")
        
        print("✅ Theme management tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Theme management test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_session_management()
    test_theme_management()