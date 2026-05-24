"""Orchestrator Agent - LLM-powered workflow coordinator."""
import logging
from src.models import AnalysisState
from src.litellm_integration.llm_client import LLMClient
from src.agents.config import get_llm_config
from src.agents.system_prompts import ORCHESTRATOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


async def orchestrator_agent(state: AnalysisState) -> dict:
    """
    Evaluate current analysis progress and decide next steps.

    Returns a decision dict with 'decision', 'next_stage', and 'reasoning'.
    """
    logger.info("Orchestrator evaluating workflow progress")

    try:
        client = LLMClient(**get_llm_config("orchestrator"))

        # Build a summary of current state for the orchestrator
        state_summary = f"""
Current Analysis State:
- Transcript size: {len(state.transcript_text or '')} chars
- One-pager size: {len(state.one_pager_text or '')} chars
- Jira ID found: {state.jira_id or 'None'}
- Entities extracted: {bool(state.entities)}
- Entity count: {len(state.entities) if state.entities else 0}
- MCP results collected: {len(state.mcp_results)} results
- Aggregated context score: {max((r.get('relevance_score', 0) for r in state.aggregated_context), default=0):.2f}
- Questions generated: {len(state.questions)}
- Execution errors: {len(state.execution_errors)}
"""

        response = await client.call_json([
            {"role": "system", "content": ORCHESTRATOR_SYSTEM_PROMPT},
            {"role": "user", "content": f"Evaluate this analysis progress and decide next steps:\n\n{state_summary}"}
        ])

        decision = response.get("decision", "PROCEED")
        next_stage = response.get("next_stage", "question_generator")
        reasoning = response.get("reasoning", "")
        notes = response.get("notes", "")

        logger.info(f"Orchestrator decision: {decision} → {next_stage} ({reasoning})")

        if not state.orchestrator_notes:
            state.orchestrator_notes = []
        state.orchestrator_notes.append(f"Stage decision: {next_stage} ({reasoning})")
        if notes:
            state.orchestrator_notes.append(notes)

        return {
            "decision": decision,
            "next_stage": next_stage,
            "reasoning": reasoning
        }

    except Exception as e:
        logger.error(f"Orchestrator failed: {e}")
        state.execution_errors.append(f"Orchestrator error: {str(e)}")
        return {
            "decision": "PROCEED",
            "next_stage": "question_generator",
            "reasoning": "Orchestrator failed, proceeding to question generation"
        }
