"""
Resource Storage Agent

Extracts, downloads, and stores resources locally for future reference.
Creates a "source of truth" snapshot of all gathered context.
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from src.models import AnalysisState
from src.config import settings

logger = logging.getLogger(__name__)


async def resource_storage_agent(state: AnalysisState) -> AnalysisState:
    """
    Store resources locally for future reference.

    Creates folder structure:
    ./output/[JIRA-ID]/
    ├── resources/
    │   ├── confluence/
    │   ├── jira/
    │   ├── salesforce/
    │   └── hubspot/
    └── metadata.json

    Args:
        state: Current analysis state with aggregated context

    Returns:
        Updated state with storage path and metadata
    """
    logger.info("Storing resources locally...")

    try:
        # Determine output folder
        folder_name = state.jira_id or f"analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        output_dir = Path(settings.OUTPUT_DIR) / folder_name
        resources_dir = output_dir / "resources"

        # Create directories
        for source in ["confluence", "jira", "salesforce", "hubspot"]:
            (resources_dir / source).mkdir(parents=True, exist_ok=True)

        logger.debug(f"Created directory structure: {output_dir}")

        # Store resources from aggregated context
        resource_manifest = []
        total_resources = 0

        if state.aggregated_context:
            for source, results in state.aggregated_context.items():
                source_dir = resources_dir / source

                for idx, result in enumerate(results, 1):
                    try:
                        # Create filename
                        filename = f"{source}-{idx:03d}.json"
                        filepath = source_dir / filename

                        # Extract and store resource
                        resource_data = {
                            "id": result.get("id", f"{source}-{idx}"),
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "source": source,
                            "relevance_score": result.get("relevance_score", 0),
                            "extracted_at": datetime.now().isoformat(),
                        }

                        # Add raw data
                        if "raw" in result:
                            resource_data["raw"] = result["raw"]

                        # Save to file
                        with open(filepath, "w") as f:
                            json.dump(resource_data, f, indent=2)

                        # Add to manifest
                        resource_manifest.append({
                            "id": resource_data["id"],
                            "source": source,
                            "title": resource_data["title"],
                            "file": filename,
                            "relevance_score": resource_data["relevance_score"],
                        })

                        total_resources += 1

                    except Exception as e:
                        logger.warning(f"Failed to store resource {source}-{idx}: {e}")

        # Create metadata
        metadata = {
            "jira_id": state.jira_id,
            "generated_at": datetime.now().isoformat(),
            "extracted_from": {
                "transcript_length": len(state.transcript_text),
                "one_pager_length": len(state.one_pager_text),
            },
            "resources": resource_manifest,
            "statistics": {
                "total_resources": total_resources,
                "by_source": {
                    source: sum(1 for r in resource_manifest if r["source"] == source)
                    for source in ["confluence", "jira", "salesforce", "hubspot"]
                },
            },
        }

        # Save metadata
        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        # Update state
        state.storage_path = str(output_dir)
        state.storage_metadata = metadata

        logger.info(f"Resource storage complete (folder: {folder_name}, total: {total_resources}, by_source: {metadata['statistics']['by_source']})")

        return state

    except Exception as e:
        logger.error(f"Resource storage agent failed: {e}")
        state.execution_errors.append(f"Resource storage error: {str(e)}")
        return state
