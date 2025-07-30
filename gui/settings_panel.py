"""
Settings panel for Make It Heavy GUI application.
Handles API key management, provider selection, and model configuration.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import yaml
import os
import sys
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_manager import ConfigurationManager, ConfigurationError, ProviderConfig
from provider_factory import ProviderClientFactory, ProviderError


@dataclass
class AppConfig:
    """Application configuration data model"""
    provider: str
    model: str
    api_keys: Dict[str, str]
    mode: str = "single"
    theme: str = "light"


class SettingsPanel:
    """Settings panel for API key management and provider configuration"""
    
    def __init__(self, parent, config_path: str = "config.yaml", on_config_change: Optional[Callable] = None):
        self.parent = parent
        self.config_path = config_path
        self.on_config_change = on_config_change
        self.config_manager = ConfigurationManager()
        
        # Available providers and their models
        self.providers = {
            "deepseek": {
                "name": "DeepSeek",
                "base_url": "https://api.deepseek.com",
                "models": ["deepseek-chat", "deepseek-reasoner"]
            },
            "openrouter": {
                "name": "OpenRouter", 
                "base_url": "https://openrouter.ai/api/v1",
                "models": [
                    "agentica-org/deepcoder-14b-preview",
                    "agentica-org/deepcoder-14b-preview:free",
                    "ai21/jamba-1.6-large",
                    "ai21/jamba-1.6-mini",
                    "aion-labs/aion-1.0",
                    "aion-labs/aion-1.0-mini",
                    "aion-labs/aion-rp-llama-3.1-8b",
                    "alfredpros/codellama-7b-instruct-solidity",
                    "alpindale/goliath-120b",
                    "amazon/nova-lite-v1",
                    "amazon/nova-micro-v1",
                    "amazon/nova-pro-v1",
                    "anthracite-org/magnum-v2-72b",
                    "anthracite-org/magnum-v4-72b",
                    "anthropic/claude-3-haiku",
                    "anthropic/claude-3-haiku:beta",
                    "anthropic/claude-3-opus",
                    "anthropic/claude-3-opus:beta",
                    "anthropic/claude-3-sonnet",
                    "anthropic/claude-3.5-haiku",
                    "anthropic/claude-3.5-haiku-20241022",
                    "anthropic/claude-3.5-haiku:beta",
                    "anthropic/claude-3.5-sonnet",
                    "anthropic/claude-3.5-sonnet-20240620",
                    "anthropic/claude-3.5-sonnet-20240620:beta",
                    "anthropic/claude-3.5-sonnet:beta",
                    "anthropic/claude-3.7-sonnet",
                    "anthropic/claude-3.7-sonnet:beta",
                    "anthropic/claude-3.7-sonnet:thinking",
                    "anthropic/claude-opus-4",
                    "anthropic/claude-sonnet-4",
                    "arcee-ai/coder-large",
                    "arcee-ai/maestro-reasoning",
                    "arcee-ai/spotlight",
                    "arcee-ai/virtuoso-large",
                    "arliai/qwq-32b-arliai-rpr-v1",
                    "arliai/qwq-32b-arliai-rpr-v1:free",
                    "baidu/ernie-4.5-300b-a47b",
                    "bytedance/ui-tars-1.5-7b",
                    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
                    "cognitivecomputations/dolphin-mixtral-8x22b",
                    "cognitivecomputations/dolphin3.0-mistral-24b:free",
                    "cognitivecomputations/dolphin3.0-r1-mistral-24b",
                    "cognitivecomputations/dolphin3.0-r1-mistral-24b:free",
                    "cohere/command",
                    "cohere/command-a",
                    "cohere/command-r",
                    "cohere/command-r-03-2024",
                    "cohere/command-r-08-2024",
                    "cohere/command-r-plus",
                    "cohere/command-r-plus-04-2024",
                    "cohere/command-r-plus-08-2024",
                    "cohere/command-r7b-12-2024",
                    "deepseek/deepseek-chat",
                    "deepseek/deepseek-chat-v3-0324",
                    "deepseek/deepseek-chat-v3-0324:free",
                    "deepseek/deepseek-prover-v2",
                    "deepseek/deepseek-r1",
                    "deepseek/deepseek-r1-0528",
                    "deepseek/deepseek-r1-0528-qwen3-8b",
                    "deepseek/deepseek-r1-0528-qwen3-8b:free",
                    "deepseek/deepseek-r1-0528:free",
                    "deepseek/deepseek-r1-distill-llama-70b",
                    "deepseek/deepseek-r1-distill-llama-70b:free",
                    "deepseek/deepseek-r1-distill-llama-8b",
                    "deepseek/deepseek-r1-distill-qwen-1.5b",
                    "deepseek/deepseek-r1-distill-qwen-14b",
                    "deepseek/deepseek-r1-distill-qwen-14b:free",
                    "deepseek/deepseek-r1-distill-qwen-32b",
                    "deepseek/deepseek-r1-distill-qwen-7b",
                    "deepseek/deepseek-r1:free",
                    "deepseek/deepseek-v3-base",
                    "eleutherai/llemma_7b",
                    "eva-unit-01/eva-qwen-2.5-72b",
                    "featherless/qwerky-72b:free",
                    "google/gemini-2.0-flash-001",
                    "google/gemini-2.0-flash-exp:free",
                    "google/gemini-2.0-flash-lite-001",
                    "google/gemini-2.5-flash",
                    "google/gemini-2.5-flash-lite",
                    "google/gemini-2.5-flash-lite-preview-06-17",
                    "google/gemini-2.5-pro",
                    "google/gemini-2.5-pro-exp-03-25",
                    "google/gemini-2.5-pro-preview",
                    "google/gemini-2.5-pro-preview-05-06",
                    "google/gemini-flash-1.5",
                    "google/gemini-flash-1.5-8b",
                    "google/gemini-pro-1.5",
                    "google/gemma-2-27b-it",
                    "google/gemma-2-9b-it",
                    "google/gemma-2-9b-it:free",
                    "google/gemma-3-12b-it",
                    "google/gemma-3-12b-it:free",
                    "google/gemma-3-27b-it",
                    "google/gemma-3-27b-it:free",
                    "google/gemma-3-4b-it",
                    "google/gemma-3-4b-it:free",
                    "google/gemma-3n-e2b-it:free",
                    "google/gemma-3n-e4b-it",
                    "google/gemma-3n-e4b-it:free",
                    "gryphe/mythomax-l2-13b",
                    "inception/mercury",
                    "inception/mercury-coder",
                    "infermatic/mn-inferor-12b",
                    "inflection/inflection-3-pi",
                    "inflection/inflection-3-productivity",
                    "liquid/lfm-3b",
                    "liquid/lfm-40b",
                    "liquid/lfm-7b",
                    "mancer/weaver",
                    "meta-llama/llama-3-70b-instruct",
                    "meta-llama/llama-3-8b-instruct",
                    "meta-llama/llama-3.1-405b",
                    "meta-llama/llama-3.1-405b-instruct",
                    "meta-llama/llama-3.1-405b-instruct:free",
                    "meta-llama/llama-3.1-70b-instruct",
                    "meta-llama/llama-3.1-8b-instruct",
                    "meta-llama/llama-3.2-11b-vision-instruct",
                    "meta-llama/llama-3.2-11b-vision-instruct:free",
                    "meta-llama/llama-3.2-1b-instruct",
                    "meta-llama/llama-3.2-3b-instruct",
                    "meta-llama/llama-3.2-3b-instruct:free",
                    "meta-llama/llama-3.2-90b-vision-instruct",
                    "meta-llama/llama-3.3-70b-instruct",
                    "meta-llama/llama-3.3-70b-instruct:free",
                    "meta-llama/llama-4-maverick",
                    "meta-llama/llama-4-scout",
                    "meta-llama/llama-guard-2-8b",
                    "meta-llama/llama-guard-3-8b",
                    "meta-llama/llama-guard-4-12b",
                    "microsoft/mai-ds-r1",
                    "microsoft/mai-ds-r1:free",
                    "microsoft/phi-3-medium-128k-instruct",
                    "microsoft/phi-3-mini-128k-instruct",
                    "microsoft/phi-3.5-mini-128k-instruct",
                    "microsoft/phi-4",
                    "microsoft/phi-4-multimodal-instruct",
                    "microsoft/phi-4-reasoning-plus",
                    "microsoft/wizardlm-2-8x22b",
                    "minimax/minimax-01",
                    "minimax/minimax-m1",
                    "mistralai/codestral-2501",
                    "mistralai/devstral-medium",
                    "mistralai/devstral-small",
                    "mistralai/devstral-small-2505",
                    "mistralai/devstral-small-2505:free",
                    "mistralai/magistral-medium-2506",
                    "mistralai/magistral-medium-2506:thinking",
                    "mistralai/magistral-small-2506",
                    "mistralai/ministral-3b",
                    "mistralai/ministral-8b",
                    "mistralai/mistral-7b-instruct",
                    "mistralai/mistral-7b-instruct-v0.1",
                    "mistralai/mistral-7b-instruct-v0.2",
                    "mistralai/mistral-7b-instruct-v0.3",
                    "mistralai/mistral-7b-instruct:free",
                    "mistralai/mistral-large",
                    "mistralai/mistral-large-2407",
                    "mistralai/mistral-large-2411",
                    "mistralai/mistral-medium-3",
                    "mistralai/mistral-nemo",
                    "mistralai/mistral-nemo:free",
                    "mistralai/mistral-saba",
                    "mistralai/mistral-small",
                    "mistralai/mistral-small-24b-instruct-2501",
                    "mistralai/mistral-small-24b-instruct-2501:free",
                    "mistralai/mistral-small-3.1-24b-instruct",
                    "mistralai/mistral-small-3.1-24b-instruct:free",
                    "mistralai/mistral-small-3.2-24b-instruct",
                    "mistralai/mistral-small-3.2-24b-instruct:free",
                    "mistralai/mistral-tiny",
                    "mistralai/mixtral-8x22b-instruct",
                    "mistralai/mixtral-8x7b-instruct",
                    "mistralai/pixtral-12b",
                    "mistralai/pixtral-large-2411",
                    "moonshotai/kimi-dev-72b:free",
                    "moonshotai/kimi-k2",
                    "moonshotai/kimi-k2:free",
                    "moonshotai/kimi-vl-a3b-thinking",
                    "moonshotai/kimi-vl-a3b-thinking:free",
                    "morph/morph-v2",
                    "morph/morph-v3-fast",
                    "morph/morph-v3-large",
                    "neversleep/llama-3-lumimaid-70b",
                    "neversleep/llama-3.1-lumimaid-8b",
                    "neversleep/noromaid-20b",
                    "nothingiisreal/mn-celeste-12b",
                    "nousresearch/deephermes-3-llama-3-8b-preview:free",
                    "nousresearch/deephermes-3-mistral-24b-preview",
                    "nousresearch/hermes-2-pro-llama-3-8b",
                    "nousresearch/hermes-3-llama-3.1-405b",
                    "nousresearch/hermes-3-llama-3.1-70b",
                    "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
                    "nvidia/llama-3.1-nemotron-70b-instruct",
                    "nvidia/llama-3.1-nemotron-ultra-253b-v1",
                    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
                    "nvidia/llama-3.3-nemotron-super-49b-v1",
                    "openai/chatgpt-4o-latest",
                    "openai/codex-mini",
                    "openai/gpt-3.5-turbo",
                    "openai/gpt-3.5-turbo-0613",
                    "openai/gpt-3.5-turbo-16k",
                    "openai/gpt-3.5-turbo-instruct",
                    "openai/gpt-4",
                    "openai/gpt-4-0314",
                    "openai/gpt-4-1106-preview",
                    "openai/gpt-4-turbo",
                    "openai/gpt-4-turbo-preview",
                    "openai/gpt-4.1",
                    "openai/gpt-4.1-mini",
                    "openai/gpt-4.1-nano",
                    "openai/gpt-4o",
                    "openai/gpt-4o-2024-05-13",
                    "openai/gpt-4o-2024-08-06",
                    "openai/gpt-4o-2024-11-20",
                    "openai/gpt-4o-mini",
                    "openai/gpt-4o-mini-2024-07-18",
                    "openai/gpt-4o-mini-search-preview",
                    "openai/gpt-4o-search-preview",
                    "openai/gpt-4o:extended",
                    "openai/o1",
                    "openai/o1-mini",
                    "openai/o1-mini-2024-09-12",
                    "openai/o1-preview",
                    "openai/o1-preview-2024-09-12",
                    "openai/o1-pro",
                    "openai/o3",
                    "openai/o3-mini",
                    "openai/o3-mini-high",
                    "openai/o3-pro",
                    "openai/o4-mini",
                    "openai/o4-mini-high",
                    "opengvlab/internvl3-14b",
                    "openrouter/auto",
                    "perplexity/r1-1776",
                    "perplexity/sonar",
                    "perplexity/sonar-deep-research",
                    "perplexity/sonar-pro",
                    "perplexity/sonar-reasoning",
                    "perplexity/sonar-reasoning-pro",
                    "pygmalionai/mythalion-13b",
                    "qwen/qwen-2-72b-instruct",
                    "qwen/qwen-2.5-72b-instruct",
                    "qwen/qwen-2.5-72b-instruct:free",
                    "qwen/qwen-2.5-7b-instruct",
                    "qwen/qwen-2.5-coder-32b-instruct",
                    "qwen/qwen-2.5-coder-32b-instruct:free",
                    "qwen/qwen-2.5-vl-7b-instruct",
                    "qwen/qwen-max",
                    "qwen/qwen-plus",
                    "qwen/qwen-turbo",
                    "qwen/qwen-vl-max",
                    "qwen/qwen-vl-plus",
                    "qwen/qwen2.5-vl-32b-instruct",
                    "qwen/qwen2.5-vl-32b-instruct:free",
                    "qwen/qwen2.5-vl-72b-instruct",
                    "qwen/qwen2.5-vl-72b-instruct:free",
                    "qwen/qwen3-14b",
                    "qwen/qwen3-14b:free",
                    "qwen/qwen3-235b-a22b",
                    "qwen/qwen3-235b-a22b-2507",
                    "qwen/qwen3-235b-a22b-2507:free",
                    "qwen/qwen3-235b-a22b-thinking-2507",
                    "qwen/qwen3-235b-a22b:free",
                    "qwen/qwen3-30b-a3b",
                    "qwen/qwen3-30b-a3b:free",
                    "qwen/qwen3-32b",
                    "qwen/qwen3-4b:free",
                    "qwen/qwen3-8b",
                    "qwen/qwen3-8b:free",
                    "qwen/qwen3-coder",
                    "qwen/qwen3-coder:free",
                    "qwen/qwq-32b",
                    "qwen/qwq-32b-preview",
                    "qwen/qwq-32b:free",
                    "raifle/sorcererlm-8x22b",
                    "rekaai/reka-flash-3",
                    "rekaai/reka-flash-3:free",
                    "sao10k/fimbulvetr-11b-v2",
                    "sao10k/l3-euryale-70b",
                    "sao10k/l3-lunaris-8b",
                    "sao10k/l3.1-euryale-70b",
                    "sao10k/l3.3-euryale-70b",
                    "sarvamai/sarvam-m",
                    "sarvamai/sarvam-m:free",
                    "scb10x/llama3.1-typhoon2-70b-instruct",
                    "shisa-ai/shisa-v2-llama3.3-70b",
                    "shisa-ai/shisa-v2-llama3.3-70b:free",
                    "sophosympatheia/midnight-rose-70b",
                    "switchpoint/router",
                    "tencent/hunyuan-a13b-instruct",
                    "tencent/hunyuan-a13b-instruct:free",
                    "thedrummer/anubis-70b-v1.1",
                    "thedrummer/anubis-pro-105b-v1",
                    "thedrummer/rocinante-12b",
                    "thedrummer/skyfall-36b-v2",
                    "thedrummer/unslopnemo-12b",
                    "thedrummer/valkyrie-49b-v1",
                    "thudm/glm-4-32b",
                    "thudm/glm-4-32b:free",
                    "thudm/glm-4.1v-9b-thinking",
                    "thudm/glm-z1-32b",
                    "thudm/glm-z1-32b:free",
                    "tngtech/deepseek-r1t-chimera:free",
                    "tngtech/deepseek-r1t2-chimera",
                    "tngtech/deepseek-r1t2-chimera:free",
                    "undi95/remm-slerp-l2-13b",
                    "undi95/toppy-m-7b",
                    "x-ai/grok-2-1212",
                    "x-ai/grok-2-vision-1212",
                    "x-ai/grok-3",
                    "x-ai/grok-3-beta",
                    "x-ai/grok-3-mini",
                    "x-ai/grok-3-mini-beta",
                    "x-ai/grok-4",
                    "x-ai/grok-vision-beta",
                    "z-ai/glm-4-32b",
                    "z-ai/glm-4.5",
                    "z-ai/glm-4.5-air"
                ]
            }
        }
        
        # Current configuration
        self.current_config = self.load_current_config()
        
        # UI components
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Set up the settings panel UI"""
        # Create main settings frame
        self.settings_frame = ttk.LabelFrame(self.parent, text="Configuration", padding=15)
        self.settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Provider selection section
        self.setup_provider_section()
        
        # API key management section
        self.setup_api_key_section()
        
        # Model selection section
        self.setup_model_section()
        
        # Mode selection section
        self.setup_mode_section()
        
        # Action buttons
        self.setup_action_buttons()
        
    def setup_provider_section(self):
        """Set up provider selection UI"""
        provider_frame = ttk.LabelFrame(self.settings_frame, text="AI Provider", padding=10)
        provider_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Provider selection
        ttk.Label(provider_frame, text="Select Provider:").pack(anchor=tk.W)
        
        self.provider_var = tk.StringVar()
        self.provider_combo = ttk.Combobox(
            provider_frame,
            textvariable=self.provider_var,
            values=[f"{key} ({info['name']})" for key, info in self.providers.items()],
            state="readonly",
            width=40
        )
        self.provider_combo.pack(fill=tk.X, pady=(5, 0))
        self.provider_combo.bind('<<ComboboxSelected>>', self.on_provider_change)
        
    def setup_api_key_section(self):
        """Set up API key management UI"""
        api_frame = ttk.LabelFrame(self.settings_frame, text="API Keys", padding=10)
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        # DeepSeek API key
        deepseek_frame = ttk.Frame(api_frame)
        deepseek_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(deepseek_frame, text="DeepSeek API Key:").pack(anchor=tk.W)
        self.deepseek_key_var = tk.StringVar()
        self.deepseek_key_entry = ttk.Entry(
            deepseek_frame,
            textvariable=self.deepseek_key_var,
            show="*",
            width=50
        )
        self.deepseek_key_entry.pack(fill=tk.X, pady=(2, 0))
        
        # OpenRouter API key
        openrouter_frame = ttk.Frame(api_frame)
        openrouter_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(openrouter_frame, text="OpenRouter API Key:").pack(anchor=tk.W)
        self.openrouter_key_var = tk.StringVar()
        self.openrouter_key_entry = ttk.Entry(
            openrouter_frame,
            textvariable=self.openrouter_key_var,
            show="*",
            width=50
        )
        self.openrouter_key_entry.pack(fill=tk.X, pady=(2, 0))
        
        # Validate button
        validate_frame = ttk.Frame(api_frame)
        validate_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.validate_button = ttk.Button(
            validate_frame,
            text="Validate API Keys",
            command=self.validate_api_keys
        )
        self.validate_button.pack(side=tk.LEFT)
        
        # Status label
        self.api_status_var = tk.StringVar()
        self.api_status_label = ttk.Label(
            validate_frame,
            textvariable=self.api_status_var,
            foreground="green"
        )
        self.api_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
    def setup_model_section(self):
        """Set up model selection UI"""
        model_frame = ttk.LabelFrame(self.settings_frame, text="Model Selection", padding=10)
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(model_frame, text="Select Model:").pack(anchor=tk.W)
        
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            state="readonly",
            width=40
        )
        self.model_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Model info label
        self.model_info_var = tk.StringVar()
        self.model_info_label = ttk.Label(
            model_frame,
            textvariable=self.model_info_var,
            foreground="gray",
            font=('TkDefaultFont', 9)
        )
        self.model_info_label.pack(anchor=tk.W, pady=(5, 0))
        
    def setup_mode_section(self):
        """Set up mode selection UI"""
        mode_frame = ttk.LabelFrame(self.settings_frame, text="Execution Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="single")
        
        # Single agent mode
        single_radio = ttk.Radiobutton(
            mode_frame,
            text="Single Agent Mode",
            variable=self.mode_var,
            value="single"
        )
        single_radio.pack(anchor=tk.W)
        
        single_info = ttk.Label(
            mode_frame,
            text="Uses one agent for faster responses",
            foreground="gray",
            font=('TkDefaultFont', 9)
        )
        single_info.pack(anchor=tk.W, padx=(20, 0))
        
        # Heavy mode
        heavy_radio = ttk.Radiobutton(
            mode_frame,
            text="Heavy Mode",
            variable=self.mode_var,
            value="heavy"
        )
        heavy_radio.pack(anchor=tk.W, pady=(10, 0))
        
        heavy_info = ttk.Label(
            mode_frame,
            text="Uses 4 parallel agents for comprehensive analysis",
            foreground="gray",
            font=('TkDefaultFont', 9)
        )
        heavy_info.pack(anchor=tk.W, padx=(20, 0))
        
    def setup_action_buttons(self):
        """Set up action buttons"""
        button_frame = ttk.Frame(self.settings_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Save button
        self.save_button = ttk.Button(
            button_frame,
            text="Save Configuration",
            command=self.save_configuration,
            style='Accent.TButton'
        )
        self.save_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Reset button
        self.reset_button = ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self.reset_to_defaults
        )
        self.reset_button.pack(side=tk.RIGHT)
        
    def load_current_config(self) -> AppConfig:
        """Load current configuration from file"""
        try:
            if os.path.exists(self.config_path):
                self.config_manager.load_config(self.config_path)
                provider_config = self.config_manager.get_provider_config()
                
                # Load API keys from config
                api_keys = {}
                config = self.config_manager.config
                
                if 'deepseek' in config and 'api_key' in config['deepseek']:
                    api_keys['deepseek'] = config['deepseek']['api_key']
                if 'openrouter' in config and 'api_key' in config['openrouter']:
                    api_keys['openrouter'] = config['openrouter']['api_key']
                
                return AppConfig(
                    provider=provider_config.provider_type,
                    model=provider_config.model,
                    api_keys=api_keys,
                    mode="single"  # Default mode
                )
            else:
                # Default configuration
                return AppConfig(
                    provider="deepseek",
                    model="deepseek-chat",
                    api_keys={},
                    mode="single"
                )
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return AppConfig(
                provider="deepseek",
                model="deepseek-chat",
                api_keys={},
                mode="single"
            )
    
    def load_settings(self):
        """Load settings into UI components"""
        # Set provider
        provider_display = f"{self.current_config.provider} ({self.providers[self.current_config.provider]['name']})"
        self.provider_var.set(provider_display)
        
        # Load models for current provider
        self.load_models_for_provider(self.current_config.provider)
        
        # Set model
        self.model_var.set(self.current_config.model)
        
        # Set API keys
        self.deepseek_key_var.set(self.current_config.api_keys.get('deepseek', ''))
        self.openrouter_key_var.set(self.current_config.api_keys.get('openrouter', ''))
        
        # Set mode
        self.mode_var.set(self.current_config.mode)
        
        # Update model info
        self.update_model_info()
        
    def on_provider_change(self, event=None):
        """Handle provider selection change"""
        provider_display = self.provider_var.get()
        provider_key = provider_display.split(' (')[0]
        
        # Load models for selected provider
        self.load_models_for_provider(provider_key)
        
        # Set default model for provider
        if provider_key in self.providers:
            default_model = self.providers[provider_key]['models'][0]
            self.model_var.set(default_model)
            self.update_model_info()
    
    def load_models_for_provider(self, provider: str):
        """Load available models for the selected provider"""
        if provider in self.providers:
            models = self.providers[provider]['models']
            self.model_combo['values'] = models
            
            # Set default model if current model is not available
            if self.model_var.get() not in models:
                self.model_var.set(models[0])
    
    def update_model_info(self):
        """Update model information display"""
        provider_key = self.provider_var.get().split(' (')[0]
        model = self.model_var.get()
        
        # Get model info from provider factory
        try:
            model_info = ProviderClientFactory.get_model_info(provider_key, model)
            if model_info:
                info_text = f"Context: {model_info.get('context_window', 'N/A')}"
                if 'cost_per_1m_input_tokens' in model_info:
                    info_text += f" | Cost: ${model_info['cost_per_1m_input_tokens']}/1M input tokens"
                self.model_info_var.set(info_text)
            else:
                self.model_info_var.set("Model information not available")
        except Exception:
            self.model_info_var.set("Model information not available")
    
    def validate_api_keys(self):
        """Validate API keys for all providers"""
        self.api_status_var.set("Validating...")
        self.validate_button.config(state="disabled")
        
        try:
            # Get current API keys
            deepseek_key = self.deepseek_key_var.get().strip()
            openrouter_key = self.openrouter_key_var.get().strip()
            
            validation_results = []
            
            # Validate DeepSeek key if provided
            if deepseek_key:
                try:
                    self.validate_single_api_key("deepseek", deepseek_key)
                    validation_results.append("DeepSeek: ✓")
                except Exception as e:
                    validation_results.append(f"DeepSeek: ✗ ({str(e)})")
            
            # Validate OpenRouter key if provided
            if openrouter_key:
                try:
                    self.validate_single_api_key("openrouter", openrouter_key)
                    validation_results.append("OpenRouter: ✓")
                except Exception as e:
                    validation_results.append(f"OpenRouter: ✗ ({str(e)})")
            
            if not deepseek_key and not openrouter_key:
                self.api_status_var.set("No API keys to validate")
            else:
                self.api_status_var.set(" | ".join(validation_results))
                
        except Exception as e:
            self.api_status_var.set(f"Validation error: {str(e)}")
        finally:
            self.validate_button.config(state="normal")
    
    def validate_single_api_key(self, provider: str, api_key: str) -> bool:
        """Validate a single API key"""
        if not api_key:
            raise ValueError("API key is empty")
        
        # Basic format validation
        if provider == "deepseek":
            if not api_key.startswith("sk-"):
                raise ValueError("DeepSeek API key should start with 'sk-'")
            if len(api_key) < 20:
                raise ValueError("DeepSeek API key appears too short")
        elif provider == "openrouter":
            if not api_key.startswith("sk-or-"):
                raise ValueError("OpenRouter API key should start with 'sk-or-'")
            if len(api_key) < 30:
                raise ValueError("OpenRouter API key appears too short")
        
        # For now, just do basic format validation
        # Full API validation can be done when actually using the key
        return True
    
    def save_configuration(self):
        """Save current configuration to file"""
        try:
            # Get current values
            provider_key = self.provider_var.get().split(' (')[0]
            model = self.model_var.get()
            deepseek_key = self.deepseek_key_var.get().strip()
            openrouter_key = self.openrouter_key_var.get().strip()
            mode = self.mode_var.get()
            
            # Validate that we have an API key for the selected provider
            if provider_key == "deepseek" and not deepseek_key:
                messagebox.showerror("Configuration Error", "DeepSeek API key is required for DeepSeek provider")
                return
            elif provider_key == "openrouter" and not openrouter_key:
                messagebox.showerror("Configuration Error", "OpenRouter API key is required for OpenRouter provider")
                return
            
            # Load existing config or create new one
            config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            
            # Update provider selection
            config['provider'] = {'type': provider_key}
            
            # Update provider-specific configuration
            if provider_key == "deepseek":
                config['deepseek'] = {
                    'api_key': deepseek_key,
                    'base_url': self.providers['deepseek']['base_url'],
                    'model': model
                }
            elif provider_key == "openrouter":
                config['openrouter'] = {
                    'api_key': openrouter_key,
                    'base_url': self.providers['openrouter']['base_url'],
                    'model': model
                }
            
            # Preserve other configuration sections
            if 'system_prompt' not in config:
                config['system_prompt'] = self.get_default_system_prompt()
            if 'agent' not in config:
                config['agent'] = {'max_iterations': 10}
            if 'orchestrator' not in config:
                config['orchestrator'] = self.get_default_orchestrator_config()
            if 'search' not in config:
                config['search'] = {'max_results': 5, 'user_agent': 'Mozilla/5.0 (compatible; Make It Heavy Agent)'}
            
            # Save configuration
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            # Update current config
            self.current_config = AppConfig(
                provider=provider_key,
                model=model,
                api_keys={
                    'deepseek': deepseek_key,
                    'openrouter': openrouter_key
                },
                mode=mode
            )
            
            # Notify parent of configuration change
            if self.on_config_change:
                self.on_config_change(self.current_config)
            
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        if messagebox.askyesno("Reset Configuration", "Are you sure you want to reset to default settings?"):
            # Reset UI to defaults
            self.provider_var.set("deepseek (DeepSeek)")
            self.load_models_for_provider("deepseek")
            self.model_var.set("deepseek-chat")
            self.deepseek_key_var.set("")
            self.openrouter_key_var.set("")
            self.mode_var.set("single")
            self.api_status_var.set("")
            self.update_model_info()
    
    def get_default_system_prompt(self) -> str:
        """Get default system prompt"""
        return """You are a helpful research assistant. When users ask questions that require 
current information or web search, use the search tool and all other tools available to find relevant 
information and provide comprehensive answers based on the results.

IMPORTANT: When you have fully satisfied the user's request and provided a complete answer, 
you MUST call the mark_task_complete tool with a summary of what was accomplished and 
a final message for the user. This signals that the task is finished."""
    
    def get_default_orchestrator_config(self) -> Dict:
        """Get default orchestrator configuration"""
        return {
            'parallel_agents': 4,
            'task_timeout': 300,
            'aggregation_strategy': 'consensus',
            'question_generation_prompt': """You are an orchestrator that needs to create {num_agents} different questions to thoroughly analyze this topic from multiple angles.

Original user query: {user_input}

Generate exactly {num_agents} different, specific questions that will help gather comprehensive information about this topic.
Each question should approach the topic from a different angle (research, analysis, verification, alternatives, etc.).

Return your response as a JSON array of strings, like this:
["question 1", "question 2", "question 3", "question 4"]

Only return the JSON array, nothing else.""",
            'synthesis_prompt': """You have {num_responses} different AI agents that analyzed the same query from different perspectives. 
Your job is to synthesize their responses into ONE comprehensive final answer.

Here are all the agent responses:

{agent_responses}

IMPORTANT: Just synthesize these into ONE final comprehensive answer that combines the best information from all agents. 
Do NOT call mark_task_complete or any other tools. Do NOT mention that you are synthesizing multiple responses. 
Simply provide the final synthesized answer directly as your response."""
        }
    
    def save_api_key(self, provider: str, key: str):
        """Save API key for a specific provider"""
        if provider == "deepseek":
            self.deepseek_key_var.set(key)
        elif provider == "openrouter":
            self.openrouter_key_var.set(key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Update current config
        self.current_config.api_keys[provider] = key
    
    def get_current_config(self) -> AppConfig:
        """Get current configuration"""
        return self.current_config