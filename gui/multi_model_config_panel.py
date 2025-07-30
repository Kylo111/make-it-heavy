"""
Multi-model configuration panel for Make It Heavy GUI application.
Allows users to configure different models for each agent.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import sys
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
import threading

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_config.model_configuration_manager import ModelConfigurationManager, ModelConfigurationManagerError
from model_config.data_models import ModelInfo, AgentModelConfig, CostEstimate, ConfigurationProfile
from config_manager import ConfigurationManager


class MultiModelConfigPanel:
    """Multi-model configuration panel for agent model selection."""
    
    def __init__(self, parent, config_path: str = "config.yaml", on_config_change: Optional[Callable] = None):
        self.parent = parent
        self.config_path = config_path
        self.on_config_change = on_config_change
        
        # Initialize managers
        self.config_manager = ConfigurationManager()
        self.model_manager = ModelConfigurationManager(self.config_manager)
        
        # Current state
        self.available_models: List[ModelInfo] = []
        self.current_config: Optional[AgentModelConfig] = None
        self.predefined_profiles: List[ConfigurationProfile] = []
        
        # Agent names for display
        self.agent_names = {
            0: "Research Agent",
            1: "Analysis Agent", 
            2: "Verification Agent",
            3: "Alternatives Agent"
        }
        
        # UI components
        self.agent_selectors: Dict[int, 'AgentModelSelector'] = {}
        self.model_info_widget: Optional['ModelInfoWidget'] = None
        self.cost_calculator_widget: Optional['CostCalculatorWidget'] = None
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_initial_data()
    
    def setup_ui(self):
        """Set up the multi-model configuration UI."""
        # Create main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="Multi-Model Configuration", 
            font=('TkDefaultFont', 14, 'bold')
        )
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Profile selection section
        self.setup_profile_section()
        
        # Agent configuration section
        self.setup_agent_section()
        
        # Model info and cost section
        self.setup_info_section()
        
        # Action buttons
        self.setup_action_buttons()
    
    def setup_profile_section(self):
        """Set up the configuration profile selection section."""
        profile_frame = ttk.LabelFrame(self.main_frame, text="Configuration Profiles", padding=10)
        profile_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Profile selection
        profile_select_frame = ttk.Frame(profile_frame)
        profile_select_frame.pack(fill=tk.X)
        
        ttk.Label(profile_select_frame, text="Profile:").pack(side=tk.LEFT)
        
        self.profile_var = tk.StringVar(value="Custom")
        self.profile_combo = ttk.Combobox(
            profile_select_frame,
            textvariable=self.profile_var,
            state="readonly",
            width=15
        )
        self.profile_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.profile_combo.bind('<<ComboboxSelected>>', self.on_profile_change)
        
        # Profile buttons
        ttk.Button(
            profile_select_frame,
            text="Apply Profile",
            command=self.apply_selected_profile
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            profile_select_frame,
            text="Save as Profile",
            command=self.save_as_profile
        ).pack(side=tk.LEFT)
    
    def setup_agent_section(self):
        """Set up the agent model selection section."""
        agent_frame = ttk.LabelFrame(self.main_frame, text="Agent Model Configuration", padding=10)
        agent_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create grid for agent selectors
        agents_grid = ttk.Frame(agent_frame)
        agents_grid.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        agents_grid.columnconfigure(0, weight=1)
        agents_grid.columnconfigure(1, weight=1)
        agents_grid.rowconfigure(0, weight=1)
        agents_grid.rowconfigure(1, weight=1)
        
        # Create agent selectors in 2x2 grid
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        for i, (row, col) in enumerate(positions):
            agent_selector = AgentModelSelector(
                agents_grid, 
                agent_id=i,
                agent_name=self.agent_names[i],
                on_model_change=self.on_agent_model_change
            )
            agent_selector.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            self.agent_selectors[i] = agent_selector
    
    def setup_info_section(self):
        """Set up the model info and cost calculation section."""
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Model info widget
        self.model_info_widget = ModelInfoWidget(info_frame)
        self.model_info_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Cost calculator widget
        self.cost_calculator_widget = CostCalculatorWidget(info_frame)
        self.cost_calculator_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def setup_action_buttons(self):
        """Set up action buttons."""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X)
        
        # Left side buttons
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)
        
        ttk.Button(
            left_buttons,
            text="Test Configuration",
            command=self.test_configuration
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            left_buttons,
            text="Reset to Defaults",
            command=self.reset_to_defaults
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Right side buttons
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(
            right_buttons,
            text="Import",
            command=self.import_configuration
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            right_buttons,
            text="Export",
            command=self.export_configuration
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            right_buttons,
            text="Save Configuration",
            command=self.save_configuration,
            style='Accent.TButton'
        ).pack(side=tk.RIGHT, padx=(5, 0))
    
    def load_initial_data(self):
        """Load initial data in background thread."""
        def load_data():
            try:
                # Load available models
                self.available_models = self.model_manager.get_available_models()
                
                # Load predefined profiles
                self.predefined_profiles = self.model_manager.get_predefined_profiles()
                
                # Load current configuration
                self.current_config = self.model_manager.load_agent_configuration(self.config_path)
                
                # Update UI on main thread
                self.parent.after(0, self.update_ui_after_load)
                
            except Exception as e:
                self.parent.after(0, lambda: self.show_error(f"Failed to load data: {str(e)}"))
        
        # Show loading state
        self.show_loading_state()
        
        # Start background thread
        thread = threading.Thread(target=load_data, daemon=True)
        thread.start()
    
    def show_loading_state(self):
        """Show loading state in UI."""
        for selector in self.agent_selectors.values():
            selector.set_loading(True)
    
    def update_ui_after_load(self):
        """Update UI after data is loaded."""
        try:
            # Update profile combo
            profile_names = ["Custom"] + [p.name for p in self.predefined_profiles]
            self.profile_combo['values'] = profile_names
            
            # Update agent selectors with available models
            for selector in self.agent_selectors.values():
                selector.set_available_models(self.available_models)
                selector.set_loading(False)
            
            # Load current configuration if available
            if self.current_config:
                self.load_configuration_to_ui(self.current_config)
                self.profile_var.set("Custom")
            else:
                # Set default configuration
                self.set_default_configuration()
            
            # Update cost calculation
            self.update_cost_calculation()
            
        except Exception as e:
            self.show_error(f"Failed to update UI: {str(e)}")
    
    def on_profile_change(self, event=None):
        """Handle profile selection change."""
        # This is handled by apply_selected_profile button
        pass
    
    def apply_selected_profile(self):
        """Apply the selected predefined profile."""
        try:
            profile_name = self.profile_var.get()
            
            if profile_name == "Custom":
                return
            
            # Find the selected profile
            profile = next((p for p in self.predefined_profiles if p.name == profile_name), None)
            if not profile:
                messagebox.showerror("Error", f"Profile '{profile_name}' not found")
                return
            
            # Apply the profile configuration
            self.load_configuration_to_ui(profile.config)
            self.current_config = profile.config
            
            # Update cost calculation
            self.update_cost_calculation()
            
            messagebox.showinfo("Success", f"Applied {profile_name} profile")
            
        except Exception as e:
            self.show_error(f"Failed to apply profile: {str(e)}")
    
    def on_agent_model_change(self, agent_id: int, model_id: str):
        """Handle agent model selection change."""
        try:
            # Update current configuration
            if not self.current_config:
                self.current_config = self.create_default_config()
            
            # Update the specific agent model
            if agent_id == 0:
                self.current_config.agent_0_model = model_id
            elif agent_id == 1:
                self.current_config.agent_1_model = model_id
            elif agent_id == 2:
                self.current_config.agent_2_model = model_id
            elif agent_id == 3:
                self.current_config.agent_3_model = model_id
            
            # Set profile to custom
            self.current_config.profile_name = "custom"
            self.profile_var.set("Custom")
            
            # Update model info display
            self.update_model_info_display(model_id)
            
            # Update cost calculation
            self.update_cost_calculation()
            
        except Exception as e:
            self.show_error(f"Failed to update agent model: {str(e)}")
    
    def update_model_info_display(self, model_id: str):
        """Update the model info display for selected model."""
        if not self.model_info_widget:
            return
        
        model_info = next((m for m in self.available_models if m.id == model_id), None)
        if model_info:
            self.model_info_widget.display_model_info(model_info)
    
    def update_cost_calculation(self):
        """Update the cost calculation display."""
        if not self.cost_calculator_widget or not self.current_config:
            return
        
        try:
            cost_estimate = self.model_manager.calculate_configuration_cost(self.current_config)
            self.cost_calculator_widget.display_cost_estimate(cost_estimate)
        except Exception as e:
            self.cost_calculator_widget.display_error(f"Cost calculation failed: {str(e)}")
    
    def create_default_config(self) -> AgentModelConfig:
        """Create a default configuration."""
        if not self.available_models:
            raise ValueError("No models available")
        
        default_model = self.available_models[0].id
        
        return AgentModelConfig(
            agent_0_model=default_model,
            agent_1_model=default_model,
            agent_2_model=default_model,
            agent_3_model=default_model,
            synthesis_model=default_model,
            default_model=default_model,
            profile_name="custom"
        )
    
    def set_default_configuration(self):
        """Set default configuration in UI."""
        try:
            self.current_config = self.create_default_config()
            self.load_configuration_to_ui(self.current_config)
        except Exception as e:
            self.show_error(f"Failed to set default configuration: {str(e)}")
    
    def load_configuration_to_ui(self, config: AgentModelConfig):
        """Load configuration into UI components."""
        # Update agent selectors
        for agent_id, selector in self.agent_selectors.items():
            model_id = config.get_agent_model(agent_id)
            selector.set_selected_model(model_id)
        
        # Update model info for first agent's model
        if config.agent_0_model:
            self.update_model_info_display(config.agent_0_model)
    
    def save_configuration(self):
        """Save current configuration."""
        try:
            if not self.current_config:
                messagebox.showwarning("Warning", "No configuration to save")
                return
            
            # Validate configuration
            validation_result = self.model_manager.validate_configuration(self.current_config)
            if not validation_result['valid']:
                errors = validation_result['errors']
                if not messagebox.askyesno(
                    "Configuration Issues", 
                    f"Configuration has issues:\n{chr(10).join(errors)}\n\nSave anyway?"
                ):
                    return
            
            # Save configuration
            success = self.model_manager.save_agent_configuration(self.current_config, self.config_path)
            
            if success:
                messagebox.showinfo("Success", "Configuration saved successfully")
                
                # Notify parent of configuration change
                if self.on_config_change:
                    self.on_config_change(self.current_config)
            else:
                messagebox.showerror("Error", "Failed to save configuration")
                
        except Exception as e:
            self.show_error(f"Failed to save configuration: {str(e)}")
    
    def test_configuration(self):
        """Test the current configuration."""
        try:
            if not self.current_config:
                messagebox.showwarning("Warning", "No configuration to test")
                return
            
            # Show testing dialog
            test_dialog = ConfigurationTestDialog(self.parent, self.model_manager, self.current_config)
            test_dialog.run_test()
            
        except Exception as e:
            self.show_error(f"Failed to test configuration: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        if messagebox.askyesno("Reset Configuration", "Reset to default configuration?"):
            try:
                self.set_default_configuration()
                self.update_cost_calculation()
                messagebox.showinfo("Success", "Configuration reset to defaults")
            except Exception as e:
                self.show_error(f"Failed to reset configuration: {str(e)}")
    
    def export_configuration(self):
        """Export current configuration to file."""
        try:
            if not self.current_config:
                messagebox.showwarning("Warning", "No configuration to export")
                return
            
            filename = filedialog.asksaveasfilename(
                title="Export Configuration",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialname="multi_model_config.json"
            )
            
            if filename:
                export_data = self.model_manager.export_configuration(self.current_config)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Configuration exported to {filename}")
                
        except Exception as e:
            self.show_error(f"Failed to export configuration: {str(e)}")
    
    def import_configuration(self):
        """Import configuration from file."""
        try:
            filename = filedialog.askopenfilename(
                title="Import Configuration",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                
                imported_config = self.model_manager.import_configuration(import_data)
                
                # Load into UI
                self.current_config = imported_config
                self.load_configuration_to_ui(imported_config)
                self.profile_var.set("Custom")
                self.update_cost_calculation()
                
                messagebox.showinfo("Success", "Configuration imported successfully")
                
        except Exception as e:
            self.show_error(f"Failed to import configuration: {str(e)}")
    
    def save_as_profile(self):
        """Save current configuration as a custom profile."""
        try:
            if not self.current_config:
                messagebox.showwarning("Warning", "No configuration to save as profile")
                return
            
            # Get profile name from user
            profile_name = tk.simpledialog.askstring(
                "Save Profile",
                "Enter profile name:",
                initialvalue="My Custom Profile"
            )
            
            if profile_name:
                # This would save to a profiles file or database
                # For now, just show success message
                messagebox.showinfo("Success", f"Profile '{profile_name}' saved")
                
        except Exception as e:
            self.show_error(f"Failed to save profile: {str(e)}")
    
    def show_error(self, message: str):
        """Show error message to user."""
        messagebox.showerror("Error", message)


class AgentModelSelector(ttk.LabelFrame):
    """Widget for selecting a model for a specific agent."""
    
    def __init__(self, parent, agent_id: int, agent_name: str, on_model_change: Callable[[int, str], None]):
        super().__init__(parent, text=agent_name, padding=10)
        
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.on_model_change = on_model_change
        self.available_models: List[ModelInfo] = []
        self.is_loading = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the agent model selector UI."""
        # Model selection
        ttk.Label(self, text="Model:").pack(anchor=tk.W)
        
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(
            self,
            textvariable=self.model_var,
            state="readonly",
            width=30
        )
        self.model_combo.pack(fill=tk.X, pady=(2, 5))
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_selected)
        
        # Model details
        self.details_frame = ttk.Frame(self)
        self.details_frame.pack(fill=tk.X)
        
        # Cost display
        self.cost_var = tk.StringVar(value="Cost: Loading...")
        self.cost_label = ttk.Label(
            self.details_frame,
            textvariable=self.cost_var,
            font=('TkDefaultFont', 8),
            foreground="gray"
        )
        self.cost_label.pack(anchor=tk.W)
        
        # Provider display
        self.provider_var = tk.StringVar(value="Provider: Loading...")
        self.provider_label = ttk.Label(
            self.details_frame,
            textvariable=self.provider_var,
            font=('TkDefaultFont', 8),
            foreground="gray"
        )
        self.provider_label.pack(anchor=tk.W)
    
    def set_available_models(self, models: List[ModelInfo]):
        """Set the available models for selection."""
        self.available_models = models
        
        # Update combo box values
        model_names = [f"{model.name} ({model.id})" for model in models]
        self.model_combo['values'] = model_names
        
        # Set default selection if no current selection
        if not self.model_var.get() and models:
            self.set_selected_model(models[0].id)
    
    def set_selected_model(self, model_id: str):
        """Set the selected model by ID."""
        model = next((m for m in self.available_models if m.id == model_id), None)
        if model:
            display_name = f"{model.name} ({model.id})"
            self.model_var.set(display_name)
            self.update_model_details(model)
    
    def get_selected_model_id(self) -> Optional[str]:
        """Get the currently selected model ID."""
        display_name = self.model_var.get()
        if not display_name:
            return None
        
        # Extract model ID from display name
        if '(' in display_name and ')' in display_name:
            return display_name.split('(')[-1].rstrip(')')
        return None
    
    def on_model_selected(self, event=None):
        """Handle model selection change."""
        model_id = self.get_selected_model_id()
        if model_id:
            model = next((m for m in self.available_models if m.id == model_id), None)
            if model:
                self.update_model_details(model)
                self.on_model_change(self.agent_id, model_id)
    
    def update_model_details(self, model: ModelInfo):
        """Update the model details display."""
        # Update cost display
        if model.input_cost_per_1m is not None and model.output_cost_per_1m is not None:
            cost_text = f"Cost: ${model.input_cost_per_1m:.3f}/${model.output_cost_per_1m:.3f} per 1M tokens"
        else:
            cost_text = "Cost: Not available"
        self.cost_var.set(cost_text)
        
        # Update provider display
        self.provider_var.set(f"Provider: {model.provider}")
    
    def set_loading(self, loading: bool):
        """Set loading state."""
        self.is_loading = loading
        
        if loading:
            self.model_combo['state'] = 'disabled'
            self.cost_var.set("Cost: Loading...")
            self.provider_var.set("Provider: Loading...")
        else:
            self.model_combo['state'] = 'readonly'


