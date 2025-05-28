"""
FastDEV MCP Server - Core implementation
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel

from .analysis.code_analyzer import CodeAnalyzer
from .core.port_manager import PortManager
from .core.process_monitor import ProcessMonitor
from .core.server_manager import ServerManager


class ServerInfo(BaseModel):
    """Information about a managed FastAPI server"""

    name: str
    port: int
    mode: str
    status: str
    pid: Optional[int] = None
    started_at: Optional[datetime] = None
    last_reload: Optional[datetime] = None
    url: str
    docs_url: str


class FastDEVServer:
    """Main FastDEV MCP Server"""

    def __init__(self, config_path: Optional[Path] = None):
        self.mcp = FastMCP("fastdev")
        self.server_manager = ServerManager()
        self.port_manager = PortManager()
        self.process_monitor = ProcessMonitor()
        self.code_analyzer = CodeAnalyzer()

        self._setup_tools()
        self._setup_resources()

    def _setup_tools(self):
        """Setup MCP tools"""

        @self.mcp.tool()
        async def ensure_running(
            name: str, path: str = ".", mode: str = "dev"
        ) -> Dict[str, Any]:
            """
            Ensure a FastAPI server is running. If already running, returns current info.
            If not, starts it intelligently.

            Args:
                name: Unique name for the server
                path: Path to the FastAPI app
                mode: Running mode (dev, prod, test)

            Returns:
                Server information including port and status
            """
            # Check if already running
            existing = self.server_manager.get_server(name)
            if existing and existing.status == "running":
                return {
                    "status": "already_running",
                    "server": existing.dict(),
                    "message": f"Server '{name}' already running on port {existing.port} with hot-reload",
                }

            # Start new server
            port = self.port_manager.get_free_port(name)
            server_info = await self.server_manager.start_server(
                name=name, path=path, port=port, mode=mode
            )

            return {
                "status": "started",
                "server": server_info.dict(),
                "message": f"Server '{name}' started on port {port}",
            }

        @self.mcp.tool()
        async def stop_server(name: str) -> Dict[str, Any]:
            """
            Gracefully stop a running server

            Args:
                name: Name of the server to stop

            Returns:
                Status of the operation
            """
            result = await self.server_manager.stop_server(name)
            return result

        @self.mcp.tool()
        async def get_logs(
            name: str, tail: int = 50, level: Optional[str] = None
        ) -> List[str]:
            """
            Get server logs

            Args:
                name: Server name
                tail: Number of recent lines to return
                level: Filter by log level (ERROR, WARNING, INFO, DEBUG)

            Returns:
                List of log lines
            """
            return self.server_manager.get_logs(name, tail, level)

        @self.mcp.tool()
        async def diagnose_crash(name: str) -> Dict[str, Any]:
            """
            Diagnose why a server crashed with actionable insights

            Args:
                name: Server name

            Returns:
                Crash analysis with error, solution, and context
            """
            return await self.server_manager.diagnose_crash(name)

        @self.mcp.tool()
        async def analyze_code(path: str = ".", fix: bool = False) -> Dict[str, Any]:
            """
            Run comprehensive code analysis using multiple tools

            Args:
                path: Path to analyze
                fix: Whether to auto-fix issues

            Returns:
                Analysis results with issues, suggestions, and metrics
            """
            return await self.code_analyzer.analyze(path, fix)

        @self.mcp.tool()
        async def run_tests(
            name: str, test_path: Optional[str] = None, watch: bool = False
        ) -> Dict[str, Any]:
            """
            Run tests for a server in isolation

            Args:
                name: Server name
                test_path: Specific test file/directory
                watch: Enable watch mode

            Returns:
                Test results
            """
            return await self.server_manager.run_tests(name, test_path, watch)

        @self.mcp.tool()
        async def health_check(name: str) -> Dict[str, Any]:
            """
            Comprehensive health check for a server

            Args:
                name: Server name

            Returns:
                Health status with metrics and recommendations
            """
            return await self.process_monitor.health_check(name)

    def _setup_resources(self):
        """Setup MCP resources"""

        @self.mcp.resource("servers/list")
        async def list_servers() -> str:
            """List all managed servers with their status"""
            servers = self.server_manager.list_servers()
            return json.dumps(servers, indent=2)

        @self.mcp.resource("servers/{name}/info")
        async def server_info(name: str) -> str:
            """Get detailed information about a specific server"""
            info = self.server_manager.get_server(name)
            if info:
                return json.dumps(info.dict(), indent=2, default=str)
            return json.dumps({"error": f"Server '{name}' not found"})

        @self.mcp.resource("metrics/summary")
        async def metrics_summary() -> str:
            """Get overall metrics for all servers"""
            metrics = await self.process_monitor.get_all_metrics()
            return json.dumps(metrics, indent=2)

    def run(self):
        """Run the MCP server"""
        self.mcp.run()


def main():
    """Entry point for FastDEV server"""
    server = FastDEVServer()
    server.run()


if __name__ == "__main__":
    main()
