"""
Tests for MCP Integration Module

Tests for schema validation, registry loading, adapter factory, and MCPManager.
"""

import pytest
from pathlib import Path
import json
import tempfile

from src.mcp_integration.schema import MCPConfig, MCPRegistry, MCPType
from src.mcp_integration.registry import MCPRegistryManager
from src.mcp_integration.factory import MCPAdapterFactory
from src.mcp_integration.base_adapter import BaseMCPAdapter
from src.mcp_integration import MCPManager


# ========== Schema Tests ==========

class TestMCPSchema:
    """Test MCP configuration schema validation"""

    def test_create_valid_mcp_config(self):
        """Test creating valid MCPConfig"""
        config = MCPConfig(
            id="test-mcp",
            name="Test MCP",
            type=MCPType.CONFLUENCE,
            enabled=True,
            config={"api_url": "https://example.com"},
            search={"query_type": "cql"},
            mapping={"title": "title"},
        )

        assert config.id == "test-mcp"
        assert config.name == "Test MCP"
        assert config.type == MCPType.CONFLUENCE
        assert config.enabled is True

    def test_mcp_config_id_lowercase(self):
        """Test that MCP ID is converted to lowercase"""
        config = MCPConfig(
            id="TEST-MCP",
            name="Test",
            type=MCPType.CONFLUENCE,
        )
        assert config.id == "test-mcp"

    def test_mcp_config_invalid_id(self):
        """Test that invalid IDs are rejected"""
        with pytest.raises(ValueError):
            MCPConfig(
                id="test@mcp!",  # Invalid characters
                name="Test",
                type=MCPType.CONFLUENCE,
            )

    def test_mcp_config_relevance_weight_bounds(self):
        """Test relevance weight validation"""
        # Valid
        config = MCPConfig(
            id="test",
            name="Test",
            type=MCPType.JIRA,
            relevance_weight=0.5,
        )
        assert config.relevance_weight == 0.5

        # Invalid - too high
        with pytest.raises(ValueError):
            MCPConfig(
                id="test",
                name="Test",
                type=MCPType.JIRA,
                relevance_weight=1.5,
            )

        # Invalid - negative
        with pytest.raises(ValueError):
            MCPConfig(
                id="test",
                name="Test",
                type=MCPType.JIRA,
                relevance_weight=-0.1,
            )

    def test_create_mcp_registry(self):
        """Test creating MCPRegistry"""
        config1 = MCPConfig(
            id="confluence",
            name="Confluence",
            type=MCPType.CONFLUENCE,
        )
        config2 = MCPConfig(
            id="jira",
            name="Jira",
            type=MCPType.JIRA,
        )

        registry = MCPRegistry(mcp_servers=[config1, config2])
        assert len(registry.mcp_servers) == 2
        assert registry.mcp_servers[0].id == "confluence"


# ========== Registry Tests ==========

