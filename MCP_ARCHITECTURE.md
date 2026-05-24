# Dynamic MCP Architecture

## Problem with Current Approach

Current hardcoded adapters:
```python
src/mcp_integration/
├── confluence_adapter.py
├── jira_adapter.py
├── salesforce_adapter.py
└── hubspot_adapter.py
```

**Issues:**
- ❌ Tight coupling to specific MCPs
- ❌ Code changes required to add new MCPs
- ❌ Duplicate logic across adapters
- ❌ No runtime flexibility
- ❌ Hard to test and maintain

---

## Solution: Configuration-Driven MCP Registry

### Overview

```
┌──────────────────┐
│   mcp.json       │  ◄─── Declarative MCP Configuration
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────┐
│  MCP Registry & Loader       │  ◄─── Discovers & loads MCPs
│  (runtime initialization)    │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Generic MCP Adapter         │  ◄─── Universal query interface
│  (REST, GraphQL, etc.)       │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  MCP Agents                  │  ◄─── LangGraph agents use MCPs
│  (auto-created per config)   │
└──────────────────────────────┘
```

---

## Implementation

### 1. MCP Configuration File (`mcp.json`)

```json
{
  "version": "1.0",
  "mcp_servers": [
    {
      "id": "confluence",
      "name": "Confluence",
      "type": "confluence",
      "enabled": true,
      "description": "Design docs, ADRs, technical specifications",
      "priority": 1,
      "config": {
        "api_url": "${CONFLUENCE_API_URL}",
        "api_key": "${CONFLUENCE_API_KEY}",
        "timeout_seconds": 30,
        "max_retries": 3,
        "retry_backoff_factor": 2.0,
        "ca_cert": null
      },
      "search": {
        "query_type": "cql",
        "max_results": 15,
        "sort_by": "relevance",
        "content_types": ["page", "blogpost"],
        "spaces": null,
        "exclude_labels": ["deprecated", "archived"],
        "include_attachments": true
      },
      "mapping": {
        "title_field": "title",
        "content_field": "body",
        "url_field": "url",
        "timestamp_field": "modified",
        "author_field": "lastModifier.displayName"
      },
      "relevance_weight": 0.95
    },
    {
      "id": "jira",
      "name": "Jira",
      "type": "jira",
      "enabled": true,
      "description": "Issues, epics, stories, technical tasks",
      "priority": 2,
      "config": {
        "api_url": "${JIRA_API_URL}",
        "api_key": "${JIRA_API_KEY}",
        "timeout_seconds": 30,
        "max_retries": 3
      },
      "search": {
        "query_type": "jql",
        "max_results": 20,
        "issue_types": ["Story", "Task", "Bug", "Epic"],
        "statuses": null,
        "projects": null,
        "expand_fields": ["changelog", "transitions"]
      },
      "mapping": {
        "title_field": "fields.summary",
        "content_field": "fields.description",
        "url_field": "self",
        "id_field": "key",
        "type_field": "fields.issuetype.name"
      },
      "relevance_weight": 0.90
    },
    {
      "id": "salesforce",
      "name": "Salesforce CRM",
      "type": "salesforce",
      "enabled": true,
      "description": "Customer accounts, opportunities, interactions",
      "priority": 3,
      "config": {
        "instance_url": "${SALESFORCE_INSTANCE_URL}",
        "client_id": "${SALESFORCE_CLIENT_ID}",
        "client_secret": "${SALESFORCE_CLIENT_SECRET}",
        "username": "${SALESFORCE_USERNAME}",
        "security_token": "${SALESFORCE_SECURITY_TOKEN}",
        "timeout_seconds": 30
      },
      "search": {
        "query_type": "soql",
        "max_results": 10,
        "sobjects": ["Account", "Opportunity", "Contact"],
        "fields": ["Id", "Name", "Type", "Industry", "BillingCity"]
      },
      "mapping": {
        "title_field": "Name",
        "content_field": "Description",
        "url_field": "Id",
        "type_field": "SobjectType"
      },
      "relevance_weight": 0.85
    },
    {
      "id": "hubspot",
      "name": "HubSpot CRM",
      "type": "hubspot",
      "enabled": true,
      "description": "Contacts, deals, feedback, support tickets",
      "priority": 4,
      "config": {
        "api_url": "https://api.hubapi.com",
        "api_key": "${HUBSPOT_API_KEY}",
        "timeout_seconds": 30
      },
      "search": {
        "query_type": "rest",
        "max_results": 15,
        "object_types": ["contacts", "deals", "tickets"],
        "properties": ["firstname", "lastname", "email", "dealstage"]
      },
      "mapping": {
        "title_field": "properties.name",
        "content_field": "properties.notes_last_updated",
        "url_field": "id"
      },
      "relevance_weight": 0.80
    },
    {
      "id": "github",
      "name": "GitHub",
      "type": "github",
      "enabled": false,
      "description": "Issues, PRs, discussions, code references",
      "priority": 5,
      "config": {
        "api_url": "https://api.github.com",
        "token": "${GITHUB_TOKEN}",
        "org": "${GITHUB_ORG}",
        "timeout_seconds": 30
      },
      "search": {
        "query_type": "graphql",
        "max_results": 20,
        "repos": null,
        "include_discussions": true
      },
      "mapping": {
        "title_field": "title",
        "content_field": "body",
        "url_field": "url"
      },
      "relevance_weight": 0.75
    },
    {
      "id": "custom_erp",
      "name": "Custom ERP System",
      "type": "generic_rest",
      "enabled": false,
      "description": "Enterprise resource planning system",
      "priority": 6,
      "config": {
        "api_url": "${ERP_API_URL}",
        "api_key": "${ERP_API_KEY}",
        "auth_type": "bearer_token",
        "timeout_seconds": 60,
        "headers": {
          "Accept": "application/json",
          "X-Custom-Header": "value"
        }
      },
      "search": {
        "query_type": "rest_post",
        "endpoint": "/api/v1/search",
        "method": "POST",
        "max_results": 50,
        "query_parameter": "search_query",
        "body_template": {
          "q": "{{query}}",
          "limit": 50,
          "offset": 0
        }
      },
      "mapping": {
        "title_field": "name",
        "content_field": "description",
        "url_field": "id"
      },
      "relevance_weight": 0.70
    },
    {
      "id": "internal_wiki",
      "name": "Internal Wiki (GraphQL)",
      "type": "generic_graphql",
      "enabled": false,
      "description": "Internal knowledge base",
      "priority": 7,
      "config": {
        "endpoint": "${WIKI_GRAPHQL_URL}",
        "api_key": "${WIKI_API_KEY}",
        "timeout_seconds": 30
      },
      "search": {
        "query_type": "graphql",
        "query_template": "query SearchWiki($query: String!) { search(q: $query) { edges { node { id title content url } } } }"
      },
      "mapping": {
        "title_field": "title",
        "content_field": "content",
        "url_field": "url"
      },
      "relevance_weight": 0.65
    }
  ]
}
```

