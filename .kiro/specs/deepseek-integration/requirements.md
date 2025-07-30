# Requirements Document

## Introduction

This feature adds DeepSeek API integration to the Make It Heavy framework as an alternative to OpenRouter. DeepSeek offers competitive AI models with function calling capabilities at significantly lower costs, making it an attractive option for users seeking cost-effective multi-agent orchestration. The integration will maintain full compatibility with existing functionality while providing users the flexibility to choose between OpenRouter and DeepSeek as their API provider.

## Requirements

### Requirement 1

**User Story:** As a developer using Make It Heavy, I want to configure the system to use DeepSeek API instead of OpenRouter, so that I can reduce my API costs while maintaining the same functionality.

#### Acceptance Criteria

1. WHEN I update the configuration file with DeepSeek API credentials THEN the system SHALL use DeepSeek API for all LLM calls
2. WHEN I specify a DeepSeek model in configuration THEN the system SHALL use that specific model (deepseek-chat or deepseek-reasoner)
3. WHEN I run the application with DeepSeek configuration THEN all existing features SHALL work identically to OpenRouter implementation

### Requirement 2

**User Story:** As a user, I want the system to automatically handle DeepSeek-specific API endpoints and authentication, so that I don't need to modify any code beyond configuration.

#### Acceptance Criteria

1. WHEN the system is configured for DeepSeek THEN it SHALL use the correct base URL (https://api.deepseek.com)
2. WHEN making API calls to DeepSeek THEN the system SHALL use proper authentication headers
3. WHEN DeepSeek API returns responses THEN the system SHALL parse them using the same OpenAI-compatible format
4. IF DeepSeek API calls fail THEN the system SHALL provide clear error messages indicating the DeepSeek-specific issue

### Requirement 3

**User Story:** As a developer, I want to easily switch between OpenRouter and DeepSeek configurations, so that I can compare performance and costs between providers.

#### Acceptance Criteria

1. WHEN I have both OpenRouter and DeepSeek configurations THEN I SHALL be able to specify which one to use via command line parameter or configuration
2. WHEN switching between providers THEN no code changes SHALL be required beyond configuration updates
3. WHEN using either provider THEN all tools and function calling SHALL work identically
4. WHEN running in either mode THEN the CLI SHALL clearly indicate which provider is being used

### Requirement 4

**User Story:** As a user, I want the system to support both DeepSeek-Chat and DeepSeek-Reasoner models, so that I can choose the appropriate model for my use case.

#### Acceptance Criteria

1. WHEN I configure deepseek-chat model THEN the system SHALL use DeepSeek-V3 for general purpose tasks
2. WHEN I configure deepseek-reasoner model THEN the system SHALL use DeepSeek-R1 for complex reasoning tasks
3. WHEN using either DeepSeek model THEN function calling SHALL work correctly
4. WHEN model responses are processed THEN the system SHALL handle both model types' output formats correctly

### Requirement 5

**User Story:** As a developer, I want comprehensive documentation and examples for DeepSeek integration, so that I can quickly set up and use the new provider.

#### Acceptance Criteria

1. WHEN I read the documentation THEN it SHALL include step-by-step DeepSeek setup instructions
2. WHEN I follow the setup guide THEN it SHALL include example configuration files for DeepSeek
3. WHEN I need to troubleshoot THEN the documentation SHALL include common DeepSeek-specific issues and solutions
4. WHEN comparing providers THEN the documentation SHALL include cost and performance comparisons

### Requirement 6

**User Story:** As a user running multi-agent orchestration, I want the DeepSeek integration to work seamlessly with parallel agent execution, so that I can benefit from cost savings across all agents.

#### Acceptance Criteria

1. WHEN running multiple agents in parallel with DeepSeek THEN all agents SHALL use DeepSeek API correctly
2. WHEN agents make concurrent API calls to DeepSeek THEN the system SHALL handle rate limiting gracefully
3. WHEN synthesizing results from DeepSeek agents THEN the final output SHALL maintain the same quality as OpenRouter
4. WHEN displaying progress during multi-agent execution THEN the UI SHALL indicate DeepSeek usage

### Requirement 7

**User Story:** As a cost-conscious user, I want to take advantage of DeepSeek's off-peak pricing, so that I can further reduce my API costs.

#### Acceptance Criteria

1. WHEN the system makes API calls during DeepSeek off-peak hours THEN it SHALL automatically benefit from reduced pricing
2. WHEN I check usage statistics THEN the system SHOULD provide information about cost savings
3. WHEN configuring the system THEN documentation SHALL explain DeepSeek's pricing tiers and off-peak hours
4. IF I want to optimize for cost THEN the system SHALL provide guidance on timing usage for maximum savings