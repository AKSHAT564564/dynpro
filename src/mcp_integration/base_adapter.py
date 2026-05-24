"""
Base MCP Adapter

Abstract base class that all MCP adapters must implement.
Defines the interface for querying and retrieving resources from MCPs.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

from .schema import MCPConfig

logger = logging.getLogger(__name__)


class BaseMCPAdapter(ABC):
    """
    Abstract base class for all MCP adapters.

    All MCP-specific adapters (Confluence, Jira, Salesforce, etc.) inherit from this
    and implement the search and get_resource methods.

    Attributes:
        config: The MCP configuration
        name: The MCP identifier
    """

    def __init__(self, config: MCPConfig):
        """
        Initialize adapter with configuration.

        Args:
            config: MCPConfig instance with credentials and parameters
        """
        self.config = config
        self.name = config.id
        logger.debug(f"Initialized {self.__class__.__name__} adapter for {self.name}")

    @abstractmethod
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute search on the MCP.

        Args:
            query: Search query string
            **kwargs: Additional search parameters

        Returns:
            List of search results with mapped fields
        """
        pass

    @abstractmethod
    async def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific resource from the MCP.

        Args:
            resource_id: Resource identifier

        Returns:
            Resource data or None if not found
        """
        pass

    def _apply_mapping(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply field mappings to transform MCP response to standard format.

        Args:
            raw_result: Raw response from MCP

        Returns:
            Mapped result with standard fields
        """
        mapped = {
            "source": self.name,
            "type": self.config.type,
            "raw": raw_result,
            "relevance_weight": self.config.relevance_weight,
        }

        # Apply mappings from config
        for standard_field, mcp_field in self.config.mapping.items():
            value = self._get_nested_value(raw_result, mcp_field)
            if value is not None:
                mapped[standard_field] = value

        return mapped

    @staticmethod
    def _get_nested_value(obj: Any, path: str) -> Optional[Any]:
        """
        Get value from nested dict/object using dot notation.

        Args:
            obj: Dictionary or object to traverse
            path: Dot-separated path (e.g., "fields.summary")

        Returns:
            Value at path or None if not found
        """
        for key in path.split('.'):
            if isinstance(obj, dict):
                obj = obj.get(key)
            elif hasattr(obj, key):
                obj = getattr(obj, key)
            else:
                return None
        return obj

    async def handle_error(self, error: Exception, context: str = "") -> None:
        """
        Handle errors during MCP operations.

        Args:
            error: The exception that occurred
            context: Context describing what was being done

        Returns:
            None (logs error)
        """
        logger.error(
            f"Error in {self.name} adapter",
            adapter=self.name,
            error_type=type(error).__name__,
            error_message=str(error),
            context=context
        )