---

### 2. MCP Configuration Schema (`src/mcp_integration/schema.py`)

```python
from typing import Dict, Optional, List, Any
from enum import Enum
from pydantic import BaseModel, Field, validator

class MCPType(str, Enum):
    """Supported MCP types"""
    CONFLUENCE = "confluence"
    JIRA = "jira"
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"

class MCPConfig(BaseModel):
    """MCP configuration schema"""
    id: str
    name: str
    type: MCPType
    enabled: bool = True
    description: Optional[str] = None
    priority: int = 0
    
    config: Dict[str, Any] = Field(description="MCP-specific config (API keys, URLs, etc.)")
    search: Dict[str, Any] = Field(description="Search strategy and parameters")
    mapping: Dict[str, str] = Field(description="Field mappings from MCP response")
    relevance_weight: float = Field(default=1.0, ge=0.0, le=1.0)
    
    @validator('id')
    def id_must_be_lowercase(cls, v):
        return v.lower()

class MCPRegistry(BaseModel):
    """Registry of all configured MCPs"""
    version: str = "1.0"
    mcp_servers: List[MCPConfig]
    
    class Config:
        use_enum_values = True
```

---

### 3. Dynamic MCP Loader (`src/mcp_integration/registry.py`)

```python
import json
from typing import Dict, List, Optional
from pathlib import Path
import os
from pydantic import ValidationError

from schema import MCPRegistry, MCPConfig, MCPType

class MCPRegistry:
    """Registry that loads and manages MCPs from config"""
    
    def __init__(self, config_path: str = "mcp.json"):
        self.config_path = Path(config_path)
        self.mcps: Dict[str, MCPConfig] = {}
        self._loaded = False
    
    def load(self) -> None:
        """Load MCPs from mcp.json"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"MCP config not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config_data = json.load(f)
        
        # Expand environment variables
        config_str = json.dumps(config_data)
        for key, value in os.environ.items():
            config_str = config_str.replace(f"${{{key}}}", value)
        config_data = json.loads(config_str)
        
        # Validate schema
        try:
            registry = MCPRegistry(**config_data)
        except ValidationError as e:
            raise ValueError(f"Invalid MCP config: {e}")
        
        # Index MCPs by ID
        for mcp_config in registry.mcp_servers:
            self.mcps[mcp_config.id] = mcp_config
        
        self._loaded = True
    
    def get_mcp(self, mcp_id: str) -> Optional[MCPConfig]:
        """Get MCP config by ID"""
        if not self._loaded:
            self.load()
        return self.mcps.get(mcp_id)
    
    def get_enabled_mcps(self) -> List[MCPConfig]:
        """Get all enabled MCPs, sorted by priority"""
        if not self._loaded:
            self.load()
        return sorted(
            [mcp for mcp in self.mcps.values() if mcp.enabled],
            key=lambda x: x.priority
        )
    
    def get_mcp_by_type(self, mcp_type: MCPType) -> List[MCPConfig]:
        """Get MCPs by type"""
        if not self._loaded:
            self.load()
        return [mcp for mcp in self.mcps.values() if mcp.type == mcp_type]
    
    def enable_mcp(self, mcp_id: str) -> None:
        """Enable an MCP at runtime"""
        if mcp := self.get_mcp(mcp_id):
            mcp.enabled = True
    
    def disable_mcp(self, mcp_id: str) -> None:
        """Disable an MCP at runtime"""
        if mcp := self.get_mcp(mcp_id):
            mcp.enabled = False
    
    def list_all_mcps(self) -> List[Dict]:
        """List all available MCPs"""
        if not self._loaded:
            self.load()
        return [
            {
                "id": mcp.id,
                "name": mcp.name,
                "type": mcp.type,
                "enabled": mcp.enabled,
                "priority": mcp.priority
            }
            for mcp in sorted(self.mcps.values(), key=lambda x: x.priority)
        ]
```

