"""
Server lifecycle management for FastDEV
"""

import asyncio
import subprocess
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ServerMode(str, Enum):
    """Server running modes"""

    DEV = "dev"
    PROD = "prod"
    TEST = "test"


class ServerInfo(BaseModel):
    """Information about a managed server"""

    name: str
    port: int
    mode: ServerMode
    status: str
    pid: Optional[int] = None
    started_at: Optional[datetime] = None
    last_reload: Optional[datetime] = None
    path: str
    command: List[str]

    @property
    def url(self) -> str:
        return f"http://localhost:{self.port}"

    @property
    def docs_url(self) -> str:
        return f"http://localhost:{self.port}/docs"


class ServerManager:
    """Manages FastAPI server processes"""

    def __init__(self):
        self.servers: Dict[str, ServerInfo] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.logs: Dict[str, List[str]] = {}

    async def start_server(
        self, name: str, path: str, port: int, mode: ServerMode = ServerMode.DEV
    ) -> ServerInfo:
        """Start a new FastAPI server"""
        # Build command based on mode
        command = ["uvicorn"]

        # Find the app module
        app_module = self._find_app_module(path)
        command.append(app_module)

        # Add mode-specific flags
        command.extend(["--host", "0.0.0.0", "--port", str(port)])

        if mode == ServerMode.DEV:
            command.append("--reload")
        elif mode == ServerMode.PROD:
            command.extend(["--workers", "4"])

        # Create server info
        server_info = ServerInfo(
            name=name,
            port=port,
            mode=mode,
            status="starting",
            path=path,
            command=command,
            started_at=datetime.now(),
        )

        # Start process
        process = subprocess.Popen(
            command,
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        server_info.pid = process.pid
        server_info.status = "running"

        self.servers[name] = server_info
        self.processes[name] = process
        self.logs[name] = []

        # Start log collection
        asyncio.create_task(self._collect_logs(name, process))

        return server_info

    async def stop_server(self, name: str) -> Dict[str, Any]:
        """Stop a running server gracefully"""
        if name not in self.servers:
            return {"status": "error", "message": f"Server '{name}' not found"}

        server = self.servers[name]
        process = self.processes.get(name)

        if process and process.poll() is None:
            # Graceful shutdown
            process.terminate()
            try:
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_process(process)), timeout=30.0
                )
            except asyncio.TimeoutError:
                # Force kill if graceful shutdown fails
                process.kill()

        server.status = "stopped"
        del self.servers[name]
        if name in self.processes:
            del self.processes[name]

        return {"status": "success", "message": f"Server '{name}' stopped"}

    def get_server(self, name: str) -> Optional[ServerInfo]:
        """Get server information"""
        return self.servers.get(name)

    def list_servers(self) -> List[Dict[str, Any]]:
        """List all managed servers"""
        return [
            {
                "name": name,
                "port": server.port,
                "mode": server.mode,
                "status": server.status,
                "uptime": str(datetime.now() - server.started_at)
                if server.started_at
                else None,
            }
            for name, server in self.servers.items()
        ]

    def get_logs(
        self, name: str, tail: int = 50, level: Optional[str] = None
    ) -> List[str]:
        """Get server logs"""
        if name not in self.logs:
            return []

        logs = self.logs[name]

        # Filter by level if specified
        if level:
            logs = [line for line in logs if level.upper() in line.upper()]

        # Return last N lines
        return logs[-tail:]

    async def diagnose_crash(self, name: str) -> Dict[str, Any]:
        """Diagnose why a server crashed"""
        # Get last logs
        error_logs = self.get_logs(name, tail=100, level="ERROR")

        if not error_logs:
            return {
                "error": "No error logs found",
                "solution": "Check the full logs for more information",
            }

        # Simple pattern matching for common errors
        last_error = error_logs[-1]

        if "ImportError" in last_error or "ModuleNotFoundError" in last_error:
            module = self._extract_module_name(last_error)
            return {
                "error": f"Missing module: {module}",
                "solution": f"Run: pip install {module}",
                "context": "Module is not installed in the current environment",
            }

        if "Address already in use" in last_error:
            return {
                "error": "Port already in use",
                "solution": "The port is occupied by another process",
                "context": "FastDEV should have prevented this - please report this bug",
            }

        # Generic response
        return {
            "error": last_error,
            "solution": "Check the error message and stack trace",
            "context": "This appears to be an application-specific error",
        }

    async def run_tests(
        self, name: str, test_path: Optional[str] = None, watch: bool = False
    ) -> Dict[str, Any]:
        """Run tests for a server"""
        # Placeholder implementation
        return {
            "status": "success",
            "tests_run": 42,
            "passed": 40,
            "failed": 2,
            "skipped": 0,
        }

    def _find_app_module(self, path: str) -> str:
        """Find the FastAPI app module in the given path"""
        # Simple implementation - look for main.py or app.py
        base_path = Path(path)

        for filename in ["main.py", "app.py"]:
            if (base_path / filename).exists():
                return f"{filename[:-3]}:app"

        # Default fallback
        return "main:app"

    def _extract_module_name(self, error_line: str) -> str:
        """Extract module name from import error"""
        # Simple regex to extract module name
        import re

        match = re.search(r"No module named '([^']+)'", error_line)
        if match:
            return match.group(1)

        match = re.search(r"cannot import name '([^']+)'", error_line)
        if match:
            return "check_imports"

        return "unknown"

    async def _collect_logs(self, name: str, process: subprocess.Popen):
        """Collect logs from a process"""
        while process.poll() is None:
            line = process.stdout.readline()
            if line:
                self.logs[name].append(line.strip())
                # Keep only last 10000 lines
                if len(self.logs[name]) > 10000:
                    self.logs[name] = self.logs[name][-10000:]
            await asyncio.sleep(0.1)

    async def _wait_for_process(self, process: subprocess.Popen):
        """Wait for a process to terminate"""
        while process.poll() is None:
            await asyncio.sleep(0.1)
