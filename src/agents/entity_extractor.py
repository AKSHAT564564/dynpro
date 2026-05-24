"""
Entity Extractor Agent

Extracts key entities from the proposal and generates search queries using LLM.
"""

import logging
import json
from src.models import AnalysisState
from src.litellm_integration.llm_client import LLMClient
from src.agents.config import get_llm_config
from src.agents.system_prompts import ENTITY_EXTRACTOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


async def entity_extractor_agent(state: AnalysisState) -> AnalysisState:
    """
    Extract entities and generate search queries using LLM.

    Extracts:
    - Jira IDs (e.g., PROJ-123)
    - Product/feature names
    - Customer names
    - Requirements and technical terms
    - Key themes

    Args:
        state: Current analysis state

    Returns:
        Updated state with extracted entities and search queries
    """
    logger.info("Extracting entities using LLM...")

    try:
        # Get LLM config
        llm_config = get_llm_config("entity_extractor")
        if not llm_config:
            logger.warning("No LLM config for entity extractor")
            state.entities = {}
            state.search_queries = {}
            return state

        # Initialize LLM client
        client = LLMClient(**llm_config)

        # Prepare input
        combined_text = f"{state.transcript_text}\n\n{state.one_pager_text}"

        # Call LLM to extract entities
        logger.debug("Calling LLM for entity extraction...")
        response_text = await client.call_json([
            {"role": "system", "content": ENTITY_EXTRACTOR_SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract entities from this proposal:\n\n{combined_text}"}
        ])

        # Extract Jira ID if found
        if "jira_ids" in response_text and response_text["jira_ids"]:
            state.jira_id = response_text["jira_ids"][0]
            logger.info(f"Found Jira ID: {state.jira_id}")

        # Store entities
        state.entities = response_text

        # Generate search queries based on extracted entities
        state.search_queries = _generate_search_queries(response_text)

        logger.info(f"Entity extraction complete (jira_ids: {len(response_text.get('jira_ids', []))}, products: {len(response_text.get('products', []))})")

        return state

    except Exception as e:
        logger.error(f"Entity extractor failed: {e}")
        state.execution_errors.append(f"Entity extraction error: {str(e)}")
        state.entities = {}
        state.search_queries = {}
        return state


def _generate_search_queries(entities: dict) -> dict:
    """
    Generate search queries for each MCP based on extracted entities.

    Args:
        entities: Dictionary of extracted entities

    Returns:
        Dictionary mapping MCP names to lists of search queries
    """
    products = entities.get("products", [])
    requirements = entities.get("requirements", [])
    technical_terms = entities.get("technical_terms", [])
    key_themes = entities.get("key_themes", [])

    # Build queries - combine multiple entity types
    base_terms = products + requirements + technical_terms + key_themes
    base_query = " ".join(base_terms[:3]) if base_terms else "feature proposal"

    return {
        "confluence": [
            base_query,
            "design architecture specification",
            "technical decision record",
        ],
        "jira": [
            base_query,
            "epic story requirements",
            "dependency blocker",
        ],
        "salesforce": [
            base_query,
            "customer opportunity deal",
            "account feedback",
        ],
        "hubspot": [
            base_query,
            "customer contact interaction",
            "deal ticket support",
        ],
    }
