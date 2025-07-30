"""
Data models for the multi-model configuration system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class ModelInfo:
    """Information about a specific model from a provider."""
    id: str
    name: str
    provider: str
    supports_function_calling: bool
    context_window: int
    input_cost_per_1m: Optional[float]
    output_cost_per_1m: Optional[float]
    description: str
    capabilities: List[str] = field(default_factory=list)
    max_tokens: Optional[int] = None
    created: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate model info after initialization."""
        if not self.id:
            raise ValueError("Model ID cannot be empty")
        if not self.name:
            raise ValueError("Model name cannot be empty")
        if not self.provider:
            raise ValueError("Provider cannot be empty")


@dataclass
class CostInfo:
    """Cost information for a model."""
    model_id: str
    input_cost_per_1m: Optional[float]
    output_cost_per_1m: Optional[float]
    currency: str = "USD"
    last_updated: Optional[datetime] = None
    
    @property
    def has_cost_data(self) -> bool:
        """Check if cost data is available."""
        return self.input_cost_per_1m is not None and self.output_cost_per_1m is not None


@dataclass
class AgentModelConfig:
    """Configuration mapping agents to specific models."""
    agent_0_model: str  # Research agent
    agent_1_model: str  # Analysis agent
    agent_2_model: str  # Verification agent
    agent_3_model: str  # Alternatives agent
    synthesis_model: str  # Synthesis agent
    default_model: str  # Fallback model
    profile_name: str = "custom"
    
    def get_agent_model(self, agent_id: int) -> str:
        """Get model for specific agent ID."""
        agent_models = {
            0: self.agent_0_model,
            1: self.agent_1_model,
            2: self.agent_2_model,
            3: self.agent_3_model
        }
        return agent_models.get(agent_id, self.default_model)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {
            'agent_0_model': self.agent_0_model,
            'agent_1_model': self.agent_1_model,
            'agent_2_model': self.agent_2_model,
            'agent_3_model': self.agent_3_model,
            'synthesis_model': self.synthesis_model,
            'default_model': self.default_model,
            'profile_name': self.profile_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'AgentModelConfig':
        """Create from dictionary format."""
        return cls(
            agent_0_model=data.get('agent_0_model', ''),
            agent_1_model=data.get('agent_1_model', ''),
            agent_2_model=data.get('agent_2_model', ''),
            agent_3_model=data.get('agent_3_model', ''),
            synthesis_model=data.get('synthesis_model', ''),
            default_model=data.get('default_model', ''),
            profile_name=data.get('profile_name', 'custom')
        )


@dataclass
class CostEstimate:
    """Cost estimate for a configuration."""
    total_input_tokens: int
    total_output_tokens: int
    total_cost: float
    per_agent_costs: Dict[int, float] = field(default_factory=dict)
    breakdown: Dict[str, float] = field(default_factory=dict)
    currency: str = "USD"
    
    @property
    def cost_per_query(self) -> float:
        """Get cost per query estimate."""
        return self.total_cost


@dataclass
class ModelTestResult:
    """Result of testing a model configuration."""
    model_id: str
    success: bool
    error_message: Optional[str] = None
    response_time: Optional[float] = None
    test_timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.test_timestamp is None:
            self.test_timestamp = datetime.now()


@dataclass
class ConfigurationProfile:
    """Predefined configuration profile."""
    name: str
    description: str
    config: AgentModelConfig
    estimated_cost_per_query: Optional[float] = None
    
    @classmethod
    def create_budget_profile(cls, available_models: List[ModelInfo]) -> 'ConfigurationProfile':
        """Create a budget-focused profile."""
        # Find cheapest models with function calling support
        budget_models = sorted(
            [m for m in available_models if m.supports_function_calling and m.input_cost_per_1m is not None],
            key=lambda x: x.input_cost_per_1m or float('inf')
        )
        
        if not budget_models:
            raise ValueError("No suitable models found for budget profile")
        
        cheapest_model = budget_models[0].id
        
        config = AgentModelConfig(
            agent_0_model=cheapest_model,
            agent_1_model=cheapest_model,
            agent_2_model=cheapest_model,
            agent_3_model=cheapest_model,
            synthesis_model=cheapest_model,
            default_model=cheapest_model,
            profile_name="budget"
        )
        
        return cls(
            name="Budget",
            description="Cost-optimized configuration using the cheapest available models",
            config=config
        )
    
    @classmethod
    def create_balanced_profile(cls, available_models: List[ModelInfo]) -> 'ConfigurationProfile':
        """Create a balanced profile."""
        function_calling_models = [m for m in available_models if m.supports_function_calling]
        
        if not function_calling_models:
            raise ValueError("No suitable models found for balanced profile")
        
        # Sort by cost and pick middle-range models
        models_with_cost = [m for m in function_calling_models if m.input_cost_per_1m is not None]
        if models_with_cost:
            models_with_cost.sort(key=lambda x: x.input_cost_per_1m)
            mid_index = len(models_with_cost) // 2
            balanced_model = models_with_cost[mid_index].id
        else:
            balanced_model = function_calling_models[0].id
        
        config = AgentModelConfig(
            agent_0_model=balanced_model,
            agent_1_model=balanced_model,
            agent_2_model=balanced_model,
            agent_3_model=balanced_model,
            synthesis_model=balanced_model,
            default_model=balanced_model,
            profile_name="balanced"
        )
        
        return cls(
            name="Balanced",
            description="Balanced configuration optimizing cost and performance",
            config=config
        )
    
    @classmethod
    def create_premium_profile(cls, available_models: List[ModelInfo]) -> 'ConfigurationProfile':
        """Create a premium profile."""
        function_calling_models = [m for m in available_models if m.supports_function_calling]
        
        if not function_calling_models:
            raise ValueError("No suitable models found for premium profile")
        
        # Find the most expensive/capable model
        models_with_cost = [m for m in function_calling_models if m.input_cost_per_1m is not None]
        if models_with_cost:
            premium_model = max(models_with_cost, key=lambda x: x.input_cost_per_1m).id
        else:
            # Fallback to first available model
            premium_model = function_calling_models[0].id
        
        config = AgentModelConfig(
            agent_0_model=premium_model,
            agent_1_model=premium_model,
            agent_2_model=premium_model,
            agent_3_model=premium_model,
            synthesis_model=premium_model,
            default_model=premium_model,
            profile_name="premium"
        )
        
        return cls(
            name="Premium",
            description="High-performance configuration using the best available models",
            config=config
        )