class TestMCPRegistry:
    """Test MCPRegistryManager functionality"""

    @pytest.fixture
    def temp_mcp_config(self):
        """Create temporary mcp.json for testing"""
        config = {
            "version": "1.0",
            "mcp_servers": [
                {
                    "id": "confluence",
                    "name": "Confluence",
                    "type": "confluence",
                    "enabled": True,
                    "priority": 1,
                    "config": {"api_url": "https://test.com", "api_key": "test"},
                    "search": {"query_type": "cql"},
                    "mapping": {"title": "title"},
                },
                {
                    "id": "jira",
                    "name": "Jira",
                    "type": "jira",
                    "enabled": False,
                    "priority": 2,
                    "config": {"api_url": "https://test.com", "api_key": "test"},
                    "search": {"query_type": "jql"},
                    "mapping": {"title": "title"},
                },
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        ) as f:
            json.dump(config, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink()

    def test_load_mcp_config(self, temp_mcp_config):
        """Test loading MCP configuration from file"""
        manager = MCPRegistryManager(temp_mcp_config)
        manager.load()

        assert len(manager.mcps) == 2
        assert "confluence" in manager.mcps
        assert "jira" in manager.mcps

    def test_get_enabled_mcps(self, temp_mcp_config):
        """Test getting only enabled MCPs"""
        manager = MCPRegistryManager(temp_mcp_config)
        manager.load()

        enabled = manager.get_enabled_mcps()
        assert len(enabled) == 1
        assert enabled[0].id == "confluence"

    def test_get_disabled_mcps(self, temp_mcp_config):
        """Test getting disabled MCPs"""
        manager = MCPRegistryManager(temp_mcp_config)
        manager.load()

        disabled = manager.get_disabled_mcps()
        assert len(disabled) == 1
        assert disabled[0].id == "jira"

    def test_get_mcp_by_type(self, temp_mcp_config):
        """Test filtering MCPs by type"""
        manager = MCPRegistryManager(temp_mcp_config)
        manager.load()

        confluence_mcps = manager.get_mcp_by_type(MCPType.CONFLUENCE)
        assert len(confluence_mcps) == 1
        assert confluence_mcps[0].id == "confluence"

    def test_enable_disable_mcp(self, temp_mcp_config):
        """Test enabling and disabling MCPs at runtime"""
        manager = MCPRegistryManager(temp_mcp_config)
        manager.load()

        # Initially disabled
        assert not manager.get_mcp("jira").enabled

        # Enable it
        success = manager.enable_mcp("jira")
        assert success is True
        assert manager.get_mcp("jira").enabled

        # Disable it
        success = manager.disable_mcp("jira")
        assert success is True
        assert not manager.get_mcp("jira").enabled

    def test_enable_nonexistent_mcp(self, temp_mcp_config):
        """Test enabling nonexistent MCP"""
        manager = MCPRegistryManager(temp_mcp_config)
        manager.load()

        success = manager.enable_mcp("nonexistent")
        assert success is False

    def test_list_all_mcps(self, temp_mcp_config):
        """Test listing all MCPs"""
        manager = MCPRegistryManager(temp_mcp_config)
        manager.load()

        mcps = manager.list_all_mcps()
        assert len(mcps) == 2
        assert all("id" in m and "name" in m for m in mcps)

    def test_count_mcps(self, temp_mcp_config):
        """Test counting MCPs by status"""
        manager = MCPRegistryManager(temp_mcp_config)
        manager.load()

        counts = manager.count_mcps()
        assert counts["total"] == 2
        assert counts["enabled"] == 1
        assert counts["disabled"] == 1

    def test_missing_config_file(self):
        """Test error when config file doesn't exist"""
        manager = MCPRegistryManager("/nonexistent/path/mcp.json")

        with pytest.raises(FileNotFoundError):
            manager.load()

    def test_invalid_config_raises_error(self):
        """Test error on invalid configuration"""
        invalid_config = {
            "version": "1.0",
            "mcp_servers": [
                {
                    "id": "test",
                    # Missing required fields
                }
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        ) as f:
            json.dump(invalid_config, f)
            temp_path = f.name

        try:
            manager = MCPRegistryManager(temp_path)
            with pytest.raises(ValueError):
                manager.load()
        finally:
            Path(temp_path).unlink()


# ========== Adapter Factory Tests ==========

class MockAdapter(BaseMCPAdapter):
    """Mock adapter for testing"""

    async def search(self, query: str, **kwargs):
        return [{"title": "Test Result"}]

    async def get_resource(self, resource_id: str):
        return {"id": resource_id, "title": "Test Resource"}


class TestMCPAdapterFactory:
    """Test MCPAdapterFactory functionality"""

    def teardown_method(self):
        """Clear adapters after each test"""
        MCPAdapterFactory.clear()

    def test_register_adapter(self):
        """Test registering a custom adapter"""
        config = MCPConfig(
            id="mock",
            name="Mock",
            type=MCPType.CONFLUENCE,
        )

        MCPAdapterFactory.register(MCPType.CONFLUENCE, MockAdapter)

        adapter = MCPAdapterFactory.create(config)
        assert isinstance(adapter, MockAdapter)

    def test_unregister_adapter(self):
        """Test unregistering an adapter"""
        MCPAdapterFactory.register(MCPType.CONFLUENCE, MockAdapter)
        assert MCPAdapterFactory.is_registered(MCPType.CONFLUENCE)

        MCPAdapterFactory.unregister(MCPType.CONFLUENCE)
        assert not MCPAdapterFactory.is_registered(MCPType.CONFLUENCE)

    def test_create_unregistered_adapter_raises_error(self):
        """Test error when creating adapter for unregistered type"""
        config = MCPConfig(
            id="test",
            name="Test",
            type=MCPType.CONFLUENCE,
        )

        with pytest.raises(ValueError):
            MCPAdapterFactory.create(config)

    def test_register_invalid_adapter_raises_error(self):
        """Test error when registering invalid adapter"""

        class InvalidAdapter:
            """Not an adapter"""
            pass

        with pytest.raises(TypeError):
            MCPAdapterFactory.register(MCPType.CONFLUENCE, InvalidAdapter)

    def test_get_registered_types(self):
        """Test getting list of registered types"""
        MCPAdapterFactory.register(MCPType.CONFLUENCE, MockAdapter)
        MCPAdapterFactory.register(MCPType.JIRA, MockAdapter)

        types = MCPAdapterFactory.get_registered_types()
        assert MCPType.CONFLUENCE in types
        assert MCPType.JIRA in types


# ========== MCPManager Tests ==========

class TestMCPManager:
    """Test MCPManager functionality"""

    @pytest.fixture
    def temp_mcp_config_simple(self):
        """Create simple mcp.json for testing"""
        config = {
            "version": "1.0",
            "mcp_servers": [
                {
                    "id": "mock1",
                    "name": "Mock 1",
                    "type": "confluence",
                    "enabled": True,
                    "priority": 1,
                    "config": {"api_url": "https://test.com"},
                    "search": {"query_type": "cql"},
                    "mapping": {"title": "title"},
                },
                {
                    "id": "mock2",
                    "name": "Mock 2",
                    "type": "jira",
                    "enabled": True,
                    "priority": 2,
                    "config": {"api_url": "https://test.com"},
                    "search": {"query_type": "jql"},
                    "mapping": {"title": "title"},
                },
            ]
        }

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        ) as f:
            json.dump(config, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink()
        MCPAdapterFactory.clear()

    @pytest.mark.asyncio
    async def test_mcp_manager_initialization(self, temp_mcp_config_simple):
        """Test MCPManager initialization"""
        # Register mock adapters
        MCPAdapterFactory.register(MCPType.CONFLUENCE, MockAdapter)
        MCPAdapterFactory.register(MCPType.JIRA, MockAdapter)

        manager = MCPManager(temp_mcp_config_simple)
        await manager.initialize()

        assert len(manager.adapters) == 2
        assert "mock1" in manager.adapters
        assert "mock2" in manager.adapters

    def test_list_mcps(self, temp_mcp_config_simple):
        """Test listing MCPs"""
        manager = MCPManager(temp_mcp_config_simple)
        mcps = manager.list_mcps()

        assert len(mcps) == 2
        assert mcps[0]["id"] == "mock1"

    def test_get_mcp_info(self, temp_mcp_config_simple):
        """Test getting MCP info"""
        manager = MCPManager(temp_mcp_config_simple)

        info = manager.get_mcp_info("mock1")
        assert info is not None
        assert info.id == "mock1"
        assert info.name == "Mock 1"

    def test_get_status(self, temp_mcp_config_simple):
        """Test getting manager status"""
        manager = MCPManager(temp_mcp_config_simple)
        status = manager.get_status()

        assert "initialized" in status
        assert "mcps" in status
        assert status["mcps"]["total"] == 2
