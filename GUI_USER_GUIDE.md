# 🖥️ Make It Heavy - GUI User Guide

This comprehensive guide covers all aspects of using the Make It Heavy graphical user interface.

## 🚀 Getting Started

### System Requirements

- **Operating System**: macOS, Windows 10+, or Linux
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB, recommended 8GB+
- **Display**: Minimum 1024x768, recommended 1920x1080+

### Installation

1. **Install GUI dependencies:**
```bash
# Install Python dependencies
uv pip install -r requirements.txt

# Install system dependencies
# macOS
brew install python-tk

# Ubuntu/Debian
sudo apt-get install python3-tk python3-pil python3-pil.imagetk

# Windows (usually included with Python)
# No additional installation needed
```

2. **Launch the GUI:**
```bash
python gui/main_app.py
```

## 🎨 Interface Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ File  Edit  View  Tools  Help                    [- □ ×]    │
├─────────────────────────────────────────────────────────────┤
│ [Chat] [Multi-Agent] [Settings] [Sessions] [Models] [Costs] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    Main Content Area                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Status: Ready | Provider: DeepSeek | Model: deepseek-chat  │
└─────────────────────────────────────────────────────────────┘
```

### Tab Navigation

- **Chat**: Interactive conversations with AI agents
- **Multi-Agent**: Grok Heavy mode with parallel agent orchestration
- **Settings**: Configuration management and API setup
- **Sessions**: Conversation history and session management
- **Models**: Multi-model configuration and comparison
- **Costs**: Usage monitoring and cost analysis

## 💬 Chat Interface

### Basic Chat Features

**Starting a Conversation:**
1. Click the Chat tab
2. Type your message in the input field at the bottom
3. Press Enter or click Send
4. Watch the response stream in real-time

**Message Features:**
- **Syntax Highlighting**: Code blocks are automatically highlighted
- **Copy Messages**: Right-click any message to copy
- **Export Chat**: Save conversations in multiple formats
- **Search History**: Use Cmd/Ctrl+F to search messages

### Advanced Chat Options

**Message Context Menu (Right-click):**
- Copy Message
- Copy Code Block
- Export Message
- Regenerate Response
- Add to Favorites

**Keyboard Shortcuts:**
- `Enter`: Send message
- `Shift+Enter`: New line in message
- `Cmd/Ctrl+L`: Clear chat
- `Cmd/Ctrl+S`: Save conversation
- `Cmd/Ctrl+F`: Search messages

### Response Streaming

The GUI provides real-time response streaming:
- **Typing Indicator**: Shows when AI is thinking
- **Progressive Display**: Messages appear as they're generated
- **Stop Generation**: Click stop button to halt response
- **Token Counter**: Real-time token usage display

## 🤖 Multi-Agent Mode

### Grok Heavy Orchestration

**Starting Multi-Agent Session:**
1. Switch to Multi-Agent tab
2. Enter your complex query
3. Click "Start Grok Heavy Analysis"
4. Monitor progress of all 4 agents

### Visual Progress Tracking

```
Agent 1: Research        [████████████████████] 100%
Agent 2: Analysis        [████████████████████] 100%
Agent 3: Alternatives    [██████████████░░░░░░]  75%
Agent 4: Verification    [████████░░░░░░░░░░░░]  40%

