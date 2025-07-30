import argparse
from agent import UniversalAgent

def main():
    """Main entry point for the Universal agent"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Universal AI Agent with Multi-Provider Support')
    parser.add_argument('--config', '-c', default='config.yaml', 
                       help='Configuration file path (default: config.yaml)')
    args = parser.parse_args()
    
    print("Universal AI Agent with Multi-Provider Support")
    print("Type 'quit', 'exit', or 'bye' to exit")
    print("-" * 50)
    
    try:
        agent = UniversalAgent(config_path=args.config)
        
        # Get provider information
        provider_info = agent.get_provider_info()
        
        print("Agent initialized successfully!")
        print(f"Provider: {provider_info['provider_name']}")
        print(f"Model: {provider_info['model_name']}")
        print(f"Base URL: {provider_info['base_url']}")
        print(f"Function Calling: {'✓' if provider_info['supports_function_calling'] else '✗'}")
        
        # Provider-specific setup notes
        if provider_info['provider_type'] == 'deepseek':
            print("Note: Make sure to set your DeepSeek API key in the configuration file")
            print("💡 Tip: Use DeepSeek during off-peak hours (16:30-00:30 UTC) for lower costs")
        elif provider_info['provider_type'] == 'openrouter':
            print("Note: Make sure to set your OpenRouter API key in the configuration file")
        else:
            print(f"Note: Make sure to set your {provider_info['provider_type']} API key in the configuration file")
        
        print("-" * 50)
    except Exception as e:
        print(f"Error initializing agent: {e}")
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
            
            print("Agent: Thinking...")
            response = agent.run(user_input)
            print(f"Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()