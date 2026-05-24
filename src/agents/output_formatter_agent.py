"""
Output Formatter Agent

Formats questions, resources, and metadata into consumable outputs:
- questions.md: Formatted questions by category
- report.html: HTML report with analysis
- SOURCE_OF_TRUTH.md: Index of all stored resources
"""

import logging
from pathlib import Path
from datetime import datetime
from src.models import AnalysisState

logger = logging.getLogger(__name__)


async def output_formatter_agent(state: AnalysisState) -> AnalysisState:
    """
    Format analysis results into multiple output formats.

    Creates:
    - questions.md: Categorized questions
    - report.html: HTML report
    - SOURCE_OF_TRUTH.md: Resource index

    Args:
        state: Current analysis state with all results

    Returns:
        Updated state with output_artifacts paths
    """
    logger.info("Formatting output artifacts...")

    try:
        if not state.storage_path:
            logger.warning("No storage path available for output formatting")
            state.output_artifacts = {}
            return state

        output_dir = Path(state.storage_path)

        # Generate questions.md
        questions_md = _format_questions_markdown(state)
        questions_path = output_dir / "questions.md"
        with open(questions_path, "w") as f:
            f.write(questions_md)
        logger.debug(f"Created questions.md")

        # Generate report.html
        report_html = _format_report_html(state)
        report_path = output_dir / "report.html"
        with open(report_path, "w") as f:
            f.write(report_html)
        logger.debug(f"Created report.html")

        # Generate SOURCE_OF_TRUTH.md
        source_of_truth_md = _format_source_of_truth(state)
        source_path = output_dir / "SOURCE_OF_TRUTH.md"
        with open(source_path, "w") as f:
            f.write(source_of_truth_md)
        logger.debug(f"Created SOURCE_OF_TRUTH.md")

        # Store artifact paths in state
        state.output_artifacts = {
            "questions": str(questions_path),
            "report": str(report_path),
            "source_of_truth": str(source_path),
        }

        questions_count = len(state.questions or [])
        resources = (state.storage_metadata or {}).get("resources", [])
        resources_count = len(resources) if resources else 0
        logger.info(f"Output formatting complete (questions: {questions_count}, resources: {resources_count})")

        return state

    except Exception as e:
        logger.error(f"Output formatter failed: {e}")
        state.execution_errors.append(f"Output formatting error: {str(e)}")
        state.output_artifacts = {}
        return state


def _format_questions_markdown(state: AnalysisState) -> str:
    """Format questions as markdown by category"""
    lines = []

    lines.append("# Clarification Questions\n")
    lines.append(f"**Generated**: {datetime.now().isoformat()}\n")
    if state.jira_id:
        lines.append(f"**Jira ID**: {state.jira_id}\n")

    if not state.questions:
        lines.append("No questions generated.\n")
        return "\n".join(lines)

    # Group by category
    by_category = {}
    for q in state.questions:
        cat = q.get("category", "general")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(q)

    # Format by priority category
    category_order = ["functional", "nonfunctional", "business"]
    for cat in category_order:
        if cat not in by_category:
            continue

        lines.append(f"\n## {cat.replace('nonfunctional', 'Non-Functional').title()} Requirements\n")

        for idx, q in enumerate(by_category[cat], 1):
            lines.append(f"### Q{idx}: {q.get('question', 'N/A')}")
            lines.append("")

            if q.get("rationale"):
                lines.append(f"**Rationale**: {q['rationale']}")
                lines.append("")

            if q.get("priority"):
                lines.append(f"**Priority**: {q['priority'].upper()}")
                lines.append("")

    # Add any other categories
    for cat in by_category:
        if cat not in category_order:
            lines.append(f"\n## {cat.title()}\n")
            for idx, q in enumerate(by_category[cat], 1):
                lines.append(f"### {q.get('question', 'N/A')}")
                if q.get("rationale"):
                    lines.append(f"\n**Rationale**: {q['rationale']}\n")

    return "\n".join(lines)


