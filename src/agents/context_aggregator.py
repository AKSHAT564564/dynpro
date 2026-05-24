"""
Context Aggregator Agent

Deduplicates, scores, and organizes results from all MCPs using LLM-powered semantic relevance.
"""

import logging
from typing import Dict, List
import json
from src.models import AnalysisState
from src.litellm_integration.llm_client import LLMClient
from src.agents.config import get_llm_config
from src.agents.system_prompts import CONTEXT_AGGREGATOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


async def context_aggregator_agent(state: AnalysisState) -> AnalysisState:
    """
    Aggregate and score context from all MCPs using LLM semantic relevance.

    Performs:
    1. Deduplication by URL/ID
    2. LLM-powered semantic relevance scoring
    3. Organization by source and type
    4. Ranking by relevance

    Args:
        state: Current analysis state with MCP results

    Returns:
        Updated state with aggregated context
    """
    logger.info("Aggregating context from MCPs...")

    try:
        if not state.mcp_results:
            logger.info("No MCP results to aggregate")
            state.aggregated_context = {}
            return state

        aggregated = {}
        client = LLMClient(**get_llm_config("context_aggregator"))

        for source, results in state.mcp_results.items():
            logger.debug(f"Processing {len(results)} results from {source}")

            # Deduplicate by URL or ID
            unique_results = {}
            for result in results:
                key = result.get("url") or result.get("id") or str(result)
                if key not in unique_results:
                    unique_results[key] = result

            logger.debug(f"Deduplicated to {len(unique_results)} unique results from {source}")

            # Score relevance using LLM
            scored_results = []
            for result in unique_results.values():
                try:
                    # Prepare result summary for LLM scoring
                    result_text = f"""
Title: {result.get('title', 'N/A')}
Content: {result.get('content', 'N/A')[:500]}
Source: {source}
"""

                    proposal_context = f"""
Proposal: {state.one_pager_text[:300]}
Key Entities: {json.dumps(state.entities or {}, default=str)[:300]}
"""

                    response = await client.call_json([
                        {"role": "system", "content": CONTEXT_AGGREGATOR_SYSTEM_PROMPT},
                        {"role": "user", "content": f"Score this result's relevance to the proposal:\n\n{result_text}\n\nProposal context:\n{proposal_context}"}
                    ])

                    score = response.get("relevance_score", 0.5)
                    if isinstance(score, str):
                        score = float(score) / 100 if float(score) > 1 else float(score)

                except Exception as e:
                    logger.debug(f"LLM scoring failed for result, using fallback: {e}")
                    score = result.get("relevance_weight", 0.5)

                scored_results.append({
                    **result,
                    "relevance_score": round(min(1.0, max(0.0, score)), 2),
                })

            # Sort by relevance (descending)
            scored_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

            aggregated[source] = scored_results

        state.aggregated_context = aggregated

        # Log summary
        total_results = sum(len(v) for v in aggregated.values())
        by_source = {src: len(results) for src, results in aggregated.items()}
        logger.info(f"Context aggregation complete (sources: {len(aggregated)}, total: {total_results}, by_source: {by_source})")

        return state

    except Exception as e:
        logger.error(f"Context aggregator failed: {e}")
        state.execution_errors.append(f"Context aggregation error: {str(e)}")
        state.aggregated_context = {}
        return state
