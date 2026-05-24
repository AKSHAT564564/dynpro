# System Architecture - Context-Aware Question Generation Tool

## 1. High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          INPUT LAYER                                    │
│  ┌──────────────────────┐  ┌──────────────────────┐                    │
│  │   Transcript File    │  │   One-Pager File     │                    │
│  └──────────┬───────────┘  └──────────┬───────────┘                    │
└─────────────┼────────────────────────┼──────────────────────────────────┘
              │                        │
              └────────────┬───────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────────────┐
│              ENTITY EXTRACTION & ANALYSIS LAYER                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ • Extract key terms (product, customer, feature, tech)          │  │
│  │ • Identify Jira IDs (PROJ-123)                                  │  │
│  │ • Extract entity names and keywords                             │  │
│  │ • Generate search queries                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────┬──────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌──────▼──────┐ ┌───────▼────────────┐ ┌──────▼──────┐
│ CONFLUENCE MCP │ │  JIRA MCP   │ │ SALESFORCE CRM MCP │ │ HUBSPOT MCP │
│ ┌────────────┐ │ ┌──────────┐ │ │ ┌───────────────┐ │ │ ┌──────────┐ │
│ │• Design    │ │ │• Issues  │ │ │ │• Accounts     │ │ │ │• Contacts│ │
│ │  Docs      │ │ │• Epics   │ │ │ │• Opportunities│ │ │ │• Deals   │ │
│ │• ADRs      │ │ │• Stories │ │ │ │• Contracts    │ │ │ │• Feedback│ │
│ │• Tech Spec │ │ │• Bugs    │ │ │ │• Interactions│ │ │ │• Tickets │ │
│ └────────────┘ │ └──────────┘ │ │ └───────────────┘ │ │ └──────────┘ │
└────────────────┘ └─────────────┘ └───────────────────┘ └─────────────┘
        │                 │                 │                 │
        └─────────────────┼─────────────────┴─────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────────────┐
│         CONTEXT AGGREGATION & RESOURCE STORAGE LAYER                   │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │ • Merge results from all MCPs                                 │   │
│  │ • Deduplicate and rank by relevance                           │   │
│  │ • Extract and download resources                              │   │
│  │ • Create folder structure: ./output/[JIRA-ID]/                │   │
│  │   ├── resources/                                              │   │
│  │   │   ├── confluence/                                         │   │
│  │   │   ├── jira/                                               │   │
│  │   │   ├── salesforce/                                         │   │
│  │   │   └── hubspot/                                            │   │
│  │   └── metadata.json                                           │   │
│  └────────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬──────────────────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────────────┐
│           QUESTION GENERATION & ANALYSIS LAYER                         │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │ • Analyze aggregated context                                  │   │
│  │ • Generate categorized questions                              │   │
│  │ • Link questions to source resources                          │   │
│  │ • Identify dependencies, blockers, gaps                       │   │
│  │ • Prioritize by relevance and impact                          │   │
│  └────────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬──────────────────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────────────┐
│              OUTPUT GENERATION LAYER                                    │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │ • Generate markdown question document                          │   │
│  │ • Create source-of-truth index                                 │   │
│  │ • Generate manifest file                                       │   │
│  │ • Link to stored resources                                     │   │
│  │ • Export to multiple formats (PDF, Docs, etc.)                 │   │
│  └────────────────────────────────────────────────────────────────┘   │
└─────────────────────────┬──────────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │   OUTPUT ARTIFACTS                  │
        │  ┌──────────────────────────────┐  │
        │  │ questions.md                 │  │
        │  │ (Question document)          │  │
        │  └──────────────────────────────┘  │
        │  ┌──────────────────────────────┐  │
        │  │ SOURCE_OF_TRUTH.md           │  │
        │  │ (Resource index & manifest)  │  │
        │  └──────────────────────────────┘  │
        │  ┌──────────────────────────────┐  │
        │  │ ./resources/ (folder)        │  │
        │  │ (Extracted & stored docs)    │  │
        │  └──────────────────────────────┘  │
        └─────────────────────────────────────┘
