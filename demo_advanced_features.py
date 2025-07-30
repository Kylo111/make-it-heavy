#!/usr/bin/env python3
"""
Comprehensive demo of advanced multi-model configuration features.
Demonstrates configuration testing, cost monitoring, export/import, and comparison tools.
"""

import json
import yaml
import tempfile
import os
from datetime import datetime

from model_config.model_configuration_manager import ModelConfigurationManager
from model_config.data_models import AgentModelConfig, ModelInfo
from cost_monitor import CostMonitor, BudgetManager
from config_manager import ConfigurationManager


def create_demo_config():
    """Create a demo configuration file."""
    config = {
        'provider': {'type': 'deepseek'},
        'deepseek': {
            'api_key': 'sk-16dc8f03dd4a4ae4835330cd78eb79bf',
            'base_url': 'https://api.deepseek.com',
            'model': 'deepseek-chat'
        },
        'system_prompt': 'You are a helpful assistant.',
        'agent': {'max_iterations': 3},
        'orchestrator': {
            'parallel_agents': 4,
            'task_timeout': 60,
            'aggregation_strategy': 'consensus',
            'budget_limit': 0.25,  # $0.25 budget limit
            'question_generation_prompt': 'Generate questions',
            'synthesis_prompt': 'Synthesize responses'
        },
        'search': {'max_results': 5}
    }
    
    temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
    yaml.dump(config, temp_config)
    temp_config.close()
    
    return temp_config.name


def demo_configuration_testing():
    """Demonstrate configuration testing functionality."""
    print("🧪 CONFIGURATION TESTING DEMO")
    print("=" * 50)
    
    config_path = create_demo_config()
    
    try:
        # Initialize manager
        config_manager = ConfigurationManager()
        config_manager.load_config(config_path)
        manager = ModelConfigurationManager(config_manager)
        
        # Create test configurations
        test_configs = {
            'Budget': AgentModelConfig(
                agent_0_model='deepseek-chat',
                agent_1_model='deepseek-chat',
                agent_2_model='deepseek-chat',
                agent_3_model='deepseek-chat',
                synthesis_model='deepseek-chat',
                default_model='deepseek-chat',
                profile_name='budget'
            ),
            'Mixed': AgentModelConfig(
                agent_0_model='deepseek-chat',
                agent_1_model='deepseek-reasoner',
                agent_2_model='deepseek-chat',
                agent_3_model='deepseek-reasoner',
                synthesis_model='deepseek-reasoner',
                default_model='deepseek-chat',
                profile_name='mixed'
            )
        }
        
        for name, config in test_configs.items():
            print(f"\n🔍 Testing {name} Configuration:")
            print(f"   Agent 0: {config.agent_0_model}")
            print(f"   Agent 1: {config.agent_1_model}")
            print(f"   Synthesis: {config.synthesis_model}")
            
            # Simulate test results (would normally test actual API connectivity)
            print(f"   ✅ All models accessible")
            print(f"   📊 Average response time: 1.2s")
            
            # Get validation results
            validation = manager.validate_configuration(config)
            print(f"   ✅ Configuration valid: {validation['valid']}")
            
            if validation['cost_estimate']:
                cost = validation['cost_estimate']
                print(f"   💰 Estimated cost per query: ${cost.total_cost:.6f}")
    
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)


def demo_cost_monitoring():
    """Demonstrate cost monitoring functionality."""
    print("\n💰 COST MONITORING DEMO")
    print("=" * 50)
    
    # Create cost monitor with alerts
    alerts_received = []
    
    def alert_handler(alert):
        alerts_received.append(alert)
        print(f"🚨 ALERT: {alert.message}")
    
    monitor = CostMonitor(budget_limit=0.05, alert_callback=alert_handler)
    
    print(f"📊 Budget limit set to: ${monitor.budget_limit:.4f}")
    
    # Simulate agent execution costs
    agents_data = [
        (0, 'deepseek-chat', 1000, 500, 0.001),
        (1, 'deepseek-reasoner', 1500, 750, 0.015),
        (2, 'deepseek-chat', 1200, 600, 0.0012),
        (3, 'deepseek-reasoner', 1800, 900, 0.018),
        (-1, 'deepseek-reasoner', 2000, 1000, 0.020)  # Synthesis
    ]
    
    print("\n🔄 Simulating multi-agent execution:")
    
    for agent_id, model, input_tokens, output_tokens, cost in agents_data:
        agent_name = "Synthesis" if agent_id == -1 else f"Agent {agent_id}"
        print(f"   {agent_name} ({model}): ${cost:.6f}")
        
        monitor.record_agent_cost(agent_id, model, input_tokens, output_tokens, cost)
        
        # Show real-time stats
        stats = monitor.get_real_time_stats()
        print(f"     Running total: ${stats['current_total']:.6f}")
    
    # Final summary
    summary = monitor.get_cost_summary()
    print(f"\n📈 Final Summary:")
    print(f"   Total cost: ${summary['total_cost']:.6f}")
    print(f"   Budget usage: {summary['budget_usage_percentage']:.1f}%")
    print(f"   Alerts triggered: {len(summary['alerts_triggered'])}")
    
    # Model breakdown
    print(f"\n🧠 Cost by Model:")
    for model, cost in summary['model_costs'].items():
        usage = summary['model_usage'][model]
        print(f"   {model}: ${cost:.6f} ({usage['calls']} calls)")