Synthesis: [░░░░░░░░░░░░░░░░░░░░] Waiting...
```

### Agent Status Indicators

- **🟢 Active**: Agent is currently processing
- **🟡 Waiting**: Agent is queued for execution
- **🔵 Complete**: Agent has finished successfully
- **🔴 Error**: Agent encountered an error
- **⏸️ Paused**: Agent execution is paused

### Multi-Agent Controls

**Execution Controls:**
- **Start**: Begin multi-agent analysis
- **Pause**: Temporarily halt all agents
- **Resume**: Continue paused execution
- **Stop**: Terminate all agents
- **Reset**: Clear current session and start over

**Configuration Options:**
- **Agent Count**: Adjust number of parallel agents (2-8)
- **Timeout**: Set maximum execution time per agent
- **Synthesis Mode**: Choose how agent responses are combined
- **Question Generation**: Enable/disable AI question generation

## ⚙️ Settings Panel

### API Configuration

**Provider Setup:**
1. Select your provider (OpenRouter, DeepSeek, etc.)
2. Enter your API key
3. Click "Test Connection" to verify
4. Save configuration

**API Key Management:**
- **Validation**: Real-time key validation
- **Security**: Keys are stored securely
- **Multiple Keys**: Support for multiple provider keys
- **Key Rotation**: Easy key updates and rotation

### Model Selection

**Model Comparison Table:**
```
┌─────────────────┬──────────┬──────────┬─────────────┬──────────┐
│ Model           │ Provider │ Cost/1M  │ Context     │ Speed    │
├─────────────────┼──────────┼──────────┼─────────────┼──────────┤
│ deepseek-chat   │ DeepSeek │ $0.14    │ 64K tokens  │ Fast     │
│ deepseek-reasoner│ DeepSeek │ $0.55    │ 64K tokens  │ Slow     │
│ gpt-4.1-mini    │ OpenRouter│ $0.15    │ 128K tokens │ Medium   │
│ claude-3.5-sonnet│ OpenRouter│ $3.00    │ 200K tokens │ Medium   │
└─────────────────┴──────────┴──────────┴─────────────┴──────────┘
```

**Model Testing:**
- **Benchmark Queries**: Test models with standard queries
- **Performance Metrics**: Compare response quality and speed
- **Cost Analysis**: Real-time cost comparison
- **Recommendations**: AI-powered model suggestions

### Theme Management

**Theme Options:**
- **Auto**: Follow system theme (recommended)
- **Light**: Always use light theme
- **Dark**: Always use dark theme
- **Custom**: Create your own theme

**Accessibility:**
- **High Contrast**: Enhanced contrast for better visibility
- **Large Fonts**: Increased font sizes
- **Color Blind Support**: Alternative color schemes
- **Screen Reader**: Improved screen reader compatibility

### Advanced Settings

**Performance Tuning:**
- **Response Buffer Size**: Adjust streaming buffer
- **Concurrent Requests**: Maximum parallel API calls
- **Cache Settings**: Response caching configuration
- **Memory Management**: GUI memory optimization

**Debug Options:**
- **Verbose Logging**: Enable detailed logs
- **API Request Logging**: Log all API interactions
- **Performance Metrics**: Show timing information
- **Error Reporting**: Enhanced error details

## 📁 Session Management

### Session Organization

**Session Categories:**
- **Work**: Professional and business-related conversations
- **Research**: Academic and research projects
- **Personal**: Personal assistance and casual chats
- **Development**: Programming and technical discussions
- **Creative**: Creative writing and brainstorming

**Session Operations:**
- **Create**: Start new categorized sessions
- **Rename**: Change session names and descriptions
- **Tag**: Add searchable tags to sessions
- **Archive**: Move old sessions to archive
- **Delete**: Permanently remove sessions

### Session Search and Filtering

**Search Options:**
- **Full Text**: Search within conversation content
- **Metadata**: Search by date, category, tags
- **Advanced**: Complex queries with operators
- **Saved Searches**: Store frequently used searches

**Filter Controls:**
```
Date Range: [Last 30 days ▼]
Category:   [All ▼]
Provider:   [All ▼]
Model:      [All ▼]
Tags:       [research, ai, development]
```

### Export and Backup

**Export Formats:**
- **Markdown**: Human-readable format with formatting
- **JSON**: Machine-readable with full metadata
- **TXT**: Plain text for simple sharing
- **PDF**: Formatted document for presentations
- **HTML**: Web-ready format with styling

**Backup Options:**
- **Auto Backup**: Automatic daily backups
- **Manual Backup**: On-demand backup creation
- **Cloud Sync**: Sync with cloud storage services
- **Import**: Restore from backup files

## 🔧 Multi-Model Configuration

### Model Comparison Dashboard

**Performance Metrics:**
```
┌─────────────────────────────────────────────────────────────┐
│                    Model Performance                        │
├─────────────────┬─────────┬─────────┬─────────┬─────────────┤
│ Metric          │ DeepSeek│ GPT-4.1 │ Claude  │ Gemini      │
├─────────────────┼─────────┼─────────┼─────────┼─────────────┤
│ Response Quality│   8.5   │   8.2   │   9.1   │    7.8      │
│ Speed (tokens/s)│   45    │   32    │   28    │    52       │
│ Cost per 1K tok │  $0.14  │  $0.15  │  $3.00  │   $0.12     │
│ Context Window  │  64K    │  128K   │  200K   │   32K       │
│ Function Calling│   Yes   │   Yes   │   Yes   │    Yes      │
└─────────────────┴─────────┴─────────┴─────────┴─────────────┘
```

### Batch Configuration

**Use Case Templates:**
- **Research Heavy**: Optimized for deep analysis and research
- **Cost Conscious**: Balanced performance and cost
- **Speed Focused**: Fastest response times
- **Quality First**: Best possible response quality
- **Development**: Optimized for coding tasks

**Configuration Profiles:**
```yaml
# Research Heavy Profile
primary_model: "deepseek-reasoner"
fallback_model: "deepseek-chat"
max_tokens: 4000
temperature: 0.3
timeout: 600

