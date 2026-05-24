"""
MCP Integration module

Dynamic MCP loading, registry, and adapter management.

This module provides a configuration-driven approach to managing multiple
MCP (Model Context Protocol) connections without hardcoding specific adapters.

Main Classes:
- MCPManager: Public API for MCP management
- MCPRegistryManager: Loads and manages MCP configurations
- MCPAdapterFactory: Creates adapter instances
- BaseMCPAdapter: Base class for all adapters

Usage:
    from src.mcp_integration import MCPManager

    manager = MCPManager()
    await manager.initialize()
    results = await manager.search_all("search query")
"""

import asyncio
import logging
from typing import Dict, List, Optional

from .registry import MCPRegistryManager
from .factory import MCPAdapterFactory
from .base_adapter import BaseMCPAdapter
from .schema import MCPConfig, MCPType

logger = logging.getLogger(__name__)


class MCPManager:
    """
    Public API for MCP management.

    Manages MCP initialization, parallel querying, and result aggregation.
    Provides unified interface to all configured MCPs.

    Attributes:
        registry: MCPRegistryManager instance
        adapters: Dictionary of initialized adapters indexed by MCP ID
    """

    def __init__(self, config_path: str = "mcp.json"):
        """
        Initialize MCPManager.

        Args:
            config_path: Path to mcp.json configuration file
        """
        self.registry = MCPRegistryManager(config_path)
        self.adapters: Dict[str, BaseMCPAdapter] = {}
        logger.debug("Initialized MCPManager")

    async def initialize(self) -> None:
        """
        Initialize all enabled MCPs.

        Loads configuration, creates adapter instances for all enabled MCPs,
        and reports initialization status.

        Should be called once at application startup.
        """
        logger.info("Initializing MCPs...")

        # Load configuration
        self.registry.load()

        # Create adapters for enabled MCPs
        for mcp_config in self.registry.get_enabled_mcps():
            try:
                adapter = MCPAdapterFactory.create(mcp_config)
                self.adapters[mcp_config.id] = adapter
                logger.info(f"✓ Initialized adapter: {mcp_config.id}")
            except Exception as e:
                logger.error(f"✗ Failed to initialize {mcp_config.id}: {e}")

        # Report status
        counts = self.registry.count_mcps()
        logger.info(
            f"MCP initialization complete",
            total=counts["total"],
            enabled=counts["enabled"],
            adapters_ready=len(self.adapters)
        )

    async def search_all(self, query: str) -> Dict[str, List]:
        """
        Search across all enabled MCPs in parallel.

        Executes search queries on all initialized adapters concurrently,
        aggregates results, and handles failures gracefully.

        Args:
            query: Search query string

        Returns:
            Dictionary mapping MCP ID to list of results

        Example:
            results = await manager.search_all("feature authentication")
            # Results: {
            #   "confluence": [{"title": "...", "url": "...", ...}],
            #   "jira": [{"key": "PROJ-123", ...}],
            #   ...
            # }
        """
        if not self.adapters:
            logger.warning("No adapters initialized. Call initialize() first.")
            return {}

        logger.debug(f"Searching {len(self.adapters)} MCPs for: {query}")

        # Create search tasks
        tasks = [
            self._search_single_mcp(mcp_id, adapter, query)
            for mcp_id, adapter in self.adapters.items()
        ]

        # Execute in parallel
        results = {}
        for mcp_id, mcp_results in await asyncio.gather(*tasks):
            results[mcp_id] = mcp_results

        logger.info(
            f"Search complete",
            query=query,
            mcps_queried=len(results),
            total_results=sum(len(r) for r in results.values())
        )

        return results

    async def _search_single_mcp(
        self,
        mcp_id: str,
        adapter: BaseMCPAdapter,
        query: str
    ) -> tuple:
        """
        Search a single MCP adapter.

        Handles exceptions gracefully and returns empty results on error.

        Args:
            mcp_id: MCP identifier
            adapter: Adapter instance
            query: Search query

        Returns:
            Tuple of (mcp_id, results_list)
        """
        try:
            logger.debug(f"Searching {mcp_id}...")
            results = await adapter.search(query)
            logger.debug(f"Got {len(results)} results from {mcp_id}")
            return (mcp_id, results)
        except Exception as e:
            logger.error(f"Error searching {mcp_id}: {e}", mcp_id=mcp_id)
            return (mcp_id, [])

    def list_mcps(self) -> List[Dict]:
        """
        List all configured MCPs.

        Returns:
            List of MCP summaries with id, name, type, enabled, priority
        """
        return self.registry.list_all_mcps()

    def get_mcp_info(self, mcp_id: str) -> Optional[MCPConfig]:
        """
        Get detailed info for a specific MCP.

        Args:
            mcp_id: MCP identifier

        Returns:
            MCPConfig or None if not found
        """
        return self.registry.get_mcp(mcp_id)

    def get_enabled_mcps(self) -> List[MCPConfig]:
        """
        Get all enabled MCPs.

        Returns:
            List of enabled MCPConfig instances
        """
        return self.registry.get_enabled_mcps()

    def enable_mcp(self, mcp_id: str) -> bool:
        """
        Enable an MCP at runtime.

        Note: This enables in registry but doesn't create adapter.
        Call initialize() again to create adapter.

        Args:
            mcp_id: MCP identifier

        Returns:
            True if successful, False if MCP not found
        """
        return self.registry.enable_mcp(mcp_id)

    def disable_mcp(self, mcp_id: str) -> bool:
        """
        Disable an MCP at runtime.

        Args:
            mcp_id: MCP identifier

        Returns:
            True if successful, False if MCP not found
        """
        success = self.registry.disable_mcp(mcp_id)
        # Remove adapter if it exists
        if success and mcp_id in self.adapters:
            del self.adapters[mcp_id]
        return success

    def get_status(self) -> Dict:
        """
        Get current manager status.

        Returns:
            Dict with configuration and adapter status
        """
        counts = self.registry.count_mcps()
        return {
            "initialized": len(self.adapters) > 0,
            "adapters_ready": len(self.adapters),
            "mcps": {
                "total": counts["total"],
                "enabled": counts["enabled"],
                "disabled": counts["disabled"],
            },
            "adapters": list(self.adapters.keys()),
        }


__all__ = [
    "MCPManager",
    "MCPRegistryManager",
    "MCPAdapterFactory",
    "BaseMCPAdapter",
]
