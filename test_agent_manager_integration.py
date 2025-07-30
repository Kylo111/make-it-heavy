#!/usr/bin/env python3
"""
Test script for AgentManager integration with GUI components.
"""

import sys
import os
import time
import threading

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.agent_manager import AgentManager, AgentProgress


def test_agent_manager_basic():
    """Test basic AgentManager functionality"""
    print("Testing AgentManager basic functionality...")
    
    try:
        # Initialize agent manager
        agent_manager = AgentManager(config_path="config.yaml")
        print("✓ AgentManager initialized successfully")
        
        # Test provider info
        provider_info = agent_manager.get_provider_info()
        print(f"✓ Provider info: {provider_info['provider_name']} - {provider_info['model_name']}")
        
        # Test mode switching
        agent_manager.set_mode("single")
        assert agent_manager.get_current_mode() == "single"
        print("✓ Single mode set successfully")
        
        agent_manager.set_mode("heavy")
        assert agent_manager.get_current_mode() == "heavy"
        print("✓ Heavy mode set successfully")
        
        # Test agent count
        agent_count = agent_manager.get_agent_count()
        print(f"✓ Agent count for heavy mode: {agent_count}")
        
        return True
        
    except Exception as e:
        print(f"✗ AgentManager test failed: {e}")
        return False


def test_single_agent_mode():
    """Test single agent mode execution"""
    print("\nTesting single agent mode...")
    
    try:
        agent_manager = AgentManager(config_path="config.yaml")
        agent_manager.set_mode("single")
        
        # Test simple query
        result = agent_manager.run_single_agent("What is 2+2?")
        print(f"✓ Single agent response: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Single agent test failed: {e}")
        return False


def test_heavy_mode_progress():
    """Test heavy mode with progress tracking"""
    print("\nTesting heavy mode with progress tracking...")
    
    try:
        agent_manager = AgentManager(config_path="config.yaml")
        agent_manager.set_mode("heavy")
        
        # Set up progress callback
        progress_updates = []
        
        def progress_callback(progress):
            progress_updates.append(progress.copy())
            print(f"Progress update: {len(progress)} agents")
            for agent_id, agent_progress in progress.items():
                print(f"  Agent {agent_id + 1}: {agent_progress.status}")
        
        agent_manager.set_progress_callback(progress_callback)
        
        # Test with simple query
        result = agent_manager.run_heavy_mode("What is the capital of France?")
        print(f"✓ Heavy mode response: {result[:100]}...")
        print(f"✓ Received {len(progress_updates)} progress updates")
        
        return True
        
    except Exception as e:
        print(f"✗ Heavy mode test failed: {e}")
        return False


def test_async_execution():
    """Test asynchronous execution"""
    print("\nTesting async execution...")
    
    try:
        agent_manager = AgentManager(config_path="config.yaml")
        agent_manager.set_mode("single")
        
        # Set up completion callback
        completion_result = []
        completion_event = threading.Event()
        
        def completion_callback(result):
            completion_result.append(result)
            completion_event.set()
        
        # Run async
        thread = agent_manager.run_async("What is 1+1?", completion_callback)
        
        # Wait for completion (with timeout)
        if completion_event.wait(timeout=30):
            print(f"✓ Async execution completed: {completion_result[0][:50]}...")
            return True
        else:
            print("✗ Async execution timed out")
            return False
        
    except Exception as e:
        print(f"✗ Async execution test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("AgentManager Integration Tests")
    print("=" * 60)
    
    tests = [
        test_agent_manager_basic,
        test_single_agent_mode,
        test_heavy_mode_progress,
        test_async_execution
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