"""Salesforce Search Agent - LLM-powered query formulation."""
import logging
from src.models import AnalysisState
from src.litellm_integration.llm_client import LLMClient
from src.agents.config import get_llm_config
from src.agents.system_prompts import SALESFORCE_AGENT_SYSTEM_PROMPT
from src.mcp_integration import MCPManager

logger = logging.getLogger(__name__)

async def salesforce_agent(state: AnalysisState) -> AnalysisState:
    """Query Salesforce for customer context and deals."""
    logger.info("Querying Salesforce...")
    try:
        if not state.entities or not get_llm_config("salesforce_agent"):
            return state

        client = LLMClient(**get_llm_config("salesforce_agent"))
        input_text = f"Entities: {state.entities}\nProposal: {state.one_pager_text[:300]}"

        response = await client.call_json([
            {"role": "system", "content": SALESFORCE_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": f"What should we search for in Salesforce?\n\n{input_text}"}
        ])

        search_queries = response.get("search_queries", [])
        if search_queries:
            manager = MCPManager()
            await manager.initialize()
            sf_adapter = manager.adapters.get("salesforce")
            if sf_adapter:
                results = await sf_adapter.search(search_queries[0])
                logger.info(f"Got {len(results)} results from Salesforce")
                if not state.mcp_results:
                    state.mcp_results = {}
                state.mcp_results["salesforce"] = results

        return state
    except Exception as e:
        logger.error(f"Salesforce agent failed: {e}")
        state.execution_errors.append(f"Salesforce search error: {str(e)}")
        return state
