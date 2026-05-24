"""
MCP Adapter Implementations

Concrete adapter implementations for each MCP source (Confluence, Jira, Salesforce, HubSpot).
These adapters make HTTP calls to the respective REST APIs.
"""

from .confluence_adapter import ConfluenceAdapter
from .jira_adapter import JiraAdapter
from .salesforce_adapter import SalesforceAdapter
from .hubspot_adapter import HubSpotAdapter

__all__ = [
    "ConfluenceAdapter",
    "JiraAdapter",
    "SalesforceAdapter",
    "HubSpotAdapter",
]
