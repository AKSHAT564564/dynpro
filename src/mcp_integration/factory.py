"""
MCP Adapter Factory

Creates appropriate adapter instances for MCP configurations.
Supports registration of custom adapters at runtime.
"""

from typing import Dict, Type, Optional
import logging

from .schema import MCPConfig, MCPType
from .base_adapter import BaseMCPAdapter

logger = logging.getLogger(__name__)


class MCPAdapterFactory:
    """
    Factory for creating MCP adapters.

    Manages a registry of adapter classes and creates instances
    based on MCP type. Supports dynamic registration of custom adapters.

    Attributes:
        _adapters: Dictionary mapping MCPType to adapter class
    """

    # Registry of available adapters
    _adapters: Dict[MCPType, Type[BaseMCPAdapter]] = {}

    @classmethod
    def create(cls, config: MCPConfig) -> BaseMCPAdapter:
        """
        Create an adapter instance for the given MCP configuration.

        Args:
            config: MCPConfig instance

        Returns:
            Initialized adapter instance

        Raises:
            ValueError: If no adapter available for MCP type
        """
        adapter_class = cls._adapters.get(config.type)

        if not adapter_class:
            raise ValueError(
                f"No adapter registered for MCP type: {config.type}\n"
                f"Available types: {list(cls._adapters.keys())}\n"
                f"Register a custom adapter with MCPAdapterFactory.register()"
            )

        logger.debug(f"Creating {config.type} adapter for {config.id}")
        return adapter_class(config)

    @classmethod
    def register(
        cls,
        mcp_type: MCPType,
        adapter_class: Type[BaseMCPAdapter]
    ) -> None:
        """
        Register a custom adapter for an MCP type.

        Allows runtime registration of adapters without code changes.

        Args:
            mcp_type: MCPType to register for
            adapter_class: Adapter class (must inherit from BaseMCPAdapter)

        Raises:
            TypeError: If adapter_class doesn't inherit from BaseMCPAdapter
        """
        if not issubclass(adapter_class, BaseMCPAdapter):
            raise TypeError(
                f"Adapter must inherit from BaseMCPAdapter, got {adapter_class}"
            )

        cls._adapters[mcp_type] = adapter_class
        logger.info(f"Registered adapter for {mcp_type}: {adapter_class.__name__}")

    @classmethod
    def unregister(cls, mcp_type: MCPType) -> None:
        """
        Unregister an adapter.

        Args:
            mcp_type: MCPType to unregister
        """
        if mcp_type in cls._adapters:
            del cls._adapters[mcp_type]
            logger.info(f"Unregistered adapter for {mcp_type}")

    @classmethod
    def get_registered_types(cls) -> list:
        """
        Get list of registered MCPTypes.

        Returns:
            List of MCPType enum values
        """
        return list(cls._adapters.keys())

    @classmethod
    def is_registered(cls, mcp_type: MCPType) -> bool:
        """
        Check if adapter is registered for type.

        Args:
            mcp_type: MCPType to check

        Returns:
            True if registered, False otherwise
        """
        return mcp_type in cls._adapters

    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered adapters (mainly for testing).
        """
        cls._adapters.clear()
        logger.debug("Cleared all registered adapters")
