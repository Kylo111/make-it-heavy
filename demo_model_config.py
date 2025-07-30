#!/usr/bin/env python3
"""
Demo script for the multi-model configuration system.
Shows how to use the backend services to manage model configurations.
"""

import sys
from model_config import ModelConfigurationManager
from model_config.data_models import AgentModelConfig
from config_manager import ConfigurationManager


def main():
    """Demo the multi-model configuration system."""
    print("🤖 Multi-Model Configuration System Demo")
    print("=" * 50)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigurationManager()
        config_manager.load_config("config.yaml")
        
        # Initialize model configuration manager
        model_manager = ModelConfigurationManager(config_manager)
        
        print("\n1. Getting available models...")
        try:
            available_models = model_manager.get_available_models()
            print(f"   Found {len(available_models)} models with function calling support:")
            
            for model in available_models[:5]:  # Show first 5
                cost_info = ""
                if model.input_cost_per_1m and model.output_cost_per_1m:
                    cost_info = f" (${model.input_cost_per_1m:.3f}/${model.output_cost_per_1m:.3f} per 1M tokens)"
                print(f"   - {model.name} ({model.id}){cost_info}")
            
            if len(available_models) > 5:
                print(f"   ... and {len(available_models) - 5} more models")
                
        except Exception as e:
            print(f"   ⚠️  Could not fetch models: {e}")
            print("   Using mock models for demo...")
            
            # Use mock models for demo
            from model_config.data_models import ModelInfo
            available_models = [
                ModelInfo(
                    id="deepseek-chat",
                    name="DeepSeek Chat",
                    provider="deepseek",
                    supports_function_calling=True,
                    context_window=64000,
                    input_cost_per_1m=0.27,
                    output_cost_per_1m=1.10,
                    description="DeepSeek chat model"
                ),
                ModelInfo(
                    id="deepseek-reasoner",
                    name="DeepSeek Reasoner",
                    provider="deepseek",
                    supports_function_calling=True,
                    context_window=64000,
                    input_cost_per_1m=0.55,
                    output_cost_per_1m=2.19,
                    description="DeepSeek reasoning model"
                )
            ]
            
            for model in available_models:
                cost_info = f" (${model.input_cost_per_1m:.3f}/${model.output_cost_per_1m:.3f} per 1M tokens)"
                print(f"   - {model.name} ({model.id}){cost_info}")
        
        if not available_models:
            print("   ❌ No models available. Please check your configuration.")
            return
        
        print("\n2. Getting predefined profiles...")
        try:
            # Mock the get_available_models for profiles
            original_method = model_manager.get_available_models
            model_manager.get_available_models = lambda: available_models
            
            profiles = model_manager.get_predefined_profiles()
            
            for profile in profiles:
                print(f"   - {profile.name}: {profile.description}")
                
            # Restore original method
            model_manager.get_available_models = original_method
            
        except Exception as e:
            print(f"   ⚠️  Could not generate profiles: {e}")
        
        print("\n3. Creating a custom configuration...")
        
        # Use first available model as default
        default_model = available_models[0].id
        
        # Create a mixed configuration if we have multiple models
        if len(available_models) >= 2:
            config = AgentModelConfig(
                agent_0_model=available_models[0].id,  # Research - use first model
                agent_1_model=available_models[1].id,  # Analysis - use second model
                agent_2_model=available_models[0].id,  # Verification - use first model
                agent_3_model=available_models[1].id,  # Alternatives - use second model
                synthesis_model=available_models[1].id,  # Synthesis - use second model
                default_model=default_model,
                profile_name="demo_mixed"
            )
            print(f"   Created mixed configuration:")
            print(f"   - Research Agent: {config.agent_0_model}")
            print(f"   - Analysis Agent: {config.agent_1_model}")
            print(f"   - Verification Agent: {config.agent_2_model}")
            print(f"   - Alternatives Agent: {config.agent_3_model}")
            print(f"   - Synthesis: {config.synthesis_model}")
        else:
            config = AgentModelConfig(
                agent_0_model=default_model,
                agent_1_model=default_model,
                agent_2_model=default_model,
                agent_3_model=default_model,
                synthesis_model=default_model,
                default_model=default_model,
                profile_name="demo_single"
            )
            print(f"   Created single-model configuration using: {default_model}")
        
        print("\n4. Validating configuration...")
        try:
            # Mock the get_available_models for validation
            original_method = model_manager.get_available_models
            model_manager.get_available_models = lambda: available_models
            
            validation_result = model_manager.validate_configuration(config)
            
            if validation_result['valid']:
                print("   ✅ Configuration is valid!")
            else:
                print("   ❌ Configuration has errors:")
                for error in validation_result['errors']:
                    print(f"      - {error}")
                
                if validation_result['suggestions']:
                    print("   💡 Suggestions:")
                    for key, suggestion in validation_result['suggestions'].items():
                        print(f"      - {key}: {suggestion}")
            
            # Restore original method
            model_manager.get_available_models = original_method
            
        except Exception as e:
            print(f"   ⚠️  Validation failed: {e}")
        
        print("\n5. Calculating cost estimate...")
        try:
            # Mock the get_available_models for cost calculation
            original_method = model_manager.get_available_models
            model_manager.get_available_models = lambda: available_models
            
            cost_estimate = model_manager.calculate_configuration_cost(config)
            
            print(f"   💰 Estimated cost per query: ${cost_estimate.total_cost:.4f}")
            print(f"   📊 Token usage: {cost_estimate.total_input_tokens:,} input, {cost_estimate.total_output_tokens:,} output")
            
            if cost_estimate.breakdown:
                print("   📋 Cost breakdown:")
                for component, cost in cost_estimate.breakdown.items():
                    print(f"      - {component}: ${cost:.4f}")
            
            # Restore original method
            model_manager.get_available_models = original_method
            
        except Exception as e:
            print(f"   ⚠️  Cost calculation failed: {e}")
        
        print("\n6. Testing configuration save/load...")
        try:
            # Save configuration
            success = model_manager.save_agent_configuration(config, "demo_config.yaml")
            if success:
                print("   ✅ Configuration saved to demo_config.yaml")
                
                # Load it back
                loaded_config = model_manager.load_agent_configuration("demo_config.yaml")
                if loaded_config:
                    print("   ✅ Configuration loaded successfully")
                    print(f"   📄 Profile: {loaded_config.profile_name}")
                else:
                    print("   ❌ Failed to load configuration")
            else:
                print("   ❌ Failed to save configuration")
                
        except Exception as e:
            print(f"   ⚠️  Save/load failed: {e}")
        
        print("\n7. Testing configuration export/import...")
        try:
            # Mock validation for export/import
            original_validate = model_manager.validate_configuration
            model_manager.validate_configuration = lambda cfg: {'valid': True, 'errors': []}
            
            # Export configuration
            export_data = model_manager.export_configuration(config, include_costs=False)
            print("   ✅ Configuration exported")
            
            # Import it back
            imported_config = model_manager.import_configuration(export_data)
            print("   ✅ Configuration imported successfully")
            print(f"   📄 Imported profile: {imported_config.profile_name}")
            
            # Restore original method
            model_manager.validate_configuration = original_validate
            
        except Exception as e:
            print(f"   ⚠️  Export/import failed: {e}")
        
        print("\n✨ Demo completed successfully!")
        print("\nThe multi-model configuration system provides:")
        print("  • Automatic model discovery from providers")
        print("  • Function calling compatibility filtering")
        print("  • Cost calculation and estimation")
        print("  • Configuration validation and suggestions")
        print("  • Predefined profiles (Budget, Balanced, Premium)")
        print("  • Configuration save/load and export/import")
        print("  • Integration with existing ConfigurationManager")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())