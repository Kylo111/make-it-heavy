#!/usr/bin/env python3
"""
Demo script for the multi-model configuration GUI.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.multi_model_config_panel import MultiModelConfigPanel


def main():
    """Run the multi-model configuration GUI demo."""
    # Create root window
    root = tk.Tk()
    root.title("Multi-Model Configuration Demo")
    root.geometry("1000x700")
    
    # Configure style for modern appearance
    style = ttk.Style()
    
    # Try to use a more modern theme if available
    available_themes = style.theme_names()
    if 'aqua' in available_themes:  # macOS native theme
        style.theme_use('aqua')
    elif 'clam' in available_themes:  # Modern alternative
        style.theme_use('clam')
    
    try:
        # Create the multi-model configuration panel
        panel = MultiModelConfigPanel(
            root,
            config_path="config.yaml",
            on_config_change=lambda config: print(f"Configuration changed: {config}")
        )
        
        print("Multi-model configuration panel created successfully!")
        print("The panel will load available models in the background...")
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        print(f"Error creating multi-model configuration panel: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()