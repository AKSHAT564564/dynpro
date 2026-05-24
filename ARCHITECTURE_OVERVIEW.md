# Architecture Overview - Complete System Design

## Quick Reference

This project uses a **modular, configuration-driven architecture** with these key components:

### 📋 Core Documents
- **requirements.md** - Functional and non-functional requirements
- **SYSTEM_ARCHITECTURE.md** - Overall system design, FastAPI + LangGraph + LiteLLM integration
- **MCP_ARCHITECTURE.md** - Dynamic MCP configuration approach (NEW! ⭐)
- **ARCHITECTURE_OVERVIEW.md** - This file

---

## System Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                        HTTP Request                             │
│           Analyst uploads Transcript + One-Pager                │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────▼───────────────────┐
        │  FastAPI Server (main.py)          │
        │  POST /analyze endpoint            │
        └────────────────┬───────────────────┘
                         │
        ┌────────────────▼───────────────────────────────────────┐
        │   LangGraph Workflow (Orchestrator)                     │
        │   ┌─────────────────────────────────────────────────┐  │
        │   │  StateGraph: AnalysisState                      │  │
        │   │  - 9 agents in sequence/parallel               │  │
        │   │  - Data flows through state                     │  │
        │   │  - Error handling & retries built-in           │  │
        │   └─────────────────────────────────────────────────┘  │
        └────────────┬───────────────────────────────────────────┘
                     │
        ┌────────────┴────────────────────────┐
        │                                     │
        ▼                                     ▼
   ┌────────────────┐         ┌──────────────────────────┐
   │Input Agent     │         │Entity Extraction Agent   │
   │(File parsing)  │         │(LiteLLM: Claude Sonnet) │
   └────────────────┘         └──────────────────────────┘
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        │                                                              │
        ▼                                                              ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │  MCP Query Agents (Dynamic, from mcp.json)                      │
   │                                                                   │
   │  ┌────────────────┐  ┌────────────────┐                         │
   │  │Confluence Agent│  │Jira Agent      │  ... [more MCPs]        │
   │  │(GPT-4 Turbo)   │  │(GPT-4 Turbo)   │                         │
   │  └────────────────┘  └────────────────┘                         │
   │     │                     │                                      │
   │     ▼                     ▼                                      │
   │  ┌─────────────────────────────────────────┐                   │
   │  │  MCPManager (reads mcp.json config)     │                   │
   │  │  - Loads all enabled MCPs dynamically   │                   │
   │  │  - Creates adapters (REST/GraphQL/etc)  │                   │
   │  │  - Executes queries in parallel         │                   │
   │  └─────────────────────────────────────────┘                   │
   └──────────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┴────────────────────────────┐
        │                                                      │
        ▼                                                      ▼
   ┌────────────────────────┐           ┌─────────────────────────────┐
   │Context Aggregator Agent│           │Resource Storage Agent       │
   │(Relevance scoring)     │           │(Create folder structure)    │
   └────────────────────────┘           └─────────────────────────────┘
        │                                       │
        └───────────────┬───────────────────────┘
                        │
        ┌───────────────▼──────────────────┐
        │Question Generator Agent          │
        │(LiteLLM: Claude Opus - Best)    │
        └───────────────┬──────────────────┘
                        │
        ┌───────────────▼──────────────────┐
        │Output Formatter Agent            │
        │├─ Markdown (questions.md)       │
        │├─ HTML Report (report.html)     │
        │├─ Source of Truth Index         │
        │└─ Metadata (metadata.json)      │
        └───────────────┬──────────────────┘
                        │
                        ▼
        ┌──────────────────────────────────┐
        │Output Folder Structure           │
        │                                  │
        │./output/[JIRA-ID]/              │
        │├─ report.html ⭐               │
        │├─ questions.md                 │
        │├─ SOURCE_OF_TRUTH.md           │
        │├─ metadata.json                │
        │└─ resources/                   │
        │   ├─ confluence/               │
        │   ├─ jira/                     │
        │   ├─ salesforce/               │
        │   └─ hubspot/                  │
        └──────────────────────────────────┘