```

## 2. Core Components & Responsibilities

### 2.1 Input Processing Module
**Responsibility**: Validate and prepare input documents

**Functions**:
- `validate_inputs()` - Check file formats and sizes
- `parse_transcript()` - Extract text from various formats (.txt, .md, .pdf, Confluence link)
- `parse_one_pager()` - Extract text from various formats
- `normalize_text()` - Clean, standardize encoding

**Output**: Normalized text strings ready for entity extraction

---

### 2.2 Entity Extraction Module
**Responsibility**: Identify searchable entities and create query parameters

**Functions**:
- `extract_jira_ids()` - Find pattern matches (e.g., PROJ-123)
- `extract_product_features()` - Identify product/feature names
- `extract_customer_names()` - Find account/customer mentions
- `extract_technical_terms()` - Identify architecture, tech stack keywords
- `generate_search_queries()` - Create optimized search strings for each MCP

**Output**: 
```json
{
  "jira_ids": ["PROJ-123", "PROJ-456"],
  "products": ["Product A", "Feature B"],
  "customers": ["Acme Corp"],
  "technical_terms": ["microservices", "API"],
  "search_queries": {
    "confluence": ["Design Product A", "..."],
    "jira": ["project = PROJ", "..."],
    "salesforce": ["Account: Acme", "..."],
    "hubspot": ["customer: Acme", "..."]
  }
}
```

---

### 2.3 MCP Integration Module
**Responsibility**: Query all external systems and aggregate results

**Subcomponents**:

#### 2.3.1 Confluence Adapter
- Query design documents by keywords
- Search technical specifications
- Retrieve ADRs (Architecture Decision Records)
- Fetch linked pages and attachments
- Rate limiting: respect API quotas

#### 2.3.2 Jira Adapter
- Search issues by JQL (Jira Query Language)
- Retrieve issue details, linked issues, comments
- Get epic/story hierarchies
- Fetch Sprint/roadmap context
- Rate limiting: batch queries

#### 2.3.3 Salesforce Adapter
- Search opportunities by account name
- Retrieve customer account context
- Get deal stage and timeline info
- Fetch customer interaction history
- Rate limiting: API call budgets

#### 2.3.4 HubSpot Adapter
- Search customers and deals
- Retrieve contact information
- Get customer feedback and tickets
- Fetch communication history
- Rate limiting: API throttling

**Common Features**:
- Parallel query execution
- Timeout handling (30s per query)
- Error recovery with retry logic
- Result caching (5-minute TTL)
- Graceful degradation (continue if one MCP fails)

**Output**: Aggregated result set with source attribution
```json
{
  "confluence": [
    {
      "title": "Design Doc",
      "url": "...",
      "content_preview": "...",
      "relevance_score": 0.95
    }
  ],
  "jira": [...],
  "salesforce": [...],
  "hubspot": [...]
}
```

---

### 2.4 Context Aggregation Module
**Responsibility**: Deduplicate, enrich, and organize results

**Functions**:
- `deduplicate_results()` - Remove duplicate entries across sources
- `calculate_relevance_score()` - Score each result (0-1)
- `organize_by_category()` - Group by type (technical, business, customer, etc.)
- `add_source_metadata()` - Attach provenance and links

**Output**: Organized, ranked context ready for question generation

---

### 2.5 Resource Storage & Extraction Module ⭐ (NEW)
**Responsibility**: Extract and store resources for future reference

**Folder Structure**:
```
./output/
├── [JIRA-ID]/                    # Primary folder named after Jira ID
│   ├── SOURCE_OF_TRUTH.md        # Master index of all resources
│   ├── metadata.json             # Extraction metadata & manifest
│   ├── questions.md              # Generated question document
│   │
│   └── resources/
│       ├── confluence/
│       │   ├── DESIGN-001.md     # Downloaded design doc
│       │   ├── ADR-002.md        # Architecture decision record
│       │   └── TECH-SPEC-003.md  # Technical specification
│       │
│       ├── jira/
│       │   ├── PROJ-123.json     # Issue details
│       │   ├── PROJ-456.json     # Related issue
│       │   └── PROJ-epic-789.json # Epic details
│       │
│       ├── salesforce/
│       │   ├── account-acme.json
│       │   ├── opp-deal-001.json
│       │   └── contract-info.json
│       │
│       └── hubspot/
│           ├── customer-acme.json
│           ├── deal-001.json
│           └── feedback-001.json
```

**Functions**:
- `create_output_folder()` - Create folder structure with Jira ID as root
- `extract_resource()` - Download and save resource from MCP
- `convert_to_markdown()` - Convert JSON/API responses to readable .md
- `create_metadata_index()` - Track all extracted resources
- `generate_source_of_truth()` - Create master index document

**Metadata Structure** (metadata.json):
```json
{
  "jira_id": "PROJ-123",
  "generated_at": "2026-05-24T10:30:00Z",
  "extracted_from": {
    "transcript": "meeting-notes.txt",
    "one_pager": "feature-proposal.md"
  },
  "resources": [
    {
      "id": "confluence-design-001",
      "source": "confluence",
      "title": "Design Document",
      "url": "https://confluence.company.com/...",
      "local_path": "resources/confluence/DESIGN-001.md",
      "extracted_at": "2026-05-24T10:30:05Z",
      "size_bytes": 15420,
      "relevance_score": 0.95
    },
    {
      "id": "jira-proj-123",
      "source": "jira",
      "title": "User Story: Feature X",
      "url": "https://jira.company.com/browse/PROJ-123",
      "local_path": "resources/jira/PROJ-123.json",
      "extracted_at": "2026-05-24T10:30:12Z",
      "size_bytes": 2340,
      "relevance_score": 0.89
    }
  ],
  "statistics": {
    "total_resources": 12,
    "by_source": {
      "confluence": 4,
      "jira": 5,
      "salesforce": 2,
      "hubspot": 1
    }
  }
}
```

**Source of Truth Index** (SOURCE_OF_TRUTH.md):
```markdown
# Source of Truth - [JIRA-ID]
Generated: [timestamp]

## Overview
- Jira Issue: [JIRA-ID](link)
- Total Resources: 12
- Last Updated: [timestamp]

## Resource Index

### Confluence Documents (4 resources)
| Document | Relevance | Path | Link |
|----------|-----------|------|------|
| Design Doc | 95% | resources/confluence/DESIGN-001.md | [link] |
| ...       | ... | ... | ... |

### Jira Issues (5 resources)
| Issue | Type | Status | Path | Link |
|-------|------|--------|------|------|
| PROJ-123 | Story | In Progress | resources/jira/PROJ-123.json | [link] |
| ...   | ... | ... | ... | ... |

### Salesforce Context (2 resources)
| Item | Account | Path | Link |
|------|---------|------|------|
| ...  | ...     | ...  | ... |

### HubSpot Interactions (1 resource)
| Item | Type | Path | Link |
|------|------|------|------|
| ...  | ...  | ...  | ... |

## Key Findings Summary
[Auto-generated summary of critical context]

## Related Issues & Dependencies
- Blocker: [Issue] ([Path])
- Related: [Issue] ([Path])

## Recommendations for Analyst
1. [Action item]
2. [Action item]
```

---

### 2.6 Question Generation Module
**Responsibility**: Synthesize context into actionable questions

**Functions**:
- `generate_functional_questions()` - Questions about features, functionality
- `generate_nonfunctional_questions()` - Questions about performance, security, scalability
- `generate_business_questions()` - Questions about requirements, customers, timelines
- `identify_gaps()` - Find areas not covered by existing context
- `identify_dependencies()` - Surface blockers and related work
- `prioritize_questions()` - Rank by importance and relevance

**Input**: Aggregated context from Section 2.5

**Output**: Structured question list with source attribution

---

### 2.7 Output Generation Module
**Responsibility**: Format and export final artifacts

**Functions**:
- `generate_question_document()` - Create markdown question doc
- `generate_source_of_truth_index()` - Create resource index
- `create_manifest_file()` - Summarize extraction
- `export_to_pdf()` - PDF export option
- `export_to_google_docs()` - Google Docs export option

**Outputs**: 
1. `questions.md` - Question document
2. `SOURCE_OF_TRUTH.md` - Resource index
3. `metadata.json` - Machine-readable manifest
4. `resources/` folder - Extracted documents

---

## 3. Data Flow Sequence Diagram

```
User Input (Transcript + One-Pager)
    │
    ▼
