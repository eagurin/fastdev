"""
Port management for FastDEV
"""

import json
import socket
from contextlib import closing
from pathlib import Path
from typing import Dict, Optional


class PortManager:
    """Manages port allocation for FastAPI servers"""

    def __init__(self, config_file: str = ".fastdev/ports.json"):
        self.config_file = Path.home() / config_file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.ports: Dict[str, int] = self._load_config()

    def _load_config(self) -> Dict[str, int]:
        """Load port configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_config(self):
        """Save port configuration to file"""
        with open(self.config_file, "w") as f:
            json.dump(self.ports, f, indent=2)

    def find_free_port(self, start: int = 8000, end: int = 9000) -> int:
        """Find a free port in the given range"""
        used_ports = set(self.ports.values())

        for port in range(start, end):
            if port in used_ports:
                continue

            if self._is_port_available(port):
                return port

        # If no port in range is free, use OS assignment
        return self._get_random_port()

    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.bind(("", port))
                return True
        except OSError:
            return False

    def _get_random_port(self) -> int:
        """Get a random available port from OS"""
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.bind(("", 0))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return sock.getsockname()[1]

    def get_free_port(self, server_name: str) -> int:
        """Get a free port for a server, reusing if possible"""
        # Check if server already has a port assigned
        if server_name in self.ports:
            port = self.ports[server_name]
            if self._is_port_available(port):
                return port

        # Find new free port
        port = self.find_free_port()
        self.ports[server_name] = port
        self._save_config()
        return port

    def release_port(self, server_name: str):
        """Release a port used by a server"""
        if server_name in self.ports:
            del self.ports[server_name]
            self._save_config()

    def get_port(self, server_name: str) -> Optional[int]:
        """Get the port assigned to a server"""
        return self.ports.get(server_name)