# Cost Conscious Profile
primary_model: "deepseek-chat"
fallback_model: "gpt-4.1-mini"
max_tokens: 2000
temperature: 0.5
timeout: 300
```

### Model Testing and Benchmarking

**Benchmark Suites:**
- **General Knowledge**: Test factual accuracy
- **Reasoning**: Complex logical problems
- **Coding**: Programming challenges
- **Creative**: Creative writing tasks
- **Analysis**: Document analysis and summarization

**Custom Benchmarks:**
- Create your own test queries
- Compare models side-by-side
- Track performance over time
- Export benchmark results

## 💰 Cost Monitoring

### Real-Time Usage Tracking

**Usage Dashboard:**
```
┌─────────────────────────────────────────────────────────────┐
│                    Today's Usage                            │
├─────────────────┬─────────┬─────────┬─────────┬─────────────┤
│ Provider        │ Requests│ Tokens  │ Cost    │ Avg/Request │
├─────────────────┼─────────┼─────────┼─────────┼─────────────┤
│ DeepSeek        │   45    │ 125.2K  │ $0.18   │   $0.004    │
│ OpenRouter      │   12    │  38.5K  │ $0.32   │   $0.027    │
├─────────────────┼─────────┼─────────┼─────────┼─────────────┤
│ Total           │   57    │ 163.7K  │ $0.50   │   $0.009    │
└─────────────────┴─────────┴─────────┴─────────┴─────────────┘
```

### Cost Analysis and Projections

**Monthly Projections:**
- Based on current usage patterns
- Seasonal adjustments
- Growth trend analysis
- Budget vs. actual tracking

**Cost Optimization Suggestions:**
- **Off-Peak Usage**: Schedule heavy tasks during off-peak hours
- **Model Selection**: Recommend cost-effective models
- **Batch Processing**: Group similar requests
- **Cache Utilization**: Reduce redundant API calls

### Budget Management

**Budget Controls:**
- **Daily Limits**: Set maximum daily spending
- **Monthly Budgets**: Track against monthly budgets
- **Alert Thresholds**: Get notified at spending milestones
- **Auto-Pause**: Automatically pause when limits are reached

**Cost Alerts:**
```
🟡 Warning: 75% of daily budget used ($7.50 of $10.00)
🔴 Alert: Monthly budget exceeded! ($105.23 of $100.00)
🟢 Info: Off-peak hours starting in 2 hours (50% discount)
```

## 🎯 Advanced Features

### Custom Agent Templates

**Template Creation:**
1. Configure agent parameters
2. Set system prompts and instructions
3. Choose tools and capabilities
4. Save as reusable template

**Template Categories:**
- **Research Assistant**: Optimized for research tasks
- **Code Reviewer**: Specialized in code analysis
- **Creative Writer**: Enhanced for creative tasks
- **Data Analyst**: Focused on data interpretation
- **Technical Support**: Troubleshooting and help

### Workflow Automation

**Automated Workflows:**
- **Scheduled Tasks**: Run agents at specific times
- **Trigger-Based**: Execute based on conditions
- **Chain Operations**: Link multiple agent tasks
- **Batch Processing**: Process multiple inputs

**Workflow Examples:**
```yaml
# Daily Research Digest
name: "Daily AI News"
schedule: "0 9 * * *"  # 9 AM daily
steps:
  - search: "latest AI developments"
  - analyze: "summarize key trends"
  - format: "create digest report"
  - save: "daily_digest.md"
```

### Integration Features

**File Integration:**
- **Drag & Drop**: Drop files directly into chat
- **File Analysis**: Automatic content analysis
- **Batch Processing**: Process multiple files
- **Export Results**: Save analysis results

**External Tools:**
- **Web Scraping**: Extract content from URLs
- **API Integration**: Connect to external APIs
- **Database Queries**: Query databases directly
- **Cloud Storage**: Sync with cloud services

## 🔧 Troubleshooting

### Common GUI Issues

**GUI Won't Start:**
```bash
# Check Python and tkinter installation
python -c "import tkinter; print('Tkinter OK')"

