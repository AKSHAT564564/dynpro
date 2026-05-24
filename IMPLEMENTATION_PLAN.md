# Implementation Plan - Context-Aware Question Generation Tool

## Overview

This document outlines the step-by-step implementation strategy to build the tool from scratch. The project is divided into **6 phases** with clear milestones and dependencies.

**Estimated Timeline**: 4-6 weeks (full-time development)

---

## Phase 1: Project Setup & Core Infrastructure (Week 1)

### Goal
Set up FastAPI project structure, dependencies, and configuration management.

### Tasks

#### 1.1 Initialize Python Project
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Initialize pip packages
pip install --upgrade pip setuptools wheel

# Create directory structure
mkdir -p src/{fastapi_app,agents,mcp_integration,resource_storage,output_generation,litellm_integration,utils}
mkdir -p output tests docs
```

**Files to Create:**
- `pyproject.toml` - Project metadata (if using Poetry)
- `requirements.txt` - Python dependencies
- `.gitignore` - Standard Python gitignore
- `.env.example` - Template for environment variables

#### 1.2 Install Core Dependencies
```
# Web Framework
fastapi==0.104.1
uvicorn==0.24.0

# Agent Orchestration
langgraph==0.0.40
langchain==0.1.0

# LLM Abstraction
litellm==1.40.0

# Data Models & Validation
pydantic==2.5.0
pydantic-settings==2.1.0

# HTTP Client
httpx==0.25.2

# Async Support
aiohttp==3.9.1

# Utilities
python-multipart==0.0.6
python-dotenv==1.0.0
structlog==23.3.0

# GraphQL (optional, for generic GraphQL adapter)
gql==3.5.0
aiohttp-transport==0.6.0

# PDF Export (optional)
weasyprint==60.0

# Testing
pytest==7.4.3
pytest-asyncio==0.23.0
pytest-mock==3.12.0

# Code Quality
black==23.12.0
ruff==0.1.8
mypy==1.7.1
```

**File to Create:**
- `requirements.txt` - Complete with versions

#### 1.3 Create Core Configuration Module
**File**: `src/config.py`

```python
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Context-Aware Question Generator"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # API Settings
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    
    # LLM Settings
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # MCP Settings
    MCP_CONFIG_PATH: str = "mcp.json"
    
    # Storage Settings
    OUTPUT_DIR: str = "./output"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

#### 1.4 Create Logging Setup
**File**: `src/utils/logging.py`

```python
import structlog
from src.config import settings

def setup_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()
```

#### 1.5 Create Basic Models
**File**: `src/models.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class AnalysisState(BaseModel):
    """LangGraph state schema"""
    # Input
    transcript_text: str
    one_pager_text: str
    jira_id: Optional[str] = None
    
    # Processing stages
    entities: Optional[Dict[str, Any]] = None
    search_queries: Optional[Dict[str, List[str]]] = None
    mcp_results: Optional[Dict[str, List[Dict]]] = None
    aggregated_context: Optional[Dict[str, Any]] = None
    
    # Storage
    storage_path: Optional[str] = None
    storage_metadata: Optional[Dict[str, Any]] = None
    
    # Output
    questions: Optional[List[Dict]] = None
    recommendations: Optional[List[str]] = None
    output_artifacts: Optional[Dict[str, str]] = None
    
    # Tracking
    execution_errors: List[str] = Field(default_factory=list)
    execution_start_time: Optional[datetime] = None
    execution_end_time: Optional[datetime] = None

class AnalysisRequest(BaseModel):
    """API request model"""
    jira_id: Optional[str] = None
    # Files handled separately in FastAPI

class AnalysisResponse(BaseModel):
    """API response model"""
    status: str  # "success", "partial", "failed"
    output_path: str
    artifacts: Dict[str, str]
    execution_time: float
    jira_id: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
```

#### 1.6 Create .env.example
**File**: `.env.example`

