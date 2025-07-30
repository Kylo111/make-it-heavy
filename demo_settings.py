#!/usr/bin/env python3
"""
Demonstration script for the SettingsPanel functionality.
This script shows the settings panel in action with sample data.
"""

import sys
import os
import tempfile
import yaml
import tkinter as tk
from tkinter import ttk

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.settings_panel import SettingsPanel


def create_demo_config():
    """Create a demo configuration file"""
    demo_config = {
        'provider': {'type': 'deepseek'},
        'deepseek': {
            'api_key': 'sk-demo-deepseek-key-12345',
            'base_url': 'https://api.deepseek.com',
            'model': 'deepseek-chat'
        },
        'openrouter': {
            'api_key': 'sk-or-demo-openrouter-key-67890',
            'base_url': 'https://openrouter.ai/api/v1',
            'model': 'anthropic/claude-3.5-sonnet'
        },
        'system_prompt': 'You are a helpful AI assistant for the Make It Heavy framework.',
        'agent': {'max_iterations': 10},
        'orchestrator': {
            'parallel_agents': 4,
            'task_timeout': 300,
            'aggregation_strategy': 'consensus'
        },
        'search': {
            'max_results': 5,
            'user_agent': 'Mozilla/5.0 (compatible; Make It Heavy Agent)'
        }
    }
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(demo_config, f, default_flow_style=False)
        return f.name


def on_config_change(config):
    """Handle configuration changes"""
    print(f"\n🔧 Configuration Changed:")
    print(f"   Provider: {config.provider}")
    print(f"   Model: {config.model}")
    print(f"   Mode: {config.mode}")
    print(f"   API Keys: {list(config.api_keys.keys())}")


def main():
    """Run the settings panel demo"""
    print("🚀 Make It Heavy - Settings Panel Demo")
    print("=" * 50)
    
    # Create demo configuration
    demo_config_path = create_demo_config()
    print(f"📁 Created demo config: {demo_config_path}")
    
    try:
        # Create main window
        root = tk.Tk()
        root.title("Make It Heavy - Settings Demo")
        root.geometry("600x800")
        
        # Configure style
        style = ttk.Style()
        if 'aqua' in style.theme_names():
            style.theme_use('aqua')
        elif 'clam' in style.theme_names():
            style.theme_use('clam')
        
        # Add title
        title_frame = ttk.Frame(root)
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(
            title_frame,
            text="Make It Heavy - Configuration Settings",
            font=('TkDefaultFont', 16, 'bold')
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Configure your AI providers and execution settings",
            font=('TkDefaultFont', 10),
            foreground='gray'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Create settings panel
        settings_panel = SettingsPanel(
            root,
            config_path=demo_config_path,
            on_config_change=on_config_change
        )
        
        # Add instructions
        instructions_frame = ttk.LabelFrame(root, text="Instructions", padding=10)
        instructions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        instructions = [
            "1. Select your preferred AI provider (DeepSeek or OpenRouter)",
            "2. Enter your API keys for the providers you want to use",
            "3. Choose a model from the available options",
            "4. Select execution mode (Single Agent or Heavy Mode)",
            "5. Click 'Validate API Keys' to test your configuration",
            "6. Click 'Save Configuration' to persist your settings"
        ]
        
        for instruction in instructions:
            ttk.Label(instructions_frame, text=instruction).pack(anchor=tk.W, pady=1)
        
        # Add demo info
        demo_frame = ttk.LabelFrame(root, text="Demo Information", padding=10)
        demo_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        demo_info = ttk.Label(
            demo_frame,
            text="This demo uses sample API keys. Replace with your actual keys for real usage.",
            foreground='orange',
            font=('TkDefaultFont', 9, 'italic')
        )
        demo_info.pack()
        
        print("\n📋 Demo Instructions:")
        print("   - The settings panel is pre-loaded with demo configuration")
        print("   - Try switching between providers to see model options change")
        print("   - API key validation is mocked for demo purposes")
        print("   - Configuration changes will be printed to console")
        print("\n🖱️  Close the window when done exploring")
        
        # Start the GUI
        root.mainloop()
        
    finally:
        # Clean up demo config file
        if os.path.exists(demo_config_path):
            os.unlink(demo_config_path)
            print(f"\n🧹 Cleaned up demo config: {demo_config_path}")


if __name__ == "__main__":
    main()