import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os

# Add the parent directory to the path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.chat_interface import ChatInterface
from gui.settings_panel import SettingsPanel, AppConfig
from gui.agent_manager import AgentManager
from gui.session_manager import SessionManager
from gui.theme_manager import ThemeManager
from gui.multi_model_config_panel import MultiModelConfigPanel


class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.current_config = None
        self.agent_manager = None
        
        # Initialize managers
        self.session_manager = SessionManager()
        self.theme_manager = ThemeManager()
        
        # Set up theme change callback
        self.theme_manager.add_theme_change_callback(self.on_theme_change)
        
        self.setup_ui()
        self.initialize_agent_manager()
        
        # Start theme monitoring for automatic theme detection
        self.theme_manager.start_theme_monitoring()
        
        # Create initial session
        self.session_manager.create_new_session()
        
    def setup_ui(self):
        """Set up the main application window and UI components"""
        # Configure main window
        self.root.title("Make It Heavy - GUI")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        
        # Configure style for modern appearance
        self.style = ttk.Style()
        
        # Try to use a more modern theme if available
        available_themes = self.style.theme_names()
        if 'aqua' in available_themes:  # macOS native theme
            self.style.theme_use('aqua')
        elif 'clam' in available_themes:  # Modern alternative
            self.style.theme_use('clam')
        
        # Apply theme styles
        self.theme_manager.configure_ttk_styles(self.style)
        
        # Create menu bar
        self.setup_menu_bar()
        
        # Create main container with notebook for tabs
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create chat tab
        self.chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="Chat")
        
        # Create sessions tab
        self.sessions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sessions_frame, text="Sessions")
        
        # Create settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Create multi-model config tab
        self.multi_model_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.multi_model_frame, text="Multi-Model Config")
        
        # Create mode selection frame in chat tab
        self.setup_mode_selection()
        
        # Create chat interface (agent manager will be set later)
        self.chat_interface = ChatInterface(
            self.chat_frame, 
            session_manager=self.session_manager,
            theme_manager=self.theme_manager
        )
        
        # Create sessions panel
        self.setup_sessions_panel()
        
        # Create settings panel
        self.settings_panel = SettingsPanel(
            self.settings_frame, 
            config_path="config.yaml",
            on_config_change=self.on_config_change
        )
        
        # Create multi-model config panel
        self.multi_model_panel = MultiModelConfigPanel(
            self.multi_model_frame,
            config_path="config.yaml",
            on_config_change=self.on_multi_model_config_change
        )
        
        # Configure window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configure window resizing
        self.root.bind('<Configure>', self.on_window_resize)
    def setup_menu_bar(self):
        """Set up the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Session", command=self.new_session, accelerator="Cmd+N")
        file_menu.add_separator()
        file_menu.add_command(label="Export Session...", command=self.export_session)
        file_menu.add_command(label="Import Session...", command=self.import_session)
        file_menu.add_separator()
        file_menu.add_command(label="Clear Current Session", command=self.clear_current_session)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme, accelerator="Cmd+T")
        view_menu.add_separator()
        view_menu.add_command(label="Sessions", command=lambda: self.notebook.select(1))
        view_menu.add_command(label="Settings", command=lambda: self.notebook.select(2))
        view_menu.add_command(label="Multi-Model Config", command=lambda: self.notebook.select(3))
        
        # Bind keyboard shortcuts
        self.root.bind_all("<Command-n>", lambda e: self.new_session())
        self.root.bind_all("<Command-t>", lambda e: self.toggle_theme())
    
    def setup_sessions_panel(self):
        """Set up the sessions management panel"""
        # Create main sessions frame
        sessions_main = ttk.Frame(self.sessions_frame)
        sessions_main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(sessions_main, text="Session Management", font=('TkDefaultFont', 14, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Control buttons frame
        controls_frame = ttk.Frame(sessions_main)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(controls_frame, text="New Session", command=self.new_session).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Refresh", command=self.refresh_sessions).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Delete Selected", command=self.delete_selected_session).pack(side=tk.LEFT, padx=(0, 5))
        
        # Sessions list frame
        list_frame = ttk.LabelFrame(sessions_main, text="Sessions", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for sessions
        columns = ('Title', 'Created', 'Last Updated', 'Messages')
        self.sessions_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.sessions_tree.heading('Title', text='Title')
        self.sessions_tree.heading('Created', text='Created')
        self.sessions_tree.heading('Last Updated', text='Last Updated')
        self.sessions_tree.heading('Messages', text='Messages')
        
        self.sessions_tree.column('Title', width=300)
        self.sessions_tree.column('Created', width=150)
        self.sessions_tree.column('Last Updated', width=150)
        self.sessions_tree.column('Messages', width=80)
        
        # Add scrollbar
        sessions_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.sessions_tree.yview)
        self.sessions_tree.configure(yscrollcommand=sessions_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.sessions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sessions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to load session
        self.sessions_tree.bind('<Double-1>', self.on_session_double_click)
        
        # Load sessions
        self.refresh_sessions()
        
    def run(self):
        """Start the application main loop"""
        self.root.mainloop()
        
    def on_config_change(self, config: AppConfig):
        """Handle configuration changes from settings panel"""
        self.current_config = config
        
        # Update agent manager with new configuration
        if self.agent_manager:
            try:
                # Get API key for selected provider
                api_key = config.api_keys.get(config.provider, "")
                if api_key:
                    self.agent_manager.update_config(config.provider, config.model, api_key)
                    print(f"Configuration updated: Provider={config.provider}, Model={config.model}")
                else:
                    print(f"Warning: No API key found for provider {config.provider}")
            except Exception as e:
                print(f"Failed to update agent configuration: {e}")
        
        # Update mode selection if different
        if config.mode != self.mode_var.get():
            self.mode_var.set(config.mode)
            self.on_mode_change()
    
    def on_multi_model_config_change(self, config):
        """Handle multi-model configuration changes"""
        try:
            # Update agent manager with multi-model configuration
            if self.agent_manager:
                self.agent_manager.set_multi_model_config(config)
                print("Multi-model configuration updated")
        except Exception as e:
            print(f"Failed to update multi-model configuration: {e}")
        
    def switch_provider(self, provider: str):
        """Switch to a different provider"""
        # This method will be used by other components
        if self.settings_panel:
            # Update settings panel if needed
            pass
            
    def switch_mode(self, mode: str):
        """Switch between single agent and heavy mode"""
        # This method will be used by other components
        if self.current_config:
            self.current_config.mode = mode
            
    def load_models(self, provider: str):
        """Load available models for a provider"""
        # This method will be used by other components
        if self.settings_panel:
            return self.settings_panel.providers.get(provider, {}).get('models', [])
        return []
    
    def setup_mode_selection(self):
        """Set up mode selection UI in chat tab"""
        # Create mode selection frame at top of chat
        mode_frame = ttk.LabelFrame(self.chat_frame, text="Execution Mode", padding=10)
        mode_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Mode selection variable
        self.mode_var = tk.StringVar(value="single")
        
        # Create radio buttons frame
        radio_frame = ttk.Frame(mode_frame)
        radio_frame.pack(fill=tk.X)
        
        # Single agent mode
        single_radio = ttk.Radiobutton(
            radio_frame,
            text="Single Agent Mode",
            variable=self.mode_var,
            value="single",
            command=self.on_mode_change
        )
        single_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        # Heavy mode
        heavy_radio = ttk.Radiobutton(
            radio_frame,
            text="Heavy Mode (4 Agents)",
            variable=self.mode_var,
            value="heavy",
            command=self.on_mode_change
        )
        heavy_radio.pack(side=tk.LEFT)
        
        # Status label
        self.mode_status_var = tk.StringVar(value="Single agent for faster responses")
        mode_status_label = ttk.Label(
            mode_frame,
            textvariable=self.mode_status_var,
            foreground="gray",
            font=('TkDefaultFont', 9)
        )
        mode_status_label.pack(anchor=tk.W, pady=(5, 0))
    
    def initialize_agent_manager(self):
        """Initialize the agent manager"""
        try:
            self.agent_manager = AgentManager(config_path="config.yaml")
            
            # Connect agent manager to chat interface
            self.chat_interface.set_agent_manager(self.agent_manager)
            
            # Set initial mode
            self.agent_manager.set_mode(self.mode_var.get())
                
        except Exception as e:
            print(f"Failed to initialize agent manager: {e}")
            # Show error in UI
            if hasattr(self, 'mode_status_var'):
                self.mode_status_var.set(f"Error: {str(e)}")
    
    def on_mode_change(self):
        """Handle mode selection change"""
        mode = self.mode_var.get()
        
        # Update status text
        if mode == "single":
            self.mode_status_var.set("Single agent for faster responses")
        else:
            self.mode_status_var.set("4 parallel agents for comprehensive analysis")
        
        # Update agent manager and chat interface
        if self.agent_manager:
            self.agent_manager.set_mode(mode)
        
        if hasattr(self, 'chat_interface'):
            self.chat_interface.set_mode(mode)
    
    def on_closing(self):
        """Handle application closing"""
        # Stop any running agents
        if self.agent_manager:
            self.agent_manager.stop_execution()
        self.root.destroy()
    
    def on_window_resize(self, event):
        """Handle window resize events for responsive layout"""
        if event.widget == self.root:
            # Update chat interface layout if needed
            if hasattr(self, 'chat_interface'):
                self.chat_interface.on_window_resize()
    
    def on_theme_change(self, theme_name: str):
        """Handle theme changes"""
        try:
            # Update ttk styles
            self.theme_manager.configure_ttk_styles(self.style)
            
            # Update chat interface theme
            if hasattr(self, 'chat_interface'):
                self.chat_interface.apply_theme()
            
            # Update root window background
            colors = self.theme_manager.get_theme_colors()
            self.root.configure(bg=colors.bg_primary)
            
        except Exception as e:
            print(f"Error applying theme: {e}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.theme_manager.toggle_theme()
    
    def new_session(self):
        """Create a new chat session"""
        try:
            self.session_manager.create_new_session()
            self.chat_interface.load_session()
            self.refresh_sessions()
            
            # Switch to chat tab
            self.notebook.select(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create new session: {str(e)}")
    
    def clear_current_session(self):
        """Clear the current session"""
        if messagebox.askyesno("Clear Session", "Are you sure you want to clear the current session?"):
            try:
                self.session_manager.clear_current_session()
                self.chat_interface.load_session()
                self.refresh_sessions()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear session: {str(e)}")
    
    def refresh_sessions(self):
        """Refresh the sessions list"""
        try:
            # Clear existing items
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)
            
            # Load sessions
            sessions = self.session_manager.get_session_list()
            
            for session in sessions:
                created_str = session['created_at'].strftime('%Y-%m-%d %H:%M')
                updated_str = session['last_updated'].strftime('%Y-%m-%d %H:%M')
                
                self.sessions_tree.insert('', tk.END, values=(
                    session['title'],
                    created_str,
                    updated_str,
                    session['message_count']
                ), tags=(session['session_id'],))
                
        except Exception as e:
            print(f"Error refreshing sessions: {e}")
    
    def on_session_double_click(self, event):
        """Handle double-click on session to load it"""
        selection = self.sessions_tree.selection()
        if selection:
            item = selection[0]
            session_id = self.sessions_tree.item(item)['tags'][0]
            self.load_session(session_id)
    
    def load_session(self, session_id: str):
        """Load a specific session"""
        try:
            session = self.session_manager.load_session(session_id)
            if session:
                self.chat_interface.load_session()
                # Switch to chat tab
                self.notebook.select(0)
            else:
                messagebox.showerror("Error", "Failed to load session")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load session: {str(e)}")
    
    def delete_selected_session(self):
        """Delete the selected session"""
        selection = self.sessions_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a session to delete")
            return
        
        item = selection[0]
        session_id = self.sessions_tree.item(item)['tags'][0]
        session_title = self.sessions_tree.item(item)['values'][0]
        
        if messagebox.askyesno("Delete Session", f"Are you sure you want to delete '{session_title}'?"):
            try:
                if self.session_manager.delete_session(session_id):
                    self.refresh_sessions()
                    # If we deleted the current session, create a new one
                    current_session = self.session_manager.get_current_session()
                    if not current_session or current_session.session_id == session_id:
                        self.new_session()
                else:
                    messagebox.showerror("Error", "Failed to delete session")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete session: {str(e)}")
    
    def export_session(self):
        """Export current session to file"""
        current_session = self.session_manager.get_current_session()
        if not current_session:
            messagebox.showwarning("No Session", "No active session to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Session",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialname=f"{current_session.title}.json"
        )
        
        if filename:
            try:
                if self.session_manager.export_session(current_session.session_id, filename):
                    messagebox.showinfo("Success", f"Session exported to {filename}")
                else:
                    messagebox.showerror("Error", "Failed to export session")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export session: {str(e)}")
    
    def import_session(self):
        """Import session from file"""
        filename = filedialog.askopenfilename(
            title="Import Session",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                session_id = self.session_manager.import_session(filename)
                if session_id:
                    self.refresh_sessions()
                    messagebox.showinfo("Success", "Session imported successfully")
                else:
                    messagebox.showerror("Error", "Failed to import session")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import session: {str(e)}")


if __name__ == "__main__":
    app = MainApplication()
    app.run()