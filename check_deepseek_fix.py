#!/usr/bin/env python3
"""
Check if your code has the latest DeepSeek empty tools fix
"""

import os
import re
import sys

def check_file_for_fix(file_path):
    """Check if a file contains the fix"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Check for dummy tool implementation
            if "dummy_tool" in content and '"type": "function"' in content:
                return True, "Found dummy tool implementation"
            
            # Check for tools parameter conditional inclusion
            if "if self.tools:" in content and "api_params" in content:
                return True, "Found conditional tools parameter inclusion"
                
            return False, "Fix not found"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def main():
    """Check for DeepSeek fix in code"""
    print("🔍 Checking for DeepSeek empty tools fix")
    print("=" * 60)
    
    files_to_check = [
        "orchestrator.py",
        "agent.py"
    ]
    
    fix_found = False
    
    for file in files_to_check:
        if os.path.exists(file):
            has_fix, message = check_file_for_fix(file)
            status = "✅" if has_fix else "❌"
            print(f"{status} {file}: {message}")
            
            if has_fix:
                fix_found = True
        else:
            print(f"⚠️ {file}: File not found")
    
    print("\n" + "=" * 60)
    if fix_found:
        print("✅ DeepSeek fix detected! Your code should handle empty tools correctly.")
        return 0
    else:
        print("❌ DeepSeek fix NOT detected. You may encounter 'Invalid tools: empty array' errors.")
        print("\nTo fix this issue:")
        print("1. Update orchestrator.py to add a dummy tool when tools array is empty")
        print("2. Or update agent.py to conditionally include tools parameter")
        print("3. Or run the latest version of the code with the fix")
        return 1

if __name__ == "__main__":
    sys.exit(main())