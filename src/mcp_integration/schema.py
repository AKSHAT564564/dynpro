"""
MCP Configuration Schema

Pydantic models for validating MCP configuration from mcp.json.
Ensures type safety and runtime validation for all MCP configurations.
"""

from typing import Dict, Optional, List, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class MCPType(str, Enum):
    """Supported MCP types"""
    CONFLUENCE = "confluence"
    JIRA = "jira"
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    GITHUB = "github"
    GENERIC_REST = "generic_rest"
    GENERIC_GRAPHQL = "generic_graphql"


class MCPConfig(BaseModel):
    """
    Configuration for a single MCP server.

    Attributes:
        id: Unique identifier for this MCP (lowercase)
        name: Human-readable name
        type: MCP type (confluence, jira, salesforce, etc.)
        enabled: Whether this MCP is active
        description: What this MCP provides
        priority: Execution priority (lower = earlier)
        config: MCP-specific configuration (API URLs, keys, etc.)
        search: Search strategy and parameters
        mapping: Field mapping from MCP response to standard format
        relevance_weight: Weight for relevance scoring (0.0-1.0)
    """

    id: str = Field(..., description="Unique MCP identifier (lowercase)")
    name: str = Field(..., description="Human-readable MCP name")
    type: MCPType = Field(..., description="MCP type")
    enabled: bool = Field(default=True, description="Whether MCP is active")
    description: Optional[str] = Field(default=None, description="MCP description")
    priority: int = Field(default=0, description="Execution priority (lower = earlier)")

    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="MCP-specific configuration (API URLs, credentials, timeouts, etc.)"
    )
    search: Dict[str, Any] = Field(
        default_factory=dict,
        description="Search strategy and parameters (query type, max results, filters, etc.)"
    )
    mapping: Dict[str, str] = Field(
        default_factory=dict,
        description="Field mappings from MCP response to standard format"
    )
    relevance_weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Weight for relevance scoring (0.0-1.0)"
    )

    @field_validator('id')
    @classmethod
    def validate_id_lowercase(cls, v: str) -> str:
        """Ensure ID is lowercase"""
        return v.lower()

    @field_validator('id')
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate ID format"""
        if not v or not all(c.isalnum() or c == '_' for c in v):
            raise ValueError("ID must contain only alphanumeric characters and underscores")
        return v


class MCPRegistry(BaseModel):
    """
    Registry of all configured MCPs.

    This is the root schema for mcp.json configuration file.
    """

    version: str = Field(default="1.0", description="Configuration version")
    mcp_servers: List[MCPConfig] = Field(
        default_factory=list,
        description="List of configured MCP servers"
    )

    class Config:
        """Pydantic configuration"""
        use_enum_values = True


# Type aliases for convenience
MCPConfigDict = Dict[str, MCPConfig]
MCPTypeList = List[MCPConfig]
