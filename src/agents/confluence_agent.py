"""
Confluence Search Agent

LLM-powered agent that queries Confluence for design docs and specifications.
"""

import logging
from src.models import AnalysisState
from src.litellm_integration.llm_client import LLMClient
from src.agents.config import get_llm_config
from src.agents.system_prompts import CONFLUENCE_AGENT_SYSTEM_PROMPT
from src.mcp_integration import MCPManager

logger = logging.getLogger(__name__)


async def confluence_agent(state: AnalysisState) -> AnalysisState:
    """
    Query Confluence for relevant context using LLM to formulate the search query.

    Args:
        state: Current analysis state with entities extracted

    Returns:
        Updated state with confluence_results
    """
    logger.info("Querying Confluence...")

    try:
        if not state.entities:
            logger.info("No entities available for Confluence search")
            return state

        # Get LLM config for confluence agent
        llm_config = get_llm_config("confluence_agent")
        if not llm_config:
            logger.warning("No LLM config for confluence agent")
            return state

        # Initialize LLM client
        client = LLMClient(**llm_config)

        # Prepare input for LLM
        input_text = f"""
Extracted entities:
- Products: {state.entities.get('products', [])}
- Requirements: {state.entities.get('requirements', [])}
- Technical terms: {state.entities.get('technical_terms', [])}

Proposal summary: {state.one_pager_text[:300]}
"""

        # LLM formulates the search query
        logger.debug("Calling LLM to formulate Confluence search query...")
        response = await client.call_json([
            {"role": "system", "content": CONFLUENCE_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": f"What should we search for in Confluence?\n\n{input_text}"}
        ])

        search_queries = response.get("search_queries", [])
        if not search_queries:
            logger.info("No search queries generated for Confluence")
            return state

        # Execute search with MCPManager
        manager = MCPManager()
        await manager.initialize()

        confluence_adapter = manager.adapters.get("confluence")
        if not confluence_adapter:
            logger.warning("Confluence adapter not initialized")
            return state

        # Execute the first search query
        results = await confluence_adapter.search(search_queries[0])
        logger.info(f"Got {len(results)} results from Confluence")

        if not state.mcp_results:
            state.mcp_results = {}
        state.mcp_results["confluence"] = results

        return state

    except Exception as e:
        logger.error(f"Confluence agent failed: {e}")
        state.execution_errors.append(f"Confluence search error: {str(e)}")
        return state
