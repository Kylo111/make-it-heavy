import time
import threading
import sys
import argparse
from orchestrator import TaskOrchestrator
from agent import UniversalAgent

class OrchestratorCLI:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.orchestrator = TaskOrchestrator(config_path=config_path)
        self.start_time = None
        self.running = False
        
        # Get provider information for display
        try:
            temp_agent = UniversalAgent(config_path=config_path, silent=True)
            provider_info = temp_agent.get_provider_info()
            
            # Create display name based on provider and model
            provider_name = provider_info['provider_name'].upper()
            model_name = provider_info['model']
            
            # Clean up model name for display
            if '/' in model_name:
                model_name = model_name.split('/')[-1]
            
            model_parts = model_name.split('-')
            # Take first 3 parts for cleaner display (e.g., gemini-2.5-flash)
            clean_name = '-'.join(model_parts[:3]) if len(model_parts) >= 3 else model_name
            
            self.model_display = f"{provider_name} {clean_name.upper()} HEAVY"
            self.provider_info = provider_info
            
        except Exception as e:
            # Fallback display name
            self.model_display = "UNIVERSAL AGENT HEAVY"
            self.provider_info = {"provider_type": "unknown", "error": str(e)}
        
    def clear_screen(self):
        """Properly clear the entire screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def format_time(self, seconds):
        """Format seconds into readable time string"""
        if seconds < 60:
            return f"{int(seconds)}S"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}M{secs}S"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}H{minutes}M"
    
    def create_progress_bar(self, status):
        """Create progress visualization based on status"""
        # ANSI color codes
        ORANGE = '\033[38;5;208m'  # Orange color
        RED = '\033[91m'           # Red color
        RESET = '\033[0m'          # Reset color
        
        if status == "QUEUED":
            return "○ " + "·" * 70
        elif status == "INITIALIZING...":
            return f"{ORANGE}◐{RESET} " + "·" * 70
        elif status == "PROCESSING...":
            # Animated processing bar in orange
            dots = f"{ORANGE}:" * 10 + f"{RESET}" + "·" * 60
            return f"{ORANGE}●{RESET} " + dots
        elif status == "COMPLETED":
            return f"{ORANGE}●{RESET} " + f"{ORANGE}:" * 70 + f"{RESET}"
        elif status.startswith("FAILED"):
            return f"{RED}✗{RESET} " + f"{RED}×" * 70 + f"{RESET}"
        else:
            return f"{ORANGE}◐{RESET} " + "·" * 70
    
    def update_display(self):
        """Update the console display with current status"""
        if not self.running:
            return
            
        # Calculate elapsed time
        elapsed = time.time() - self.start_time if self.start_time else 0
        time_str = self.format_time(elapsed)
        
        # Get current progress
        progress = self.orchestrator.get_progress_status()
        
        # Clear screen properly
        self.clear_screen()
        
        # Header with dynamic model name
        print(self.model_display)
        if self.running:
            print(f"● RUNNING • {time_str}")
        else:
            print(f"● COMPLETED • {time_str}")
        print()
        
        # Agent status lines
        for i in range(self.orchestrator.num_agents):
            status = progress.get(i, "QUEUED")
            progress_bar = self.create_progress_bar(status)
            print(f"AGENT {i+1:02d}  {progress_bar}")
        
        print()
        sys.stdout.flush()
    
    def progress_monitor(self):
        """Monitor and update progress display in separate thread"""
        while self.running:
            self.update_display()
            time.sleep(1.0)  # Update every 1 second (reduced flicker)
    
    def run_task(self, user_input):
        """Run orchestrator task with live progress display"""
        self.start_time = time.time()
        self.running = True
        
        # Start progress monitoring in background thread
        progress_thread = threading.Thread(target=self.progress_monitor, daemon=True)
        progress_thread.start()
        
        try:
            # Run the orchestrator
            result = self.orchestrator.orchestrate(user_input)
            
            # Stop progress monitoring
            self.running = False
            
            # Final display update
            self.update_display()
            
            # Show results
            print("=" * 80)
            print("FINAL RESULTS")
            print("=" * 80)
            print()
            print(result)
            print()
            print("=" * 80)
            
            return result
            
        except Exception as e:
            self.running = False
            self.update_display()
            print(f"\nError during orchestration: {str(e)}")
            return None
    
    def interactive_mode(self):
        """Run interactive CLI session"""
        print("Multi-Agent Orchestrator")
        print(f"Configured for {self.orchestrator.num_agents} parallel agents")
        print("Type 'quit', 'exit', or 'bye' to exit")
        print("-" * 50)
        
        try:
            # Display provider information
            if 'error' not in self.provider_info:
                print(f"Provider: {self.provider_info['provider_name']}")
                print(f"Model: {self.provider_info['model_name']}")
                print(f"Base URL: {self.provider_info['base_url']}")
                print(f"Function Calling: {'✓' if self.provider_info['supports_function_calling'] else '✗'}")
                
                # Provider-specific setup notes
                if self.provider_info['provider_type'] == 'deepseek':
                    print("Note: Make sure to set your DeepSeek API key in the configuration file")
                    print("💡 Tip: Use DeepSeek during off-peak hours (16:30-00:30 UTC) for lower costs")
                elif self.provider_info['provider_type'] == 'openrouter':
                    print("Note: Make sure to set your OpenRouter API key in the configuration file")
                else:
                    print(f"Note: Make sure to set your {self.provider_info['provider_type']} API key in the configuration file")
            else:
                print(f"Warning: Could not get provider info: {self.provider_info['error']}")
            
            print("Orchestrator initialized successfully!")
            print("-" * 50)
        except Exception as e:
            print(f"Error initializing orchestrator: {e}")
            print("Make sure you have:")
            print("1. Set your API key in the configuration file")
            print("2. Installed all dependencies with: pip install -r requirements.txt")
            print("3. Used a valid configuration file (try --config config_deepseek.yaml for DeepSeek)")
            return
        
        while True:
            try:
                user_input = input("\nUser: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    print("Please enter a question or command.")
                    continue
                
                print("\nOrchestrator: Starting multi-agent analysis...")
                print()
                
                # Run task with live progress
                result = self.run_task(user_input)
                
                if result is None:
                    print("Task failed. Please try again.")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                print("Please try again or type 'quit' to exit.")

def main():
    """Main entry point for the orchestrator CLI"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Multi-Agent Orchestrator with Multi-Provider Support')
    parser.add_argument('--config', '-c', default='config.yaml', 
                       help='Configuration file path (default: config.yaml)')
    args = parser.parse_args()
    
    cli = OrchestratorCLI(config_path=args.config)
    cli.interactive_mode()

if __name__ == "__main__":
    main()