"""
MCP Registry and Configuration Loader

Loads MCP configurations from mcp.json at runtime and manages the registry.
Supports environment variable expansion and validation.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .schema import MCPRegistry, MCPConfig, MCPType

logger = logging.getLogger(__name__)


class MCPRegistryManager:
    """
    Manages the registry of configured MCPs.

    Loads configurations from mcp.json, validates them, and provides
    access to MCPs by ID, type, or status.

    Attributes:
        config_path: Path to mcp.json file
        mcps: Dictionary of loaded MCPs indexed by ID
    """

    def __init__(self, config_path: str = "mcp.json"):
        """
        Initialize registry manager.

        Args:
            config_path: Path to mcp.json configuration file
        """
        self.config_path = Path(config_path)
        self.mcps: Dict[str, MCPConfig] = {}
        self._loaded = False
        logger.debug(f"Initialized MCPRegistryManager with config: {config_path}")

    def load(self) -> None:
        """
        Load MCPs from mcp.json configuration file.

        Performs:
        1. Read and parse JSON
        2. Expand environment variables
        3. Validate against schema
        4. Index MCPs by ID

        Raises:
            FileNotFoundError: If mcp.json doesn't exist
            ValueError: If configuration is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"MCP configuration not found at: {self.config_path}\n"
                "Please create mcp.json from mcp.json.example"
            )

        logger.info(f"Loading MCP configuration from {self.config_path}")

        # Read JSON file
        with open(self.config_path, 'r') as f:
            config_data = json.load(f)

        # Expand environment variables (${VAR_NAME} → value)
        config_str = json.dumps(config_data)
        import os
        for key, value in os.environ.items():
            config_str = config_str.replace(f"${{{key}}}", str(value))
        config_data = json.loads(config_str)

        # Validate against schema
        try:
            registry = MCPRegistry(**config_data)
        except Exception as e:
            raise ValueError(f"Invalid MCP configuration: {e}")

        # Index MCPs by ID
        for mcp_config in registry.mcp_servers:
            self.mcps[mcp_config.id] = mcp_config
            status = "enabled" if mcp_config.enabled else "disabled"
            logger.info(
                f"Registered MCP",
                mcp_id=mcp_config.id,
                mcp_type=mcp_config.type,
                status=status,
                priority=mcp_config.priority
            )

        self._loaded = True
        logger.info(
            f"Loaded {len(self.mcps)} MCP configurations"
            f" ({len(self.get_enabled_mcps())} enabled)"
        )

    def _ensure_loaded(self) -> None:
        """Ensure MCPs are loaded before accessing them."""
        if not self._loaded:
            self.load()

    def get_mcp(self, mcp_id: str) -> Optional[MCPConfig]:
        """
        Get MCP configuration by ID.

        Args:
            mcp_id: MCP identifier

        Returns:
            MCPConfig or None if not found
        """
        self._ensure_loaded()
        return self.mcps.get(mcp_id)

    def get_enabled_mcps(self) -> List[MCPConfig]:
        """
        Get all enabled MCPs sorted by priority.

        Returns:
            List of enabled MCPs (sorted by priority, lower first)
        """
        self._ensure_loaded()
        return sorted(
            [mcp for mcp in self.mcps.values() if mcp.enabled],
            key=lambda x: x.priority
        )

    def get_mcp_by_type(self, mcp_type: MCPType) -> List[MCPConfig]:
        """
        Get all MCPs of a specific type.

        Args:
            mcp_type: MCPType to filter by

        Returns:
            List of MCPs matching the type
        """
        self._ensure_loaded()
        return [
            mcp for mcp in self.mcps.values()
            if mcp.type == mcp_type
        ]

    def get_disabled_mcps(self) -> List[MCPConfig]:
        """
        Get all disabled MCPs.

        Returns:
            List of disabled MCPs
        """
        self._ensure_loaded()
        return [mcp for mcp in self.mcps.values() if not mcp.enabled]

    def enable_mcp(self, mcp_id: str) -> bool:
        """
        Enable an MCP at runtime.

        Args:
            mcp_id: MCP identifier

        Returns:
            True if successful, False if MCP not found
        """
        self._ensure_loaded()
        if mcp := self.get_mcp(mcp_id):
            mcp.enabled = True
            logger.info(f"Enabled MCP: {mcp_id}")
            return True
        logger.warning(f"MCP not found: {mcp_id}")
        return False

    def disable_mcp(self, mcp_id: str) -> bool:
        """
        Disable an MCP at runtime.

        Args:
            mcp_id: MCP identifier

        Returns:
            True if successful, False if MCP not found
        """
        self._ensure_loaded()
        if mcp := self.get_mcp(mcp_id):
            mcp.enabled = False
            logger.info(f"Disabled MCP: {mcp_id}")
            return True
        logger.warning(f"MCP not found: {mcp_id}")
        return False

    def list_all_mcps(self) -> List[Dict]:
        """
        Get summary of all configured MCPs.

        Returns:
            List of dicts with id, name, type, enabled, priority
        """
        self._ensure_loaded()
        return [
            {
                "id": mcp.id,
                "name": mcp.name,
                "type": mcp.type,
                "enabled": mcp.enabled,
                "priority": mcp.priority,
                "description": mcp.description,
            }
            for mcp in sorted(self.mcps.values(), key=lambda x: x.priority)
        ]

    def count_mcps(self) -> Dict[str, int]:
        """
        Get count of MCPs by status.

        Returns:
            Dict with total, enabled, disabled counts
        """
        self._ensure_loaded()
        total = len(self.mcps)
        enabled = len(self.get_enabled_mcps())
        disabled = len(self.get_disabled_mcps())
        return {
            "total": total,
            "enabled": enabled,
            "disabled": disabled,
        }