┌─────────────────────────────┐
│ Entity Extraction           │
│ - Identify JIRA-ID         │
│ - Extract key terms        │
│ - Create search queries    │
└──────────┬──────────────────┘
           │
           ▼
    ┌──────┴──────┬──────────┬──────────┐
    │             │          │          │
    ▼             ▼          ▼          ▼
┌────────┐  ┌────────┐  ┌─────────┐  ┌──────┐
│Conf.   │  │ Jira   │  │Salesforce │HubSpot│
│Query   │  │ Query  │  │ Query   │  │Query │
└────┬───┘  └───┬────┘  └────┬────┘  └───┬──┘
     │          │            │           │
     └──────────┼────────────┴───────────┘
                │
                ▼
        ┌──────────────────────┐
        │ Aggregate Results    │
        │ - Merge all sources  │
        │ - Deduplicate        │
        │ - Rank by relevance  │
        └──────────┬───────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
    ┌──────────────┐    ┌──────────────────┐
    │ Store        │    │ Generate         │
    │ Resources    │    │ Questions        │
    │ (by source)  │    │ (categorized)    │
    └──────┬───────┘    └────────┬─────────┘
           │                     │
           └─────────────┬───────┘
                         │
                         ▼
            ┌────────────────────────┐
            │ Generate Output Files  │
            │ - questions.md         │
            │ - SOURCE_OF_TRUTH.md   │
            │ - metadata.json        │
            │ - resources/ folder    │
            └────────────┬───────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │ Output: ./output/      │
            │         [JIRA-ID]/     │
            └────────────────────────┘
```

---

## 4. Project Folder Structure

```
dynpro/
├── README.md                      # Project overview and usage
├── requirements.md                # Requirements document
├── SYSTEM_ARCHITECTURE.md         # This file
│
├── .env.example                   # Environment variables template
├── .env.local                     # Local environment overrides (gitignored)
├── .gitignore                     # Git ignore rules
├── mcp.json                       # ⭐ Dynamic MCP configuration (see MCP_ARCHITECTURE.md)
│
├── src/
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration (API keys, settings)
│   ├── models.py                  # Pydantic data models & State schemas
│   │
│   ├── fastapi_app/
│   │   ├── __init__.py
│   │   ├── app.py                 # FastAPI application setup
│   │   ├── routes.py              # API endpoints
│   │   ├── middleware.py          # CORS, logging, error handling
│   │   └── dependencies.py        # Dependency injection
│   │
│   ├── agents/                    # LangGraph agents & orchestration
│   │   ├── __init__.py
│   │   ├── agents_config.py       # Agent definitions & LLM config
│   │   ├── state.py               # AnalysisState definition
│   │   ├── workflow.py            # LangGraph StateGraph definition
│   │   │
│   │   ├── input_processor.py     # Input parsing agent
│   │   ├── entity_extractor.py    # Entity extraction agent (uses LiteLLM)
│   │   ├── context_aggregator.py  # Result aggregation agent
│   │   ├── resource_storage.py    # Resource storage agent
│   │   ├── question_generator.py  # Question generation agent (uses LiteLLM)
│   │   └── output_formatter.py    # Output formatting agent
│   │
│   ├── mcp_integration/           # Dynamic MCP loader (config-driven)
│   │   ├── __init__.py            # MCPManager (public API)
│   │   ├── registry.py            # MCPRegistry (loads mcp.json)
│   │   ├── schema.py              # Pydantic MCP config schema
│   │   ├── factory.py             # MCPAdapterFactory
│   │   ├── generic_adapter.py     # Generic REST/GraphQL adapters
│   │   ├── adapters/              # Type-specific adapters (optional)
│   │   │   ├── confluence.py
│   │   │   ├── jira.py
│   │   │   ├── salesforce.py
│   │   │   └── hubspot.py
│   │   └── exceptions.py          # MCP-specific exceptions
│   │
│   ├── resource_storage/          # Resource persistence & management
│   │   ├── __init__.py
│   │   ├── storage_manager.py     # Create folders, store files
│   │   ├── metadata_builder.py    # Build metadata.json
│   │   ├── resource_converter.py  # Convert to markdown/JSON
│   │   └── index_generator.py     # Generate SOURCE_OF_TRUTH.md
│   │
│   ├── output_generation/         # Output artifact generation
│   │   ├── __init__.py
│   │   ├── markdown_formatter.py  # Generate Markdown documents
│   │   ├── html_formatter.py      # Generate HTML reports (Jinja2)
│   │   ├── pdf_exporter.py        # Export to PDF
│   │   └── templates/             # Jinja2 templates
│   │       ├── report_base.html   # Base HTML template
│   │       └── components/        # Reusable HTML components
│   │
│   ├── litellm_integration/       # LiteLLM wrapper & configuration
│   │   ├── __init__.py
│   │   ├── llm_client.py          # LiteLLM client wrapper
│   │   ├── prompts.py             # LLM prompts for different agents
│   │   ├── caching.py             # LLM response caching
│   │   └── rate_limiter.py        # Rate limiting for LLM calls
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── file_helpers.py        # File operations
│       ├── text_processing.py     # Text normalization, cleaning
│       ├── logging.py             # Structured logging setup
│       └── validators.py          # Input validation
│
├── output/                        # Generated analysis outputs (created at runtime)
│   └── [JIRA-ID]/                # Folder per analyzed Jira ID
│       ├── SOURCE_OF_TRUTH.md     # Master resource index
│       ├── questions.md           # Generated questions document
│       ├── report.html            # Interactive HTML report
│       ├── metadata.json          # Extraction metadata & manifest
│       │
│       └── resources/             # Extracted resources by source
│           ├── confluence/        # Confluence documents
│           │   ├── DESIGN-001.md
│           │   └── ADR-002.md
│           ├── jira/              # Jira issues
│           │   ├── PROJ-123.json
│           │   └── PROJ-456.json
│           ├── salesforce/        # Salesforce records
│           │   ├── account-acme.json
│           │   └── opportunity-001.json
│           └── hubspot/           # HubSpot interactions
│               ├── customer-acme.json
│               └── feedback-001.json
│
├── docker/                        # Docker configuration
│   ├── Dockerfile                 # Multi-stage build
│   └── docker-compose.yml         # Local development setup
│
├── docs/                          # Documentation
│   ├── API.md                     # API documentation
│   ├── DEPLOYMENT.md              # Deployment guide
│   └── USAGE.md                   # User guide
│
├── .env.example                   # Environment variables template
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Poetry or setuptools config (optional)
└── .github/
    └── workflows/                 # CI/CD pipelines
        ├── test.yml               # Run tests
        └── lint.yml               # Lint and format checks
