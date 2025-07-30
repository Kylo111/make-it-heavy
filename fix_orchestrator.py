#!/usr/bin/env python3
"""
Fix orchestrator synthesis issue with DeepSeek
"""

import json
import yaml
import sys
from agent import UniversalAgent
from orchestrator import TaskOrchestrator

def apply_monkey_patch():
    """Apply monkey patch to fix the issue"""
    print("🔧 Applying monkey patch to fix DeepSeek empty tools issue")
    
    # Store original run method
    original_run = UniversalAgent.run
    
    # Define patched run method
    def patched_run(self, user_input):
        """Patched run method that handles empty tools array"""
        print(f"[PATCH] Using patched run method (tools: {len(self.tools)})")
        
        # If tools array is empty, add a dummy tool
        if not self.tools:
            print("[PATCH] Adding dummy tool because tools array is empty")
            dummy_tool = {
                "type": "function",
                "function": {
                    "name": "dummy_tool",
                    "description": "A dummy tool that does nothing",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            self.tools = [dummy_tool]
            print("[PATCH] Dummy tool added")
        
        # Call original run method
        return original_run(self, user_input)
    
    # Apply the patch
    UniversalAgent.run = patched_run
    print("✅ Monkey patch applied successfully")

def test_orchestrator():
    """Test orchestrator with the patch"""
    print("\n🧪 Testing orchestrator with patch")
    print("=" * 60)
    
    try:
        orchestrator = TaskOrchestrator('config_deepseek.yaml', silent=False)
        print("✅ Orchestrator initialized")
        
        # Test synthesis with mock responses
        test_responses = [
            "This is response from agent 1 with some detailed information.",
            "This is response from agent 2 with alternative perspective."
        ]
        
        result = orchestrator._aggregate_consensus(test_responses, [])
        print("✅ Synthesis completed without errors")
        print(f"✅ Result generated ({len(result)} characters)")
        print(f"First 100 chars: {result[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False

def main():
    """Apply fix and test it"""
    print("🚀 Fixing DeepSeek Empty Tools Issue")
    print("=" * 60)
    
    # Apply the monkey patch
    apply_monkey_patch()
    
    # Test the fix
    success = test_orchestrator()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Fix successful! Orchestrator synthesis is now working correctly.")
        print("\nTo permanently fix this issue:")
        print("1. Add the dummy tool logic to the run() method in agent.py")
        print("2. Or ensure tools array is never empty before calling run()")
        return 0
    else:
        print("⚠️ Fix failed. The issue may be more complex than expected.")
        return 1

if __name__ == "__main__":
    sys.exit(main())