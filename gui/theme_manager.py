"""
Theme Manager for Make It Heavy GUI application.
Handles dark mode support with automatic macOS theme detection.
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import os
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class ThemeColors:
    """Theme color definitions"""
    # Background colors
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    bg_chat: str
    
    # Text colors
    text_primary: str
    text_secondary: str
    text_muted: str
    
    # Message colors
    user_message_bg: str
    user_message_fg: str
    agent_message_bg: str
    agent_message_fg: str
    system_message_bg: str
    system_message_fg: str
    
    # UI element colors
    accent_color: str
    border_color: str
    highlight_color: str
    error_color: str
    success_color: str
    warning_color: str
    
    # Input colors
    input_bg: str
    input_fg: str
    input_border: str
    input_focus_border: str


class ThemeManager:
    """
    Manages application themes with automatic macOS theme detection.
    """
    
    def __init__(self):
        self.current_theme = "light"
        self.theme_change_callbacks: List[Callable[[str], None]] = []
        
        # Define theme colors
        self.themes = {
            "light": ThemeColors(
                # Background colors
                bg_primary="#ffffff",
                bg_secondary="#f8f9fa",
                bg_tertiary="#e9ecef",
                bg_chat="#ffffff",
                
                # Text colors
                text_primary="#212529",
                text_secondary="#495057",
                text_muted="#6c757d",
                
                # Message colors
                user_message_bg="#007bff",
                user_message_fg="#ffffff",
                agent_message_bg="#f8f9fa",
                agent_message_fg="#333333",
                system_message_bg="#e9ecef",
                system_message_fg="#6c757d",
                
                # UI element colors
                accent_color="#007bff",
                border_color="#dee2e6",
                highlight_color="#007bff",
                error_color="#dc3545",
                success_color="#28a745",
                warning_color="#ffc107",
                
                # Input colors
                input_bg="#ffffff",
                input_fg="#495057",
                input_border="#ced4da",
                input_focus_border="#007bff"
            ),
            
            "dark": ThemeColors(
                # Background colors
                bg_primary="#1e1e1e",
                bg_secondary="#2d2d2d",
                bg_tertiary="#3d3d3d",
                bg_chat="#1e1e1e",
                
                # Text colors
                text_primary="#ffffff",
                text_secondary="#e0e0e0",
                text_muted="#a0a0a0",
                
                # Message colors
                user_message_bg="#0d6efd",
                user_message_fg="#ffffff",
                agent_message_bg="#2d2d2d",
                agent_message_fg="#e0e0e0",
                system_message_bg="#3d3d3d",
                system_message_fg="#a0a0a0",
                
                # UI element colors
                accent_color="#0d6efd",
                border_color="#495057",
                highlight_color="#0d6efd",
                error_color="#dc3545",
                success_color="#198754",
                warning_color="#ffc107",
                
                # Input colors
                input_bg="#2d2d2d",
                input_fg="#e0e0e0",
                input_border="#495057",
                input_focus_border="#0d6efd"
            )
        }
        
        # Detect initial theme
        self.current_theme = self.detect_system_theme()
    
    def detect_system_theme(self) -> str:
        """Detect system theme (macOS specific)"""
        if sys.platform == "darwin":
            try:
                # Use AppleScript to detect dark mode on macOS
                result = subprocess.run([
                    'osascript', '-e',
                    'tell application "System Events" to tell appearance preferences to get dark mode'
                ], capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    is_dark = result.stdout.strip().lower() == 'true'
                    return "dark" if is_dark else "light"
                    
            except Exception as e:
                print(f"Error detecting macOS theme: {e}")
        
        # Fallback to light theme
        return "light"
    
    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.current_theme
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> ThemeColors:
        """Get theme colors for specified theme (or current theme)"""
        theme = theme_name or self.current_theme
        return self.themes.get(theme, self.themes["light"])
    
    def set_theme(self, theme_name: str):
        """Set application theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self._notify_theme_change()
        else:
            raise ValueError(f"Unknown theme: {theme_name}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(new_theme)
    
    def auto_detect_and_apply(self):
        """Auto-detect system theme and apply if different"""
        detected_theme = self.detect_system_theme()
        if detected_theme != self.current_theme:
            self.set_theme(detected_theme)
    
    def add_theme_change_callback(self, callback: Callable[[str], None]):
        """Add callback for theme changes"""
        self.theme_change_callbacks.append(callback)
    
    def remove_theme_change_callback(self, callback: Callable[[str], None]):
        """Remove theme change callback"""
        if callback in self.theme_change_callbacks:
            self.theme_change_callbacks.remove(callback)
    
    def _notify_theme_change(self):
        """Notify all callbacks of theme change"""
        for callback in self.theme_change_callbacks:
            try:
                callback(self.current_theme)
            except Exception as e:
                print(f"Error in theme change callback: {e}")
    
    def apply_theme_to_widget(self, widget: tk.Widget, widget_type: str = "default"):
        """Apply current theme to a specific widget"""
        colors = self.get_theme_colors()
        
        try:
            if widget_type == "chat_display":
                widget.configure(
                    bg=colors.bg_chat,
                    fg=colors.text_primary,
                    selectbackground=colors.accent_color,
                    highlightbackground=colors.border_color,
                    highlightcolor=colors.accent_color
                )
            
            elif widget_type == "input":
                widget.configure(
                    bg=colors.input_bg,
                    fg=colors.input_fg,
                    highlightbackground=colors.input_border,
                    highlightcolor=colors.input_focus_border,
                    insertbackground=colors.text_primary
                )
            
            elif widget_type == "frame":
                widget.configure(bg=colors.bg_primary)
            
            elif widget_type == "label":
                widget.configure(
                    bg=colors.bg_primary,
                    fg=colors.text_primary
                )
            
            elif widget_type == "button":
                widget.configure(
                    bg=colors.accent_color,
                    fg=colors.user_message_fg,
                    activebackground=colors.highlight_color,
                    activeforeground=colors.user_message_fg
                )
                
        except Exception as e:
            print(f"Error applying theme to widget: {e}")
    
    def configure_ttk_styles(self, style: ttk.Style):
        """Configure ttk styles for current theme"""
        colors = self.get_theme_colors()
        
        try:
            # Configure general styles
            style.configure('TFrame', background=colors.bg_primary)
            style.configure('TLabel', background=colors.bg_primary, foreground=colors.text_primary)
            style.configure('TButton', background=colors.bg_secondary, foreground=colors.text_primary)
            style.configure('TEntry', fieldbackground=colors.input_bg, foreground=colors.input_fg)
            style.configure('TCombobox', fieldbackground=colors.input_bg, foreground=colors.input_fg)
            style.configure('TNotebook', background=colors.bg_primary)
            style.configure('TNotebook.Tab', background=colors.bg_secondary, foreground=colors.text_primary)
            
            # Configure custom styles
            style.configure('Chat.TFrame', background=colors.bg_chat)
            style.configure('Message.TFrame', background=colors.bg_secondary, relief='solid', borderwidth=1)
            
            # User message styles
            style.configure('UserMessage.TFrame', 
                          background=colors.user_message_bg, 
                          relief='solid', 
                          borderwidth=1)
            style.configure('UserMessage.TLabel', 
                          background=colors.user_message_bg, 
                          foreground=colors.user_message_fg, 
                          padding=10)
            
            # Agent message styles
            style.configure('AgentMessage.TFrame', 
                          background=colors.agent_message_bg, 
                          relief='solid', 
                          borderwidth=1)
            style.configure('AgentMessage.TLabel', 
                          background=colors.agent_message_bg, 
                          foreground=colors.agent_message_fg, 
                          padding=10)
            
            # System message styles
            style.configure('SystemMessage.TFrame', 
                          background=colors.system_message_bg, 
                          relief='solid', 
                          borderwidth=1)
            style.configure('SystemMessage.TLabel', 
                          background=colors.system_message_bg, 
                          foreground=colors.system_message_fg, 
                          padding=5)
            
            # Accent button style
            style.configure('Accent.TButton', 
                          background=colors.accent_color, 
                          foreground=colors.user_message_fg,
                          focuscolor='none')
            style.map('Accent.TButton',
                     background=[('active', colors.highlight_color)])
            
            # Status styles
            style.configure('Success.TLabel', 
                          background=colors.bg_primary, 
                          foreground=colors.success_color)
            style.configure('Error.TLabel', 
                          background=colors.bg_primary, 
                          foreground=colors.error_color)
            style.configure('Warning.TLabel', 
                          background=colors.bg_primary, 
                          foreground=colors.warning_color)
            
        except Exception as e:
            print(f"Error configuring ttk styles: {e}")
    
    def get_message_tag_config(self, message_type: str) -> Dict[str, Any]:
        """Get text tag configuration for chat messages"""
        colors = self.get_theme_colors()
        
        base_font = ('SF Pro Display', 12) if sys.platform == 'darwin' else ('Segoe UI', 10)
        small_font = ('SF Pro Display', 9) if sys.platform == 'darwin' else ('Segoe UI', 8)
        mono_font = ('Courier New', 10) if sys.platform == 'darwin' else ('Consolas', 9)
        
        configs = {
            "user_message": {
                "background": colors.user_message_bg,
                "foreground": colors.user_message_fg,
                "font": base_font + ('normal',),
                "spacing1": 8,
                "spacing3": 8,
                "lmargin1": 80,
                "lmargin2": 80,
                "rmargin": 20,
                "wrap": tk.WORD,
                "relief": 'solid',
                "borderwidth": 0
            },
            
            "agent_message": {
                "background": colors.agent_message_bg,
                "foreground": colors.agent_message_fg,
                "font": base_font + ('normal',),
                "spacing1": 8,
                "spacing3": 8,
                "lmargin1": 20,
                "lmargin2": 20,
                "rmargin": 80,
                "wrap": tk.WORD,
                "relief": 'solid',
                "borderwidth": 0
            },
            
            "system_message": {
                "background": colors.system_message_bg,
                "foreground": colors.system_message_fg,
                "font": base_font[:-1] + (11, 'italic') if sys.platform == 'darwin' else base_font[:-1] + (9, 'italic'),
                "spacing1": 5,
                "spacing3": 5,
                "justify": tk.CENTER,
                "wrap": tk.WORD
            },
            
            "timestamp": {
                "foreground": colors.text_muted,
                "font": small_font,
                "spacing3": 2
            },
            
            "heavy_mode_header": {
                "foreground": colors.text_primary,
                "font": base_font[:-1] + (12, 'bold') if sys.platform == 'darwin' else base_font[:-1] + (11, 'bold'),
                "spacing1": 10,
                "spacing3": 5,
                "justify": tk.CENTER
            },
            
            "agent_progress": {
                "foreground": colors.text_secondary,
                "font": mono_font,
                "spacing1": 2,
                "spacing3": 2,
                "wrap": tk.NONE
            },
            
            "processing": {
                "foreground": colors.accent_color,
                "font": base_font[:-1] + (11, 'italic') if sys.platform == 'darwin' else base_font[:-1] + (10, 'italic'),
                "spacing1": 5,
                "spacing3": 5,
                "justify": tk.CENTER
            },
            
            "error": {
                "foreground": colors.error_color,
                "font": base_font + ('normal',),
                "spacing1": 5,
                "spacing3": 5
            },
            
            "success": {
                "foreground": colors.success_color,
                "font": base_font + ('normal',),
                "spacing1": 5,
                "spacing3": 5
            }
        }
        
        return configs.get(message_type, {})
    
    def start_theme_monitoring(self, check_interval: int = 5000):
        """Start monitoring system theme changes (macOS only)"""
        if sys.platform != "darwin":
            return
        
        def check_theme():
            try:
                detected_theme = self.detect_system_theme()
                if detected_theme != self.current_theme:
                    self.set_theme(detected_theme)
            except Exception as e:
                print(f"Error checking system theme: {e}")
        
        # Schedule periodic theme checks
        def schedule_check():
            check_theme()
            # Schedule next check
            tk._default_root.after(check_interval, schedule_check)
        
        if tk._default_root:
            tk._default_root.after(check_interval, schedule_check)