```

### 4.1 Output Folder Structure (Runtime Generated)

Each analysis creates a timestamped folder named after the detected Jira ID:

```
output/
├── PROJ-123/                      # Primary analysis output
│   ├── report.html               # 📊 Interactive HTML visualization
│   ├── questions.md              # Questions in Markdown format
│   ├── SOURCE_OF_TRUTH.md        # Master resource index
│   ├── metadata.json             # Machine-readable metadata
│   │
│   └── resources/
│       ├── confluence/
│       │   ├── design-doc-001.md
│       │   ├── adr-microservices.md
│       │   └── tech-spec-api.md
│       │
│       ├── jira/
│       │   ├── PROJ-123.json (analyzed issue)
│       │   ├── PROJ-456.json (related)
│       │   ├── PROJ-789.json (blocker)
│       │   └── PROJ-epic-200.json
│       │
│       ├── salesforce/
│       │   ├── account-acme-corp.json
│       │   ├── opportunity-deal-001.json
│       │   └── contract-sla.json
│       │
│       └── hubspot/
│           ├── contact-john-doe.json
│           ├── deal-proposal.json
│           └── feedback-feature-request.json
│
└── PROJ-456/                      # Another analysis
    ├── report.html
    ├── questions.md
    └── ...
```

---

## 5. Key Design Decisions

### 5.1 Parallel MCP Queries
- **Decision**: Execute all MCP queries concurrently
- **Rationale**: Minimize total execution time, parallelize I/O
- **Implementation**: Use Python `asyncio` or `ThreadPoolExecutor`

### 5.2 Resource Storage Structure
- **Decision**: Organize by source system first, not by document type
- **Rationale**: Easy to refresh from specific MCP, maintains source separation, clear audit trail
- **Alternative Considered**: Organize by type (architecture, requirements, customer, etc.)

### 5.3 Jira ID as Folder Root
- **Decision**: Use Jira ID as primary folder identifier
- **Rationale**: Jira issues are the most common tracking artifact in orgs, easy to reference, natural hierarchical anchor
- **Fallback**: Use generated ID (timestamp + hash) if no Jira ID found

### 5.4 Local Storage for Offline Reference
- **Decision**: Download and store all resources locally
- **Rationale**: 
  - Create "source of truth" snapshot
  - Offline accessibility
  - Supports versioning/diff if extracted multiple times
  - Audit trail of what context was available at analysis time
  - Avoids API quota issues on future reviews

### 5.5 Graceful Degradation
- **Decision**: Continue if some MCPs fail/timeout
- **Rationale**: Tool remains useful even with partial data, user gets context from available sources
- **Implementation**: Catch exceptions per adapter, report failures in output

---

## 6. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Web Service** | FastAPI 0.104+ | REST API, async request handling |
| **Multi-Agent Orchestration** | LangGraph 0.1+ | Agent coordination, state management, workflow execution |
| **LLM Abstraction** | LiteLLM 1.40+ | Multi-model/provider support, caching, rate limiting |
| **Language** | Python 3.10+ | Core implementation |
| **Async Runtime** | `asyncio` | Parallel MCP queries, concurrent agent execution |
| **Data Models** | Pydantic 2.0+ | Type validation, serialization |
| **MCP Clients** | Official SDKs | Confluence, Jira, Salesforce, HubSpot APIs |
| **Markdown** | `python-markdown` | Generate and validate markdown |
| **File Storage** | Local filesystem | Resource persistence, source of truth |
| **Logging** | `structlog` | Structured logging, debugging |
| **HTML Generation** | `jinja2` | Template-based HTML report generation |
| **Export** | `weasyprint` or `reportlab` | PDF export from HTML |

---

## 7. FastAPI + LangGraph + LiteLLM Integration Architecture

### 7.1 Three-Layer Integration Model

```
┌──────────────────────────────────────────────────────────────────────┐
│                         FastAPI (HTTP Layer)                         │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ POST /analyze                                                  │ │
│  │ ├─ transcript: UploadFile                                     │ │
│  │ ├─ one_pager: UploadFile                                      │ │
│  │ └─ Returns: {status, output_path, metadata}                   │ │
│  └────────────────────┬───────────────────────────────────────────┘ │
└─────────────────────────┼──────────────────────────────────────────────┘
                          │
        ┌─────────────────▼──────────────────────────┐
        │   LangGraph Workflow (Orchestrator)        │
        │   ┌────────────────────────────────────┐  │
        │   │ StateGraph: AnalysisState          │  │
        │   │ ├─ Nodes: [Agent Definitions]      │  │
        │   │ └─ Edges: [Dependencies]           │  │
        │   └────────────────────────────────────┘  │
        └─────────────────┬──────────────────────────┘
                          │
        ┌─────────────────┴─────────────────────────────┐
        │                                               │
        ▼                                               ▼