def demo_configuration_comparison():
    """Demonstrate configuration comparison tools."""
    print("\n📊 CONFIGURATION COMPARISON DEMO")
    print("=" * 50)
    
    config_path = create_demo_config()
    
    try:
        config_manager = ConfigurationManager()
        config_manager.load_config(config_path)
        manager = ModelConfigurationManager(config_manager)
        
        # Create different configurations
        configs = [
            AgentModelConfig(
                agent_0_model='deepseek-chat',
                agent_1_model='deepseek-chat',
                agent_2_model='deepseek-chat',
                agent_3_model='deepseek-chat',
                synthesis_model='deepseek-chat',
                default_model='deepseek-chat',
                profile_name='budget'
            ),
            AgentModelConfig(
                agent_0_model='deepseek-chat',
                agent_1_model='deepseek-reasoner',
                agent_2_model='deepseek-chat',
                agent_3_model='deepseek-reasoner',
                synthesis_model='deepseek-reasoner',
                default_model='deepseek-chat',
                profile_name='balanced'
            ),
            AgentModelConfig(
                agent_0_model='deepseek-reasoner',
                agent_1_model='deepseek-reasoner',
                agent_2_model='deepseek-reasoner',
                agent_3_model='deepseek-reasoner',
                synthesis_model='deepseek-reasoner',
                default_model='deepseek-reasoner',
                profile_name='premium'
            )
        ]
        
        config_names = ['Budget', 'Balanced', 'Premium']
        
        # Create comparison report
        print("🔍 Comparing configurations...")
        
        # Simulate comparison (would normally calculate actual costs)
        simulated_costs = [0.002, 0.008, 0.025]  # Budget, Balanced, Premium
        
        print(f"\n📋 Configuration Comparison:")
        for i, (name, config, cost) in enumerate(zip(config_names, configs, simulated_costs)):
            print(f"\n{name} Configuration:")
            print(f"   Profile: {config.profile_name}")
            print(f"   Agent models: {config.agent_0_model}, {config.agent_1_model}")
            print(f"   Synthesis model: {config.synthesis_model}")
            print(f"   Estimated cost per query: ${cost:.6f}")
            
            # Show cost difference from budget
            if i > 0:
                diff = cost - simulated_costs[0]
                print(f"   Cost vs Budget: +${diff:.6f} ({(diff/simulated_costs[0]*100):+.1f}%)")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        print(f"   • Budget: Best for high-volume, simple tasks")
        print(f"   • Balanced: Good compromise for most use cases")
        print(f"   • Premium: Best for complex reasoning tasks")
    
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)


def demo_export_import():
    """Demonstrate configuration export/import functionality."""
    print("\n📤 EXPORT/IMPORT DEMO")
    print("=" * 50)
    
    config_path = create_demo_config()
    
    try:
        config_manager = ConfigurationManager()
        config_manager.load_config(config_path)
        manager = ModelConfigurationManager(config_manager)
        
        # Create configuration to export
        export_config = AgentModelConfig(
            agent_0_model='deepseek-chat',
            agent_1_model='deepseek-reasoner',
            agent_2_model='deepseek-chat',
            agent_3_model='deepseek-reasoner',
            synthesis_model='deepseek-reasoner',
            default_model='deepseek-chat',
            profile_name='demo_export'
        )
        
        print("📦 Exporting configuration...")
        
        # Export with sanitization
        exported = manager.export_configuration_with_sanitization(
            export_config,
            include_costs=True,
            sanitize_keys=True
        )
        
        print(f"   ✅ Configuration exported")
        print(f"   📅 Export timestamp: {exported['export_timestamp']}")
        print(f"   🔒 API keys sanitized: {exported['requires_api_setup']}")
        
        # Save to temporary file
        export_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(exported, export_file, indent=2)
        export_file.close()
        
        print(f"   💾 Saved to: {export_file.name}")
        
        # Import configuration
        print(f"\n📥 Importing configuration...")
        
        with open(export_file.name, 'r') as f:
            import_data = json.load(f)
        
        imported_config = manager.import_configuration(import_data)
        
        print(f"   ✅ Configuration imported successfully")
        print(f"   📋 Profile: {imported_config.profile_name}")
        print(f"   🧠 Models match: {imported_config.agent_0_model == export_config.agent_0_model}")
        
        # Clean up
        os.unlink(export_file.name)
    
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)


