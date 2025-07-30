# Design Document

## Overview

Interfejs graficzny dla Make It Heavy będzie zbudowany jako aplikacja desktopowa w Pythonie wykorzystująca bibliotekę Tkinter dla GUI. Aplikacja będzie działać jako wrapper dla istniejących modułów (main.py, make_it_heavy.py) i zapewni nowoczesny, intuicyjny interfejs podobny do aplikacji chat.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GUI Application                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Main Window   │  │  Config Manager │  │ Chat Window │ │
│  │   (Settings)    │  │   (API Keys)    │  │ (Dialogue)  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Backend Integration                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ UniversalAgent  │  │ TaskOrchestrator│  │ Config YAML │ │
│  │   (main.py)     │  │(make_it_heavy.py)│  │   Manager   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

1. **GUI Layer** (Tkinter-based)
   - MainApplication: Główne okno aplikacji
   - ChatInterface: Interfejs konwersacji
   - SettingsPanel: Panel konfiguracji
   - ProgressDisplay: Wyświetlanie postępu dla Heavy Mode

2. **Integration Layer**
   - AgentManager: Wrapper dla UniversalAgent i TaskOrchestrator
   - ConfigManager: Zarządzanie konfiguracją YAML
   - ModelProvider: Pobieranie list modeli od dostawców

3. **Backend Layer** (Istniejące moduły)
   - UniversalAgent (agent.py)
   - TaskOrchestrator (orchestrator.py)
   - Configuration system (config.yaml)

## Components and Interfaces

### 1. MainApplication Class

**Responsibilities:**
- Inicjalizacja głównego okna aplikacji
- Zarządzanie layoutem i nawigacją
- Koordynacja między komponentami

**Key Methods:**
```python
class MainApplication:
    def __init__(self)
    def setup_ui(self)
    def switch_provider(self, provider: str)
    def switch_mode(self, mode: str)
    def load_models(self, provider: str)
```

### 2. ChatInterface Class

**Responsibilities:**
- Wyświetlanie konwersacji w stylu chat
- Obsługa input użytkownika
- Wyświetlanie odpowiedzi agentów
- Progress tracking dla Heavy Mode

**Key Methods:**
```python
class ChatInterface:
    def __init__(self, parent)
    def add_message(self, sender: str, message: str)
    def send_message(self, message: str)
    def show_progress(self, progress_data: dict)
    def clear_chat(self)
```

### 3. SettingsPanel Class

**Responsibilities:**
- Konfiguracja kluczy API
- Wybór dostawcy i modelu
- Wybór trybu pracy (Single/Heavy)
- Zapisywanie ustawień

**Key Methods:**
```python
class SettingsPanel:
    def __init__(self, parent)
    def save_api_key(self, provider: str, key: str)
    def load_models(self, provider: str) -> List[str]
    def validate_api_key(self, provider: str, key: str) -> bool
    def update_config(self, config_data: dict)
```

### 4. AgentManager Class

**Responsibilities:**
- Integracja z UniversalAgent i TaskOrchestrator
- Zarządzanie wykonaniem zadań
- Callback dla progress updates

**Key Methods:**
```python
class AgentManager:
    def __init__(self, config_path: str)
    def run_single_agent(self, message: str, callback=None) -> str
    def run_heavy_mode(self, message: str, progress_callback=None) -> str
    def get_available_models(self, provider: str) -> List[str]
    def update_config(self, provider: str, model: str, api_key: str)
```

## Data Models

### Configuration Model
```python
@dataclass
class AppConfig:
    provider: str  # "deepseek" or "openrouter"
    model: str
    api_keys: Dict[str, str]  # provider -> api_key
    mode: str  # "single" or "heavy"
    theme: str  # "light" or "dark"
```

### Chat Message Model
```python
@dataclass
class ChatMessage:
    sender: str  # "user" or "agent"
    content: str
    timestamp: datetime
    message_type: str  # "text", "progress", "error"
```

### Progress Model (Heavy Mode)
```python
@dataclass
class AgentProgress:
    agent_id: int
    status: str  # "QUEUED", "PROCESSING...", "COMPLETED", "FAILED"
    progress_bar: str
    result: Optional[str] = None
```

## Error Handling

### API Key Validation
- Walidacja kluczy API przy zapisywaniu
- Wyświetlanie komunikatów o błędach
- Fallback do domyślnych ustawień

### Network Errors
- Timeout handling dla API calls
- Retry mechanism z exponential backoff
- User-friendly error messages

### Configuration Errors
- Walidacja plików YAML
- Backup configuration
- Recovery mechanisms

## Testing Strategy

### Unit Tests
- Testowanie każdego komponentu GUI osobno
- Mock integration z backend modules
- Testowanie error handling scenarios

### Integration Tests
- Testowanie komunikacji GUI ↔ Backend
- Testowanie flow dla różnych trybów
- Testowanie konfiguracji i zapisywania ustawień

### UI Tests
- Testowanie responsywności interfejsu
- Testowanie dark/light mode
- Testowanie na różnych rozdzielczościach macOS

### Manual Testing
- Testowanie user experience
- Testowanie na różnych wersjach macOS
- Performance testing z Heavy Mode

## Implementation Approach

### Phase 1: Core GUI Structure
- Stworzenie podstawowej struktury okna
- Implementacja ChatInterface
- Podstawowa integracja z UniversalAgent

### Phase 2: Configuration Management
- SettingsPanel z API key management
- Provider/model selection
- Configuration persistence

### Phase 3: Heavy Mode Integration
- Progress display dla TaskOrchestrator
- Real-time updates
- Multi-agent visualization

### Phase 4: Polish & UX
- Dark mode support
- Animations i transitions
- Error handling i user feedback

## Technology Stack

### GUI Framework
- **Tkinter**: Wbudowana biblioteka Python, natywna dla macOS
- **tkinter.ttk**: Themed widgets dla nowoczesnego wyglądu
- **Pillow**: Obsługa ikon i obrazów

### Integration
- **PyYAML**: Zarządzanie konfiguracją (już w projekcie)
- **threading**: Asynchroniczne wykonanie zadań
- **queue**: Thread-safe komunikacja

### Optional Enhancements
- **ttkthemes**: Dodatkowe motywy dla lepszego wyglądu
- **tkinter-tooltip**: Tooltips dla lepszego UX

## File Structure

```
gui/
├── __init__.py
├── main_app.py          # MainApplication class
├── chat_interface.py    # ChatInterface class  
├── settings_panel.py    # SettingsPanel class
├── agent_manager.py     # AgentManager class
├── models.py           # Data models
├── utils.py            # Utility functions
└── assets/             # Icons, images
    ├── icons/
    └── themes/
```

## Deployment Considerations

### macOS Compatibility
- Testowanie na macOS Intel
- Native look and feel
- Proper app bundling z py2app

### Distribution
- Standalone executable
- Minimal dependencies
- Easy installation process