```env
# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# FastAPI
API_PORT=8000
API_HOST=0.0.0.0

# LLM Providers
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Storage
OUTPUT_DIR=./output

# MCP Configuration
MCP_CONFIG_PATH=mcp.json

# Confluence
CONFLUENCE_API_URL=https://company.confluence.com
CONFLUENCE_API_KEY=your_key_here

# Jira
JIRA_API_URL=https://company.atlassian.net
JIRA_API_KEY=your_key_here

# Salesforce
SALESFORCE_INSTANCE_URL=https://company.salesforce.com
SALESFORCE_CLIENT_ID=your_id_here
SALESFORCE_CLIENT_SECRET=your_secret_here
SALESFORCE_USERNAME=your_username_here
SALESFORCE_SECURITY_TOKEN=your_token_here

# HubSpot
HUBSPOT_API_KEY=your_key_here

# GitHub (optional)
GITHUB_TOKEN=your_token_here
GITHUB_ORG=your_org_here
```

### Deliverables
- ✅ Project structure created
- ✅ Dependencies installed
- ✅ Configuration module working
- ✅ Environment setup complete

### Testing
```bash
pytest tests/test_config.py
```

---

## Phase 2: MCP Integration Framework (Week 1-2)

### Goal
Implement dynamic MCP loading, registry, and generic adapters.

### Dependencies
- Phase 1 complete

### Tasks

#### 2.1 Create MCP Schema & Validation
**File**: `src/mcp_integration/schema.py`

```python
from typing import Dict, Optional, List, Any
from enum import Enum
from pydantic import BaseModel, Field, validator

class MCPType(str, Enum):
    CONFLUENCE = "confluence"
    JIRA = "jira"
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    GITHUB = "github"
    GENERIC_REST = "generic_rest"
    GENERIC_GRAPHQL = "generic_graphql"

class MCPConfig(BaseModel):
    """Individual MCP configuration"""
    id: str
    name: str
    type: MCPType
    enabled: bool = True
    description: Optional[str] = None
    priority: int = 0
    config: Dict[str, Any] = Field(description="MCP-specific credentials/settings")
    search: Dict[str, Any] = Field(description="Search parameters")
    mapping: Dict[str, str] = Field(description="Field mappings")
    relevance_weight: float = Field(default=1.0, ge=0.0, le=1.0)
    
    @validator('id')
    def id_lowercase(cls, v):
        return v.lower()

class MCPRegistry(BaseModel):
    """Complete registry schema"""
    version: str = "1.0"
    mcp_servers: List[MCPConfig]
```

#### 2.2 Create MCP Registry Loader
**File**: `src/mcp_integration/registry.py`

```python
import json
from pathlib import Path
import os
from typing import Dict, List, Optional
import logging

from .schema import MCPRegistry, MCPConfig, MCPType

logger = logging.getLogger(__name__)

class MCPRegistryManager:
    """Load and manage MCPs from mcp.json"""
    
    def __init__(self, config_path: str = "mcp.json"):
        self.config_path = Path(config_path)
        self.mcps: Dict[str, MCPConfig] = {}
        self._loaded = False
    
    def load(self) -> None:
        """Load MCPs from configuration file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"MCP config not found: {self.config_path}")
        
        # Load JSON
        with open(self.config_path, 'r') as f:
            config_data = json.load(f)
        
        # Expand environment variables
        config_str = json.dumps(config_data)
        for key, value in os.environ.items():
            config_str = config_str.replace(f"${{{key}}}", value)
        config_data = json.loads(config_str)
        
        # Validate
        registry = MCPRegistry(**config_data)
        
        # Index by ID
        for mcp_config in registry.mcp_servers:
            self.mcps[mcp_config.id] = mcp_config
            logger.info(f"Registered MCP: {mcp_config.id} ({mcp_config.type})")
        
        self._loaded = True
    
    def get_mcp(self, mcp_id: str) -> Optional[MCPConfig]:
        if not self._loaded:
            self.load()
        return self.mcps.get(mcp_id)
    
    def get_enabled_mcps(self) -> List[MCPConfig]:
        if not self._loaded:
            self.load()
        return sorted(
            [m for m in self.mcps.values() if m.enabled],
            key=lambda x: x.priority
        )
    
    def list_all(self) -> List[Dict]:
        if not self._loaded:
            self.load()
        return [
            {
                "id": m.id,
                "name": m.name,
                "type": m.type,
                "enabled": m.enabled,
                "priority": m.priority
            }
            for m in sorted(self.mcps.values(), key=lambda x: x.priority)
        ]
```

#### 2.3 Create Base Adapter
**File**: `src/mcp_integration/base_adapter.py`

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

from .schema import MCPConfig

logger = logging.getLogger(__name__)