┌──────────────────────────┐              ┌───────────────────────┐
│  Input Processor Agent   │              │Entity Extractor Agent │
│  ├─ Parse files          │              │├─ LiteLLM (Claude)   │
│  └─ Normalize text       │              │└─ Extract entities    │
└──────────────────────────┘              └───────────────────────┘
        │                                        │
        └────────────────┬───────────────────────┘
                         │
        ┌────────────────┴──────────────────────────────┐
        │                                               │
        ▼                                               ▼
┌──────────────────────────┐              ┌───────────────────────┐
│ Confluence Query Agent   │              │   Jira Query Agent    │
│├─ LiteLLM (GPT-4-turbo)  │              │├─ LiteLLM (GPT-4)     │
│└─ Search design docs     │              │└─ Search issues       │
└──────────────────────────┘              └───────────────────────┘
        │                                        │
        │                    ┌────────────────┬──┘
        │                    │                │
        ▼                    ▼                ▼
┌──────────────────────┐  ┌─────────────────────────┐
│Salesforce Query Agent│  │HubSpot Query Agent      │
│├─LiteLLM (Haiku)     │  │├─LiteLLM (Haiku)        │
│└─Search accounts     │  │└─Search customers       │
└──────────────────────┘  └─────────────────────────┘
        │                         │
        └────────────┬────────────┘
                     │
        ┌────────────▼───────────────────────┐
        │Context Aggregator Agent            │
        │├─ LiteLLM (Sonnet) - Relevance     │
        │├─ Deduplicate results              │
        │└─ Rank by importance               │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼───────────────────────┐
        │Resource Storage Agent              │
        │├─ Create output folder             │
        │├─ Store resources by source        │
        │└─ Generate metadata.json           │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼───────────────────────┐
        │Question Generator Agent            │
        │├─ LiteLLM (Claude Opus) - Best     │
        │├─ Generate categorized questions   │
        │└─ Link to resources                │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼───────────────────────┐
        │Output Formatter Agent              │
        │├─ Generate questions.md            │
        │├─ Generate SOURCE_OF_TRUTH.md      │
        │├─ Generate HTML report             │
        │└─ Create manifest files            │
        └────────────┬───────────────────────┘
                     │
                     ▼
    ┌────────────────────────────┐
    │   Output Artifacts         │
    │ ├─ questions.md            │
    │ ├─ SOURCE_OF_TRUTH.md      │
    │ ├─ report.html (NEW)        │
    │ ├─ metadata.json           │
    │ └─ resources/              │
    └────────────────────────────┘
```

### 7.2 Agent Definitions & LLM Configuration

```python
# agents_config.py
AGENT_CONFIG = {
    "input_processor": {
        "model": None,  # No LLM needed
        "description": "Parse and validate input documents",
        "inputs": ["transcript", "one_pager"],
        "outputs": ["normalized_text"]
    },
    
    "entity_extractor": {
        "model": "claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "temperature": 0.3,
        "description": "Extract entities and generate search queries",
        "inputs": ["normalized_text"],
        "outputs": ["entities", "search_queries"],
        "cache": True
    },
    
    "confluence_query": {
        "model": "gpt-4-turbo",
        "provider": "openai",
        "temperature": 0.2,
        "description": "Query Confluence for design docs",
        "inputs": ["search_queries"],
        "outputs": ["confluence_results"],
        "parallel": True
    },
    
    "jira_query": {
        "model": "gpt-4-turbo",
        "provider": "openai",
        "temperature": 0.2,
        "description": "Query Jira for issues",
        "inputs": ["search_queries"],
        "outputs": ["jira_results"],
        "parallel": True
    },
    
    "salesforce_query": {
        "model": "claude-3-haiku-20240307",
        "provider": "anthropic",
        "temperature": 0.2,
        "description": "Query Salesforce for customer context",
        "inputs": ["search_queries"],
        "outputs": ["salesforce_results"],
        "parallel": True
    },
    
    "hubspot_query": {
        "model": "claude-3-haiku-20240307",
        "provider": "anthropic",
        "temperature": 0.2,
        "description": "Query HubSpot for feedback",
        "inputs": ["search_queries"],
        "outputs": ["hubspot_results"],
        "parallel": True
    },
    
    "context_aggregator": {
        "model": "claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "temperature": 0.1,
        "description": "Aggregate and score results",
        "inputs": ["confluence_results", "jira_results", "salesforce_results", "hubspot_results"],
        "outputs": ["aggregated_context"],
        "cache": True
    },
    
    "resource_storage": {
        "model": None,  # No LLM needed
        "description": "Store resources locally",
        "inputs": ["aggregated_context"],
        "outputs": ["storage_path", "metadata"],
        "jira_id_source": "entities"
    },
    
    "question_generator": {
        "model": "claude-3-opus-20250219",
        "provider": "anthropic",
        "temperature": 0.5,
        "description": "Generate high-quality questions",
        "inputs": ["aggregated_context", "storage_metadata"],
        "outputs": ["questions", "recommendations"],
        "max_questions": 15
    },
    
    "output_formatter": {
        "model": None,  # No LLM needed
        "description": "Format outputs (Markdown, HTML, JSON)",
        "inputs": ["questions", "aggregated_context", "storage_metadata"],
        "outputs": ["questions.md", "report.html", "SOURCE_OF_TRUTH.md", "metadata.json"]
    }
}
```

### 7.3 State Management (LangGraph State Schema)

```python
# state.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class AnalysisState(BaseModel):
    # Input
    transcript_text: str
    one_pager_text: str
    jira_id: Optional[str] = None
    
    # Entity Extraction
    entities: Optional[Dict[str, Any]] = None
    search_queries: Optional[Dict[str, List[str]]] = None
    
    # MCP Results
    confluence_results: Optional[List[Dict]] = None
    jira_results: Optional[List[Dict]] = None
    salesforce_results: Optional[List[Dict]] = None
    hubspot_results: Optional[List[Dict]] = None
    
    # Aggregation
    aggregated_context: Optional[Dict[str, Any]] = None
    
    # Storage
    storage_path: Optional[str] = None
    storage_metadata: Optional[Dict[str, Any]] = None
    
    # Generation
    questions: Optional[List[Dict]] = None
    recommendations: Optional[List[str]] = None
    
    # Output
    output_artifacts: Optional[Dict[str, str]] = None
    
    # Execution tracking
    execution_errors: List[str] = []
    execution_time: Optional[float] = None
