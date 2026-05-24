"""
LangGraph Workflow

Defines the state graph and orchestrates all agents.
"""

import logging
import asyncio
from langgraph.graph import StateGraph, END
from src.models import AnalysisState
from src.agents.input_processor import input_processor_agent
from src.agents.entity_extractor import entity_extractor_agent
from src.agents.orchestrator_agent import orchestrator_agent
from src.agents.confluence_agent import confluence_agent
from src.agents.jira_agent import jira_agent
from src.agents.salesforce_agent import salesforce_agent
from src.agents.hubspot_agent import hubspot_agent
from src.agents.context_aggregator import context_aggregator_agent
from src.agents.resource_storage_agent import resource_storage_agent
from src.agents.question_generator_agent import question_generator_agent
from src.agents.output_formatter_agent import output_formatter_agent

logger = logging.getLogger(__name__)


def _wrap_agent(agent_func):
    """Wrap an agent to ensure it returns a dict for LangGraph."""
    async def wrapper(state: dict) -> dict:
        analysis_state = AnalysisState(**state) if isinstance(state, dict) else state
        result = await agent_func(analysis_state)
        if isinstance(result, AnalysisState):
            return result.model_dump(exclude_none=True)
        return result
    return wrapper


async def parallel_mcp_queries(state: AnalysisState) -> dict:
    """
    Execute all 4 MCP source queries in parallel.

    This node orchestrates concurrent calls to Confluence, Jira, Salesforce, and HubSpot agents.
    """
    logger.info("Starting parallel MCP queries...")

    if not state.entities:
        logger.info("No entities for MCP queries, skipping")
        if not state.mcp_results:
            state.mcp_results = {}
        return state.model_dump(exclude_none=True)

    # Initialize mcp_results dict if needed
    if not state.mcp_results:
        state.mcp_results = {}

    # Run all 4 agents concurrently
    results = await asyncio.gather(
        confluence_agent(state),
        jira_agent(state),
        salesforce_agent(state),
        hubspot_agent(state),
        return_exceptions=True
    )

    # Merge results from all agents into the state
    for result in results:
        if isinstance(result, Exception):
            logger.warning(f"MCP agent failed: {result}")
            state.execution_errors.append(str(result))
        elif isinstance(result, AnalysisState):
            # Merge mcp_results from this agent
            if result.mcp_results:
                state.mcp_results.update(result.mcp_results)
            # Merge any errors
            if result.execution_errors:
                for error in result.execution_errors:
                    if error not in state.execution_errors:
                        state.execution_errors.append(error)

    logger.info(f"Parallel MCP queries complete (sources: {len(state.mcp_results)}, total results: {sum(len(r) for r in state.mcp_results.values())})")
    return state.model_dump(exclude_none=True)


def build_analysis_workflow():
    """
    Build the LangGraph workflow for analysis.

    Workflow sequence:
    1. Input Processor - Validate and normalize input
    2. Entity Extractor - Extract entities and generate queries
    3. Orchestrator - Decide what to do next
    4. Parallel MCP Queries - Query Confluence, Jira, Salesforce, HubSpot concurrently
    5. Context Aggregator - Score and rank results by relevance
    6. Resource Storage - Store resources locally
    7. Question Generator - Generate clarification questions
    8. Output Formatter - Format outputs (questions.md, report.html, SOURCE_OF_TRUTH.md)

    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Building analysis workflow...")

    # Create state graph
    workflow = StateGraph(AnalysisState)

    # Add agent nodes with wrapper to ensure dict returns
    workflow.add_node("input_processor", _wrap_agent(input_processor_agent))
    workflow.add_node("entity_extractor", _wrap_agent(entity_extractor_agent))
    workflow.add_node("orchestrator", _wrap_agent(orchestrator_agent))
    workflow.add_node("parallel_mcp_queries", parallel_mcp_queries)
    workflow.add_node("context_aggregator", _wrap_agent(context_aggregator_agent))
    workflow.add_node("resource_storage", _wrap_agent(resource_storage_agent))
    workflow.add_node("question_generator", _wrap_agent(question_generator_agent))
    workflow.add_node("output_formatter", _wrap_agent(output_formatter_agent))

    logger.debug("Added agent nodes to workflow")

    # Define entry point
    workflow.set_entry_point("input_processor")

    # Define edges (dependencies between agents)
    workflow.add_edge("input_processor", "entity_extractor")
    workflow.add_edge("entity_extractor", "orchestrator")
    workflow.add_edge("orchestrator", "parallel_mcp_queries")
    workflow.add_edge("parallel_mcp_queries", "context_aggregator")
    workflow.add_edge("context_aggregator", "resource_storage")
    workflow.add_edge("resource_storage", "question_generator")
    workflow.add_edge("question_generator", "output_formatter")
    workflow.add_edge("output_formatter", END)

    logger.debug("Defined workflow edges")

    # Compile workflow
    compiled_workflow = workflow.compile()

    logger.info("Workflow built successfully")

    return compiled_workflow


# Singleton instance
_workflow_instance = None


def get_workflow():
    """Get or create the analysis workflow"""
    global _workflow_instance
    if _workflow_instance is None:
        _workflow_instance = build_analysis_workflow()
    return _workflow_instance
