"""
Data Models for the Application

Pydantic models for request/response handling and internal state management.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalysisState(BaseModel):
    """
    LangGraph State Schema

    This model represents the state that flows through all agents in the LangGraph workflow.
    Each agent updates relevant fields as it processes the analysis.
    """

    # ========== Input Data ==========
    transcript_text: str = Field(description="Transcript content from analyst")
    one_pager_text: str = Field(description="One-pager document content")
    jira_id: Optional[str] = Field(default=None, description="Detected Jira issue ID (e.g., PROJ-123)")

    # ========== Entity Extraction Results ==========
    entities: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Extracted entities: Jira IDs, products, customers, technical terms"
    )
    search_queries: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Search queries generated for each MCP (confluence, jira, salesforce, hubspot)"
    )

    # ========== MCP Query Results ==========
    mcp_results: Optional[Dict[str, List[Dict[str, Any]]]] = Field(
        default=None,
        description="Raw results from all MCPs, organized by source"
    )

    # ========== Aggregated Context ==========
    aggregated_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Aggregated, deduplicated, and scored context from all MCPs"
    )

    # ========== Resource Storage ==========
    storage_path: Optional[str] = Field(
        default=None,
        description="Path to output folder where resources are stored"
    )
    storage_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadata about stored resources (count, timestamps, etc.)"
    )

    # ========== Generated Output ==========
    questions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Generated questions categorized by type (functional, non-functional, business)"
    )
    output_artifacts: Optional[Dict[str, str]] = Field(
        default=None,
        description="Paths to generated output files (questions.md, report.html, etc.)"
    )

    # ========== Execution Tracking ==========
    execution_errors: List[str] = Field(
        default_factory=list,
        description="Errors encountered during execution"
    )
    execution_start_time: Optional[datetime] = Field(
        default=None,
        description="Timestamp when analysis started"
    )
    orchestrator_notes: Optional[List[str]] = Field(
        default=None,
        description="Notes from orchestrator about workflow decisions"
    )

    class Config:
        """Pydantic configuration"""
        arbitrary_types_allowed = True


class AnalysisRequest(BaseModel):
    """
    API Request Model for Analysis Endpoint

    Analyst submits transcript and one-pager files for analysis.
    """

    jira_id: Optional[str] = Field(
        default=None,
        description="(Optional) Jira issue ID. If provided, output folder will use this as name."
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "jira_id": "PROJ-123"
            }
        }


class AnalysisResponse(BaseModel):
    """
    API Response Model for Analysis Endpoint

    Returns results of analysis and paths to generated artifacts.
    """

    status: str = Field(
        description="Analysis status: 'success' (all MCPs queried), 'partial' (some MCPs failed), 'failed' (complete failure)"
    )
    output_path: str = Field(
        description="Path to output folder containing all generated artifacts"
    )
    artifacts: Dict[str, str] = Field(
        description="Mapping of artifact names to their file paths"
    )
    execution_time: float = Field(
        description="Total execution time in seconds"
    )
    jira_id: Optional[str] = Field(
        default=None,
        description="Jira ID used for output folder naming"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Any errors encountered during execution"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "status": "success",
                "output_path": "./output/PROJ-123/",
                "artifacts": {
                    "questions": "./output/PROJ-123/questions.md",
                    "report": "./output/PROJ-123/report.html",
                    "source_of_truth": "./output/PROJ-123/SOURCE_OF_TRUTH.md",
                    "metadata": "./output/PROJ-123/metadata.json"
                },
                "execution_time": 127.45,
                "jira_id": "PROJ-123",
                "errors": []
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(description="Service status")
    version: str = Field(description="API version")
    environment: str = Field(description="Running environment (development/production)")


class MCPListResponse(BaseModel):
    """MCP listing response"""

    mcps: List[Dict[str, Any]] = Field(
        description="List of configured MCPs with their status"
    )
    total: int = Field(description="Total number of MCPs")
    enabled: int = Field(description="Number of enabled MCPs")
