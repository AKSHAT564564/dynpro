"""
LangGraph Workflow

Defines the state graph and orchestrates all agents.
"""

import logging
from langgraph.graph import StateGraph, END
from src.models import AnalysisState
from src.agents.input_processor import input_processor_agent
from src.agents.entity_extractor import entity_extractor_agent
from src.agents.mcp_query_agent import mcp_query_agent
from src.agents.context_aggregator import context_aggregator_agent
from src.agents.resource_storage_agent import resource_storage_agent
from src.agents.question_generator_agent import question_generator_agent
from src.agents.output_formatter_agent import output_formatter_agent

logger = logging.getLogger(__name__)


def build_analysis_workflow():
    """
    Build the LangGraph workflow for analysis.

    Workflow sequence:
    1. Input Processor - Validate and normalize input
    2. Entity Extractor - Extract entities and generate queries
    3. MCP Query - Query all MCPs in parallel
    4. Context Aggregator - Deduplicate and score results
    5. Resource Storage - Store resources locally
    6. Question Generator - Generate clarification questions
    7. Output Formatter - Format outputs (questions.md, report.html, SOURCE_OF_TRUTH.md)

    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Building analysis workflow...")

    # Create state graph
    workflow = StateGraph(AnalysisState)

    # Add agent nodes
    workflow.add_node("input_processor", input_processor_agent)
    workflow.add_node("entity_extractor", entity_extractor_agent)
    workflow.add_node("mcp_query", mcp_query_agent)
    workflow.add_node("context_aggregator", context_aggregator_agent)
    workflow.add_node("resource_storage", resource_storage_agent)
    workflow.add_node("question_generator", question_generator_agent)
    workflow.add_node("output_formatter", output_formatter_agent)

    logger.debug("Added agent nodes to workflow")

    # Define entry point
    workflow.set_entry_point("input_processor")

    # Define edges (dependencies between agents)
    workflow.add_edge("input_processor", "entity_extractor")
    workflow.add_edge("entity_extractor", "mcp_query")
    workflow.add_edge("mcp_query", "context_aggregator")
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