---

### 4. Generic MCP Adapter (`src/mcp_integration/generic_adapter.py`)

```python
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import httpx
import asyncio

from schema import MCPConfig

class BaseMCPAdapter(ABC):
    """Base class for all MCP adapters"""
    
    def __init__(self, config: MCPConfig):
        self.config = config
        self.name = config.id
    
    @abstractmethod
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Execute search on MCP"""
        pass
    
    @abstractmethod
    async def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """Fetch specific resource from MCP"""
        pass
    
    def _apply_mapping(self, raw_result: Dict) -> Dict:
        """Map MCP response fields to standard format"""
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
        """Get value from nested dict using dot notation"""
        for key in path.split('.'):
            if isinstance(obj, dict):
                obj = obj.get(key)
            else:
                return None
        return obj

class ConfluenceAdapter(BaseMCPAdapter):
    """Confluence-specific adapter"""
    # Implementation for Confluence-specific features
    pass

class JiraAdapter(BaseMCPAdapter):
    """Jira-specific adapter"""
    # Implementation for Jira-specific features
    pass

# ... More type-specific adapters
```

---

### 5. MCP Factory (`src/mcp_integration/factory.py`)

```python
from typing import Dict
from schema import MCPConfig, MCPType

class MCPAdapterFactory:
    """Factory to create appropriate adapter for MCP config"""
    
    _adapters = {
        MCPType.CONFLUENCE: ConfluenceAdapter,
        MCPType.JIRA: JiraAdapter,
        MCPType.SALESFORCE: SalesforceAdapter,
        MCPType.HUBSPOT: HubspotAdapter
    }
    
    @classmethod
    def create(cls, config: MCPConfig):
        """Create appropriate adapter for config"""
        adapter_class = cls._adapters.get(config.type)
        if not adapter_class:
            raise ValueError(f"Unknown MCP type: {config.type}")
        return adapter_class(config)
    
    @classmethod
    def register(cls, mcp_type: MCPType, adapter_class):
        """Register custom adapter for type"""
        cls._adapters[mcp_type] = adapter_class
```

