"""
Question Generator Agent

Generates clarification questions from aggregated context using LLM.
"""

import logging
import json
from src.models import AnalysisState
from src.litellm_integration.llm_client import LLMClient
from src.agents.config import get_llm_config

logger = logging.getLogger(__name__)


async def question_generator_agent(state: AnalysisState) -> AnalysisState:
    """
    Generate clarification questions from context.

    Creates questions categorized by:
    - Functional requirements
    - Non-functional requirements
    - Business/customer context
    - Dependencies and blockers

    Args:
        state: Current analysis state with aggregated context

    Returns:
        Updated state with generated questions
    """
    logger.info("Generating questions...")

    try:
        if not state.aggregated_context:
            logger.info("No aggregated context available for question generation")
            state.questions = []
            return state

        # Get LLM config
        llm_config = get_llm_config("question_generator")
        if not llm_config:
            logger.warning("No LLM config for question generator")
            state.questions = []
            return state

        # Initialize LLM client
        client = LLMClient(**llm_config)

        # Prepare context summary
        context_summary = _build_context_summary(state)

        # Build prompt
        prompt = _build_question_prompt(context_summary, state.jira_id)

        # Call LLM
        logger.debug("Calling LLM for question generation...")
        response_text = await client.call([{"role": "user", "content": prompt}])

        # Parse response
        try:
            questions = json.loads(response_text)
            if isinstance(questions, dict) and "questions" in questions:
                questions = questions["questions"]
            elif not isinstance(questions, list):
                questions = []
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON, using text response")
            questions = [{"question": response_text, "category": "general"}]

        state.questions = questions

        categories = len(set(q.get("category", "general") for q in questions))
        logger.info(f"Question generation complete (total: {len(questions)}, categories: {categories})")

        return state

    except Exception as e:
        logger.error(f"Question generator failed: {e}")
        state.execution_errors.append(f"Question generation error: {str(e)}")
        state.questions = []
        return state


def _build_context_summary(state: AnalysisState) -> str:
    """Build a summary of aggregated context for the LLM"""
    lines = []

    # Add input summary
    lines.append("## Input Context")
    lines.append(f"Jira ID: {state.jira_id or 'Not found'}")
    lines.append(f"Transcript preview: {state.transcript_text[:300]}...")
    lines.append(f"One-pager preview: {state.one_pager_text[:300]}...")

    # Add extracted entities
    if state.entities:
        lines.append("\n## Extracted Entities")
        for key, value in state.entities.items():
            lines.append(f"- {key}: {value}")

    # Add MCP results summary
    if state.mcp_results:
        lines.append("\n## MCP Results")
        for source, results in state.mcp_results.items():
            lines.append(f"- {source}: {len(results)} results")

    # Add aggregated context summary
    if state.aggregated_context:
        lines.append("\n## Aggregated Context")
        for source, results in state.aggregated_context.items():
            if results:
                lines.append(f"\n### {source.upper()}")
                for result in results[:3]:  # Top 3 results per source
                    lines.append(f"- {result.get('title', 'Untitled')}")
                    lines.append(f"  Score: {result.get('relevance_score', 0)}")

    return "\n".join(lines)


def _build_question_prompt(context: str, jira_id: str = None) -> str:
    """Build the prompt for question generation"""
    return f"""You are a business analyst reviewing a feature proposal.
Based on the context below, generate 8-12 clarification questions the analyst should ask.

Format your response as JSON with this structure:
{{
  "questions": [
    {{
      "category": "functional|nonfunctional|business",
      "question": "What is...",
      "rationale": "Why this matters",
      "priority": "high|medium|low"
    }},
    ...
  ]
}}

Categories:
- functional: Questions about features, functionality, requirements
- nonfunctional: Questions about performance, security, scalability, reliability
- business: Questions about customer needs, business goals, timeline, costs

CONTEXT:
{context}

REQUIREMENTS:
1. Questions should be specific to the proposal, not generic
2. Each question should be actionable and answerable
3. Prioritize questions that identify risks or gaps
4. Reference specific findings from the context when relevant
5. Avoid yes/no questions - ask for clarification and details

Generate questions that would help validate requirements before implementation."""
