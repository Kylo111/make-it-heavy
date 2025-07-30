# 🔄 DeepSeek Migration Guide

This guide provides detailed instructions for migrating from OpenRouter to DeepSeek, or setting up a hybrid configuration with both providers.

## 📋 Quick Migration Checklist

- [ ] **Get DeepSeek API Key**: Sign up at [platform.deepseek.com](https://platform.deepseek.com)
- [ ] **Add Credits**: Minimum $5 recommended for testing
- [ ] **Backup Configuration**: `cp config.yaml config_backup.yaml`
- [ ] **Choose Model**: DeepSeek-V3 (general) or DeepSeek-R1 (reasoning)
- [ ] **Update Configuration**: Use provided templates
- [ ] **Test Setup**: Run both single and multi-agent modes
- [ ] **Monitor Costs**: Track your savings

## 🚀 Step-by-Step Migration

### Step 1: DeepSeek Account Setup

1. **Create Account**
   - Visit [platform.deepseek.com](https://platform.deepseek.com)
   - Sign up with email or GitHub
   - Verify your email address

2. **Generate API Key**
   - Go to API Keys section in dashboard
   - Click "Create New Key"
   - Copy and securely store your API key
   - Set appropriate permissions (ensure function calling is enabled)

3. **Add Credits**
   - Navigate to Billing section
   - Add minimum $5 for testing (recommended $20+ for regular use)
   - DeepSeek offers very competitive pricing

### Step 2: Configuration Migration

#### Option A: General Purpose (Recommended)

**Use DeepSeek-V3 for most tasks:**

```bash
# Copy the template
cp config_deepseek.yaml config.yaml

# Edit the configuration
nano config.yaml  # or your preferred editor
```

**Configuration structure:**
```yaml
# Provider selection
provider:
  type: "deepseek"

# DeepSeek API settings
deepseek:
  api_key: "YOUR_DEEPSEEK_API_KEY"  # Replace with your actual key
  base_url: "https://api.deepseek.com"
  model: "deepseek-chat"

# Agent settings (same as before)
agent:
  max_iterations: 10
  system_prompt: |
    You are a helpful AI assistant with access to various tools...

# Orchestrator settings (same as before)
orchestrator:
  parallel_agents: 4
  task_timeout: 300
  question_generation_prompt: |
    You are an orchestrator that needs to create {num_agents} different questions...
  synthesis_prompt: |
    You have {num_responses} different AI agents that analyzed the same query...

# Tool settings (same as before)
search:
  max_results: 5
  user_agent: "Mozilla/5.0 (compatible; Make It Heavy Agent)"
```

#### Option B: Complex Reasoning Tasks

**Use DeepSeek-R1 for advanced reasoning:**

```bash
# Copy the reasoner template
cp config_deepseek_reasoner.yaml config.yaml

# Edit the configuration
nano config.yaml
```

**Key differences:**
```yaml
deepseek:
  model: "deepseek-reasoner"  # Uses DeepSeek-R1 instead of DeepSeek-V3

orchestrator:
  task_timeout: 600  # Longer timeout for reasoning tasks
```

### Step 3: Testing Your Migration

#### Test Single Agent Mode
```bash
# Test basic functionality
uv run main.py

# Example test query
> "What are the latest developments in AI?"
```

#### Test Multi-Agent Mode
```bash
# Test orchestration
uv run make_it_heavy.py

# Example test query
> "Analyze the pros and cons of remote work"
```

#### Verify Tool Integration
```bash
# Test with a query that uses multiple tools
> "Search for information about Python 3.12 features and create a summary file"
```

### Step 4: Performance Validation

#### Response Quality Check
- Compare responses between old and new configurations
- DeepSeek-V3 should match GPT-4.1 Mini quality
- DeepSeek-R1 should provide detailed reasoning steps

#### Speed Comparison
- DeepSeek-V3: Similar speed to GPT-4.1 Mini
- DeepSeek-R1: Slower due to reasoning (similar to o1-preview)

#### Cost Monitoring
- Track token usage in DeepSeek dashboard
- Compare costs with previous OpenRouter usage
- Expected savings: 60-90% depending on model

## 🔧 Advanced Configuration

### Hybrid Setup (Multiple Providers)

Keep multiple configurations for different use cases:

```bash
# Configuration files
config.yaml                    # Current active config
config_openrouter.yaml         # OpenRouter backup
config_deepseek.yaml           # DeepSeek general use
config_deepseek_reasoner.yaml  # DeepSeek reasoning
config_premium.yaml            # Premium models for critical tasks
```

**Usage examples:**
```bash
# Daily tasks with DeepSeek
uv run make_it_heavy.py --config config_deepseek.yaml

# Complex reasoning with DeepSeek-R1
uv run main.py --config config_deepseek_reasoner.yaml

# Critical tasks with premium models
uv run make_it_heavy.py --config config_premium.yaml
```

### Environment-Specific Configuration

**Development Environment:**
```yaml
# config_dev.yaml
provider:
  type: "deepseek"
deepseek:
  model: "deepseek-chat"  # Cost-effective for testing
orchestrator:
  parallel_agents: 2      # Fewer agents for faster iteration
```

**Production Environment:**
```yaml
# config_prod.yaml
provider:
  type: "deepseek"
deepseek:
  model: "deepseek-reasoner"  # Higher quality for production
orchestrator:
  parallel_agents: 4          # Full agent count
  task_timeout: 600           # Longer timeout for reliability
```

## 💰 Cost Optimization Strategies

### Off-Peak Usage

**DeepSeek Off-Peak Hours (Beijing Time):**
- **Start**: 11:00 PM (23:00)
- **End**: 7:00 AM (07:00)
- **Discount**: Up to 50% off

**Time Zone Conversions:**
| Time Zone | Off-Peak Hours |
|-----------|----------------|
| UTC | 3:00 PM - 11:00 PM |
| EST | 10:00 AM - 6:00 PM |
| PST | 7:00 AM - 3:00 PM |
| CET | 4:00 PM - 12:00 AM |
| JST | 12:00 AM - 8:00 AM |

**Optimization Script:**
```python
from datetime import datetime
import pytz

def is_deepseek_off_peak():
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_time = datetime.now(beijing_tz)
    hour = beijing_time.hour
    return hour >= 23 or hour < 7

# Use in your automation
if is_deepseek_off_peak():
    print("Off-peak hours - running batch processing")
    # Run your heavy workloads
```

### Model Selection Strategy

**Cost vs Performance Matrix:**

| Task Type | Recommended Model | Cost Level | Quality Level |
|-----------|------------------|------------|---------------|
| General Q&A | deepseek-chat | Very Low | High |
| Code Review | deepseek-chat | Very Low | High |
| Math Problems | deepseek-reasoner | Low | Very High |
| Complex Analysis | deepseek-reasoner | Low | Very High |
| Creative Writing | deepseek-chat | Very Low | High |
| Research Tasks | deepseek-chat | Very Low | High |

### Batch Processing Optimization

**Efficient Batch Configuration:**
```yaml
# config_batch.yaml
orchestrator:
  parallel_agents: 6        # More agents for batch processing
  task_timeout: 900         # Longer timeout for complex batches
  
deepseek:
  model: "deepseek-chat"    # Cost-effective for high volume
```

## 🛠️ Troubleshooting Migration Issues

### Common Migration Problems

#### Configuration Format Issues
```bash
# Error: Old configuration format detected
# Solution: Update to new universal format

# Before (legacy format - still works)
openrouter:
  api_key: "your_openrouter_key"
  base_url: "https://openrouter.ai/api/v1"
  model: "openai/gpt-4.1-mini"

# After (new universal format - recommended)
provider:
  type: "openrouter"
openrouter:
  api_key: "your_openrouter_key"
  base_url: "https://openrouter.ai/api/v1"
  model: "openai/gpt-4.1-mini"
```

#### API Key Problems
```bash
# Error: Invalid API key
# Solutions:
1. Verify key is correctly copied (no extra spaces)
2. Check key permissions in DeepSeek dashboard
3. Ensure account has sufficient credits
4. Verify key hasn't expired
```

#### Tools Array Issues (Fixed)
```bash
# Error: Invalid 'tools': empty array. Expected an array with minimum length 1
# This was a known issue with DeepSeek API during multi-agent synthesis
# Solution: Already fixed in the latest version
# - System now adds a dummy tool in the agent.run() method when tools array is empty
# - The dummy tool is never called but satisfies DeepSeek API requirements
# - No action needed if using current code
# - Update your code if you encounter this error
```

#### Model Access Issues
```bash
# Error: Model not found
# Solution: Use correct model names
deepseek:
  model: "deepseek-chat"      # ✅ Correct
  model: "deepseek-v3"        # ❌ Incorrect
  model: "deepseek-reasoner"  # ✅ Correct
  model: "deepseek-r1"        # ❌ Incorrect
```

### Performance Issues

#### Slow Response Times
```yaml
# Optimization for speed
orchestrator:
  parallel_agents: 2        # Reduce concurrent load
  task_timeout: 180         # Shorter timeout

deepseek:
  model: "deepseek-chat"    # Faster than reasoner
```

#### Memory Issues
```yaml
# Reduce memory usage
agent:
  max_iterations: 5         # Fewer iterations
  
orchestrator:
  parallel_agents: 2        # Fewer concurrent agents
```

### Rollback Procedures

#### Quick Rollback
```bash
# Restore previous configuration
cp config_backup.yaml config.yaml

# Or use specific provider
uv run main.py --config config_openrouter.yaml
```

#### Gradual Rollback
```bash
# Test specific components
uv run main.py --config config_openrouter.yaml  # Test single agent
uv run make_it_heavy.py --config config_openrouter.yaml  # Test multi-agent
```

## 📊 Migration Success Metrics

### Cost Savings Tracking

**Before Migration (Example):**
- Provider: OpenRouter GPT-4.1 Mini
- Monthly usage: 100 sessions
- Average tokens per session: 50,000
- Monthly cost: ~$3.00

**After Migration:**
- Provider: DeepSeek-V3
- Monthly usage: 100 sessions
- Average tokens per session: 50,000
- Monthly cost: ~$1.00
- **Savings: 67%**

**With Off-Peak Optimization:**
- Monthly cost: ~$0.50
- **Total savings: 83%**

### Quality Metrics

**Response Quality Checklist:**
- [ ] Answers are comprehensive and accurate
- [ ] Tool integration works correctly
- [ ] Multi-agent synthesis maintains quality
- [ ] Function calling operates properly
- [ ] Error handling works as expected

### Performance Metrics

**Speed Benchmarks:**
- Single agent response time: < 30 seconds (typical)
- Multi-agent orchestration: < 2 minutes (typical)
- Tool execution: < 10 seconds per tool call

## 🎯 Next Steps After Migration

### Optimization Opportunities

1. **Fine-tune Configuration**
   - Adjust timeout values based on your use cases
   - Optimize agent count for your workload
   - Customize prompts for better results

2. **Implement Monitoring**
   - Track cost savings over time
   - Monitor response quality
   - Set up alerts for API issues

3. **Explore Advanced Features**
   - Experiment with DeepSeek-R1 for complex tasks
   - Set up automated off-peak processing
   - Create task-specific configurations

### Community and Support

**Getting Help:**
- GitHub Issues: Report problems and get community support
- DeepSeek Documentation: [platform.deepseek.com/api-docs](https://platform.deepseek.com/api-docs)
- Community Discord: Join discussions with other users

**Contributing Back:**
- Share your configuration optimizations
- Report any issues you encounter
- Contribute to documentation improvements

---

**Migration Complete!** 🎉

You should now be running Make It Heavy with DeepSeek integration, enjoying significant cost savings while maintaining high-quality AI assistance.

**Quick Test Command:**
```bash
uv run make_it_heavy.py
> "Test my new DeepSeek integration with a multi-agent analysis"
```