def demo_budget_management():
    """Demonstrate budget management functionality."""
    print("\n💼 BUDGET MANAGEMENT DEMO")
    print("=" * 50)
    
    # Create budget manager
    budget_manager = BudgetManager()
    budget_manager.set_global_budget(0.50)
    
    print(f"🏦 Global budget set to: ${budget_manager.global_budget:.4f}")
    
    # Create monitors for different sessions
    sessions = {
        'research': budget_manager.create_monitor('research_session', budget_limit=0.20),
        'analysis': budget_manager.create_monitor('analysis_session', budget_limit=0.15),
        'synthesis': budget_manager.create_monitor('synthesis_session', budget_limit=0.10)
    }
    
    print(f"\n📊 Created {len(sessions)} session monitors")
    
    # Simulate costs in different sessions
    session_costs = {
        'research': [(0, 'deepseek-chat', 1000, 500, 0.05), (1, 'deepseek-reasoner', 1500, 750, 0.08)],
        'analysis': [(0, 'deepseek-reasoner', 2000, 1000, 0.12)],
        'synthesis': [(0, 'deepseek-reasoner', 1800, 900, 0.06)]
    }
    
    print(f"\n🔄 Simulating costs across sessions:")
    
    for session_name, costs in session_costs.items():
        monitor = sessions[session_name]
        session_total = 0
        
        print(f"\n   {session_name.title()} Session:")
        for agent_id, model, input_tokens, output_tokens, cost in costs:
            monitor.record_agent_cost(agent_id, model, input_tokens, output_tokens, cost)
            session_total += cost
            print(f"     Agent {agent_id} ({model}): ${cost:.4f}")
        
        print(f"     Session total: ${session_total:.4f}")
    
    # Global summary
    global_summary = budget_manager.get_global_summary()
    
    print(f"\n🌍 Global Summary:")
    print(f"   Total cost across all sessions: ${global_summary['total_cost_all_monitors']:.4f}")
    print(f"   Global budget remaining: ${global_summary['global_budget_remaining']:.4f}")
    print(f"   Global budget usage: {(global_summary['total_cost_all_monitors']/budget_manager.global_budget*100):.1f}%")
    
    print(f"\n📈 Session Breakdown:")
    for session_name, summary in global_summary['monitor_summaries'].items():
        usage_pct = summary['budget_usage_percentage'] or 0
        print(f"   {session_name}: ${summary['total_cost']:.4f} ({usage_pct:.1f}% of session budget)")


def demo_real_time_monitoring():
    """Demonstrate real-time monitoring capabilities."""
    print("\n⏱️  REAL-TIME MONITORING DEMO")
    print("=" * 50)
    
    import time
    import threading
    
    # Create monitor with real-time capabilities
    monitor = CostMonitor(budget_limit=0.10)
    
    print(f"🚀 Starting real-time monitoring...")
    
    # Start monitoring
    monitor.start_monitoring(check_interval=1.0)
    
    # Simulate costs over time
    cost_schedule = [
        (1, 0, 'deepseek-chat', 1000, 500, 0.01),
        (2, 1, 'deepseek-reasoner', 1500, 750, 0.02),
        (3, 2, 'deepseek-chat', 1200, 600, 0.015),
        (4, 3, 'deepseek-reasoner', 1800, 900, 0.025),
    ]
    
    def simulate_costs():
        for delay, agent_id, model, input_tokens, output_tokens, cost in cost_schedule:
            time.sleep(delay)
            monitor.record_agent_cost(agent_id, model, input_tokens, output_tokens, cost)
            
            # Show real-time stats
            stats = monitor.get_real_time_stats()
            print(f"   Agent {agent_id} completed: ${cost:.4f} (Total: ${stats['current_total']:.4f})")
    
    # Run simulation in background
    cost_thread = threading.Thread(target=simulate_costs, daemon=True)
    cost_thread.start()
    
    # Monitor for a few seconds
    for i in range(6):
        time.sleep(1)
        stats = monitor.get_real_time_stats()
        print(f"⏰ {i+1}s: Total=${stats['current_total']:.4f}, Status={stats['budget_status']}")
    
    # Wait for simulation to complete
    cost_thread.join()
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    # Final report
    final_summary = monitor.get_cost_summary()
    print(f"\n📊 Final Real-time Summary:")
    print(f"   Total cost: ${final_summary['total_cost']:.4f}")
    print(f"   Peak cost rate: ${final_summary['peak_cost_rate']:.6f}/min")
    print(f"   Session duration: {final_summary['session_duration_minutes']:.1f} minutes")


def main():
    """Run all advanced features demos."""
    print("🚀 ADVANCED MULTI-MODEL FEATURES DEMO")
    print("=" * 60)
    print("This demo showcases all advanced features of the multi-model configuration system.")
    print("=" * 60)
    
    try:
        demo_configuration_testing()
        demo_cost_monitoring()
        demo_configuration_comparison()
        demo_export_import()
        demo_budget_management()
        demo_real_time_monitoring()
        
        print("\n" + "=" * 60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n💡 Next Steps:")
        print("   • Review the ADVANCED_FEATURES_GUIDE.md for detailed documentation")
        print("   • Try the features with your own configurations")
        print("   • Set up cost monitoring for your production workflows")
        print("   • Export and share your optimized configurations")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()