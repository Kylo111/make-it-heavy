"""
Agent Manager for Make It Heavy GUI application.
Handles integration with UniversalAgent and TaskOrchestrator systems.
"""

import threading
import time
import yaml
import os
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime

# Import existing agent systems
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import UniversalAgent
from orchestrator import TaskOrchestrator
from config_manager import ConfigurationManager
from provider_factory import ProviderClientFactory


@dataclass
class AgentProgress:
    """Progress information for Heavy Mode agents"""
    agent_id: int
    status: str  # "QUEUED", "INITIALIZING...", "PROCESSING...", "COMPLETED", "FAILED"
    progress_bar: str
    result: Optional[str] = None
    execution_time: float = 0.0


class AgentManager:
    """
    Manages integration with UniversalAgent (single mode) and TaskOrchestrator (heavy mode).
    Provides unified interface for GUI to interact with agent systems.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config_manager = ConfigurationManager()
        self.current_mode = "single"
        self.is_running = False
        self.progress_callback = None
        self.completion_callback = None
        
        # Heavy mode components
        self.orchestrator = None
        self.progress_monitor_thread = None
        self.agent_progress = {}
        
        # Load initial configuration
        self.reload_config()
    
    def reload_config(self):
        """Reload configuration from file"""
        try:
            self.config_manager.load_config(self.config_path)
            self.provider_config = self.config_manager.get_provider_config()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            raise
    
    def update_config(self, provider: str, model: str, api_key: str):
        """Update configuration with new provider/model/API key"""
        try:
            # Load existing config
            config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            
            # Update provider selection
            config['provider'] = {'type': provider}
            
            # Update provider-specific configuration
            if provider == "deepseek":
                config['deepseek'] = {
                    'api_key': api_key,
                    'base_url': "https://api.deepseek.com",
                    'model': model
                }
            elif provider == "openrouter":
                config['openrouter'] = {
                    'api_key': api_key,
                    'base_url': "https://openrouter.ai/api/v1",
                    'model': model
                }
            
            # Save configuration
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            # Reload configuration
            self.reload_config()
            
        except Exception as e:
            raise Exception(f"Failed to update configuration: {str(e)}")
    
    def get_available_models(self, provider: str) -> List[str]:
        """Get available models for a provider"""
        providers = {
            "deepseek": ["deepseek-chat", "deepseek-reasoner"],
            "openrouter": [
                "anthropic/claude-3.5-sonnet",
                "openai/gpt-4-turbo",
                "openai/gpt-4",
                "google/gemini-2.0-flash-001",
                "meta-llama/llama-3.1-405b-instruct"
            ]
        }
        return providers.get(provider, [])
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get current provider information"""
        try:
            temp_agent = UniversalAgent(config_path=self.config_path, silent=True)
            return temp_agent.get_provider_info()
        except Exception as e:
            return {
                "provider_type": "unknown",
                "provider_name": "Unknown",
                "model": "unknown",
                "model_name": "Unknown",
                "base_url": "unknown",
                "supports_function_calling": False,
                "error": str(e)
            }
    
    def set_mode(self, mode: str):
        """Set execution mode (single or heavy)"""
        if mode not in ["single", "heavy"]:
            raise ValueError(f"Invalid mode: {mode}. Must be 'single' or 'heavy'")
        self.current_mode = mode
    
    def set_progress_callback(self, callback: Callable[[Dict[int, AgentProgress]], None]):
        """Set callback for progress updates (Heavy Mode)"""
        self.progress_callback = callback
    
    def set_completion_callback(self, callback: Callable[[str], None]):
        """Set callback for task completion"""
        self.completion_callback = callback
    
    def run_single_agent(self, message: str) -> str:
        """Run single agent mode"""
        try:
            self.is_running = True
            
            # Create agent
            agent = UniversalAgent(config_path=self.config_path, silent=True)
            
            # Run agent
            response = agent.run(message)
            
            self.is_running = False
            return response
            
        except Exception as e:
            self.is_running = False
            raise Exception(f"Single agent execution failed: {str(e)}")
    
    def run_heavy_mode(self, message: str) -> str:
        """Run heavy mode with progress tracking"""
        try:
            self.is_running = True
            
            # Create orchestrator
            self.orchestrator = TaskOrchestrator(config_path=self.config_path, silent=True)
            
            # Initialize progress tracking
            self.agent_progress = {}
            for i in range(self.orchestrator.num_agents):
                self.agent_progress[i] = AgentProgress(
                    agent_id=i,
                    status="QUEUED",
                    progress_bar=self._create_progress_bar("QUEUED")
                )
            
            # Start progress monitoring
            if self.progress_callback:
                self.progress_monitor_thread = threading.Thread(
                    target=self._monitor_heavy_mode_progress,
                    daemon=True
                )
                self.progress_monitor_thread.start()
            
            # Run orchestrator
            result = self.orchestrator.orchestrate(message)
            
            # Update final progress
            for i in range(self.orchestrator.num_agents):
                if self.agent_progress[i].status != "FAILED":
                    self.agent_progress[i].status = "COMPLETED"
                    self.agent_progress[i].progress_bar = self._create_progress_bar("COMPLETED")
            
            # Final progress update
            if self.progress_callback:
                self.progress_callback(self.agent_progress.copy())
            
            self.is_running = False
            return result
            
        except Exception as e:
            self.is_running = False
            # Update all agents to failed status
            for i in range(len(self.agent_progress)):
                self.agent_progress[i].status = f"FAILED: {str(e)}"
                self.agent_progress[i].progress_bar = self._create_progress_bar(f"FAILED: {str(e)}")
            
            if self.progress_callback:
                self.progress_callback(self.agent_progress.copy())
            
            raise Exception(f"Heavy mode execution failed: {str(e)}")
    
    def _monitor_heavy_mode_progress(self):
        """Monitor progress for heavy mode execution"""
        while self.is_running and self.orchestrator:
            try:
                # Get progress from orchestrator
                orchestrator_progress = self.orchestrator.get_progress_status()
                
                # Update our progress tracking
                for agent_id, status in orchestrator_progress.items():
                    if agent_id in self.agent_progress:
                        self.agent_progress[agent_id].status = status
                        self.agent_progress[agent_id].progress_bar = self._create_progress_bar(status)
                
                # Call progress callback
                if self.progress_callback:
                    self.progress_callback(self.agent_progress.copy())
                
                time.sleep(1.0)  # Update every second
                
            except Exception as e:
                print(f"Progress monitoring error: {e}")
                break
    
    def _create_progress_bar(self, status: str) -> str:
        """Create progress bar visualization based on status"""
        if status == "QUEUED":
            return "○ " + "·" * 70
        elif status == "INITIALIZING...":
            return "◐ " + "·" * 70
        elif status == "PROCESSING...":
            # Animated processing bar
            dots = ":" * 10 + "·" * 60
            return "● " + dots
        elif status == "COMPLETED":
            return "● " + ":" * 70
        elif status.startswith("FAILED"):
            return "✗ " + "×" * 70
        else:
            return "◐ " + "·" * 70
    
    def run_async(self, message: str, completion_callback: Optional[Callable[[str], None]] = None):
        """Run agent asynchronously in background thread"""
        def run_in_background():
            try:
                if self.current_mode == "single":
                    result = self.run_single_agent(message)
                else:
                    result = self.run_heavy_mode(message)
                
                # Call completion callback (only once)
                callback_to_use = completion_callback or self.completion_callback
                if callback_to_use:
                    callback_to_use(result)
                    
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                callback_to_use = completion_callback or self.completion_callback
                if callback_to_use:
                    callback_to_use(error_msg)
        
        # Start background thread
        thread = threading.Thread(target=run_in_background, daemon=True)
        thread.start()
        return thread
    
    def is_agent_running(self) -> bool:
        """Check if agent is currently running"""
        return self.is_running
    
    def stop_execution(self):
        """Stop current execution (if possible)"""
        self.is_running = False
        # Note: This is a soft stop - actual agent execution may continue
        # until it reaches a natural stopping point
    
    def get_current_mode(self) -> str:
        """Get current execution mode"""
        return self.current_mode
    
    def get_agent_count(self) -> int:
        """Get number of agents for current mode"""
        if self.current_mode == "single":
            return 1
        else:
            try:
                if not self.orchestrator:
                    # Load config to get agent count
                    with open(self.config_path, 'r') as f:
                        config = yaml.safe_load(f)
                    return config.get('orchestrator', {}).get('parallel_agents', 4)
                return self.orchestrator.num_agents
            except:
                return 4  # Default