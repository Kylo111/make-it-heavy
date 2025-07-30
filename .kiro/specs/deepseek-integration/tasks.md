# Implementation Plan

- [x] 1. Create DeepSeek configuration system and provider factory
  - Implement enhanced configuration loader that supports multiple providers (OpenRouter and DeepSeek)
  - Create provider client factory that generates appropriate OpenAI clients based on configuration
  - Add configuration validation for DeepSeek-specific parameters (api_key, base_url, model)
  - Create example configuration files for DeepSeek (config_deepseek.yaml)
  - Write unit tests for configuration loading and provider factory functionality
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 3.1, 3.2_

- [ ] 2. Create UniversalAgent class to replace OpenRouterAgent
  - Create UniversalAgent class in agent.py that uses ConfigurationManager and ProviderClientFactory
  - Implement provider-agnostic initialization that works with both OpenRouter and DeepSeek
  - Add provider information display in agent initialization and runtime
  - Ensure function calling works identically with DeepSeek API
  - Implement provider-specific error handling with user-friendly error messages
  - Maintain backward compatibility with existing OpenRouterAgent interface
  - _Requirements: 1.3, 2.3, 2.4, 4.1, 4.2, 4.3, 4.4_

- [x] 3. Update CLI applications to use UniversalAgent
  - Modify main.py to use UniversalAgent instead of OpenRouterAgent
  - Update main.py to display which provider is being used at startup
  - Add command-line parameter support for specifying configuration file in main.py
  - Update orchestrator.py to use UniversalAgent instead of OpenRouterAgent
  - Update make_it_heavy.py to show provider information in the CLI interface
  - Test both single-agent and multi-agent modes with DeepSeek configuration files
  - _Requirements: 3.3, 6.1, 6.2, 6.3, 6.4_

- [x] 4. Create comprehensive integration tests
  - Write integration tests for single-agent mode with DeepSeek configuration
  - Write integration tests for multi-agent orchestration with DeepSeek
  - Test provider switching functionality between OpenRouter and DeepSeek configurations
  - Test error handling and recovery scenarios with both providers
  - Add tests for configuration validation and provider factory functionality
  - Test command-line parameter functionality for configuration file selection
  - _Requirements: 2.4, 4.4, 6.1, 6.2_

- [x] 5. Update documentation and create migration guide
  - Update README.md with DeepSeek integration information and setup instructions
  - Document cost comparison between OpenRouter and DeepSeek models
  - Add troubleshooting section for common DeepSeek-specific issues and configuration problems
  - Include information about DeepSeek's off-peak pricing and optimization tips
  - Create migration guide for users switching from OpenRouter to DeepSeek
  - Add provider selection examples and configuration guidance with sample files
  - Document command-line usage for different configuration files
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 7.3, 7.4_