# Install missing dependencies
pip install pillow matplotlib pandas numpy

# Launch with debug mode
python gui/main_app.py --debug
```

**Performance Issues:**
- **Memory Usage**: Monitor RAM usage in Activity Monitor/Task Manager
- **Response Lag**: Check network connection and API status
- **UI Freezing**: Reduce concurrent operations
- **Large Sessions**: Archive old conversations

**Theme Problems:**
- **Dark Mode**: Check system theme settings
- **Font Issues**: Verify system fonts are available
- **Color Problems**: Reset to default theme
- **Layout Issues**: Check display scaling settings

### Debug Tools

**Built-in Diagnostics:**
- **Connection Test**: Verify API connectivity
- **Performance Monitor**: Track response times
- **Memory Usage**: Monitor resource consumption
- **Error Logs**: View detailed error information

**Log Files:**
```
~/.make_it_heavy/logs/
├── gui.log          # GUI-specific logs
├── api.log          # API interaction logs
├── error.log        # Error and exception logs
└── performance.log  # Performance metrics
```

## 📚 Tips and Best Practices

### Productivity Tips

**Keyboard Shortcuts:**
- `Cmd/Ctrl+N`: New conversation
- `Cmd/Ctrl+T`: New tab
- `Cmd/Ctrl+W`: Close tab
- `Cmd/Ctrl+S`: Save session
- `Cmd/Ctrl+F`: Search
- `Cmd/Ctrl+,`: Settings
- `F11`: Toggle fullscreen

**Workflow Optimization:**
- **Use Templates**: Create reusable agent configurations
- **Organize Sessions**: Use categories and tags effectively
- **Monitor Costs**: Set budgets and alerts
- **Batch Similar Tasks**: Group related queries
- **Use Off-Peak Hours**: Schedule heavy tasks for cost savings

### Security Best Practices

**API Key Security:**
- **Never Share**: Don't share API keys in screenshots or exports
- **Regular Rotation**: Change keys periodically
- **Secure Storage**: Keys are encrypted in local storage
- **Access Control**: Use separate keys for different purposes

**Data Privacy:**
- **Local Storage**: Conversations stored locally by default
- **Export Control**: Be careful when exporting sensitive data
- **Session Cleanup**: Regularly clean up old sessions
- **Backup Security**: Encrypt backups containing sensitive data

### Performance Optimization

**Resource Management:**
- **Close Unused Tabs**: Reduce memory usage
- **Limit History**: Set reasonable message history limits
- **Cache Management**: Clear cache periodically
- **Background Tasks**: Minimize concurrent operations

**Cost Optimization:**
- **Model Selection**: Choose appropriate models for tasks
- **Token Management**: Monitor token usage patterns
- **Off-Peak Scheduling**: Use cheaper off-peak hours
- **Batch Processing**: Group similar requests

## 🆘 Getting Help

### Support Resources

**Documentation:**
- **User Guide**: This comprehensive guide
- **API Documentation**: Provider-specific API docs
- **Video Tutorials**: Step-by-step video guides
- **FAQ**: Frequently asked questions

**Community Support:**
- **GitHub Issues**: Report bugs and request features
- **Discord Community**: Real-time chat support
- **Reddit Community**: Discussion and tips
- **Stack Overflow**: Technical questions

**Professional Support:**
- **Priority Support**: Faster response times
- **Custom Integration**: Tailored solutions
- **Training Sessions**: Personalized training
- **Consulting Services**: Expert guidance

### Reporting Issues

**Bug Reports:**
1. **Reproduce**: Ensure the issue is reproducible
2. **Collect Info**: Gather system information and logs
3. **Screenshots**: Include relevant screenshots
4. **Steps**: Provide detailed reproduction steps
5. **Submit**: Create GitHub issue with all information

**Feature Requests:**
1. **Search Existing**: Check if feature already requested
2. **Use Case**: Explain why the feature is needed
3. **Details**: Provide specific implementation ideas
4. **Priority**: Indicate importance level
5. **Submit**: Create feature request on GitHub

---

## 🎉 Conclusion

The Make It Heavy GUI provides a powerful, user-friendly interface for interacting with AI agents. Whether you're conducting research, analyzing data, or having creative conversations, the GUI offers the tools and features you need to be productive.

For additional help or questions, please refer to the main README.md or reach out to the community through our support channels.

Happy chatting! 🚀