def _format_report_html(state: AnalysisState) -> str:
    """Format analysis as HTML report"""
    execution_time = 0
    if state.execution_start_time:
        execution_time = (datetime.now() - state.execution_start_time).total_seconds()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a73e8;
            border-bottom: 3px solid #1a73e8;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #202124;
            margin-top: 30px;
        }}
        .header-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 4px;
        }}
        .info-item {{
            padding: 10px;
        }}
        .info-label {{
            font-weight: bold;
            color: #666;
            font-size: 0.9em;
        }}
        .info-value {{
            color: #1a73e8;
            font-size: 1.1em;
            margin-top: 5px;
        }}
        .question {{
            padding: 15px;
            margin: 10px 0;
            background: #f9f9f9;
            border-left: 4px solid #1a73e8;
            border-radius: 4px;
        }}
        .question-text {{
            font-weight: bold;
            margin-bottom: 8px;
            color: #202124;
        }}
        .question-meta {{
            font-size: 0.9em;
            color: #666;
        }}
        .priority-high {{ color: #d33b27; font-weight: bold; }}
        .priority-medium {{ color: #f57c00; font-weight: bold; }}
        .priority-low {{ color: #558b2f; font-weight: bold; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-box {{
            padding: 15px;
            background: #e8f0fe;
            border-radius: 4px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #1a73e8;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        .error {{
            padding: 10px;
            margin: 10px 0;
            background: #fce4ec;
            border-left: 4px solid #c2185b;
            border-radius: 4px;
            color: #880e4f;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Feature Proposal Analysis Report</h1>

        <div class="header-info">
            <div class="info-item">
                <div class="info-label">Generated</div>
                <div class="info-value">{datetime.now().isoformat()}</div>
            </div>
            {f'<div class="info-item"><div class="info-label">Jira ID</div><div class="info-value">{state.jira_id}</div></div>' if state.jira_id else ''}
            <div class="info-item">
                <div class="info-label">Execution Time</div>
                <div class="info-value">{execution_time:.2f}s</div>
            </div>
        </div>

        <h2>Analysis Summary</h2>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{len(state.questions or [])}</div>
                <div class="stat-label">Questions</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{sum(len(v) for v in (state.mcp_results or {}).values())}</div>
                <div class="stat-label">MCP Results</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{len(state.entities or {})}</div>
                <div class="stat-label">Entities</div>
            </div>
        </div>

        <h2>Clarification Questions</h2>
"""

    if state.questions:
        by_category = {}
        for q in state.questions:
            cat = q.get("category", "general")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(q)

        for cat in ["functional", "nonfunctional", "business"]:
            if cat not in by_category:
                continue
            html += f"<h3>{cat.replace('nonfunctional', 'Non-Functional').title()}</h3>\n"
            for q in by_category[cat]:
                priority = q.get("priority", "medium")
                html += f"""
        <div class="question">
            <div class="question-text">{q.get('question', 'N/A')}</div>
            <div class="question-meta">
                Priority: <span class="priority-{priority}">{priority.upper()}</span>
                {f" | Rationale: {q.get('rationale', 'N/A')}" if q.get('rationale') else ""}
            </div>
        </div>
"""
    else:
        html += "<p>No questions generated.</p>\n"

    if state.execution_errors:
        html += "<h2>Errors</h2>\n"
        for error in state.execution_errors:
            html += f'<div class="error">{error}</div>\n'

    html += """
    </div>
</body>
</html>
"""
    return html


def _format_source_of_truth(state: AnalysisState) -> str:
    """Generate source of truth index"""
    lines = []

    lines.append("# Source of Truth\n")
    lines.append("Complete index of all extracted resources and context.\n")

    if state.jira_id:
        lines.append(f"**Jira ID**: {state.jira_id}\n")

    lines.append(f"**Generated**: {datetime.now().isoformat()}\n")

    # Extracted entities
    if state.entities:
        lines.append("\n## Extracted Entities\n")
        for key, value in state.entities.items():
            lines.append(f"- **{key}**: {value}")

    # MCP Results summary
    if state.mcp_results:
        lines.append("\n## MCP Results by Source\n")
        for source, results in state.mcp_results.items():
            lines.append(f"\n### {source.upper()} ({len(results)} results)\n")
            for result in results[:10]:  # Top 10 per source
                title = result.get("title", "Untitled")
                url = result.get("url", "")
                lines.append(f"- [{title}]({url})" if url else f"- {title}")

    # Aggregated context
    if state.aggregated_context:
        lines.append("\n## Aggregated Context (Ranked by Relevance)\n")
        for source, results in state.aggregated_context.items():
            lines.append(f"\n### {source.upper()}\n")
            for result in results[:10]:
                title = result.get("title", "Untitled")
                score = result.get("relevance_score", 0)
                url = result.get("url", "")
                lines.append(f"- [{title}]({url}) (score: {score:.2f})" if url else f"- {title} (score: {score:.2f})")

    # Resource storage metadata
    if state.storage_metadata:
        lines.append("\n## Stored Resources\n")
        metadata = state.storage_metadata
        lines.append(f"**Total Resources**: {metadata.get('statistics', {}).get('total_resources', 0)}\n")

        by_source = metadata.get("statistics", {}).get("by_source", {})
        if by_source:
            lines.append("**By Source**:\n")
            for source, count in by_source.items():
                if count > 0:
                    lines.append(f"- {source.title()}: {count}")

    return "\n".join(lines)
