"""
Process monitoring for FastDEV
"""

from datetime import datetime
from typing import Any, Dict, Optional

import psutil


class ProcessMonitor:
    """Monitors FastAPI server processes"""

    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}

    async def health_check(self, name: str) -> Dict[str, Any]:
        """Perform comprehensive health check on a server"""
        # Get server info from somewhere (would be injected)
        # For now, return mock data

        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory": {
                        "total": memory.total,
                        "available": memory.available,
                        "percent": memory.percent,
                    },
                    "disk": {
                        "total": disk.total,
                        "free": disk.free,
                        "percent": disk.percent,
                    },
                },
                "checks": {
                    "server_running": True,
                    "port_accessible": True,
                    "memory_ok": memory.percent < 90,
                    "cpu_ok": cpu_percent < 80,
                    "disk_ok": disk.percent < 90,
                },
                "recommendations": [],
            }

            # Add recommendations based on checks
            if memory.percent > 80:
                health_status["status"] = "warning"
                health_status["recommendations"].append(
                    "Memory usage is high. Consider increasing available memory."
                )

            if cpu_percent > 70:
                health_status["status"] = "warning"
                health_status["recommendations"].append(
                    "CPU usage is high. Consider optimizing endpoints or scaling."
                )

            if disk.percent > 80:
                health_status["status"] = "warning"
                health_status["recommendations"].append(
                    "Disk space is running low. Clean up logs or increase storage."
                )

            return health_status

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to perform health check",
            }

    async def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics for all servers"""
        # Placeholder implementation
        return {
            "timestamp": datetime.now().isoformat(),
            "servers": {"total": 2, "running": 2, "stopped": 0, "errored": 0},
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
            },
            "total_requests": 12543,
            "total_errors": 23,
            "avg_response_time_ms": 45.7,
        }

    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a process"""
        try:
            process = psutil.Process(pid)
            return {
                "pid": pid,
                "name": process.name(),
                "status": process.status(),
                "cpu_percent": process.cpu_percent(interval=1),
                "memory_info": process.memory_info()._asdict(),
                "create_time": datetime.fromtimestamp(
                    process.create_time()
                ).isoformat(),
                "num_threads": process.num_threads(),
            }
        except psutil.NoSuchProcess:
            return None