```

---

## Key Architectural Decisions

### 1. **FastAPI for HTTP Service** ✅
- **Why**: Modern, async-first, auto-documentation with Swagger
- **Responsibility**: Handle HTTP requests, route to LangGraph workflow
- **Endpoint**: `POST /analyze` (transcript + one-pager)

### 2. **LangGraph for Orchestration** ✅
- **Why**: Excellent for multi-agent workflows, state management, error handling
- **Responsibility**: Define workflow, execute agents, manage state transitions
- **9 Agents**: Input → Entity → MCPs → Aggregate → Store → Generate → Format
- **State**: AnalysisState Pydantic model flows through all agents

### 3. **LiteLLM for LLM Abstraction** ✅
- **Why**: Multi-provider support, cost optimization, caching
- **Responsibility**: Wrap all LLM calls, allow dynamic model/provider selection
- **Per-Agent Config**: Each agent can use different models (Claude/GPT/etc.)
- **Examples**:
  - Entity Extraction: Claude 3.5 Sonnet
  - Query Building: GPT-4 Turbo
  - Relevance Scoring: Claude Haiku (cheaper)
  - Question Generation: Claude Opus (best quality)

### 4. **Configuration-Driven MCPs** ✅ (NEW!)
- **Why**: Zero code changes to add new MCPs, runtime flexibility
- **Responsibility**: mcp.json defines all MCPs dynamically
- **MCPManager**: Loads config, creates adapters, manages queries
- **Support**: REST, GraphQL, Confluence, Jira, Salesforce, HubSpot, custom
- **Add New MCP**: Edit mcp.json, no code changes needed

### 5. **Local Resource Storage** ✅
- **Why**: Create "source of truth" snapshot, offline access, audit trail
- **Responsibility**: Download and organize resources by source
- **Structure**: `./output/[JIRA-ID]/resources/{confluence,jira,salesforce,hubspot}/`
- **Metadata**: Track all extracted resources, timestamps, relevance scores

### 6. **HTML Report Visualization** ✅
- **Why**: Interactive, professional, printable to PDF
- **Responsibility**: Render questions, resources, recommendations in HTML
- **Features**: Tabbed navigation, source links, progress tracking, checkboxes
- **Templates**: Jinja2 templates for flexible customization

---

## Data Flow

### Phase 1: Input Processing
```
Analyst Input (files)
    ↓
FastAPI receives request
    ↓
Input Processor Agent
    ├─ Parse transcript
    ├─ Parse one-pager
    └─ Return: normalized_text
```

### Phase 2: Entity Extraction
```
normalized_text
    ↓
Entity Extractor Agent (LiteLLM: Claude)
    ├─ Extract: Jira IDs, products, customers, tech terms
    ├─ Generate search queries for each MCP
    └─ Return: entities, search_queries
```

### Phase 3: Parallel MCP Queries
```
search_queries
    ↓
MCPManager (reads mcp.json)
    ├─ Create adapters for all enabled MCPs
    ├─ Execute queries in parallel
    ├─ Confluence Agent → Design docs
    ├─ Jira Agent → Issues
    ├─ Salesforce Agent → Accounts
    └─ HubSpot Agent → Interactions
    ↓
Return: confluence_results, jira_results, salesforce_results, hubspot_results
```

### Phase 4: Aggregation & Storage
```
All MCP results
    ↓
Context Aggregator Agent (LiteLLM: Sonnet)
    ├─ Merge results
    ├─ Deduplicate
    ├─ Score relevance
    └─ Return: aggregated_context
    ↓
Resource Storage Agent
    ├─ Create folder: ./output/[JIRA-ID]/
    ├─ Store resources by source
    ├─ Generate metadata.json
    └─ Return: storage_path, storage_metadata
```

### Phase 5: Question Generation
```
aggregated_context + storage_metadata
    ↓
Question Generator Agent (LiteLLM: Claude Opus)
    ├─ Analyze context
    ├─ Generate categorized questions
    ├─ Link to resources
    ├─ Identify gaps & dependencies
    └─ Return: questions, recommendations
```

### Phase 6: Output Generation
```
questions + aggregated_context + metadata
    ↓
Output Formatter Agent
    ├─ Generate questions.md
    ├─ Generate SOURCE_OF_TRUTH.md (resource index)
    ├─ Generate report.html (interactive visualization)
    ├─ Generate metadata.json (manifest)
    └─ Return: output_artifacts
    ↓
All files saved to: ./output/[JIRA-ID]/
```

---

## Configuration Files

### `.env` - Environment Variables
```bash
# LiteLLM / LLM Providers
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# MCP Credentials (referenced in mcp.json)
CONFLUENCE_API_URL=https://company.confluence.com
CONFLUENCE_API_KEY=...

