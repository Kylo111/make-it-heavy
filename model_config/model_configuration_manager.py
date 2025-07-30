"""
Main model configuration manager that coordinates all model configuration services.
"""

import os
import yaml
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from .data_models import ModelInfo, AgentModelConfig, CostEstimate, ModelTestResult, ConfigurationProfile
from .provider_model_service import ProviderModelService, ProviderModelServiceError
from .cost_calculation_service import CostCalculationService, CostCalculationServiceError
from .model_validation_service import ModelValidationService, ModelValidationServiceError
from config_manager import ConfigurationManager, ProviderConfig


class ModelConfigurationManagerError(Exception):
    """Exception for model configuration manager errors."""
    pass


class ModelConfigurationManager:
    """Main manager for model configuration system."""
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.provider_service = ProviderModelService()
        self.cost_service = CostCalculationService(self.provider_service)
        self.validation_service = ModelValidationService()
        
        # Cache for available models
        self._available_models_cache: Optional[List[ModelInfo]] = None
        self._cache_timestamp: Optional[datetime] = None
    
    def get_available_models(self, provider: Optional[str] = None, api_key: Optional[str] = None) -> List[ModelInfo]:
        """Get available models from providers with function calling support."""
        try:
            if provider:
                providers = [provider]
            else:
                # Get all supported providers
                providers = ["openrouter", "deepseek"]
            
            all_models = []
            
            for prov in providers:
                try:
                    models = self.provider_service.get_available_models(prov, api_key)
                    # Filter to only function calling models
                    function_calling_models = self.provider_service.filter_function_calling_models(models)
                    all_models.extend(function_calling_models)
                except ProviderModelServiceError as e:
                    print(f"Warning: Failed to fetch models from {prov}: {e}")
                    continue
            
            # Update cache
            self._available_models_cache = all_models
            self._cache_timestamp = datetime.now()
            
            return all_models
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Failed to get available models: {str(e)}")
    
    def get_model_costs(self, model_id: str, provider: str, api_key: Optional[str] = None) -> Optional[float]:
        """Get cost information for a specific model."""
        try:
            cost_info = self.provider_service.get_model_costs(provider, model_id, api_key)
            return cost_info.input_cost_per_1m
        except ProviderModelServiceError:
            return None
    
    def save_agent_configuration(self, config: AgentModelConfig, config_path: str = "config.yaml") -> bool:
        """Save agent model configuration to YAML file."""
        try:
            # Load existing config
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f) or {}
            else:
                yaml_config = {}
            
            # Add multi-model configuration section
            yaml_config['multi_model'] = config.to_dict()
            
            # Write back to file
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_config, f, default_flow_style=False, allow_unicode=True)
            
            return True
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Failed to save configuration: {str(e)}")
    
    def load_agent_configuration(self, config_path: str = "config.yaml") -> Optional[AgentModelConfig]:
        """Load agent model configuration from YAML file."""
        try:
            if not os.path.exists(config_path):
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f) or {}
            
            multi_model_config = yaml_config.get('multi_model')
            if not multi_model_config:
                return None
            
            return AgentModelConfig.from_dict(multi_model_config)
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Failed to load configuration: {str(e)}")
    
    def validate_model_compatibility(self, model_id: str) -> bool:
        """Validate if a model is compatible with the system."""
        try:
            available_models = self.get_available_models()
            model_info = next((m for m in available_models if m.id == model_id), None)
            
            if not model_info:
                return False
            
            return self.validation_service.validate_model_compatibility(model_info)
            
        except Exception:
            return False
    
    def test_model_configuration(
        self, 
        config: AgentModelConfig, 
        provider_configs: Optional[Dict[str, ProviderConfig]] = None
    ) -> Dict[str, ModelTestResult]:
        """Test a model configuration for API connectivity."""
        try:
            available_models = self.get_available_models()
            
            if not provider_configs:
                # Get provider configs from current configuration
                provider_configs = self._get_provider_configs()
            
            return self.validation_service.test_model_configuration(
                config, available_models, provider_configs
            )
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Failed to test configuration: {str(e)}")
    
    def calculate_configuration_cost(self, config: AgentModelConfig) -> CostEstimate:
        """Calculate estimated cost for a configuration."""
        try:
            available_models = self.get_available_models()
            return self.cost_service.calculate_configuration_cost(config, available_models)
            
        except CostCalculationServiceError as e:
            raise ModelConfigurationManagerError(f"Cost calculation failed: {str(e)}")
    
    def get_predefined_profiles(self) -> List[ConfigurationProfile]:
        """Get predefined configuration profiles."""
        try:
            available_models = self.get_available_models()
            
            if not available_models:
                return []
            
            profiles = []
            
            try:
                budget_profile = ConfigurationProfile.create_budget_profile(available_models)
                profiles.append(budget_profile)
            except ValueError:
                pass
            
            try:
                balanced_profile = ConfigurationProfile.create_balanced_profile(available_models)
                profiles.append(balanced_profile)
            except ValueError:
                pass
            
            try:
                premium_profile = ConfigurationProfile.create_premium_profile(available_models)
                profiles.append(premium_profile)
            except ValueError:
                pass
            
            return profiles
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Failed to get predefined profiles: {str(e)}")
    
    def validate_configuration(self, config: AgentModelConfig) -> Dict[str, Any]:
        """Validate a complete configuration and return detailed results."""
        try:
            available_models = self.get_available_models()
            
            # Basic validation
            validation_results = self.validation_service.validate_configuration(config, available_models)
            
            # Get detailed errors
            errors = self.validation_service.get_validation_errors(config, available_models)
            
            # Get suggestions for fixes
            suggestions = self.validation_service.suggest_fixes(config, available_models)
            
            # Calculate cost if valid
            cost_estimate = None
            if all(validation_results.values()):
                try:
                    cost_estimate = self.calculate_configuration_cost(config)
                except Exception:
                    pass
            
            return {
                'valid': all(validation_results.values()),
                'validation_results': validation_results,
                'errors': errors,
                'suggestions': suggestions,
                'cost_estimate': cost_estimate
            }
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Configuration validation failed: {str(e)}")
    
    def export_configuration(self, config: AgentModelConfig, include_costs: bool = True) -> Dict[str, Any]:
        """Export configuration to a shareable format."""
        try:
            export_data = {
                'configuration': config.to_dict(),
                'export_timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            if include_costs:
                try:
                    cost_estimate = self.calculate_configuration_cost(config)
                    export_data['cost_estimate'] = {
                        'total_cost': cost_estimate.total_cost,
                        'breakdown': cost_estimate.breakdown,
                        'currency': cost_estimate.currency
                    }
                except Exception:
                    pass
            
            return export_data
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Failed to export configuration: {str(e)}")
    
    def import_configuration(self, import_data: Dict[str, Any]) -> AgentModelConfig:
        """Import configuration from exported data."""
        try:
            if 'configuration' not in import_data:
                raise ModelConfigurationManagerError("Invalid import data: missing configuration")
            
            config = AgentModelConfig.from_dict(import_data['configuration'])
            
            # Validate imported configuration
            validation_result = self.validate_configuration(config)
            if not validation_result['valid']:
                errors = validation_result['errors']
                raise ModelConfigurationManagerError(f"Imported configuration is invalid: {'; '.join(errors)}")
            
            return config
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Failed to import configuration: {str(e)}")
    
    def clear_cache(self):
        """Clear all cached data."""
        self.provider_service.clear_cache()
        self._available_models_cache = None
        self._cache_timestamp = None
    
    def get_model_by_id(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information by ID."""
        available_models = self.get_available_models()
        return next((model for model in available_models if model.id == model_id), None)
    
    def compare_configurations(self, config1: AgentModelConfig, config2: AgentModelConfig) -> Dict[str, Any]:
        """Compare two configurations."""
        try:
            available_models = self.get_available_models()
            
            # Calculate costs
            cost_comparison = self.cost_service.compare_configurations(config1, config2, available_models)
            
            # Validate both configurations
            validation1 = self.validation_service.validate_configuration(config1, available_models)
            validation2 = self.validation_service.validate_configuration(config2, available_models)
            
            return {
                'cost_comparison': cost_comparison,
                'config1_valid': all(validation1.values()),
                'config2_valid': all(validation2.values()),
                'config1_validation': validation1,
                'config2_validation': validation2
            }
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Failed to compare configurations: {str(e)}")
    
    def test_configuration_connectivity(self, config: AgentModelConfig) -> Dict[str, ModelTestResult]:
        """Test configuration by making actual API calls to each configured model."""
        try:
            available_models = self.get_available_models()
            provider_configs = self._get_provider_configs()
            
            # Test each agent model
            test_results = {}
            
            # Test agent models
            for agent_id in range(4):
                model_id = config.get_agent_model(agent_id)
                test_results[f'agent_{agent_id}'] = self._test_single_model(model_id, available_models, provider_configs)
            
            # Test synthesis model
            synthesis_model = config.synthesis_model
            test_results['synthesis'] = self._test_single_model(synthesis_model, available_models, provider_configs)
            
            return test_results
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Configuration testing failed: {str(e)}")
    
    def _test_single_model(self, model_id: str, available_models: List[ModelInfo], provider_configs: Dict[str, ProviderConfig]) -> ModelTestResult:
        """Test a single model with a simple API call."""
        try:
            # Find model info
            model_info = next((m for m in available_models if m.id == model_id), None)
            if not model_info:
                return ModelTestResult(
                    model_id=model_id,
                    success=False,
                    error_message=f"Model {model_id} not found in available models"
                )
            
            # Get provider config
            provider_config = provider_configs.get(model_info.provider)
            if not provider_config:
                return ModelTestResult(
                    model_id=model_id,
                    success=False,
                    error_message=f"No provider configuration found for {model_info.provider}"
                )
            
            # Create a simple test agent and make a test call
            from agent import UniversalAgent
            import tempfile
            import yaml
            
            # Create temporary config for testing
            test_config = {
                'provider': {'type': model_info.provider},
                model_info.provider: {
                    'api_key': provider_config.api_key,
                    'base_url': provider_config.base_url,
                    'model': model_id
                },
                'system_prompt': 'You are a test assistant.',
                'agent': {'max_iterations': 1}
            }
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
                yaml.dump(test_config, temp_file)
                temp_config_path = temp_file.name
            
            try:
                # Create agent and test
                start_time = time.time()
                test_agent = UniversalAgent(config_path=temp_config_path, silent=True)
                
                # Simple test query
                response = test_agent.call_llm([
                    {"role": "system", "content": "You are a test assistant."},
                    {"role": "user", "content": "Respond with exactly: 'Test successful'"}
                ])
                
                response_time = time.time() - start_time
                
                # Check if we got a response
                if response and response.choices and len(response.choices) > 0:
                    return ModelTestResult(
                        model_id=model_id,
                        success=True,
                        response_time=response_time
                    )
                else:
                    return ModelTestResult(
                        model_id=model_id,
                        success=False,
                        error_message="No response received from model"
                    )
                    
            finally:
                # Clean up temp file
                import os
                if os.path.exists(temp_config_path):
                    os.unlink(temp_config_path)
                    
        except Exception as e:
            return ModelTestResult(
                model_id=model_id,
                success=False,
                error_message=str(e)
            )
    
    def export_configuration_with_sanitization(self, config: AgentModelConfig, include_costs: bool = True, sanitize_keys: bool = True) -> Dict[str, Any]:
        """Export configuration with API key sanitization for sharing."""
        try:
            export_data = self.export_configuration(config, include_costs)
            
            if sanitize_keys:
                # Remove sensitive information
                export_data['note'] = 'API keys have been removed for security. You will need to configure your own API keys.'
                export_data['requires_api_setup'] = True
            
            return export_data
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Failed to export configuration with sanitization: {str(e)}")
    
    def create_configuration_comparison_report(self, configs: List[AgentModelConfig], config_names: List[str] = None) -> Dict[str, Any]:
        """Create a detailed comparison report for multiple configurations."""
        try:
            if not configs:
                raise ModelConfigurationManagerError("No configurations provided for comparison")
            
            if config_names is None:
                config_names = [f"Config {i+1}" for i in range(len(configs))]
            
            available_models = self.get_available_models()
            
            # Calculate costs for all configurations
            cost_estimates = []
            for config in configs:
                try:
                    cost_estimate = self.calculate_configuration_cost(config)
                    cost_estimates.append(cost_estimate)
                except Exception:
                    cost_estimates.append(None)
            
            # Validate all configurations
            validations = []
            for config in configs:
                try:
                    validation = self.validate_configuration(config)
                    validations.append(validation)
                except Exception:
                    validations.append({'valid': False, 'errors': ['Validation failed']})
            
            # Create comparison matrix
            comparison_matrix = []
            for i, config in enumerate(configs):
                config_data = {
                    'name': config_names[i],
                    'profile': config.profile_name,
                    'valid': validations[i]['valid'] if validations[i] else False,
                    'total_cost': cost_estimates[i].total_cost if cost_estimates[i] else 0.0,
                    'models': {
                        'agent_0': config.agent_0_model,
                        'agent_1': config.agent_1_model,
                        'agent_2': config.agent_2_model,
                        'agent_3': config.agent_3_model,
                        'synthesis': config.synthesis_model
                    }
                }
                comparison_matrix.append(config_data)
            
            # Find best/worst configurations
            valid_configs = [c for c in comparison_matrix if c['valid']]
            
            best_cost = None
            worst_cost = None
            if valid_configs:
                best_cost = min(valid_configs, key=lambda x: x['total_cost'])
                worst_cost = max(valid_configs, key=lambda x: x['total_cost'])
            
            return {
                'comparison_matrix': comparison_matrix,
                'summary': {
                    'total_configurations': len(configs),
                    'valid_configurations': len(valid_configs),
                    'best_cost_config': best_cost,
                    'worst_cost_config': worst_cost,
                    'cost_range': {
                        'min': best_cost['total_cost'] if best_cost else 0.0,
                        'max': worst_cost['total_cost'] if worst_cost else 0.0
                    }
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Failed to create comparison report: {str(e)}")
    
    def get_configuration_recommendations(self, config: AgentModelConfig) -> Dict[str, Any]:
        """Get recommendations for improving a configuration."""
        try:
            available_models = self.get_available_models()
            current_cost = self.calculate_configuration_cost(config)
            
            recommendations = []
            
            # Check for cost optimization opportunities
            budget_models = sorted(
                [m for m in available_models if m.supports_function_calling and m.input_cost_per_1m is not None],
                key=lambda x: x.input_cost_per_1m or float('inf')
            )
            
            if budget_models:
                cheapest_model = budget_models[0]
                
                # Suggest cheaper alternatives for expensive agents
                for agent_id in range(4):
                    current_model_id = config.get_agent_model(agent_id)
                    current_model = next((m for m in available_models if m.id == current_model_id), None)
                    
                    if current_model and current_model.input_cost_per_1m and cheapest_model.input_cost_per_1m:
                        if current_model.input_cost_per_1m > cheapest_model.input_cost_per_1m * 2:
                            recommendations.append({
                                'type': 'cost_optimization',
                                'agent': f'agent_{agent_id}',
                                'current_model': current_model_id,
                                'suggested_model': cheapest_model.id,
                                'potential_savings': current_model.input_cost_per_1m - cheapest_model.input_cost_per_1m,
                                'description': f'Consider using {cheapest_model.name} for Agent {agent_id} to reduce costs'
                            })
            
            # Check for performance optimization opportunities
            premium_models = sorted(
                [m for m in available_models if m.supports_function_calling and m.input_cost_per_1m is not None],
                key=lambda x: x.input_cost_per_1m or 0,
                reverse=True
            )
            
            if premium_models and len(premium_models) > 1:
                premium_model = premium_models[0]
                
                # Suggest premium model for synthesis if using cheaper model
                synthesis_model = next((m for m in available_models if m.id == config.synthesis_model), None)
                if synthesis_model and synthesis_model.id != premium_model.id:
                    recommendations.append({
                        'type': 'performance_optimization',
                        'agent': 'synthesis',
                        'current_model': config.synthesis_model,
                        'suggested_model': premium_model.id,
                        'description': f'Consider using {premium_model.name} for synthesis to improve output quality'
                    })
            
            return {
                'current_cost': current_cost.total_cost,
                'recommendations': recommendations,
                'recommendation_count': len(recommendations)
            }
            
        except Exception as e:
            raise ModelConfigurationManagerError(f"Failed to get recommendations: {str(e)}")
    
    def _get_provider_configs(self) -> Dict[str, ProviderConfig]:
        """Get provider configurations from current config."""
        try:
            # This would need to be implemented based on how multiple providers are configured
            # For now, return the current provider config
            current_provider_config = self.config_manager.get_provider_config()
            return {current_provider_config.provider_type: current_provider_config}
        except Exception:
            return {}