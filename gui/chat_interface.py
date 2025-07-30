import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from typing import Optional, Dict
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.agent_manager import AgentManager, AgentProgress
from gui.session_manager import SessionManager
from gui.theme_manager import ThemeManager


class ChatInterface:
    def __init__(self, parent, agent_manager: Optional[AgentManager] = None, 
                 session_manager: Optional[SessionManager] = None,
                 theme_manager: Optional[ThemeManager] = None):
        self.parent = parent
        self.agent_manager = agent_manager
        self.session_manager = session_manager
        self.theme_manager = theme_manager
        self.current_mode = "single"
        self.is_processing = False
        self.progress_widgets = {}  # Store progress widgets for Heavy Mode
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the chat interface components"""
        # Create main chat frame
        self.chat_frame = ttk.Frame(self.parent, style='Chat.TFrame')
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create chat display area
        self.setup_chat_display()
        
        # Create input area
        self.setup_input_area()
        
        # Load current session or add welcome message
        self.load_session()
        
    def setup_chat_display(self):
        """Set up the scrollable chat display area"""
        # Create frame for chat messages
        display_frame = ttk.Frame(self.chat_frame)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create scrollable text widget for chat history
        self.chat_display = scrolledtext.ScrolledText(
            display_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('SF Pro Display', 12) if sys.platform == 'darwin' else ('Segoe UI', 10),
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=15,
            highlightthickness=1
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Apply theme to chat display
        if self.theme_manager:
            self.theme_manager.apply_theme_to_widget(self.chat_display, "chat_display")
        else:
            # Fallback colors
            self.chat_display.configure(
                bg='#ffffff',
                fg='#333333',
                selectbackground='#007bff',
                highlightcolor='#007bff',
                highlightbackground='#e9ecef'
            )
        
        # Configure text tags for different message types
        self.configure_message_tags()
        
    def configure_message_tags(self):
        """Configure text tags for different message types"""
        if not self.theme_manager:
            # Fallback to default configuration if no theme manager
            self._configure_default_tags()
            return
        
        # Configure tags using theme manager
        tag_types = [
            "user_message", "agent_message", "system_message", "timestamp",
            "heavy_mode_header", "agent_progress", "processing", "error", "success"
        ]
        
        for tag_type in tag_types:
            config = self.theme_manager.get_message_tag_config(tag_type)
            if config:
                self.chat_display.tag_configure(tag_type, **config)
    
    def _configure_default_tags(self):
        """Fallback tag configuration without theme manager"""
        # User message style - modern chat bubble appearance
        self.chat_display.tag_configure(
            "user_message",
            background="#007bff",
            foreground="white",
            font=('SF Pro Display', 12, 'normal') if sys.platform == 'darwin' else ('Segoe UI', 10, 'normal'),
            spacing1=8,
            spacing3=8,
            lmargin1=80,
            lmargin2=80,
            rmargin=20,
            wrap=tk.WORD,
            relief='solid',
            borderwidth=0
        )
        
        # Agent message style - modern chat bubble appearance
        self.chat_display.tag_configure(
            "agent_message",
            background="#f8f9fa",
            foreground="#333333",
            font=('SF Pro Display', 12, 'normal') if sys.platform == 'darwin' else ('Segoe UI', 10, 'normal'),
            spacing1=8,
            spacing3=8,
            lmargin1=20,
            lmargin2=20,
            rmargin=80,
            wrap=tk.WORD,
            relief='solid',
            borderwidth=0
        )
        
        # System message style
        self.chat_display.tag_configure(
            "system_message",
            background="#e9ecef",
            foreground="#6c757d",
            font=('SF Pro Display', 11, 'italic') if sys.platform == 'darwin' else ('Segoe UI', 9, 'italic'),
            spacing1=5,
            spacing3=5,
            justify=tk.CENTER,
            wrap=tk.WORD
        )
        
        # Timestamp style
        self.chat_display.tag_configure(
            "timestamp",
            foreground="#6c757d",
            font=('SF Pro Display', 9) if sys.platform == 'darwin' else ('Segoe UI', 8),
            spacing3=2
        )
        
        # Heavy mode progress styles
        self.chat_display.tag_configure(
            "heavy_mode_header",
            foreground="#333333",
            font=('SF Pro Display', 12, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 11, 'bold'),
            spacing1=10,
            spacing3=5,
            justify=tk.CENTER
        )
        
        self.chat_display.tag_configure(
            "agent_progress",
            foreground="#666666",
            font=('Courier New', 10) if sys.platform == 'darwin' else ('Consolas', 9),
            spacing1=2,
            spacing3=2,
            wrap=tk.NONE
        )
        
        # Processing indicator style
        self.chat_display.tag_configure(
            "processing",
            foreground="#007bff",
            font=('SF Pro Display', 11, 'italic') if sys.platform == 'darwin' else ('Segoe UI', 10, 'italic'),
            spacing1=5,
            spacing3=5,
            justify=tk.CENTER
        )
        
    def setup_input_area(self):
        """Set up the message input area"""
        # Create input frame
        input_frame = ttk.Frame(self.chat_frame)
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Create input text widget
        self.message_input = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            font=('SF Pro Display', 12) if sys.platform == 'darwin' else ('Segoe UI', 10),
            relief='flat',
            borderwidth=0,
            padx=10,
            pady=8,
            highlightthickness=1
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Apply theme to input
        if self.theme_manager:
            self.theme_manager.apply_theme_to_widget(self.message_input, "input")
        else:
            # Fallback colors
            self.message_input.configure(
                bg='#ffffff',
                fg='#333333',
                highlightcolor='#007bff',
                highlightbackground='#e9ecef',
                insertbackground='#333333'
            )
        
        # Create send button
        self.send_button = ttk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            style='Accent.TButton'
        )
        self.send_button.pack(side=tk.RIGHT, padx=(0, 0))
        
        # Configure button style
        style = ttk.Style()
        style.configure('Accent.TButton', font=('SF Pro Display', 11, 'bold') if sys.platform == 'darwin' else ('Segoe UI', 9, 'bold'))
        
        # Bind keyboard events
        self.message_input.bind('<Return>', self.on_enter_key)
        self.message_input.bind('<Shift-Return>', self.on_shift_enter)
        
        # Focus on input
        self.message_input.focus_set()
        
    def on_enter_key(self, event):
        """Handle Enter key press - send message"""
        self.send_message()
        return 'break'  # Prevent default behavior
        
    def on_shift_enter(self, event):
        """Handle Shift+Enter - new line"""
        return None  # Allow default behavior (new line)
        
    def send_message(self):
        """Send user message"""
        if self.is_processing:
            return  # Don't send if already processing
            
        message = self.message_input.get("1.0", tk.END).strip()
        if not message:
            return  # Don't send empty messages
        
        if not self.agent_manager:
            self.show_error_message("Agent manager not initialized. Please check configuration.")
            return
        
        try:
            # Add user message to chat
            self.add_message("user", message)
            
            # Clear input
            self.message_input.delete("1.0", tk.END)
            
            # Disable send button during processing
            self.is_processing = True
            self.send_button.config(state="disabled", text="Processing...")
            
            # Show processing indicator
            if self.current_mode == "heavy":
                self.show_heavy_mode_progress()
            else:
                self.show_loading_indicator("Agent is thinking...")
            
            # Clear any existing callbacks first
            self.agent_manager.set_completion_callback(None)
            self.agent_manager.set_progress_callback(None)
            
            # Set up new callbacks
            self.agent_manager.set_completion_callback(self.on_agent_completion)
            if self.current_mode == "heavy":
                self.agent_manager.set_progress_callback(self.on_progress_update)
            
            # Run agent asynchronously
            self.agent_manager.run_async(message)
            
        except Exception as e:
            # Handle errors during message sending
            self.is_processing = False
            self.send_button.config(state="normal", text="Send")
            self.show_error_message(f"Failed to send message: {str(e)}")
            
    def add_message(self, sender: str, message: str, timestamp: Optional[datetime] = None, 
                   message_type: str = "text", save_to_session: bool = True):
        """Add a message to the chat display"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Save to session if enabled
        if save_to_session and self.session_manager:
            self.session_manager.add_message(sender, message, message_type)
            
        # Enable text widget for editing
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        time_str = timestamp.strftime("%H:%M")
        self.chat_display.insert(tk.END, f"{time_str}\n", "timestamp")
        
        # Determine tag based on message type and sender
        if message_type == "error":
            tag = "error"
            display_message = f"Error: {message}\n\n"
        elif message_type == "success":
            tag = "success"
            display_message = f"{message}\n\n"
        elif message_type == "processing":
            tag = "processing"
            display_message = f"{message}\n\n"
        elif sender == "user":
            tag = "user_message"
            display_message = f"You: {message}\n\n"
        elif sender == "agent":
            tag = "agent_message"
            display_message = f"Agent: {message}\n\n"
        elif sender == "system":
            tag = "system_message"
            display_message = f"{message}\n\n"
        else:
            tag = "system_message"
            display_message = f"{message}\n\n"
        
        # Add message with appropriate tag
        self.chat_display.insert(tk.END, display_message, tag)
            
        # Disable text widget to prevent editing
        self.chat_display.config(state=tk.DISABLED)
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Create new session if session manager is available
        if self.session_manager:
            self.session_manager.create_new_session()
        
        # Add welcome message back
        self.add_message("system", "Chat cleared. Ready for new conversation!", save_to_session=False)
    
    def set_agent_manager(self, agent_manager: AgentManager):
        """Set the agent manager for this chat interface"""
        self.agent_manager = agent_manager
    
    def set_mode(self, mode: str):
        """Set the execution mode (single or heavy)"""
        self.current_mode = mode
        if self.agent_manager:
            self.agent_manager.set_mode(mode)
        
        # Update welcome message based on mode
        mode_name = "Heavy Mode (4 agents)" if mode == "heavy" else "Single Agent Mode"
        self.add_message("system", f"Switched to {mode_name}")
    
    def on_agent_completion(self, result: str):
        """Handle agent completion"""
        try:
            # Re-enable send button
            self.is_processing = False
            self.send_button.config(state="normal", text="Send")
            
            # Clear progress display if in heavy mode
            if self.current_mode == "heavy":
                self.clear_progress_display()
            
            # Check if result is an error
            if result.startswith("Error:"):
                self.show_error_message(result[6:])  # Remove "Error:" prefix
            else:
                # Add agent response
                self.add_message("agent", result)
                
        except Exception as e:
            print(f"Error handling agent completion: {e}")
            self.is_processing = False
            self.send_button.config(state="normal", text="Send")
            self.show_error_message(f"Error processing response: {str(e)}")
    
    def on_progress_update(self, progress: Dict[int, AgentProgress]):
        """Handle progress updates for Heavy Mode"""
        if self.current_mode != "heavy":
            return
        
        # Update progress display
        self.update_progress_display(progress)
    
    def show_heavy_mode_progress(self):
        """Show initial Heavy Mode progress display"""
        # Enable text widget for editing
        self.chat_display.config(state=tk.NORMAL)
        
        # Add Heavy Mode header
        self.chat_display.insert(tk.END, "HEAVY MODE - 4 AGENTS PROCESSING\n", "heavy_mode_header")
        
        # Store the position where progress starts
        self.progress_start_pos = self.chat_display.index(tk.END)
        
        # Add initial progress lines for each agent
        agent_count = self.agent_manager.get_agent_count() if self.agent_manager else 4
        for i in range(agent_count):
            progress_line = f"AGENT {i+1:02d}  ○ " + "·" * 70 + "\n"
            self.chat_display.insert(tk.END, progress_line, "agent_progress")
        
        self.chat_display.insert(tk.END, "\n", "agent_progress")
        
        # Disable text widget
        self.chat_display.config(state=tk.DISABLED)
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
    
    def update_progress_display(self, progress: Dict[int, AgentProgress]):
        """Update the Heavy Mode progress display"""
        if not hasattr(self, 'progress_start_pos'):
            return
        
        # Enable text widget for editing
        self.chat_display.config(state=tk.NORMAL)
        
        # Calculate the range to replace
        start_line = int(self.progress_start_pos.split('.')[0])
        agent_count = len(progress)
        end_pos = f"{start_line + agent_count}.0"
        
        # Clear existing progress lines
        self.chat_display.delete(self.progress_start_pos, end_pos)
        
        # Insert updated progress lines
        self.chat_display.mark_set(tk.INSERT, self.progress_start_pos)
        for i in range(agent_count):
            if i in progress:
                agent_progress = progress[i]
                progress_line = f"AGENT {i+1:02d}  {agent_progress.progress_bar}\n"
                self.chat_display.insert(tk.INSERT, progress_line, "agent_progress")
        
        # Disable text widget
        self.chat_display.config(state=tk.DISABLED)
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
    
    def clear_progress_display(self):
        """Clear the Heavy Mode progress display"""
        if hasattr(self, 'progress_start_pos'):
            # Enable text widget for editing
            self.chat_display.config(state=tk.NORMAL)
            
            # Calculate the range to clear
            start_line = int(self.progress_start_pos.split('.')[0]) - 1  # Include header
            agent_count = self.agent_manager.get_agent_count() if self.agent_manager else 4
            end_pos = f"{start_line + agent_count + 2}.0"  # Include header and extra newline
            
            # Clear progress display
            self.chat_display.delete(f"{start_line}.0", end_pos)
            
            # Disable text widget
            self.chat_display.config(state=tk.DISABLED)
            
            # Remove progress start position
            delattr(self, 'progress_start_pos')
    
    def load_session(self):
        """Load current session messages into chat display"""
        # Clear current display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        if self.session_manager:
            current_session = self.session_manager.get_current_session()
            if current_session and current_session.messages:
                # Load messages from session
                for message in current_session.messages:
                    self.add_message(
                        message.sender, 
                        message.content, 
                        message.timestamp,
                        save_to_session=False  # Don't save when loading
                    )
            else:
                # Add welcome message for new session
                self.add_message("system", "Welcome to Make It Heavy! Type your message below to get started.", save_to_session=False)
        else:
            # Fallback welcome message
            self.add_message("system", "Welcome to Make It Heavy! Type your message below to get started.", save_to_session=False)
    
    def apply_theme(self):
        """Apply current theme to chat interface"""
        if not self.theme_manager:
            return
        
        try:
            # Apply theme to widgets
            self.theme_manager.apply_theme_to_widget(self.chat_display, "chat_display")
            self.theme_manager.apply_theme_to_widget(self.message_input, "input")
            
            # Reconfigure message tags
            self.configure_message_tags()
            
        except Exception as e:
            print(f"Error applying theme to chat interface: {e}")
    
    def on_window_resize(self):
        """Handle window resize for responsive layout"""
        try:
            # Adjust chat display height based on window size
            window_height = self.parent.winfo_height()
            if window_height > 0:
                # Calculate appropriate height for chat display
                # This is a simple responsive adjustment
                pass
                
        except Exception as e:
            print(f"Error handling window resize: {e}")
    
    def show_error_message(self, error_msg: str):
        """Show error message in chat"""
        self.add_message("system", f"Error: {error_msg}", message_type="error")
    
    def show_success_message(self, success_msg: str):
        """Show success message in chat"""
        self.add_message("system", success_msg, message_type="success")
    
    def show_loading_indicator(self, message: str = "Processing..."):
        """Show loading indicator"""
        self.add_message("system", message, message_type="processing")