---

### 6. Updated MCP Integration Module

```python
# src/mcp_integration/__init__.py

from registry import MCPRegistry
from factory import MCPAdapterFactory

class MCPManager:
    """Manages dynamic MCP initialization and queries"""
    
    def __init__(self, config_path: str = "mcp.json"):
        self.registry = MCPRegistry(config_path)
        self.registry.load()
        self.adapters = {}
    
    async def initialize_adapters(self):
        """Create adapters for all enabled MCPs"""
        for mcp_config in self.registry.get_enabled_mcps():
            adapter = MCPAdapterFactory.create(mcp_config)
            self.adapters[mcp_config.id] = adapter
    
    async def search_all(self, query: str) -> Dict[str, List]:
        """Search across all enabled MCPs"""
        results = {}
        tasks = []
        
        for mcp_id, adapter in self.adapters.items():
            tasks.append(self._search_mcp(mcp_id, adapter, query))
        
        for mcp_id, mcp_results in await asyncio.gather(*tasks):
            results[mcp_id] = mcp_results
        
        return results
    
    async def _search_mcp(self, mcp_id: str, adapter, query: str):
        try:
            results = await adapter.search(query)
            return (mcp_id, results)
        except Exception as e:
            logger.error(f"Error querying {mcp_id}: {e}")
            return (mcp_id, [])
```

---

## Updated Project Structure

```
src/
├── mcp_integration/
│   ├── __init__.py              # MCPManager (public API)
│   ├── registry.py              # MCPRegistry (loads mcp.json)
│   ├── schema.py                # Pydantic schemas
│   ├── factory.py               # MCPAdapterFactory
│   ├── generic_adapter.py       # Generic adapters (REST, GraphQL)
│   ├── adapters/                # Type-specific adapters (optional)
│   │   ├── confluence.py
│   │   ├── jira.py
│   │   └── ...
│   └── exceptions.py            # MCP-specific exceptions
│
└── mcp.json                     # Configuration file (moved to root)
```

---

## Usage Example

### Agent Integration

```python
# agents/mcp_query_agent.py
from mcp_integration import MCPManager

class MCPQueryAgent:
    """Dynamic MCP query agent"""
    
    def __init__(self):
        self.mcp_manager = MCPManager(config_path="mcp.json")
    
    async def execute(self, state: AnalysisState):
        # Initialize adapters on first run
        if not self.mcp_manager.adapters:
            await self.mcp_manager.initialize_adapters()
        
        # Get enabled MCPs
        enabled = self.mcp_manager.registry.get_enabled_mcps()
        logger.info(f"Querying {len(enabled)} MCPs: {[m.id for m in enabled]}")
        
        # Search across all MCPs
        results = await self.mcp_manager.search_all(
            query=state.search_queries['general']
        )
        
        # Organize results by source
        state.mcp_results = results
        return state
```

### Adding New MCP at Runtime

```python
# No code changes needed! Just update mcp.json:

{
  "id": "my_custom_system",
  "name": "My Custom System",
  "type": "generic_rest",
  "enabled": true,
  "config": {
    "api_url": "https://api.custom.com",
    "api_key": "${CUSTOM_API_KEY}"
  },
  "search": {...},
  "mapping": {...}
}
```

---

## Benefits

✅ **No Code Changes** - Add MCPs via config
✅ **Dynamic Loading** - MCPs loaded at runtime
✅ **Type Support** - REST, GraphQL, specific services
✅ **Easy Extension** - Register custom adapters via factory
✅ **Environment Flexibility** - Env vars expanded in config
✅ **Type Safe** - Pydantic schema validation
✅ **Parallel Queries** - Built-in async support
✅ **Error Resilience** - Graceful failure per MCP
✅ **Audit Trail** - All MCPs and configs in one place

