"""
API Routes

Defines all API endpoints for the application.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import time
import logging
from datetime import datetime
from pathlib import Path

from src.models import AnalysisResponse, AnalysisState
from src.config import settings
from src.agents.workflow import get_workflow

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    transcript: UploadFile = File(..., description="Meeting transcript or notes"),
    one_pager: UploadFile = File(..., description="One-pager or proposal document"),
):
    """
    Analyze transcript and one-pager documents.

    Aggregates context from configured MCPs (Confluence, Jira, Salesforce, HubSpot)
    and generates clarification questions for business analyst review.

    Args:
        transcript: Transcript file (txt, md, pdf)
        one_pager: One-pager file (txt, md, pdf)

    Returns:
        AnalysisResponse with status, output path, artifacts, and execution time

    Raises:
        HTTPException: If analysis fails or files are invalid
    """
    start_time = time.time()
    analysis_state = None

    try:
        # Read files
        logger.info("Reading input files...")
        transcript_text = (await transcript.read()).decode('utf-8')
        one_pager_text = (await one_pager.read()).decode('utf-8')

        if not transcript_text or not one_pager_text:
            raise ValueError("Input files cannot be empty")

        logger.info(f"Files read successfully (transcript: {len(transcript_text)} bytes, one_pager: {len(one_pager_text)} bytes)")

        # Create initial analysis state
        analysis_state = AnalysisState(
            transcript_text=transcript_text,
            one_pager_text=one_pager_text,
            execution_start_time=datetime.now(),
        )

        # Invoke LangGraph workflow
        logger.info("Invoking analysis workflow...")
        workflow = get_workflow()
        final_state = await workflow.ainvoke(analysis_state.model_dump())

        # Convert final_state dict back to AnalysisState object
        final_state = AnalysisState(**final_state)

        # Determine output folder name
        output_folder = final_state.jira_id or f"analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        output_path = Path(settings.OUTPUT_DIR) / output_folder

        # Create output directory if needed
        output_path.mkdir(parents=True, exist_ok=True)

        # Store metadata about the analysis
        import json
        metadata = {
            "jira_id": final_state.jira_id,
            "generated_at": datetime.now().isoformat(),
            "execution_time": time.time() - start_time,
            "entities": final_state.entities,
            "mcp_results_count": sum(len(r) for r in (final_state.mcp_results or {}).values()),
            "errors": final_state.execution_errors,
        }
        with open(output_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        execution_time = time.time() - start_time

        logger.info(f"Analysis completed (jira_id: {final_state.jira_id}, time: {execution_time:.2f}s, errors: {len(final_state.execution_errors)})")

        artifacts = {
            "metadata": str(output_path / "metadata.json"),
        }

        if final_state.output_artifacts:
            artifacts.update(final_state.output_artifacts)

        return AnalysisResponse(
            status="success" if not final_state.execution_errors else "partial",
            output_path=str(output_path),
            artifacts=artifacts,
            execution_time=execution_time,
            jira_id=final_state.jira_id,
            errors=final_state.execution_errors,
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        execution_time = time.time() - start_time
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        execution_time = time.time() - start_time

        # Return partial response with error
        if analysis_state:
            analysis_state.execution_errors.append(str(e))

        raise HTTPException(status_code=500, detail=str(e))
