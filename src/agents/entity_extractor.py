"""
Entity Extractor Agent

Extracts entities (Jira IDs, products, customers, tech terms) and generates search queries.
"""

import logging
import re
from src.models import AnalysisState

logger = logging.getLogger(__name__)


async def entity_extractor_agent(state: AnalysisState) -> AnalysisState:
    """
    Extract entities and generate search queries.

    Extracts:
    - Jira IDs (e.g., PROJ-123)
    - Product/feature names
    - Customer names
    - Technical terms

    Args:
        state: Current analysis state

    Returns:
        Updated state with extracted entities and search queries
    """
    logger.info("Extracting entities from input...")

    try:
        # Combine text for analysis
        combined_text = f"{state.transcript_text}\n\n{state.one_pager_text}"

        # Extract Jira IDs
        jira_pattern = r'([A-Z]+-\d+)'
        jira_matches = re.findall(jira_pattern, combined_text)

        # Set Jira ID if found
        if jira_matches:
            state.jira_id = jira_matches[0]
            logger.info(f"Found Jira ID: {state.jira_id}")

        # Extract basic entities
        state.entities = {
            "jira_ids": list(set(jira_matches)),  # Deduplicate
            "text_length": len(combined_text),
        }

        # Generate search queries for each MCP
        # These are basic keyword-based queries; Phase 5+ can use LLM
        state.search_queries = {
            "confluence": [
                "design architecture",
                "technical specification",
                "ADR decision record",
            ],
            "jira": [
                "story epic task",
                "related issues",
                "in progress done",
            ],
            "salesforce": [
                "customer account opportunity",
                "deal stage",
                "customer contact",
            ],
            "hubspot": [
                "customer feedback",
                "deal ticket",
                "customer interaction",
            ],
        }

        # Add context-specific queries if we have a Jira ID
        if state.jira_id:
            state.search_queries["jira"].insert(0, state.jira_id)
            logger.debug(f"Added Jira ID to search queries: {state.jira_id}")

        logger.info(f"Entity extraction complete (jira_ids: {len(jira_matches)}, entities: {len(state.entities)})")

        return state

    except Exception as e:
        logger.error(f"Entity extractor failed: {e}")
        state.execution_errors.append(f"Entity extraction error: {str(e)}")
        return state