JIRA_API_URL=https://company.atlassian.net
JIRA_API_KEY=...

SALESFORCE_INSTANCE_URL=https://company.salesforce.com
SALESFORCE_CLIENT_ID=...
SALESFORCE_CLIENT_SECRET=...

HUBSPOT_API_KEY=...

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
OUTPUT_DIR=./output
```

### `mcp.json` - MCP Configuration ⭐ (NEW!)
```json
{
  "version": "1.0",
  "mcp_servers": [
    {
      "id": "confluence",
      "name": "Confluence",
      "type": "confluence",
      "enabled": true,
      "config": {
        "api_url": "${CONFLUENCE_API_URL}",
        "api_key": "${CONFLUENCE_API_KEY}"
      },
      "search": {...},
      "mapping": {...},
      "relevance_weight": 0.95
    },
    // ... more MCPs
    // To add new MCP: just add another entry here!
    // No code changes needed!
  ]
}
```

### `agents_config.py` - Agent & LLM Configuration
```python
AGENT_CONFIG = {
    "entity_extractor": {
        "model": "claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "temperature": 0.3
    },
    "confluence_query": {
        "model": "gpt-4-turbo",
        "provider": "openai",
        "temperature": 0.2
    },
    // ... more agent configs
}
```

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| Web Framework | FastAPI | 0.104+ |
| Agent Orchestration | LangGraph | 0.1+ |
| LLM Abstraction | LiteLLM | 1.40+ |
| Language | Python | 3.10+ |
| Async Runtime | asyncio | Built-in |
| Data Models | Pydantic | 2.0+ |
| HTML Templates | Jinja2 | 3.0+ |
| HTTP Client | httpx | 0.25+ |
| Logging | structlog | 23.0+ |
| GraphQL Support | gql | 3.0+ (optional) |
| PDF Export | weasyprint | 60.0+ (optional) |

---

## Key Features Summary

### ✅ Multi-Agent Orchestration
- 9 specialized agents working in sequence/parallel
- State management across agents
- Built-in error handling and retries

### ✅ Dynamic MCP Integration
- No code changes to add/remove MCPs
- Configuration-driven (mcp.json)
- Support for REST, GraphQL, and specific services
- Graceful degradation if MCP fails

### ✅ Smart LLM Usage
- Different models for different tasks
- Cost optimization (expensive models only where needed)
- Multi-provider support (Anthropic, OpenAI, etc.)
- Built-in caching and rate limiting

### ✅ Resource Management
- Local storage of all extracted resources
- Organized by source (Confluence, Jira, Salesforce, HubSpot)
- Source-of-truth index for future reference
- Full audit trail with timestamps

### ✅ Interactive Output
- Professional HTML report with tabbed navigation
- Markdown questions document
- Machine-readable metadata
- Print-to-PDF support
- Resource links and source attribution

### ✅ Extensibility
- Add new MCPs without code
- Add new agents to workflow
- Custom LLM models per agent
- HTML template customization
- Type-specific adapter registration

---

## Deployment Considerations

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Run FastAPI server
uvicorn src.main:app --reload
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]
```

### Production Checklist
- [ ] All env variables configured
- [ ] mcp.json validated and deployed
- [ ] API keys for all MCPs set
- [ ] Output directory permissions configured
- [ ] Logging configured for production
- [ ] Error monitoring (Sentry, etc.)
- [ ] Rate limiting configured
- [ ] CORS settings appropriate
- [ ] Database/storage for analysis history
- [ ] CI/CD pipeline configured

---

## Next Steps

1. **Phase 1**: Create IMPLEMENTATION_PLAN.md (detailed steps)
2. **Phase 2**: Set up FastAPI project structure
3. **Phase 3**: Implement LangGraph workflow and agents
4. **Phase 4**: Integrate LiteLLM for LLM calls
5. **Phase 5**: Build MCPManager and config loader
6. **Phase 6**: Implement HTML report generation
7. **Phase 7**: Testing and validation

---

## Document Index

- 📋 **requirements.md** - What we're building
- 🏗️ **SYSTEM_ARCHITECTURE.md** - How it works (FastAPI + LangGraph + LiteLLM)
- ⚙️ **MCP_ARCHITECTURE.md** - Dynamic MCP configuration
- 📖 **ARCHITECTURE_OVERVIEW.md** - This file (quick reference)
- 🔧 **IMPLEMENTATION_PLAN.md** - How to build it (coming next)

