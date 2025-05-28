"""
Tests for port management
"""

import tempfile
from pathlib import Path

import pytest

from fastdev.core.port_manager import PortManager


class TestPortManager:
    """Test PortManager functionality"""

    @pytest.fixture
    def port_manager(self):
        """Create a PortManager with temporary config file"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            pm = PortManager(config_file=f.name)
            yield pm
            # Cleanup
            Path(f.name).unlink(missing_ok=True)

    def test_find_free_port(self, port_manager):
        """Test finding a free port"""
        port = port_manager.find_free_port()
        assert 8000 <= port <= 9000 or port > 9000

    def test_get_free_port_assigns_port(self, port_manager):
        """Test that get_free_port assigns and remembers ports"""
        server_name = "test-server"
        port1 = port_manager.get_free_port(server_name)

        # Should return the same port for the same server
        port2 = port_manager.get_free_port(server_name)
        assert port1 == port2

    def test_release_port(self, port_manager):
        """Test releasing a port"""
        server_name = "test-server"
        port = port_manager.get_free_port(server_name)

        # Release the port
        port_manager.release_port(server_name)

        # Should get a potentially different port now
        assert port_manager.get_port(server_name) is None

    def test_persistence(self):
        """Test that port assignments persist across instances"""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            config_file = f.name

        try:
            # First instance
            pm1 = PortManager(config_file=config_file)
            port1 = pm1.get_free_port("test-server")

            # Second instance should load the same config
            pm2 = PortManager(config_file=config_file)
            port2 = pm2.get_port("test-server")

            assert port1 == port2
        finally:
            Path(config_file).unlink(missing_ok=True)
