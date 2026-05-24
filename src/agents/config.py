"""
Agent Configuration

Defines LLM models and parameters for each agent in the workflow.
All settings configurable via environment variables with defaults.

Environment variable format: AGENT_<AGENT_NAME>_<FIELD>
Examples:
  AGENT_ORCHESTRATOR_MODEL=gpt-4
  AGENT_QUESTION_GENERATOR_TEMPERATURE=0.7
  AGENT_CONFLUENCE_AGENT_PROVIDER=openai
"""

import os

# Default configuration - used as fallback
DEFAULT_AGENT_CONFIG = {
    "input_processor": {
        "description": "Parse and validate input files",
        "uses_llm": False,
    },
    "orchestrator": {
        "model": "claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "temperature": 0.2,
        "description": "Coordinate workflow and decide next steps",
        "uses_llm": True,
    },
    "entity_extractor": {
        "model": "claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "temperature": 0.3,
        "description": "Extract entities and generate search queries",
        "uses_llm": True,
    },
    "confluence_agent": {
        "model": "claude-3-5-haiku-20241022",
        "provider": "anthropic",
        "temperature": 0.2,
        "description": "Formulate Confluence search query and retrieve results",
        "uses_llm": True,
    },
    "jira_agent": {
        "model": "claude-3-5-haiku-20241022",
        "provider": "anthropic",
        "temperature": 0.2,
        "description": "Formulate JQL query and retrieve Jira results",
        "uses_llm": True,
    },
    "salesforce_agent": {
        "model": "claude-3-5-haiku-20241022",
        "provider": "anthropic",
        "temperature": 0.2,
        "description": "Formulate SOQL query and retrieve Salesforce results",
        "uses_llm": True,
    },
    "hubspot_agent": {
        "model": "claude-3-5-haiku-20241022",
        "provider": "anthropic",
        "temperature": 0.2,
        "description": "Formulate HubSpot search query and retrieve results",
        "uses_llm": True,
    },
    "mcp_query": {
        "description": "Query all configured MCPs in parallel",
        "uses_llm": False,
    },
    "context_aggregator": {
        "model": "claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "temperature": 0.1,
        "description": "Aggregate and score results by relevance",
        "uses_llm": True,
    },
    "resource_storage": {
        "description": "Store resources locally",
        "uses_llm": False,
    },
    "question_generator": {
        "model": "claude-3-opus-20240229",
        "provider": "anthropic",
        "temperature": 0.5,
        "description": "Generate high-quality clarification questions",
        "uses_llm": True,
        "max_tokens": 4096,
    },
    "output_formatter": {
        "description": "Format outputs (Markdown, HTML, JSON)",
        "uses_llm": False,
    },
}


def get_agent_config(agent_name: str) -> dict:
    """
    Get configuration for a specific agent with environment variable overrides.

    Environment variables format: AGENT_<AGENT_NAME>_<FIELD>
    Example: AGENT_ORCHESTRATOR_MODEL, AGENT_QUESTION_GENERATOR_TEMPERATURE

    Args:
        agent_name: Name of the agent (e.g., 'orchestrator', 'confluence_agent')

    Returns:
        Configuration dict with LLM settings
    """
    config = DEFAULT_AGENT_CONFIG.get(agent_name, {}).copy()

    # Override with environment variables: AGENT_<AGENT_NAME>_<FIELD>
    prefix = f"AGENT_{agent_name.upper()}_"
    for field in ["model", "provider", "temperature", "max_tokens"]:
        env_key = f"{prefix}{field.upper()}"
        if env_key in os.environ:
            value = os.environ[env_key]
            # Convert to appropriate types
            if field == "temperature":
                config[field] = float(value)
            elif field == "max_tokens":
                config[field] = int(value)
            else:
                config[field] = value

    return config


def get_llm_config(agent_name: str) -> dict:
    """
    Get LLM configuration for an agent.

    Args:
        agent_name: Name of the agent

    Returns:
        LLM config dict with model, provider, temperature, max_tokens
    """
    config = get_agent_config(agent_name)
    if not config.get("uses_llm"):
        return {}

    return {
        "model": config.get("model"),
        "provider": config.get("provider"),
        "temperature": config.get("temperature"),
        "max_tokens": config.get("max_tokens"),
    }
