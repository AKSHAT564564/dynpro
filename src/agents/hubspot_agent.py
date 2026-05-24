"""HubSpot Search Agent - LLM-powered query formulation."""
import logging
from src.models import AnalysisState
from src.litellm_integration.llm_client import LLMClient
from src.agents.config import get_llm_config
from src.agents.system_prompts import HUBSPOT_AGENT_SYSTEM_PROMPT
from src.mcp_integration import MCPManager

logger = logging.getLogger(__name__)

async def hubspot_agent(state: AnalysisState) -> AnalysisState:
    """Query HubSpot for customer feedback and interactions."""
    logger.info("Querying HubSpot...")
    try:
        if not state.entities or not get_llm_config("hubspot_agent"):
            return state

        client = LLMClient(**get_llm_config("hubspot_agent"))
        input_text = f"Entities: {state.entities}\nProposal: {state.one_pager_text[:300]}"

        response = await client.call_json([
            {"role": "system", "content": HUBSPOT_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": f"What should we search for in HubSpot?\n\n{input_text}"}
        ])

        search_queries = response.get("search_queries", [])
        if search_queries:
            manager = MCPManager()
            await manager.initialize()
            hs_adapter = manager.adapters.get("hubspot")
            if hs_adapter:
                results = await hs_adapter.search(search_queries[0])
                logger.info(f"Got {len(results)} results from HubSpot")

        return state
    except Exception as e:
        logger.error(f"HubSpot agent failed: {e}")
        state.execution_errors.append(f"HubSpot search error: {str(e)}")
        return state
