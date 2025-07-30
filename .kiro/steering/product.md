# Make It Heavy

Make It Heavy is a Python framework that emulates Grok heavy functionality using a multi-agent system. It leverages OpenRouter's API to deliver comprehensive, multi-perspective analysis through intelligent agent orchestration.

## Core Functionality

- **Multi-Agent System**: Deploys 4 specialized agents simultaneously for deep analysis
- **Dynamic Question Generation**: Creates custom research questions tailored to each query
- **Real-time Orchestration**: Provides live visual feedback during multi-agent execution
- **Intelligent Synthesis**: Combines multiple agent perspectives into unified answers

## Usage Modes

1. **Single Agent Mode** (`main.py`): Runs a single agent with full tool access for simpler tasks
2. **Grok Heavy Mode** (`make_it_heavy.py`): Runs 4 parallel agents for comprehensive analysis

## Key Components

- Agent System: Self-contained agent implementation with tool access
- Orchestrator: Manages parallel execution and response synthesis
- Tool System: Auto-discovers and loads tools from the `tools/` directory