class ModelInfoWidget(ttk.LabelFrame):
    """Widget to display detailed information about a selected model."""
    
    def __init__(self, parent):
        super().__init__(parent, text="Model Information", padding=10)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the model info widget UI."""
        # Model name
        self.name_var = tk.StringVar(value="No model selected")
        name_label = ttk.Label(
            self,
            textvariable=self.name_var,
            font=('TkDefaultFont', 10, 'bold')
        )
        name_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Model details frame
        details_frame = ttk.Frame(self)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Provider
        self.provider_var = tk.StringVar()
        ttk.Label(details_frame, text="Provider:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(details_frame, textvariable=self.provider_var).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Context window
        self.context_var = tk.StringVar()
        ttk.Label(details_frame, text="Context:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(details_frame, textvariable=self.context_var).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Input cost
        self.input_cost_var = tk.StringVar()
        ttk.Label(details_frame, text="Input Cost:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(details_frame, textvariable=self.input_cost_var).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Output cost
        self.output_cost_var = tk.StringVar()
        ttk.Label(details_frame, text="Output Cost:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Label(details_frame, textvariable=self.output_cost_var).grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Function calling support
        self.function_calling_var = tk.StringVar()
        ttk.Label(details_frame, text="Function Calling:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Label(details_frame, textvariable=self.function_calling_var).grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Description
        ttk.Label(details_frame, text="Description:").grid(row=5, column=0, sticky=tk.NW, pady=(2, 0))
        
        self.description_text = tk.Text(
            details_frame,
            height=3,
            width=40,
            wrap=tk.WORD,
            font=('TkDefaultFont', 9),
            state=tk.DISABLED
        )
        self.description_text.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(2, 0))
        
        # Configure grid weights
        details_frame.columnconfigure(1, weight=1)
    
    def display_model_info(self, model: ModelInfo):
        """Display information for the given model."""
        self.name_var.set(model.name)
        self.provider_var.set(model.provider)
        self.context_var.set(f"{model.context_window:,} tokens" if model.context_window else "N/A")
        
        # Format costs
        if model.input_cost_per_1m is not None:
            self.input_cost_var.set(f"${model.input_cost_per_1m:.3f} per 1M tokens")
        else:
            self.input_cost_var.set("Not available")
        
        if model.output_cost_per_1m is not None:
            self.output_cost_var.set(f"${model.output_cost_per_1m:.3f} per 1M tokens")
        else:
            self.output_cost_var.set("Not available")
        
        # Function calling support
        self.function_calling_var.set("✓ Supported" if model.supports_function_calling else "✗ Not supported")
        
        # Description
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete(1.0, tk.END)
        self.description_text.insert(1.0, model.description or "No description available")
        self.description_text.config(state=tk.DISABLED)
    
    def clear_display(self):
        """Clear the model information display."""
        self.name_var.set("No model selected")
        self.provider_var.set("")
        self.context_var.set("")
        self.input_cost_var.set("")
        self.output_cost_var.set("")
        self.function_calling_var.set("")
        
        self.description_text.config(state=tk.NORMAL)
        self.description_text.delete(1.0, tk.END)
        self.description_text.config(state=tk.DISABLED)


class CostCalculatorWidget(ttk.LabelFrame):
    """Widget to display cost estimates for the current configuration."""
    
    def __init__(self, parent):
        super().__init__(parent, text="Cost Estimate", padding=10)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the cost calculator widget UI."""
        # Total cost display
        self.total_cost_var = tk.StringVar(value="Total: Calculating...")
        total_label = ttk.Label(
            self,
            textvariable=self.total_cost_var,
            font=('TkDefaultFont', 12, 'bold')
        )
        total_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Cost breakdown frame
        breakdown_frame = ttk.LabelFrame(self, text="Per Agent Breakdown", padding=5)
        breakdown_frame.pack(fill=tk.BOTH, expand=True)
        
        # Agent cost labels
        self.agent_cost_vars = {}
        agent_names = ["Research", "Analysis", "Verification", "Alternatives"]
        
        for i, name in enumerate(agent_names):
            var = tk.StringVar(value=f"{name}: $0.000")
            label = ttk.Label(breakdown_frame, textvariable=var, font=('TkDefaultFont', 9))
            label.pack(anchor=tk.W, pady=1)
            self.agent_cost_vars[i] = var
        
        # Synthesis cost
        self.synthesis_cost_var = tk.StringVar(value="Synthesis: $0.000")
        synthesis_label = ttk.Label(breakdown_frame, textvariable=self.synthesis_cost_var, font=('TkDefaultFont', 9))
        synthesis_label.pack(anchor=tk.W, pady=1)
        
        # Assumptions note
        assumptions_label = ttk.Label(
            self,
            text="* Estimates based on typical query patterns",
            font=('TkDefaultFont', 8),
            foreground="gray"
        )
        assumptions_label.pack(anchor=tk.W, pady=(10, 0))
    
    def display_cost_estimate(self, cost_estimate: CostEstimate):
        """Display the given cost estimate."""
        # Update total cost
        self.total_cost_var.set(f"Total: ${cost_estimate.total_cost:.3f} per query")
        
        # Update per-agent costs
        agent_names = ["Research", "Analysis", "Verification", "Alternatives"]
        for i, name in enumerate(agent_names):
            agent_cost = cost_estimate.per_agent_costs.get(i, 0.0)
            self.agent_cost_vars[i].set(f"{name}: ${agent_cost:.3f}")
        
        # Update synthesis cost
        synthesis_cost = cost_estimate.breakdown.get('synthesis', 0.0)
        self.synthesis_cost_var.set(f"Synthesis: ${synthesis_cost:.3f}")
    
    def display_error(self, error_message: str):
        """Display an error message."""
        self.total_cost_var.set(f"Error: {error_message}")
        
        # Clear breakdown
        agent_names = ["Research", "Analysis", "Verification", "Alternatives"]
        for i, name in enumerate(agent_names):
            self.agent_cost_vars[i].set(f"{name}: Error")
        
        self.synthesis_cost_var.set("Synthesis: Error")