class BaseMCPAdapter(ABC):
    """Base adapter for all MCPs"""
    
    def __init__(self, config: MCPConfig):
        self.config = config
        self.name = config.id
    
    @abstractmethod
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search MCP"""
        pass
    
    def _apply_mapping(self, raw_result: Dict) -> Dict:
        """Map response fields to standard format"""
        mapped = {
            "source": self.name,
            "raw": raw_result
        }
        
        for standard_field, mcp_field in self.config.mapping.items():
            value = self._get_nested_value(raw_result, mcp_field)
            if value:
                mapped[standard_field] = value
        
        return mapped
    
    @staticmethod
    def _get_nested_value(obj: Dict, path: str) -> Any:
        for key in path.split('.'):
            if isinstance(obj, dict):
                obj = obj.get(key)
            else:
                return None
        return obj
```

#### 2.4 Create Generic REST Adapter
**File**: `src/mcp_integration/generic_adapter.py`

```python
import httpx
import logging
from typing import List, Dict, Any

from .base_adapter import BaseMCPAdapter

logger = logging.getLogger(__name__)

class GenericRESTAdapter(BaseMCPAdapter):
    """Generic REST API adapter"""
    
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        config = self.config.config
        search_config = self.config.search
        
        url = f"{config['api_url']}{search_config.get('endpoint', '/search')}"
        headers = {
            "Authorization": f"Bearer {config.get('api_key', '')}"
        }
        headers.update(config.get('headers', {}))
        
        # Build body
        body = search_config.get('body_template', {}).copy()
        query_param = search_config.get('query_parameter', 'q')
        body[query_param] = query
        
        try:
            async with httpx.AsyncClient(
                timeout=config.get('timeout_seconds', 30)
            ) as client:
                response = await client.request(
                    method=search_config.get('method', 'POST'),
                    url=url,
                    json=body,
                    headers=headers
                )
                response.raise_for_status()
                results = response.json()
        except Exception as e:
            logger.error(f"Error querying {self.name}: {e}")
            return []
        
        # Parse and map results
        items = results.get('results', results.get('items', []))
        max_results = search_config.get('max_results', 10)
        
        return [
            self._apply_mapping(item)
            for item in items[:max_results]
        ]
```

#### 2.5 Create Adapter Factory
**File**: `src/mcp_integration/factory.py`

```python
from typing import Type
import logging

from .schema import MCPConfig, MCPType
from .base_adapter import BaseMCPAdapter
from .generic_adapter import GenericRESTAdapter

logger = logging.getLogger(__name__)

class MCPAdapterFactory:
    """Create adapters for MCPs"""
    
    _adapters: dict = {
        MCPType.GENERIC_REST: GenericRESTAdapter,
        # Type-specific adapters to be added in Phase 3
    }
    
    @classmethod
    def create(cls, config: MCPConfig) -> BaseMCPAdapter:
        """Create appropriate adapter"""
        adapter_class = cls._adapters.get(config.type)
        
        if not adapter_class:
            # Fallback to generic REST for unknown types
            logger.warning(f"No specific adapter for {config.type}, using GenericRESTAdapter")
            adapter_class = GenericRESTAdapter
        
        return adapter_class(config)
    
    @classmethod
    def register(cls, mcp_type: MCPType, adapter_class: Type[BaseMCPAdapter]):
        """Register custom adapter"""
        cls._adapters[mcp_type] = adapter_class
```

#### 2.6 Create MCP Manager (Public API)
**File**: `src/mcp_integration/__init__.py`

```python
import asyncio
from typing import Dict, List
import logging

from .registry import MCPRegistryManager
from .factory import MCPAdapterFactory
from .base_adapter import BaseMCPAdapter

logger = logging.getLogger(__name__)

class MCPManager:
    """Public API for MCP management"""
    
    def __init__(self, config_path: str = "mcp.json"):
        self.registry = MCPRegistryManager(config_path)
        self.adapters: Dict[str, BaseMCPAdapter] = {}
    
    async def initialize(self) -> None:
        """Initialize all enabled MCPs"""
        self.registry.load()
        
        for mcp_config in self.registry.get_enabled_mcps():
            try:
                adapter = MCPAdapterFactory.create(mcp_config)
                self.adapters[mcp_config.id] = adapter
                logger.info(f"Initialized adapter: {mcp_config.id}")
            except Exception as e:
                logger.error(f"Failed to initialize {mcp_config.id}: {e}")
    
    async def search_all(self, query: str) -> Dict[str, List]:
        """Search across all enabled MCPs in parallel"""
        if not self.adapters:
            await self.initialize()
        
        tasks = [
            self._search_mcp(mcp_id, adapter, query)
            for mcp_id, adapter in self.adapters.items()
        ]
        
        results = {}
        for mcp_id, mcp_results in await asyncio.gather(*tasks):
            results[mcp_id] = mcp_results
        
        return results
    
    async def _search_mcp(self, mcp_id: str, adapter: BaseMCPAdapter, query: str):
        """Search single MCP"""
        try:
            results = await adapter.search(query)
            return (mcp_id, results)
        except Exception as e:
            logger.error(f"Error searching {mcp_id}: {e}")
            return (mcp_id, [])
    
    def list_mcps(self) -> List[Dict]:
        """List all available MCPs"""
        return self.registry.list_all()
```

#### 2.7 Copy mcp.json Template
**File**: `mcp.json`

Copy from the MCP_ARCHITECTURE.md (complete configuration with all 7 MCPs, with Confluence/Jira/Salesforce/HubSpot enabled, others disabled).

### Deliverables
- ✅ MCP schema and validation
- ✅ Dynamic registry loader
- ✅ Base adapter class
- ✅ Generic REST adapter
- ✅ Adapter factory
- ✅ MCPManager (public API)
- ✅ mcp.json configuration

### Testing
```bash
pytest tests/test_mcp_integration/
# Tests for registry loading, adapter creation, config validation
```

---

## Phase 3: FastAPI Application Setup (Week 2)

### Goal
Create FastAPI app structure, endpoints, middleware, and request handling.

### Dependencies
- Phase 1 complete
- Phase 2 complete

### Tasks

#### 3.1 Create FastAPI App
**File**: `src/fastapi_app/app.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.config import settings
from src.utils.logging import setup_logging
from .routes import router

setup_logging()
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Context-Aware Question Generation Tool",
        version="0.1.0",
        debug=settings.DEBUG
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(router)
    
    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    # List MCPs endpoint
    @app.get("/mcps")
    async def list_mcps():
        from src.mcp_integration import MCPManager
        manager = MCPManager()
        return {"mcps": manager.list_mcps()}
    
    return app

app = create_app()
```

#### 3.2 Create Routes
**File**: `src/fastapi_app/routes.py`

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import time
import logging

from src.models import AnalysisResponse
from src.mcp_integration import MCPManager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    transcript: UploadFile = File(...),
    one_pager: UploadFile = File(...)
):
    """
    Analyze transcript and one-pager documents.
    
    Returns question document, resources, and metadata.
    """
    start_time = time.time()
    
    try:
        # Read files
        transcript_text = (await transcript.read()).decode('utf-8')
        one_pager_text = (await one_pager.read()).decode('utf-8')
        
        # TODO: Invoke LangGraph workflow
        # For now, return placeholder
        
        execution_time = time.time() - start_time
        
        return AnalysisResponse(
            status="success",
            output_path="./output/PLACEHOLDER/",
            artifacts={
                "questions": "./output/PLACEHOLDER/questions.md",
                "report": "./output/PLACEHOLDER/report.html",
                "source_of_truth": "./output/PLACEHOLDER/SOURCE_OF_TRUTH.md"
            },
            execution_time=execution_time,
            jira_id="PLACEHOLDER-123"
        )
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### 3.3 Create Main Entry Point
**File**: `src/main.py`

```python
from fastapi import FastAPI
import uvicorn
import logging

from src.config import settings
from src.fastapi_app.app import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
```

#### 3.4 Create __init__.py Files
```bash
touch src/__init__.py
touch src/fastapi_app/__init__.py
touch src/mcp_integration/__init__.py  # Already exists
touch src/agents/__init__.py
touch src/resource_storage/__init__.py
touch src/output_generation/__init__.py
touch src/litellm_integration/__init__.py
touch src/utils/__init__.py
```

### Deliverables
- ✅ FastAPI app setup
- ✅ Routes created
- ✅ CORS middleware configured
- ✅ Health check endpoint
- ✅ MCP listing endpoint
- ✅ Placeholder analyze endpoint

### Testing
```bash
# Start server
python -m uvicorn src.main:app --reload

# Test in another terminal
curl http://localhost:8000/health
curl http://localhost:8000/mcps
```

---

## Phase 4: LangGraph Workflow & Agents (Week 2-3)

### Goal
Implement LangGraph StateGraph and all 9 agents.

### Dependencies
- Phase 1-3 complete

### Tasks

#### 4.1 Create Agent Configurations
**File**: `src/agents/config.py`

```python
AGENT_CONFIG = {
    "input_processor": {
        "model": None,
        "description": "Parse and validate input files"
    },
    "entity_extractor": {
        "model": "claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "temperature": 0.3,
        "description": "Extract entities and generate search queries"
    },
    # ... rest of agents from requirements
}
```

#### 4.2 Create Input Processor Agent
**File**: `src/agents/input_processor.py`

```python
import logging
from src.models import AnalysisState

logger = logging.getLogger(__name__)

async def input_processor_agent(state: AnalysisState) -> AnalysisState:
    """Validate and normalize input"""
    logger.info("Processing input...")
    
    # Normalize text
    state.transcript_text = state.transcript_text.strip()
    state.one_pager_text = state.one_pager_text.strip()
    
    # Validate
    if not state.transcript_text or not state.one_pager_text:
        state.execution_errors.append("Empty input files")
    
    logger.info("Input processing complete")
    return state
```

#### 4.3 Create Entity Extractor Agent
**File**: `src/agents/entity_extractor.py`

```python
import logging
import re
from src.models import AnalysisState
from src.litellm_integration import LLMClient

logger = logging.getLogger(__name__)

async def entity_extractor_agent(state: AnalysisState) -> AnalysisState:
    """Extract entities using LLM"""
    logger.info("Extracting entities...")
    
    llm = LLMClient(model="claude-3-5-sonnet-20241022")
    
    # Extract Jira ID
    jira_pattern = r'([A-Z]+-\d+)'
    jira_matches = re.findall(jira_pattern, state.transcript_text + state.one_pager_text)
    
    if jira_matches:
        state.jira_id = jira_matches[0]
    
    # TODO: Use LLM for semantic entity extraction
    state.entities = {
        "jira_ids": jira_matches,
        "extracted_at": "iso_timestamp"
    }
    
    # Generate search queries
    state.search_queries = {
        "confluence": ["query1", "query2"],
        "jira": ["query1"],
        "salesforce": ["query1"],
        "hubspot": ["query1"]
    }
    
    logger.info(f"Extracted entities: {state.entities}")
    return state
```

#### 4.4 Create MCP Query Agent
**File**: `src/agents/mcp_query_agent.py`

```python
import logging
from src.models import AnalysisState
from src.mcp_integration import MCPManager

logger = logging.getLogger(__name__)

async def mcp_query_agent(state: AnalysisState) -> AnalysisState:
    """Query all MCPs in parallel"""
    logger.info("Querying MCPs...")
    
    manager = MCPManager()
    await manager.initialize()
    
    # Build combined query
    query = f"{state.one_pager_text[:500]} {' '.join(state.search_queries.get('confluence', []))}"
    
    # Search all MCPs
    results = await manager.search_all(query)
    
    state.mcp_results = results
    logger.info(f"Got results from {len(results)} MCPs")
    
    return state
```

#### 4.5 Create Context Aggregator Agent
**File**: `src/agents/context_aggregator.py`

```python
import logging
from typing import Dict, Any, List
from src.models import AnalysisState

logger = logging.getLogger(__name__)

async def context_aggregator_agent(state: AnalysisState) -> AnalysisState:
    """Aggregate and score MCP results"""
    logger.info("Aggregating context...")
    
    aggregated = {}
    
    for source, results in (state.mcp_results or {}).items():
        # Deduplicate
        unique_results = {}
        for result in results:
            key = result.get('raw', {}).get('url', result.get('raw', {}).get('id', ''))
            if key not in unique_results:
                unique_results[key] = result
        
        # Score relevance (TODO: use LLM for semantic scoring)
        scored = []
        for result in unique_results.values():
            scored.append({
                **result,
                "relevance_score": 0.85  # Placeholder
            })
        
        aggregated[source] = scored
    
    state.aggregated_context = aggregated
    logger.info(f"Aggregated {sum(len(v) for v in aggregated.values())} results")
    
    return state
```

#### 4.6 Create LangGraph Workflow
**File**: `src/agents/workflow.py`

```python
from langgraph.graph import StateGraph, END
from src.models import AnalysisState
from .input_processor import input_processor_agent
from .entity_extractor import entity_extractor_agent
from .mcp_query_agent import mcp_query_agent
from .context_aggregator import context_aggregator_agent
# Import other agents as they're created

def build_analysis_workflow():
    """Build LangGraph workflow"""
    workflow = StateGraph(AnalysisState)
    
    # Add nodes
    workflow.add_node("input_processor", input_processor_agent)
    workflow.add_node("entity_extractor", entity_extractor_agent)
    workflow.add_node("mcp_query", mcp_query_agent)
    workflow.add_node("context_aggregator", context_aggregator_agent)
    
    # Define edges
    workflow.set_entry_point("input_processor")
    workflow.add_edge("input_processor", "entity_extractor")
    workflow.add_edge("entity_extractor", "mcp_query")
    workflow.add_edge("mcp_query", "context_aggregator")
    # Add more edges as agents are created
    
    workflow.add_edge("context_aggregator", END)
    
    return workflow.compile()
```

### Deliverables
- ✅ Agent configurations
- ✅ Input processor agent
- ✅ Entity extractor agent
- ✅ MCP query agent
- ✅ Context aggregator agent
- ✅ LangGraph workflow compiled

### Testing
```bash
pytest tests/test_agents/
# Unit tests for each agent
```

---

## Phase 5: LiteLLM Integration & Remaining Agents (Week 3-4)

### Goal
Implement LiteLLM wrapper and complete remaining agents (resource storage, question generation, output formatting).

### Dependencies
- Phase 4 complete

### Tasks

#### 5.1 Create LiteLLM Wrapper
**File**: `src/litellm_integration/llm_client.py`

```python
from litellm import completion, acompletion
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    """Wrapper around LiteLLM"""
    
    def __init__(self, model: str, provider: str = "anthropic", **kwargs):
        self.model = model
        self.provider = provider
        self.kwargs = kwargs
    
    async def call(self, messages: List[Dict], **options) -> str:
        """Make async LLM call"""
        try:
            response = await acompletion(
                model=self.model,
                messages=messages,
                **{**self.kwargs, **options}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
```

#### 5.2 Create Question Generator Agent
**File**: `src/agents/question_generator.py`

```python
import logging
import json
from src.models import AnalysisState
from src.litellm_integration import LLMClient

logger = logging.getLogger(__name__)

async def question_generator_agent(state: AnalysisState) -> AnalysisState:
    """Generate questions from aggregated context"""
    logger.info("Generating questions...")
    
    llm = LLMClient(model="claude-3-opus-20250219")
    
    # Prepare context summary
    context_summary = json.dumps(state.aggregated_context, indent=2)[:2000]
    
    prompt = f"""
    Based on this context:
    {context_summary}
    
    Generate 10-15 clarification questions for a business analyst to review.
    Format as JSON with: [{"category": "functional|nonfunctional|business", "question": "...", "relevance": 0.9}]
    """
    
    response = await llm.call([{"role": "user", "content": prompt}])
    
    # Parse response
    try:
        questions = json.loads(response)
        state.questions = questions
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM response")
        state.questions = []
    
    logger.info(f"Generated {len(state.questions)} questions")
    return state
```

#### 5.3 Create Resource Storage Agent
**File**: `src/agents/resource_storage_agent.py`

```python
import logging
import json
from pathlib import Path
from datetime import datetime
from src.models import AnalysisState
from src.config import settings

logger = logging.getLogger(__name__)

async def resource_storage_agent(state: AnalysisState) -> AnalysisState:
    """Store resources locally"""
    logger.info("Storing resources...")
    
    # Determine folder name
    folder_name = state.jira_id or f"analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    output_dir = Path(settings.OUTPUT_DIR) / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create resource subdirectories
    for source in ["confluence", "jira", "salesforce", "hubspot"]:
        (output_dir / "resources" / source).mkdir(parents=True, exist_ok=True)
    
    # Store resources
    metadata = {
        "jira_id": state.jira_id,
        "generated_at": datetime.utcnow().isoformat(),
        "resources": [],
        "statistics": {}
    }
    
    for source, results in (state.aggregated_context or {}).items():
        source_path = output_dir / "resources" / source
        
        for idx, result in enumerate(results, 1):
            # Save as JSON
            filename = f"{source}-{idx}.json"
            with open(source_path / filename, 'w') as f:
                json.dump(result['raw'], f, indent=2)
            
            metadata["resources"].append({
                "id": result.get('id', f"{source}-{idx}"),
                "source": source,
                "path": f"resources/{source}/{filename}"
            })
    
    # Save metadata
    with open(output_dir / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    state.storage_path = str(output_dir)
    state.storage_metadata = metadata
    
    logger.info(f"Stored resources to {output_dir}")
    return state
```

#### 5.4 Create Output Formatter Agent
**File**: `src/agents/output_formatter_agent.py`

```python
import logging
from pathlib import Path
from src.models import AnalysisState

logger = logging.getLogger(__name__)

async def output_formatter_agent(state: AnalysisState) -> AnalysisState:
    """Generate output artifacts"""
    logger.info("Formatting output...")
    
    output_dir = Path(state.storage_path)
    
    # Generate questions.md
    md_content = "# Generated Questions\n\n"
    for q in (state.questions or []):
        md_content += f"## Q: {q.get('question', '')}\n"
        md_content += f"Category: {q.get('category', 'general')}\n"
        md_content += f"Relevance: {q.get('relevance', 0)}\n\n"
    
    with open(output_dir / "questions.md", 'w') as f:
        f.write(md_content)
    
    # TODO: Generate HTML report
    # TODO: Generate SOURCE_OF_TRUTH.md
    
    state.output_artifacts = {
        "questions.md": str(output_dir / "questions.md"),
        "report.html": str(output_dir / "report.html"),
        "source_of_truth.md": str(output_dir / "SOURCE_OF_TRUTH.md"),
        "metadata.json": str(output_dir / "metadata.json")
    }
    
    logger.info("Output formatting complete")
    return state
```

#### 5.5 Update Workflow with New Agents
**File**: `src/agents/workflow.py` (update)

```python
# Add new nodes
workflow.add_node("resource_storage", resource_storage_agent)
workflow.add_node("question_generator", question_generator_agent)
workflow.add_node("output_formatter", output_formatter_agent)

# Connect edges
workflow.add_edge("context_aggregator", "resource_storage")
workflow.add_edge("resource_storage", "question_generator")
workflow.add_edge("question_generator", "output_formatter")
workflow.add_edge("output_formatter", END)
```

### Deliverables
- ✅ LiteLLM client wrapper
- ✅ Question generator agent
- ✅ Resource storage agent
- ✅ Output formatter agent
- ✅ Complete LangGraph workflow

### Testing
```bash
pytest tests/test_agents/test_question_generator.py
pytest tests/test_agents/test_resource_storage.py
```

---

## Phase 6: HTML Report & Final Integration (Week 4-5)

### Goal
Implement HTML report generation and integrate everything together.

### Dependencies
- Phase 5 complete

### Tasks

#### 6.1 Create Jinja2 Templates
**File**: `src/output_generation/templates/report.html`

```html
<!-- HTML template from SYSTEM_ARCHITECTURE.md Section 8.2 -->
```

#### 6.2 Create HTML Formatter
**File**: `src/output_generation/html_formatter.py`

```python
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class HTMLReportGenerator:
    def __init__(self):
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    def generate(self, context: Dict, output_path: str) -> str:
        """Generate HTML report"""
        template = self.env.get_template("report.html")
        html = template.render(**context)
        
        with open(output_path, 'w') as f:
            f.write(html)
        
        logger.info(f"Generated HTML report: {output_path}")
        return output_path
```

#### 6.3 Update FastAPI Routes
**File**: `src/fastapi_app/routes.py` (update)

```python
# Update the /analyze endpoint to invoke LangGraph workflow

from src.agents.workflow import build_analysis_workflow
from src.models import AnalysisState
import datetime

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    transcript: UploadFile = File(...),
    one_pager: UploadFile = File(...)
):
    start_time = datetime.datetime.now()
    
    # Read files
    transcript_text = (await transcript.read()).decode('utf-8')
    one_pager_text = (await one_pager.read()).decode('utf-8')
    
    # Create initial state
    initial_state = AnalysisState(
        transcript_text=transcript_text,
        one_pager_text=one_pager_text,
        execution_start_time=start_time
    )
    
    # Execute workflow
    workflow = build_analysis_workflow()
    final_state = await workflow.ainvoke(initial_state)
    
    execution_time = (datetime.datetime.now() - start_time).total_seconds()
    
    return AnalysisResponse(
        status="success" if not final_state.execution_errors else "partial",
        output_path=final_state.storage_path,
        artifacts=final_state.output_artifacts,
        execution_time=execution_time,
        jira_id=final_state.jira_id,
        errors=final_state.execution_errors
    )
```

#### 6.4 Create Docker Support
**File**: `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY src src/
COPY mcp.json .
COPY .env .env

# Create output directory
RUN mkdir -p output

# Run app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./output:/app/output
      - ./.env:/app/.env
```

#### 6.5 Create Integration Tests
**File**: `tests/test_integration.py`

```python
import pytest
from src.models import AnalysisState
from src.agents.workflow import build_analysis_workflow

@pytest.mark.asyncio
async def test_full_workflow():
    """Test complete workflow"""
    state = AnalysisState(
        transcript_text="Sample transcript with PROJ-123 mentioned",
        one_pager_text="Sample proposal about feature X"
    )
    
    workflow = build_analysis_workflow()
    result = await workflow.ainvoke(state)
    
    assert result.jira_id == "PROJ-123"
    assert result.questions is not None
    assert result.storage_path is not None
```

### Deliverables
- ✅ Jinja2 HTML templates
- ✅ HTML report generator
- ✅ Updated FastAPI routes with workflow
- ✅ Docker support
- ✅ Integration tests

### Testing
```bash
# Run integration tests
pytest tests/test_integration.py -v

# Start application
docker-compose up

# Test endpoint
curl -X POST http://localhost:8000/analyze \
  -F "transcript=@sample.txt" \
  -F "one_pager=@proposal.md"
```

---

## Phase 7: Polish & Deployment (Week 5-6)

### Tasks

- [ ] Code review and optimization
- [ ] Add comprehensive documentation
- [ ] Add API documentation (Swagger)
- [ ] Performance testing
- [ ] Security audit
- [ ] Setup CI/CD pipeline
- [ ] Deployment guide
- [ ] User guide

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Code coverage >80%
- [ ] Environment variables configured
- [ ] mcp.json validated
- [ ] API keys set for all MCPs
- [ ] Database/logging setup

### Deployment
- [ ] Build Docker image
- [ ] Run integration tests
- [ ] Deploy to staging
- [ ] Smoke tests pass
- [ ] Deploy to production
- [ ] Monitor logs

### Post-Deployment
- [ ] Verify all endpoints working
- [ ] Check output folder permissions
- [ ] Monitor API performance
- [ ] Setup alerting

---

## Summary Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| 1 | Week 1 | Project setup, dependencies, config |
| 2 | Week 1-2 | MCP registry, adapters, factory |
| 3 | Week 2 | FastAPI app, routes, endpoints |
| 4 | Week 2-3 | LangGraph workflow, 4 agents |
| 5 | Week 3-4 | LiteLLM, question gen, storage |
| 6 | Week 4-5 | HTML reports, integration |
| 7 | Week 5-6 | Polish, documentation, deployment |
| **Total** | **4-6 weeks** | **Complete production system** |

---

## Key Files Created (Reference)

```
src/
├── main.py
├── config.py
├── models.py
├── fastapi_app/
│   ├── app.py
│   ├── routes.py
│   └── __init__.py
├── mcp_integration/
│   ├── __init__.py
│   ├── schema.py
│   ├── registry.py
│   ├── base_adapter.py
│   ├── generic_adapter.py
│   ├── factory.py
│   └── exceptions.py
├── agents/
│   ├── __init__.py
│   ├── config.py
│   ├── workflow.py
│   ├── input_processor.py
│   ├── entity_extractor.py
│   ├── mcp_query_agent.py
│   ├── context_aggregator.py
│   ├── resource_storage_agent.py
│   ├── question_generator.py
│   └── output_formatter_agent.py
├── litellm_integration/
│   ├── __init__.py
│   └── llm_client.py
├── output_generation/
│   ├── __init__.py
│   ├── html_formatter.py
│   └── templates/
│       └── report.html
├── resource_storage/
│   ├── __init__.py
│   └── storage_manager.py
└── utils/
    ├── __init__.py
    └── logging.py

Root Files:
├── requirements.txt
├── mcp.json
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

