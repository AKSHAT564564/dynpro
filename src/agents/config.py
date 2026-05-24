"""
Agent Configuration

Defines LLM models and parameters for each agent in the workflow.
"""

AGENT_CONFIG = {
    "input_processor": {
        "description": "Parse and validate input files",
        "uses_llm": False,
    },
    "entity_extractor": {
        "model": "claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "temperature": 0.3,
        "description": "Extract entities and generate search queries",
        "uses_llm": True,
    },
    "confluence_query": {
        "model": "gpt-4-turbo",
        "provider": "openai",
        "temperature": 0.2,
        "description": "Query Confluence for design docs",
        "uses_llm": True,
    },
    "jira_query": {
        "model": "gpt-4-turbo",
        "provider": "openai",
        "temperature": 0.2,
        "description": "Query Jira for issues",
        "uses_llm": True,
    },
    "salesforce_query": {
        "model": "claude-3-haiku-20240307",
        "provider": "anthropic",
        "temperature": 0.2,
        "description": "Query Salesforce for customer context",
        "uses_llm": True,
    },
    "hubspot_query": {
        "model": "claude-3-haiku-20240307",
        "provider": "anthropic",
        "temperature": 0.2,
        "description": "Query HubSpot for feedback",
        "uses_llm": True,
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
        "model": "claude-3-opus-20250219",
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
    """Get configuration for a specific agent"""
    return AGENT_CONFIG.get(agent_name, {})


def get_llm_config(agent_name: str) -> dict:
    """Get LLM configuration for an agent"""
    config = get_agent_config(agent_name)
    if not config.get("uses_llm"):
        return {}

    return {
        "model": config.get("model"),
        "provider": config.get("provider"),
        "temperature": config.get("temperature"),
        "max_tokens": config.get("max_tokens"),
    }
