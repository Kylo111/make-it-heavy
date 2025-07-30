# Advanced Multi-Model Configuration Features Guide

This guide covers the advanced features of the Make It Heavy multi-model configuration system, including configuration testing, cost monitoring, export/import functionality, and comparison tools.

## Table of Contents

1. [Configuration Testing](#configuration-testing)
2. [Cost Monitoring and Budget Alerts](#cost-monitoring-and-budget-alerts)
3. [Configuration Export/Import](#configuration-exportimport)
4. [Configuration Comparison Tools](#configuration-comparison-tools)
5. [Configuration Recommendations](#configuration-recommendations)
6. [Real-time Cost Monitoring](#real-time-cost-monitoring)
7. [Budget Management](#budget-management)
8. [Examples and Use Cases](#examples-and-use-cases)

## Configuration Testing

### Overview
The configuration testing feature allows you to validate that all configured models are accessible and working correctly before running actual multi-agent tasks.

### Usage

```python
from model_config.model_configuration_manager import ModelConfigurationManager
from model_config.data_models import AgentModelConfig
from config_manager import ConfigurationManager

# Load configuration
config_manager = ConfigurationManager()
config_manager.load_config('config.yaml')
manager = ModelConfigurationManager(config_manager)

# Create test configuration
test_config = AgentModelConfig(
    agent_0_model='deepseek-chat',
    agent_1_model='deepseek-reasoner',
    agent_2_model='deepseek-chat',
    agent_3_model='deepseek-reasoner',
    synthesis_model='deepseek-reasoner',
    default_model='deepseek-chat',
    profile_name='test'
)

# Test configuration
results = manager.test_configuration_connectivity(test_config)

# Check results
for agent, result in results.items():
    if result.success:
        print(f"✅ {agent}: {result.model_id} - Response time: {result.response_time:.2f}s")
    else:
        print(f"❌ {agent}: {result.model_id} - Error: {result.error_message}")
```

### What Gets Tested
- API connectivity to each configured model
- Model availability and accessibility
- Basic function calling capability
- Response time measurement

## Cost Monitoring and Budget Alerts

### Overview
Real-time cost monitoring tracks spending during multi-agent execution and provides budget alerts to prevent unexpected costs.

### Configuration

Add budget settings to your `config.yaml`:

```yaml
orchestrator:
  parallel_agents: 4
  task_timeout: 300
  aggregation_strategy: "consensus"
  budget_limit: 0.50  # $0.50 budget limit
```

### Usage

```python
from orchestrator import TaskOrchestrator

# Initialize orchestrator with cost monitoring
orchestrator = TaskOrchestrator('config.yaml')

# Run with automatic cost monitoring
result = orchestrator.orchestrate("Your query here")

# Get cost summary
cost_summary = orchestrator.get_cost_monitoring_summary()
print(f"Total cost: ${cost_summary['total_cost']:.6f}")
print(f"Budget remaining: ${cost_summary['budget_remaining']:.6f}")
```

### Alert Types
- **Warning**: 50% of budget used
- **Critical**: 80% of budget used  
- **Budget Exceeded**: 100% of budget used

### Manual Cost Monitoring

```python
from cost_monitor import CostMonitor

# Create cost monitor with custom alerts
def custom_alert_handler(alert):
    print(f"ALERT: {alert.message}")
    # Send email, log to file, etc.

monitor = CostMonitor(budget_limit=1.0, alert_callback=custom_alert_handler)

# Record costs manually
monitor.record_agent_cost(
    agent_id=0,
    model='deepseek-chat',
    input_tokens=1000,
    output_tokens=500,
    cost=0.001
)

# Get real-time statistics
stats = monitor.get_real_time_stats()
print(f"Current total: ${stats['current_total']:.6f}")
print(f"Budget status: {stats['budget_status']}")
```

## Configuration Export/Import

### Overview
Export and import configurations to share setups between users or backup your configurations.

### Export Configuration

```python
from model_config.model_configuration_manager import ModelConfigurationManager

manager = ModelConfigurationManager()

# Export with cost information and API key sanitization
exported = manager.export_configuration_with_sanitization(
    config=your_config,
    include_costs=True,
    sanitize_keys=True
)

# Save to file
import json
with open('my_config_export.json', 'w') as f:
    json.dump(exported, f, indent=2)
```

### Import Configuration

```python
# Load from file
with open('my_config_export.json', 'r') as f:
    imported_data = json.load(f)

# Import configuration
imported_config = manager.import_configuration(imported_data)

# Save to your config file
manager.save_agent_configuration(imported_config, 'config.yaml')
```

### Export Format

```json
{
  "configuration": {
    "agent_0_model": "deepseek-chat",
    "agent_1_model": "deepseek-reasoner",
    "synthesis_model": "deepseek-reasoner",
    "default_model": "deepseek-chat",
    "profile_name": "custom"
  },
  "cost_estimate": {
    "total_cost": 0.0045,
    "breakdown": {
      "agent_0": 0.001,
      "agent_1": 0.002,
      "synthesis": 0.0015
    },
    "currency": "USD"
  },
  "export_timestamp": "2024-01-15T10:30:00",
  "version": "1.0",
  "note": "API keys have been removed for security. You will need to configure your own API keys.",
  "requires_api_setup": true
}
```

## Configuration Comparison Tools

### Overview
Compare multiple configurations to understand cost differences and make informed decisions.

### Basic Comparison

```python
# Create configurations to compare
config1 = AgentModelConfig(...)  # Budget configuration
config2 = AgentModelConfig(...)  # Premium configuration

# Compare configurations
comparison = manager.compare_configurations(config1, config2)

print(f"Config 1 valid: {comparison['config1_valid']}")
print(f"Config 2 valid: {comparison['config2_valid']}")
print(f"Cost difference: ${comparison['cost_comparison']['cost_difference']:.6f}")
```

### Detailed Comparison Report

```python
configs = [budget_config, balanced_config, premium_config]
config_names = ['Budget', 'Balanced', 'Premium']

report = manager.create_configuration_comparison_report(configs, config_names)

# Print summary
summary = report['summary']
print(f"Total configurations: {summary['total_configurations']}")
print(f"Valid configurations: {summary['valid_configurations']}")
print(f"Best cost: {summary['best_cost_config']['name']} - ${summary['best_cost_config']['total_cost']:.6f}")
print(f"Worst cost: {summary['worst_cost_config']['name']} - ${summary['worst_cost_config']['total_cost']:.6f}")

# Print detailed matrix
for config_data in report['comparison_matrix']:
    print(f"\n{config_data['name']} ({config_data['profile']}):")
    print(f"  Valid: {config_data['valid']}")
    print(f"  Total cost: ${config_data['total_cost']:.6f}")
    print(f"  Models: {config_data['models']}")
```

## Configuration Recommendations

### Overview
Get intelligent recommendations for optimizing your configuration based on cost and performance considerations.

### Usage

```python
recommendations = manager.get_configuration_recommendations(your_config)

print(f"Current cost: ${recommendations['current_cost']:.6f}")
print(f"Recommendations: {recommendations['recommendation_count']}")

for rec in recommendations['recommendations']:
    print(f"\n{rec['type'].title()} for {rec['agent']}:")
    print(f"  Current: {rec['current_model']}")
    print(f"  Suggested: {rec['suggested_model']}")
    print(f"  Description: {rec['description']}")
    
    if 'potential_savings' in rec:
        print(f"  Potential savings: ${rec['potential_savings']:.6f} per 1M tokens")
```

### Recommendation Types
- **Cost Optimization**: Suggests cheaper models for expensive agents
- **Performance Optimization**: Suggests premium models for critical tasks (like synthesis)

## Real-time Cost Monitoring

### Overview
Monitor costs in real-time during execution with live statistics and alerts.

### Advanced Monitoring

```python
from cost_monitor import CostMonitor

# Create monitor with custom alerts
monitor = CostMonitor(budget_limit=2.0)

# Add custom alert thresholds
monitor.add_custom_alert(0.5, "Custom warning at $0.50", "custom_warning")
monitor.add_custom_alert(1.5, "Custom critical at $1.50", "custom_critical")

# Start monitoring
monitor.start_monitoring(check_interval=2.0)  # Check every 2 seconds

# Your code that generates costs...
monitor.record_agent_cost(0, 'model1', 1000, 500, 0.3)
monitor.record_agent_cost(1, 'model2', 1500, 750, 0.4)

# Get live statistics
stats = monitor.get_real_time_stats()
print(f"Current total: ${stats['current_total']:.6f}")
print(f"Recent cost (1min): ${stats['recent_cost_1min']:.6f}")
print(f"Active agents: {stats['active_agents']}")
print(f"Cost rate: ${stats['cost_rate_per_minute']:.6f}/min")

# Export detailed report
report = monitor.export_cost_report(include_detailed_entries=True)

# Stop monitoring
monitor.stop_monitoring()
```

### Context Manager Usage

```python
# Use as context manager for automatic start/stop
with CostMonitor(budget_limit=1.0) as monitor:
    # Your code here
    monitor.record_agent_cost(0, 'model', 1000, 500, 0.1)
    
    # Monitor automatically starts and stops
```

## Budget Management

### Overview
Manage multiple cost monitors and global budgets across different sessions or projects.

### Usage

```python
from cost_monitor import BudgetManager

# Create budget manager
budget_manager = BudgetManager()

# Create monitors for different sessions
session1_monitor = budget_manager.create_monitor('research_session', budget_limit=0.5)
session2_monitor = budget_manager.create_monitor('analysis_session', budget_limit=0.3)

# Set global budget
budget_manager.set_global_budget(1.0)

# Record costs in different sessions
session1_monitor.record_agent_cost(0, 'model1', 1000, 500, 0.1)
session2_monitor.record_agent_cost(0, 'model2', 1500, 750, 0.2)

# Get global summary
global_summary = budget_manager.get_global_summary()
print(f"Total cost across all sessions: ${global_summary['total_cost_all_monitors']:.6f}")
print(f"Global budget remaining: ${global_summary['global_budget_remaining']:.6f}")

# Get individual session summaries
for session_name, summary in global_summary['monitor_summaries'].items():
    print(f"\n{session_name}:")
    print(f"  Cost: ${summary['total_cost']:.6f}")
    print(f"  Budget usage: {summary['budget_usage_percentage']:.1f}%")
```

## Examples and Use Cases

### Example 1: Testing Before Production

```python
# Test configuration before using in production
def validate_production_config():
    manager = ModelConfigurationManager()
    
    # Load production config
    prod_config = manager.load_agent_configuration('production_config.yaml')
    
    # Test connectivity
    test_results = manager.test_configuration_connectivity(prod_config)
    
    # Check if all tests passed
    all_passed = all(result.success for result in test_results.values())
    
    if all_passed:
        print("✅ Production configuration validated successfully")
        return True
    else:
        print("❌ Production configuration validation failed:")
        for agent, result in test_results.items():
            if not result.success:
                print(f"  {agent}: {result.error_message}")
        return False

# Use in deployment pipeline
if validate_production_config():
    # Deploy to production
    pass
else:
    # Fix configuration issues
    pass
```

### Example 2: Cost-Optimized Research Session

```python
def run_cost_optimized_research(queries, budget_limit=1.0):
    """Run research session with strict budget control."""
    
    with CostMonitor(budget_limit=budget_limit) as monitor:
        orchestrator = TaskOrchestrator('config.yaml')
        orchestrator.cost_monitor = monitor
        
        results = []
        
        for i, query in enumerate(queries):
            print(f"\nProcessing query {i+1}/{len(queries)}: {query[:50]}...")
            
            # Check budget before processing
            if monitor.total_cost >= budget_limit * 0.9:
                print("⚠️  Approaching budget limit, stopping early")
                break
            
            try:
                result = orchestrator.orchestrate(query)
                results.append(result)
                
                # Show cost update
                stats = monitor.get_real_time_stats()
                print(f"💰 Cost so far: ${stats['current_total']:.6f}")
                
            except Exception as e:
                print(f"❌ Query failed: {e}")
                continue
        
        # Final cost report
        final_summary = monitor.get_cost_summary()
        print(f"\n📊 Final Report:")
        print(f"Total cost: ${final_summary['total_cost']:.6f}")
        print(f"Budget usage: {final_summary['budget_usage_percentage']:.1f}%")
        print(f"Queries processed: {len(results)}/{len(queries)}")
        
        return results

# Usage
research_queries = [
    "What are the latest developments in AI?",
    "How does quantum computing work?",
    "What are the benefits of renewable energy?"
]

results = run_cost_optimized_research(research_queries, budget_limit=0.50)
```

### Example 3: Configuration Optimization Workflow

```python
def optimize_configuration():
    """Find the best configuration for your use case."""
    
    manager = ModelConfigurationManager()
    
    # Get predefined profiles
    profiles = manager.get_predefined_profiles()
    
    print("Available profiles:")
    for profile in profiles:
        print(f"  {profile.name}: {profile.description}")
    
    # Create comparison report
    configs = [profile.config for profile in profiles]
    names = [profile.name for profile in profiles]
    
    report = manager.create_configuration_comparison_report(configs, names)
    
    # Show comparison
    print("\nConfiguration Comparison:")
    for config_data in report['comparison_matrix']:
        print(f"\n{config_data['name']}:")
        print(f"  Cost per query: ${config_data['total_cost']:.6f}")
        print(f"  Valid: {config_data['valid']}")
    
    # Get recommendations for best cost config
    best_config = report['summary']['best_cost_config']
    if best_config:
        best_config_obj = next(
            profile.config for profile in profiles 
            if profile.name == best_config['name']
        )
        
        recommendations = manager.get_configuration_recommendations(best_config_obj)
        
        print(f"\nRecommendations for {best_config['name']} configuration:")
        for rec in recommendations['recommendations']:
            print(f"  {rec['description']}")
    
    return profiles

# Usage
optimized_profiles = optimize_configuration()
```

## Best Practices

### 1. Always Test Configurations
- Test configurations before production use
- Validate after making changes
- Monitor test response times

### 2. Set Appropriate Budgets
- Start with conservative budget limits
- Monitor actual usage patterns
- Adjust based on requirements

### 3. Use Cost Monitoring
- Enable real-time monitoring for expensive operations
- Set up custom alerts for your use case
- Export cost reports for analysis

### 4. Regular Configuration Reviews
- Compare configurations periodically
- Check for new model availability
- Optimize based on usage patterns

### 5. Backup and Share Configurations
- Export successful configurations
- Share optimized setups with team
- Version control configuration files

## Troubleshooting

### Common Issues

1. **Configuration Test Failures**
   - Check API keys and connectivity
   - Verify model availability
   - Check rate limits

2. **Cost Monitoring Not Working**
   - Ensure budget_limit is set in config
   - Check cost monitor initialization
   - Verify model cost information availability

3. **Export/Import Issues**
   - Validate JSON format
   - Check configuration compatibility
   - Ensure required fields are present

4. **High Costs**
   - Review model selection
   - Check token usage patterns
   - Consider cheaper alternatives for non-critical agents

### Getting Help

- Check logs for detailed error messages
- Use test functionality to isolate issues
- Review configuration validation results
- Monitor cost patterns for optimization opportunities