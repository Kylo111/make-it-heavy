# Project Structure

## Core Files

- `main.py`: Entry point for single agent mode
- `make_it_heavy.py`: Entry point for multi-agent (Grok heavy) mode
- `agent.py`: Core agent implementation with tool integration
- `orchestrator.py`: Multi-agent orchestration logic
- `config.yaml`: Configuration file for all settings
- `README.md`: Project documentation

## Directory Structure

```
make-it-heavy/
├── main.py                 # Single agent CLI
├── make_it_heavy.py        # Multi-agent orchestrator CLI  
├── agent.py                # Core agent implementation
├── orchestrator.py         # Multi-agent orchestration logic
├── config.yaml             # Configuration file
├── requirements.txt        # Python dependencies
├── README.md               # Documentation
└── tools/                  # Tool system
    ├── __init__.py         # Auto-discovery system
    ├── base_tool.py        # Tool base class
    ├── search_tool.py      # Web search
    ├── calculator_tool.py  # Math calculations  
    ├── read_file_tool.py   # File reading
    ├── write_file_tool.py  # File writing
    └── task_done_tool.py   # Task completion
```

## Architecture Patterns

### Agent System (`agent.py`)

- `OpenRouterAgent` class handles:
  - Configuration loading
  - Tool discovery and mapping
  - LLM API calls
  - Tool call execution
  - Agentic loop implementation

### Orchestrator System (`orchestrator.py`)

- `TaskOrchestrator` class manages:
  - Task decomposition into subtasks
  - Parallel agent execution
  - Progress tracking
  - Result aggregation

### CLI Interface (`make_it_heavy.py`)

- `OrchestratorCLI` class provides:
  - Interactive command-line interface
  - Real-time progress visualization
  - Result display

### Tool System (`tools/`)

- Each tool inherits from `BaseTool` and implements:
  - `name`: Tool identifier
  - `description`: Tool purpose
  - `parameters`: JSON schema for arguments
  - `execute`: Implementation logic

## Code Organization Principles

1. **Modularity**: Each component has a single responsibility
2. **Configuration-driven**: Settings in `config.yaml` control behavior
3. **Dynamic discovery**: Tools are automatically loaded from `tools/` directory
4. **Error handling**: Graceful fallbacks at all levels
5. **Thread safety**: Proper locking for shared resources