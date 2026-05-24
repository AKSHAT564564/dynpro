"""
MCP Query Agent

Queries all configured MCPs in parallel and aggregates results.
"""

import logging
from src.models import AnalysisState
from src.mcp_integration import MCPManager

logger = logging.getLogger(__name__)


async def mcp_query_agent(state: AnalysisState) -> AnalysisState:
    """
    Query all configured MCPs in parallel.

    Executes search across Confluence, Jira, Salesforce, HubSpot, etc.
    Handles failures gracefully - continues with available MCPs.

    Args:
        state: Current analysis state with entities and search queries

    Returns:
        Updated state with MCP results
    """
    logger.info("Querying MCPs...")

    try:
        # Initialize MCP manager
        manager = MCPManager()

        try:
            await manager.initialize()
            logger.debug(f"Initialized {len(manager.adapters)} MCP adapters")
        except Exception as e:
            logger.warning(f"MCP initialization failed, continuing with available MCPs: {e}")
            state.execution_errors.append(f"MCP initialization warning: {str(e)}")

        # If no adapters available, return early
        if not manager.adapters:
            logger.warning("No MCP adapters available")
            state.mcp_results = {}
            return state

        # Build combined search query
        one_pager_preview = state.one_pager_text[:500]

        # Add extracted entities to search
        jira_id_str = f"Jira ID: {state.jira_id}" if state.jira_id else ""

        search_query = f"{one_pager_preview}\n{jira_id_str}".strip()

        logger.debug(f"Searching with query length: {len(search_query)}")

        # Search all MCPs in parallel
        results = await manager.search_all(search_query)

        # Store results
        state.mcp_results = results

        # Log summary
        total_results = sum(len(r) for r in results.values())
        breakdown = {mcp_id: len(r) for mcp_id, r in results.items()}
        logger.info(f"MCP queries complete (mcps: {len(results)}, total_results: {total_results}, breakdown: {breakdown})")

        return state

    except Exception as e:
        logger.error(f"MCP query agent failed: {e}")
        state.execution_errors.append(f"MCP query error: {str(e)}")
        state.mcp_results = {}
        return state
