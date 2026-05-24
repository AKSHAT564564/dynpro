"""
Context Aggregator Agent

Deduplicates, scores, and organizes results from all MCPs.
"""

import logging
from typing import Dict, List
from src.models import AnalysisState

logger = logging.getLogger(__name__)


async def context_aggregator_agent(state: AnalysisState) -> AnalysisState:
    """
    Aggregate and score context from all MCPs.

    Performs:
    1. Deduplication by URL/ID
    2. Relevance scoring (basic keyword matching)
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

        for source, results in state.mcp_results.items():
            logger.debug(f"Processing {len(results)} results from {source}")

            # Deduplicate by URL or ID
            unique_results = {}
            for result in results:
                key = result.get("url") or result.get("id") or str(result)
                if key not in unique_results:
                    unique_results[key] = result

            logger.debug(f"Deduplicated to {len(unique_results)} unique results from {source}")

            # Score relevance (basic implementation)
            scored_results = []
            for result in unique_results.values():
                # Base score from MCP config relevance_weight
                score = result.get("relevance_weight", 0.8)

                # Boost score if keywords match
                title = str(result.get("title", "")).lower()
                content = str(result.get("content", "")).lower()
                keywords = ["requirement", "specification", "design", "architecture", "feature"]

                for keyword in keywords:
                    if keyword in title or keyword in content:
                        score = min(1.0, score + 0.05)  # Max 1.0

                scored_results.append({
                    **result,
                    "relevance_score": round(score, 2),
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
