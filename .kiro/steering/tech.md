# Technical Stack

## Core Technologies

- **Language**: Python 3.8+
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (recommended)
- **API Integration**: OpenRouter API via OpenAI client library
- **Configuration**: YAML-based configuration

## Key Dependencies

- `openai`: Client library for OpenRouter API access
- `pyyaml`: YAML parsing for configuration
- `concurrent.futures`: Parallel execution for multi-agent orchestration
- `threading`: Thread management for progress monitoring

## Project Setup

1. Create a virtual environment with uv:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Configure API key in `config.yaml`

## Running the Application

### Single Agent Mode
```bash
uv run main.py
```

### Multi-Agent (Grok Heavy) Mode
```bash
uv run make_it_heavy.py
```

## Configuration

All configuration is managed through `config.yaml`:

- OpenRouter API settings (API key, base URL, model)
- System prompt for agents
- Agent settings (max iterations)
- Orchestrator settings (parallel agents, timeout, aggregation strategy)
- Tool-specific settings

## Development Guidelines

### Adding New Tools

1. Create a new file in `tools/` directory
2. Inherit from `BaseTool`
3. Implement required methods: `name`, `description`, `parameters`, `execute`
4. The tool will be automatically discovered and loaded

### Customizing Models

Update the model in `config.yaml`:
```yaml
openrouter:
  model: "anthropic/claude-3.5-sonnet"  # For complex reasoning
  model: "openai/gpt-4.1-mini"          # For cost efficiency
  model: "google/gemini-2.0-flash-001"  # For speed
```