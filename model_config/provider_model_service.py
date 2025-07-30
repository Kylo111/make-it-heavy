"""
Service for fetching model information from different providers.
"""

import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .data_models import ModelInfo, CostInfo


class ProviderModelServiceError(Exception):
    """Base exception for provider model service errors."""
    pass


class ProviderModelService:
    """Service for fetching model information from OpenRouter and DeepSeek APIs."""
    
    def __init__(self):
        self.model_cache: Dict[str, List[ModelInfo]] = {}
        self.cost_cache: Dict[str, CostInfo] = {}
        self.model_cache_ttl = timedelta(hours=1)
        self.cost_cache_ttl = timedelta(hours=24)
        self.last_model_fetch: Dict[str, datetime] = {}
        self.last_cost_fetch: Dict[str, datetime] = {}
    
    def get_available_models(self, provider: str, api_key: Optional[str] = None) -> List[ModelInfo]:
        """Get available models from a provider with caching."""
        # Check cache first
        if self._is_model_cache_valid(provider):
            return self.model_cache[provider]
        
        # Fetch fresh data
        if provider == "openrouter":
            models = self._fetch_openrouter_models(api_key)
        elif provider == "deepseek":
            models = self._fetch_deepseek_models(api_key)
        else:
            raise ProviderModelServiceError(f"Unsupported provider: {provider}")
        
        # Update cache
        self.model_cache[provider] = models
        self.last_model_fetch[provider] = datetime.now()
        
        return models
    
    def get_model_costs(self, provider: str, model_id: str, api_key: Optional[str] = None) -> CostInfo:
        """Get cost information for a specific model with caching."""
        cache_key = f"{provider}:{model_id}"
        
        # Check cache first
        if self._is_cost_cache_valid(cache_key):
            return self.cost_cache[cache_key]
        
        # Fetch fresh data
        if provider == "openrouter":
            cost_info = self._fetch_openrouter_model_cost(model_id, api_key)
        elif provider == "deepseek":
            cost_info = self._fetch_deepseek_model_cost(model_id, api_key)
        else:
            raise ProviderModelServiceError(f"Unsupported provider: {provider}")
        
        # Update cache
        self.cost_cache[cache_key] = cost_info
        self.last_cost_fetch[cache_key] = datetime.now()
        
        return cost_info
    
    def filter_function_calling_models(self, models: List[ModelInfo]) -> List[ModelInfo]:
        """Filter models to only include those with function calling support."""
        return [model for model in models if model.supports_function_calling]
    
    def clear_cache(self):
        """Clear all cached data."""
        self.model_cache.clear()
        self.cost_cache.clear()
        self.last_model_fetch.clear()
        self.last_cost_fetch.clear()
    
    def _is_model_cache_valid(self, provider: str) -> bool:
        """Check if model cache is still valid."""
        if provider not in self.model_cache:
            return False
        
        last_fetch = self.last_model_fetch.get(provider)
        if not last_fetch:
            return False
        
        return datetime.now() - last_fetch < self.model_cache_ttl
    
    def _is_cost_cache_valid(self, cache_key: str) -> bool:
        """Check if cost cache is still valid."""
        if cache_key not in self.cost_cache:
            return False
        
        last_fetch = self.last_cost_fetch.get(cache_key)
        if not last_fetch:
            return False
        
        return datetime.now() - last_fetch < self.cost_cache_ttl
    
    def _fetch_openrouter_models(self, api_key: Optional[str] = None) -> List[ModelInfo]:
        """Fetch available models from OpenRouter API."""
        try:
            headers = {}
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            
            response = requests.get(
                'https://openrouter.ai/api/v1/models',
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            models = []
            
            for model_data in data.get('data', []):
                # Extract model information
                model_id = model_data.get('id', '')
                name = model_data.get('name', model_id)
                context_window = model_data.get('context_length', 0)
                
                # Check function calling support
                supports_function_calling = self._check_openrouter_function_calling(model_data)
                
                # Extract pricing information
                pricing = model_data.get('pricing', {})
                input_cost = self._parse_cost(pricing.get('prompt'))
                output_cost = self._parse_cost(pricing.get('completion'))
                
                # Extract capabilities
                capabilities = []
                if model_data.get('top_provider', {}).get('is_moderated'):
                    capabilities.append('moderated')
                if supports_function_calling:
                    capabilities.append('function_calling')
                
                model_info = ModelInfo(
                    id=model_id,
                    name=name,
                    provider='openrouter',
                    supports_function_calling=supports_function_calling,
                    context_window=context_window,
                    input_cost_per_1m=input_cost,
                    output_cost_per_1m=output_cost,
                    description=model_data.get('description', ''),
                    capabilities=capabilities,
                    max_tokens=model_data.get('max_tokens'),
                    created=datetime.now()
                )
                models.append(model_info)
            
            return models
            
        except requests.RequestException as e:
            raise ProviderModelServiceError(f"Failed to fetch OpenRouter models: {str(e)}")
        except Exception as e:
            raise ProviderModelServiceError(f"Error processing OpenRouter models: {str(e)}")
    
    def _fetch_deepseek_models(self, api_key: Optional[str] = None) -> List[ModelInfo]:
        """Fetch available models from DeepSeek API."""
        try:
            headers = {'Content-Type': 'application/json'}
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            
            response = requests.get(
                'https://api.deepseek.com/models',
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            models = []
            
            for model_data in data.get('data', []):
                model_id = model_data.get('id', '')
                name = model_data.get('name', model_id)
                
                # DeepSeek models generally support function calling
                supports_function_calling = True
                
                # Get context window (DeepSeek models typically have 64k context)
                context_window = 64000
                
                # DeepSeek pricing (as of current knowledge)
                input_cost, output_cost = self._get_deepseek_pricing(model_id)
                
                capabilities = ['function_calling', 'json_output']
                if 'reasoner' in model_id.lower():
                    capabilities.append('advanced_reasoning')
                
                model_info = ModelInfo(
                    id=model_id,
                    name=name,
                    provider='deepseek',
                    supports_function_calling=supports_function_calling,
                    context_window=context_window,
                    input_cost_per_1m=input_cost,
                    output_cost_per_1m=output_cost,
                    description=f"DeepSeek model: {name}",
                    capabilities=capabilities,
                    created=datetime.now()
                )
                models.append(model_info)
            
            return models
            
        except requests.RequestException as e:
            # If API call fails, return known DeepSeek models
            return self._get_known_deepseek_models()
        except Exception as e:
            raise ProviderModelServiceError(f"Error processing DeepSeek models: {str(e)}")
    
    def _get_known_deepseek_models(self) -> List[ModelInfo]:
        """Return known DeepSeek models as fallback."""
        return [
            ModelInfo(
                id='deepseek-chat',
                name='DeepSeek-V3',
                provider='deepseek',
                supports_function_calling=True,
                context_window=64000,
                input_cost_per_1m=0.27,
                output_cost_per_1m=1.10,
                description='DeepSeek-V3 for general purpose tasks',
                capabilities=['function_calling', 'json_output'],
                created=datetime.now()
            ),
            ModelInfo(
                id='deepseek-reasoner',
                name='DeepSeek-R1',
                provider='deepseek',
                supports_function_calling=True,
                context_window=64000,
                input_cost_per_1m=0.55,
                output_cost_per_1m=2.19,
                description='DeepSeek-R1 with advanced reasoning capabilities',
                capabilities=['function_calling', 'json_output', 'advanced_reasoning'],
                created=datetime.now()
            )
        ]
    
    def _fetch_openrouter_model_cost(self, model_id: str, api_key: Optional[str] = None) -> CostInfo:
        """Fetch cost information for a specific OpenRouter model."""
        try:
            headers = {}
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            
            response = requests.get(
                f'https://openrouter.ai/api/v1/models/{model_id}',
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            pricing = data.get('pricing', {})
            
            return CostInfo(
                model_id=model_id,
                input_cost_per_1m=self._parse_cost(pricing.get('prompt')),
                output_cost_per_1m=self._parse_cost(pricing.get('completion')),
                last_updated=datetime.now()
            )
            
        except requests.RequestException as e:
            raise ProviderModelServiceError(f"Failed to fetch OpenRouter cost for {model_id}: {str(e)}")
    
    def _fetch_deepseek_model_cost(self, model_id: str, api_key: Optional[str] = None) -> CostInfo:
        """Fetch cost information for a specific DeepSeek model."""
        input_cost, output_cost = self._get_deepseek_pricing(model_id)
        
        return CostInfo(
            model_id=model_id,
            input_cost_per_1m=input_cost,
            output_cost_per_1m=output_cost,
            last_updated=datetime.now()
        )
    
    def _get_deepseek_pricing(self, model_id: str) -> tuple[Optional[float], Optional[float]]:
        """Get pricing for DeepSeek models."""
        pricing_map = {
            'deepseek-chat': (0.27, 1.10),
            'deepseek-reasoner': (0.55, 2.19)
        }
        return pricing_map.get(model_id, (None, None))
    
    def _parse_cost(self, cost_str: Optional[str]) -> Optional[float]:
        """Parse cost string to float (cost per 1M tokens)."""
        if not cost_str:
            return None
        
        try:
            # Remove currency symbols and convert to float
            cost_str = cost_str.replace('$', '').replace(',', '')
            cost = float(cost_str)
            
            # OpenRouter typically provides cost per 1K tokens, convert to per 1M
            if cost < 10.0:  # Assume it's per 1K tokens if less than $10
                cost = cost * 1000
            
            return cost
        except (ValueError, TypeError):
            return None
    
    def _check_openrouter_function_calling(self, model_data: Dict) -> bool:
        """Check if an OpenRouter model supports function calling."""
        # Check if model explicitly supports function calling
        if model_data.get('supports_function_calling'):
            return True
        
        # Check model name/id for known function calling models
        model_id = model_data.get('id', '').lower()
        function_calling_models = [
            'gpt-4', 'gpt-3.5', 'claude', 'gemini', 'llama-3', 'mistral'
        ]
        
        return any(model_name in model_id for model_name in function_calling_models)