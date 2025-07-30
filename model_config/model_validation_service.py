"""
Service for validating model compatibility and availability.
"""

import time
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
from .data_models import ModelInfo, AgentModelConfig, ModelTestResult
from config_manager import ProviderConfig
from provider_factory import ProviderClientFactory


class ModelValidationServiceError(Exception):
    """Exception for model validation errors."""
    pass


class ModelValidationService:
    """Service for validating model compatibility and availability."""
    
    def __init__(self):
        self.test_prompt = "Hello! This is a test message to verify model functionality. Please respond with 'Test successful' and call the test_function if available."
        self.test_functions = [
            {
                "type": "function",
                "function": {
                    "name": "test_function",
                    "description": "A test function to verify function calling capability",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "description": "Test status"
                            }
                        },
                        "required": ["status"]
                    }
                }
            }
        ]
    
    def validate_model_compatibility(self, model_info: ModelInfo) -> bool:
        """Validate if a model is compatible with the system requirements."""
        # Check function calling support
        if not model_info.supports_function_calling:
            return False
        
        # Check context window (minimum 4k tokens)
        if model_info.context_window < 4000:
            return False
        
        # Check if model ID is valid format
        if not model_info.id or len(model_info.id.strip()) == 0:
            return False
        
        return True
    
    def validate_configuration(self, config: AgentModelConfig, available_models: List[ModelInfo]) -> Dict[str, bool]:
        """Validate an entire agent configuration."""
        model_ids = {model.id for model in available_models}
        compatible_models = {model.id for model in available_models if self.validate_model_compatibility(model)}
        
        validation_results = {}
        
        # Validate each agent model
        for agent_id in range(4):
            model_id = config.get_agent_model(agent_id)
            agent_key = f"agent_{agent_id}"
            
            if model_id not in model_ids:
                validation_results[agent_key] = False
            elif model_id not in compatible_models:
                validation_results[agent_key] = False
            else:
                validation_results[agent_key] = True
        
        # Validate synthesis model
        if config.synthesis_model not in model_ids:
            validation_results["synthesis"] = False
        elif config.synthesis_model not in compatible_models:
            validation_results["synthesis"] = False
        else:
            validation_results["synthesis"] = True
        
        # Validate default model
        if config.default_model not in model_ids:
            validation_results["default"] = False
        elif config.default_model not in compatible_models:
            validation_results["default"] = False
        else:
            validation_results["default"] = True
        
        return validation_results
    
    def test_model_configuration(
        self, 
        config: AgentModelConfig, 
        available_models: List[ModelInfo],
        provider_configs: Dict[str, ProviderConfig]
    ) -> Dict[str, ModelTestResult]:
        """Test actual API connectivity for each model in the configuration."""
        model_map = {model.id: model for model in available_models}
        test_results = {}
        
        # Get unique models to test
        models_to_test = set()
        for agent_id in range(4):
            models_to_test.add(config.get_agent_model(agent_id))
        models_to_test.add(config.synthesis_model)
        models_to_test.add(config.default_model)
        
        # Test each unique model
        for model_id in models_to_test:
            model_info = model_map.get(model_id)
            if not model_info:
                test_results[model_id] = ModelTestResult(
                    model_id=model_id,
                    success=False,
                    error_message="Model not found in available models"
                )
                continue
            
            # Get provider config for this model
            provider_config = provider_configs.get(model_info.provider)
            if not provider_config:
                test_results[model_id] = ModelTestResult(
                    model_id=model_id,
                    success=False,
                    error_message=f"No provider configuration found for {model_info.provider}"
                )
                continue
            
            # Test the model
            test_results[model_id] = self._test_single_model(model_info, provider_config)
        
        return test_results
    
    def check_model_availability(
        self, 
        model_id: str, 
        provider: str, 
        provider_config: ProviderConfig
    ) -> bool:
        """Check if a specific model is available from the provider."""
        try:
            client = ProviderClientFactory.create_client(provider_config)
            
            # Try to make a simple completion request
            response = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1,
                timeout=10
            )
            
            return True
            
        except Exception:
            return False
    
    def get_validation_errors(
        self, 
        config: AgentModelConfig, 
        available_models: List[ModelInfo]
    ) -> List[str]:
        """Get detailed validation error messages for a configuration."""
        errors = []
        model_map = {model.id: model for model in available_models}
        compatible_models = {model.id for model in available_models if self.validate_model_compatibility(model)}
        
        # Check each agent model
        for agent_id in range(4):
            model_id = config.get_agent_model(agent_id)
            
            if not model_id:
                errors.append(f"Agent {agent_id} has no model assigned")
            elif model_id not in model_map:
                errors.append(f"Agent {agent_id} model '{model_id}' not found in available models")
            elif model_id not in compatible_models:
                model_info = model_map[model_id]
                if not model_info.supports_function_calling:
                    errors.append(f"Agent {agent_id} model '{model_id}' does not support function calling")
                if model_info.context_window < 4000:
                    errors.append(f"Agent {agent_id} model '{model_id}' has insufficient context window ({model_info.context_window} tokens)")
        
        # Check synthesis model
        if not config.synthesis_model:
            errors.append("No synthesis model assigned")
        elif config.synthesis_model not in model_map:
            errors.append(f"Synthesis model '{config.synthesis_model}' not found in available models")
        elif config.synthesis_model not in compatible_models:
            model_info = model_map[config.synthesis_model]
            if not model_info.supports_function_calling:
                errors.append(f"Synthesis model '{config.synthesis_model}' does not support function calling")
        
        # Check default model
        if not config.default_model:
            errors.append("No default model assigned")
        elif config.default_model not in model_map:
            errors.append(f"Default model '{config.default_model}' not found in available models")
        elif config.default_model not in compatible_models:
            model_info = model_map[config.default_model]
            if not model_info.supports_function_calling:
                errors.append(f"Default model '{config.default_model}' does not support function calling")
        
        return errors
    
    def suggest_fixes(
        self, 
        config: AgentModelConfig, 
        available_models: List[ModelInfo]
    ) -> Dict[str, str]:
        """Suggest fixes for configuration issues."""
        suggestions = {}
        compatible_models = [model for model in available_models if self.validate_model_compatibility(model)]
        
        if not compatible_models:
            suggestions["general"] = "No compatible models available. Please check provider configuration."
            return suggestions
        
        # Get a good fallback model
        fallback_model = compatible_models[0].id
        if len(compatible_models) > 1:
            # Prefer models with lower cost if available
            models_with_cost = [m for m in compatible_models if m.input_cost_per_1m is not None]
            if models_with_cost:
                fallback_model = min(models_with_cost, key=lambda x: x.input_cost_per_1m).id
        
        model_map = {model.id: model for model in available_models}
        
        # Check each agent model
        for agent_id in range(4):
            model_id = config.get_agent_model(agent_id)
            
            if not model_id or model_id not in model_map:
                suggestions[f"agent_{agent_id}"] = f"Use available model: {fallback_model}"
            elif not self.validate_model_compatibility(model_map[model_id]):
                suggestions[f"agent_{agent_id}"] = f"Replace with compatible model: {fallback_model}"
        
        # Check synthesis model
        if not config.synthesis_model or config.synthesis_model not in model_map:
            suggestions["synthesis"] = f"Use available model: {fallback_model}"
        elif not self.validate_model_compatibility(model_map[config.synthesis_model]):
            suggestions["synthesis"] = f"Replace with compatible model: {fallback_model}"
        
        # Check default model
        if not config.default_model or config.default_model not in model_map:
            suggestions["default"] = f"Use available model: {fallback_model}"
        elif not self.validate_model_compatibility(model_map[config.default_model]):
            suggestions["default"] = f"Replace with compatible model: {fallback_model}"
        
        return suggestions
    
    def _test_single_model(self, model_info: ModelInfo, provider_config: ProviderConfig) -> ModelTestResult:
        """Test a single model for API connectivity and function calling."""
        start_time = time.time()
        
        try:
            # Create client for this provider
            client = ProviderClientFactory.create_client(provider_config)
            
            # Test basic completion
            response = client.chat.completions.create(
                model=model_info.id,
                messages=[{"role": "user", "content": self.test_prompt}],
                tools=self.test_functions if model_info.supports_function_calling else None,
                max_tokens=100,
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            # Check if response is valid
            if not response.choices or not response.choices[0].message:
                return ModelTestResult(
                    model_id=model_info.id,
                    success=False,
                    error_message="Invalid response from model",
                    response_time=response_time
                )
            
            # Check function calling if supported
            if model_info.supports_function_calling:
                message = response.choices[0].message
                if not message.tool_calls:
                    return ModelTestResult(
                        model_id=model_info.id,
                        success=False,
                        error_message="Model did not call test function despite function calling support",
                        response_time=response_time
                    )
            
            return ModelTestResult(
                model_id=model_info.id,
                success=True,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return ModelTestResult(
                model_id=model_info.id,
                success=False,
                error_message=str(e),
                response_time=response_time
            )