```

### 7.4 FastAPI Endpoint Example

```python
# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from langgraph.graph import StateGraph
import time

app = FastAPI(title="Context-Aware Question Generator")

@app.post("/analyze")
async def analyze(
    transcript: UploadFile = File(...),
    one_pager: UploadFile = File(...)
):
    """
    Analyze transcript and one-pager to generate questions.
    
    Returns:
        - status: "success" | "partial" | "failed"
        - output_path: Path to output folder
        - artifacts: {questions_url, html_report_url, metadata_url}
        - execution_time: Total processing time
    """
    start_time = time.time()
    
    try:
        # 1. Read input files
        transcript_text = await transcript.read()
        one_pager_text = await one_pager.read()
        
        # 2. Create initial state
        initial_state = AnalysisState(
            transcript_text=transcript_text.decode(),
            one_pager_text=one_pager_text.decode()
        )
        
        # 3. Execute workflow
        workflow = build_analysis_workflow()
        final_state = await workflow.ainvoke(initial_state)
        
        # 4. Return results
        execution_time = time.time() - start_time
        
        return JSONResponse({
            "status": "success",
            "output_path": final_state.storage_path,
            "artifacts": final_state.output_artifacts,
            "execution_time": execution_time,
            "jira_id": final_state.jira_id
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "failed", "error": str(e)}
        )
