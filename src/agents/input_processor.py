"""
Input Processor Agent

Validates and normalizes input documents.
"""

import logging
from src.models import AnalysisState

logger = logging.getLogger(__name__)


async def input_processor_agent(state: AnalysisState) -> AnalysisState:
    """
    Process and validate input documents.

    Args:
        state: Current analysis state

    Returns:
        Updated state with normalized text
    """
    logger.info("Processing input documents...")

    try:
        # Normalize text
        state.transcript_text = state.transcript_text.strip()
        state.one_pager_text = state.one_pager_text.strip()

        # Validate
        if not state.transcript_text:
            state.execution_errors.append("Transcript is empty")
            logger.error("Transcript validation failed: empty")

        if not state.one_pager_text:
            state.execution_errors.append("One-pager is empty")
            logger.error("One-pager validation failed: empty")

        logger.info(f"Input processing complete (transcript: {len(state.transcript_text)} bytes, one_pager: {len(state.one_pager_text)} bytes, errors: {len(state.execution_errors)})")

        return state

    except Exception as e:
        logger.error(f"Input processor failed: {e}")
        state.execution_errors.append(f"Input processor error: {str(e)}")
        return state