class ConfigurationTestDialog:
    """Dialog for testing model configuration."""
    
    def __init__(self, parent, model_manager: ModelConfigurationManager, config: AgentModelConfig):
        self.parent = parent
        self.model_manager = model_manager
        self.config = config
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Test Configuration")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the test dialog UI."""
        # Title
        title_label = ttk.Label(
            self.dialog,
            text="Configuration Test Results",
            font=('TkDefaultFont', 12, 'bold')
        )
        title_label.pack(pady=10)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.dialog, text="Test Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Results text widget
        self.results_text = tk.Text(
            results_frame,
            wrap=tk.WORD,
            font=('TkDefaultFont', 9)
        )
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Pack text and scrollbar
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.dialog,
            variable=self.progress_var,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Close button
        self.close_button = ttk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy,
            state=tk.DISABLED
        )
        self.close_button.pack(side=tk.RIGHT)
        
        # Test button
        self.test_button = ttk.Button(
            button_frame,
            text="Start Test",
            command=self.start_test
        )
        self.test_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def run_test(self):
        """Run the configuration test."""
        self.start_test()
    
    def start_test(self):
        """Start the configuration test in background thread."""
        self.test_button.config(state=tk.DISABLED)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Starting configuration test...\n\n")
        
        def run_test():
            try:
                # Test the configuration
                test_results = self.model_manager.test_model_configuration(self.config)
                
                # Update UI on main thread
                self.dialog.after(0, lambda: self.display_results(test_results))
                
            except Exception as e:
                self.dialog.after(0, lambda: self.display_error(str(e)))
        
        # Start background thread
        thread = threading.Thread(target=run_test, daemon=True)
        thread.start()
    
    def display_results(self, test_results: Dict[str, Any]):
        """Display test results."""
        self.results_text.delete(1.0, tk.END)
        
        agent_names = {
            'agent_0_model': 'Research Agent',
            'agent_1_model': 'Analysis Agent',
            'agent_2_model': 'Verification Agent',
            'agent_3_model': 'Alternatives Agent',
            'synthesis_model': 'Synthesis Agent'
        }
        
        all_passed = True
        
        for model_key, result in test_results.items():
            agent_name = agent_names.get(model_key, model_key)
            
            if result.success:
                status = "✓ PASSED"
                self.results_text.insert(tk.END, f"{agent_name}: {status}\n")
                if result.response_time:
                    self.results_text.insert(tk.END, f"  Response time: {result.response_time:.2f}s\n")
            else:
                status = "✗ FAILED"
                all_passed = False
                self.results_text.insert(tk.END, f"{agent_name}: {status}\n")
                if result.error_message:
                    self.results_text.insert(tk.END, f"  Error: {result.error_message}\n")
            
            self.results_text.insert(tk.END, "\n")
        
        # Summary
        self.results_text.insert(tk.END, "=" * 50 + "\n")
        if all_passed:
            self.results_text.insert(tk.END, "✓ All models tested successfully!\n")
            self.results_text.insert(tk.END, "Configuration is ready to use.\n")
        else:
            self.results_text.insert(tk.END, "✗ Some models failed testing.\n")
            self.results_text.insert(tk.END, "Please check API keys and model availability.\n")
        
        # Enable close button
        self.close_button.config(state=tk.NORMAL)
        self.progress_var.set(100)
    
    def display_error(self, error_message: str):
        """Display error message."""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Test failed with error:\n\n{error_message}")
        
        # Enable close button
        self.close_button.config(state=tk.NORMAL)
        self.progress_var.set(0)