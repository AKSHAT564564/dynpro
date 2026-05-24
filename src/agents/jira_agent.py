"""Jira Search Agent - LLM-powered query formulation."""
import logging
from src.models import AnalysisState
from src.litellm_integration.llm_client import LLMClient
from src.agents.config import get_llm_config
from src.agents.system_prompts import JIRA_AGENT_SYSTEM_PROMPT
from src.mcp_integration import MCPManager

logger = logging.getLogger(__name__)

async def jira_agent(state: AnalysisState) -> AnalysisState:
    """Query Jira for related issues and blockers."""
    logger.info("Querying Jira...")
    try:
        if not state.entities or not get_llm_config("jira_agent"):
            return state

        client = LLMClient(**get_llm_config("jira_agent"))
        input_text = f"Entities: {state.entities}\nProposal: {state.one_pager_text[:300]}"

        response = await client.call_json([
            {"role": "system", "content": JIRA_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": f"What should we search for in Jira?\n\n{input_text}"}
        ])

        search_queries = response.get("search_queries", [])
        if search_queries:
            manager = MCPManager()
            await manager.initialize()
            jira_adapter = manager.adapters.get("jira")
            if jira_adapter:
                results = await jira_adapter.search(search_queries[0])
                logger.info(f"Got {len(results)} results from Jira")
                if not state.mcp_results:
                    state.mcp_results = {}
                state.mcp_results["jira"] = results

        return state
    except Exception as e:
        logger.error(f"Jira agent failed: {e}")
        state.execution_errors.append(f"Jira search error: {str(e)}")
        return state