```

---

## 8. HTML Output Format & Visualization

### 8.1 HTML Report Structure

The tool generates an interactive HTML report (`report.html`) with the following features:

```
┌─────────────────────────────────────────────────────┐
│          CONTEXT-AWARE QUESTION REPORT              │
│                  [PROJECT-ID]                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ✓ Executive Summary                               │
│    • Analysis Date                                 │
│    • Total Resources Extracted                     │
│    • Total Questions Generated                     │
│    • Critical Dependencies Found                   │
│                                                     │
│  ✓ Quick Navigation                                │
│    [Functional] [Non-Functional] [Business]        │
│    [Dependencies] [Resources] [Recommendations]    │
│                                                     │
├─────────────────────────────────────────────────────┤
│  SECTION 1: FUNCTIONAL REQUIREMENTS QUESTIONS       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Q1: Feature X specification...                    │
│      Source: ✓ Jira-123 (Issue) | Confluence-45   │
│      Relevance: 95%                                │
│      Related Work:                                 │
│        └─ Jira-456 (linked issue)                  │
│        └─ resources/confluence/DESIGN-001.md       │
│                                                     │
│  Q2: Integration points...                         │
│      [expand details]                              │
│                                                     │
├─────────────────────────────────────────────────────┤
│  SECTION 2: NON-FUNCTIONAL REQUIREMENTS            │
├─────────────────────────────────────────────────────┤
│  [Similar structure for performance, security...]  │
│                                                     │
├─────────────────────────────────────────────────────┤
│  SECTION 3: BUSINESS & CUSTOMER CONTEXT            │
├─────────────────────────────────────────────────────┤
│  [Customer requirements, deal context...]          │
│                                                     │
├─────────────────────────────────────────────────────┤
│  SECTION 4: TECHNICAL CONTEXT & CONSTRAINTS        │
├─────────────────────────────────────────────────────┤
│  Design Decision: Microservices Architecture       │
│    • Rationale: [from Confluence doc]             │
│    • Implications: Requires independent scaling    │
│    • Source: resources/confluence/ADR-002.md       │
│                                                     │
├─────────────────────────────────────────────────────┤
│  SECTION 5: DEPENDENCIES & BLOCKERS                │
├─────────────────────────────────────────────────────┤
│  🔴 BLOCKER: Jira-999 - API Rate Limit             │
│      Impact: HIGH                                  │
│      Status: In Progress                           │
│      Link: resources/jira/PROJ-999.json            │
│                                                     │
├─────────────────────────────────────────────────────┤
│  SECTION 6: RESOURCE SUMMARY                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Confluence Documents (4)                          │
│    ├─ Design Document.md (relevance: 95%)         │
│    ├─ ADR-002.md (relevance: 87%)                 │
│    └─ ...                                          │
│                                                     │
│  Jira Issues (5)                                   │
│    ├─ PROJ-123 (Story, In Progress)               │
│    └─ ...                                          │
│                                                     │
│  Salesforce Accounts (2)                           │
│    └─ Acme Corp (High Priority Customer)           │
│                                                     │
│  HubSpot Interactions (1)                          │
│    └─ Support Ticket: Feature Request              │
│                                                     │
├─────────────────────────────────────────────────────┤
│  SECTION 7: RECOMMENDED NEXT STEPS                 │
├─────────────────────────────────────────────────────┤
│  1. ☐ Review Jira-123 acceptance criteria         │
│  2. ☐ Schedule design review with team            │
│  3. ☐ Validate customer requirements (Acme Corp) │
│  4. ☐ Check blockers before proceeding            │
│                                                     │
├─────────────────────────────────────────────────────┤
│  METADATA                                           │
├─────────────────────────────────────────────────────┤
│  Generated: 2026-05-24 10:30 UTC                   │
│  Processing Time: 2m 34s                          │
│  Jira ID: PROJ-123                                │
│  Output Location: ./output/PROJ-123/              │
│  Source of Truth: SOURCE_OF_TRUTH.md              │
│                                                     │
│  [Download PDF] [Copy Link] [Share]               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 8.2 HTML Template (Jinja2)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Report - {{ jira_id }}</title>
    <style>
        :root {
            --primary: #0066cc;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
            --gray: #6b7280;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: #f9fafb;
        }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        
        .header {
            background: linear-gradient(135deg, var(--primary), #0052a3);
            color: white;
            padding: 3rem 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }
        
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; font-size: 1.1rem; }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.1);
            padding: 1rem;
            border-radius: 6px;
            border-left: 4px solid rgba(255,255,255,0.3);
        }
        
        .stat-card .value { font-size: 1.8rem; font-weight: bold; }
        .stat-card .label { font-size: 0.9rem; opacity: 0.8; }
        
        .section {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            margin-bottom: 2rem;
            overflow: hidden;
        }
        
        .section-header {
            background: #f3f4f6;
            padding: 1.5rem;
            border-bottom: 2px solid #e5e7eb;
        }
        
        .section-header h2 {
            font-size: 1.5rem;
            color: var(--primary);
        }
        
        .section-content { padding: 1.5rem; }
        
        .question-item {
            border-left: 4px solid var(--primary);
            padding: 1.5rem;
            margin-bottom: 1rem;
            background: #f9fafb;
            border-radius: 4px;
        }
        
        .question-item h4 { margin-bottom: 0.5rem; color: #1f2937; }
        
        .question-meta {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
            flex-wrap: wrap;
            font-size: 0.9rem;
        }
        
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-weight: 500;
            font-size: 0.85rem;
        }
        
        .badge-success { background: #d1fae5; color: #065f46; }
        .badge-warning { background: #fef3c7; color: #92400e; }
        .badge-danger { background: #fee2e2; color: #991b1b; }
        
        .source-link {
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }
        
        .source-link:hover { text-decoration: underline; }
        
        .resources-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
        }
        
        .resource-card {
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 1.5rem;
            background: #fafafa;
        }
        
        .resource-card h4 { margin-bottom: 0.5rem; }
        .resource-card .count { font-size: 2rem; font-weight: bold; color: var(--primary); }
        .resource-card .label { color: var(--gray); }
        
        .nav-tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid #e5e7eb;
            flex-wrap: wrap;
        }
        
        .nav-tabs button {
            background: none;
            border: none;
            padding: 0.75rem 1.5rem;
            cursor: pointer;
            color: var(--gray);
            font-weight: 500;
            border-bottom: 3px solid transparent;
            transition: all 0.2s;
        }
        
        .nav-tabs button.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
        
        .nav-tabs button:hover { color: #1f2937; }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: var(--gray);
            border-top: 1px solid #e5e7eb;
            margin-top: 3rem;
        }
        
        .action-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
            justify-content: center;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 6px;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: var(--primary);
            color: white;
        }
        
        .btn-primary:hover { background: #0052a3; }
        
        .btn-secondary {
            background: white;
            color: var(--primary);
            border: 2px solid var(--primary);
        }
        
        .btn-secondary:hover { background: #f0f7ff; }
        
        @media print {
            body { background: white; }
            .section { page-break-inside: avoid; }
            .action-buttons { display: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📋 Analysis Report</h1>
            <p>Context-Aware Question Generation</p>
            <div class="stats">
                <div class="stat-card">
                    <div class="value">{{ total_resources }}</div>
                    <div class="label">Resources Extracted</div>
                </div>
                <div class="stat-card">
                    <div class="value">{{ total_questions }}</div>
                    <div class="label">Questions Generated</div>
                </div>
                <div class="stat-card">
                    <div class="value">{{ jira_id }}</div>
                    <div class="label">Jira Issue</div>
                </div>
                <div class="stat-card">
                    <div class="value">{{ execution_time }}s</div>
                    <div class="label">Processing Time</div>
                </div>
            </div>
        </div>
        
        <!-- Quick Navigation -->
        <div class="nav-tabs">
            <button class="nav-tab-btn active" onclick="showTab('overview')">Overview</button>
            <button class="nav-tab-btn" onclick="showTab('functional')">Functional</button>
            <button class="nav-tab-btn" onclick="showTab('nonfunctional')">Non-Functional</button>
            <button class="nav-tab-btn" onclick="showTab('business')">Business</button>
            <button class="nav-tab-btn" onclick="showTab('resources')">Resources</button>
            <button class="nav-tab-btn" onclick="showTab('recommendations')">Next Steps</button>
        </div>
        
        <!-- Executive Summary -->
        <div class="section" id="overview-tab">
            <div class="section-header">
                <h2>📊 Executive Summary</h2>
            </div>
            <div class="section-content">
                <p><strong>Analysis Date:</strong> {{ generated_at }}</p>
                <p><strong>Total Resources Extracted:</strong> {{ total_resources }}</p>
                <p><strong>Questions Generated:</strong> {{ total_questions }}</p>
                <p><strong>Critical Dependencies:</strong> {{ critical_dependencies }}</p>
                <p style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
                    {{ summary_text }}
                </p>
            </div>
        </div>
        
        <!-- Functional Questions -->
        <div class="section" id="functional-tab" style="display: none;">
            <div class="section-header">
                <h2>✅ Functional Requirements Questions</h2>
            </div>
            <div class="section-content">
                {% for question in functional_questions %}
                <div class="question-item">
                    <h4>Q{{ loop.index }}: {{ question.text }}</h4>
                    <div class="question-meta">
                        <span>📍 Source: 
                            {% for source in question.sources %}
                            <a href="{{ source.url }}" class="source-link">{{ source.name }}</a>
                            {% endfor %}
                        </span>
                        <span class="badge badge-success">Relevance: {{ (question.relevance * 100)|int }}%</span>
                    </div>
                    {% if question.related_work %}
                    <p style="margin-top: 0.75rem; font-size: 0.9rem;">
                        <strong>Related Work:</strong><br>
                        {% for work in question.related_work %}
                        • <a href="{{ work.path }}" class="source-link">{{ work.title }}</a><br>
                        {% endfor %}
                    </p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Non-Functional Questions -->
        <div class="section" id="nonfunctional-tab" style="display: none;">
            <div class="section-header">
                <h2>⚙️ Non-Functional Requirements Questions</h2>
            </div>
            <div class="section-content">
                {% for question in nonfunctional_questions %}
                <div class="question-item">
                    <h4>Q{{ loop.index }}: {{ question.text }}</h4>
                    <div class="question-meta">
                        <span>📍 Source: {{ question.source_name }}</span>
                        <span class="badge badge-success">Relevance: {{ (question.relevance * 100)|int }}%</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Business Questions -->
        <div class="section" id="business-tab" style="display: none;">
            <div class="section-header">
                <h2>💼 Business & Customer Context</h2>
            </div>
            <div class="section-content">
                {% for question in business_questions %}
                <div class="question-item">
                    <h4>Q{{ loop.index }}: {{ question.text }}</h4>
                    <div class="question-meta">
                        <span>📍 Source: {{ question.source_name }}</span>
                        <span class="badge badge-warning">Relevance: {{ (question.relevance * 100)|int }}%</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Resources Summary -->
        <div class="section" id="resources-tab" style="display: none;">
            <div class="section-header">
                <h2>📚 Extracted Resources Summary</h2>
            </div>
            <div class="section-content">
                <div class="resources-grid">
                    <div class="resource-card">
                        <div class="count">{{ confluence_count }}</div>
                        <div class="label">Confluence Documents</div>
                    </div>
                    <div class="resource-card">
                        <div class="count">{{ jira_count }}</div>
                        <div class="label">Jira Issues</div>
                    </div>
                    <div class="resource-card">
                        <div class="count">{{ salesforce_count }}</div>
                        <div class="label">Salesforce Records</div>
                    </div>
                    <div class="resource-card">
                        <div class="count">{{ hubspot_count }}</div>
                        <div class="label">HubSpot Items</div>
                    </div>
                </div>
                
                <div style="margin-top: 2rem;">
                    <h3>Resource Details</h3>
                    <p><strong>📂 Storage Location:</strong> <code>{{ storage_location }}</code></p>
                    <p style="margin-top: 0.5rem;"><strong>📋 Source of Truth:</strong> <a href="{{ source_of_truth_url }}" class="source-link">SOURCE_OF_TRUTH.md</a></p>
                    <p style="margin-top: 0.5rem;"><strong>📊 Metadata:</strong> <a href="{{ metadata_url }}" class="source-link">metadata.json</a></p>
                </div>
            </div>
        </div>
        
        <!-- Recommendations -->
        <div class="section" id="recommendations-tab" style="display: none;">
            <div class="section-header">
                <h2>🎯 Recommended Next Steps</h2>
            </div>
            <div class="section-content">
                {% for rec in recommendations %}
                <div style="display: flex; gap: 1rem; margin-bottom: 1rem; align-items: flex-start;">
                    <input type="checkbox" style="margin-top: 0.3rem; cursor: pointer;">
                    <div>
                        <strong>{{ rec.title }}</strong>
                        <p style="margin-top: 0.25rem; color: var(--gray); font-size: 0.9rem;">{{ rec.description }}</p>
                        {% if rec.related_resource %}
                        <p style="margin-top: 0.25rem; font-size: 0.9rem;">
                            Related: <a href="{{ rec.related_resource.path }}" class="source-link">{{ rec.related_resource.name }}</a>
                        </p>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 2rem; margin-top: 2rem;">
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="window.print()">🖨️ Print / Save PDF</button>
                <button class="btn btn-secondary" onclick="copyToClipboard()">📋 Copy Link</button>
            </div>
            
            <div class="footer">
                <p>Generated on {{ generated_at }} UTC</p>
                <p>Processing Time: {{ execution_time }}s</p>
                <p>Jira ID: <strong>{{ jira_id }}</strong></p>
                <p style="margin-top: 1rem; font-size: 0.85rem;">
                    Output Location: <code>./output/{{ jira_id }}/</code>
                </p>
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            const tabs = document.querySelectorAll('[id$="-tab"]');
            tabs.forEach(tab => tab.style.display = 'none');
            
            const buttons = document.querySelectorAll('.nav-tab-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            
            document.getElementById(tabName + '-tab').style.display = 'block';
            event.target.classList.add('active');
        }
        
        function copyToClipboard() {
            const url = window.location.href;
            navigator.clipboard.writeText(url).then(() => {
                alert('Link copied to clipboard!');
            });
        }
    </script>
</body>
</html>
```

---

## 9. Security & Privacy Considerations

- **MCP Authentication**: Store API keys in environment variables or secure config
- **Data Masking**: Option to redact PII (customer names, emails, etc.)
- **Access Control**: Respect MCP permission models (don't fetch restricted data)
- **Audit Logging**: Log all MCP queries and resource extractions
- **Local Storage**: Ensure output folder has appropriate file permissions

---

## 10. Error Handling Strategy

| Scenario | Handling |
|----------|----------|
| Invalid input file | Reject with clear error message |
| MCP timeout (>30s) | Log warning, continue with other sources |
| MCP authentication failure | Log error, skip that source, notify user |
| MCP rate limiting | Implement exponential backoff & retry |
| Duplicate results | Deduplicate by URL/ID |
| Storage write failure | Retry with backoff, fail gracefully |
| Question generation timeout | Return partial results with warning |

---

## 11. Performance Targets

| Metric | Target |
|--------|--------|
| Entity extraction | <5 seconds |
| MCP queries (parallel) | <30 seconds |
| Context aggregation | <5 seconds |
| Resource download & storage | <20 seconds |
| Question generation | <10 seconds |
| Total end-to-end | <2-3 minutes |

---

## 12. Future Extensibility

- **Additional MCPs**: Add new adapters following base adapter pattern
- **Custom Question Templates**: Allow users to define question patterns
- **Semantic Search**: Upgrade to vector-based search for better relevance
- **Change Tracking**: Store multiple analysis runs and diff results
- **Feedback Loop**: Track which questions were useful (improve algorithm)
- **Webhooks**: Notify downstream systems when analysis completes
- **WebSocket Support**: Real-time progress streaming to connected clients
- **Multi-language Support**: Translate questions and reports to other languages
- **Advanced Visualization**: Interactive dependency graphs and timelines
