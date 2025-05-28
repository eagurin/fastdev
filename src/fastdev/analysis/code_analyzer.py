"""
Code analysis for FastDEV
"""

import asyncio
import subprocess
from typing import Any, Dict


class CodeAnalyzer:
    """Analyzes FastAPI code using multiple tools"""

    def __init__(self):
        self.tools = {
            "black": self._run_black,
            "isort": self._run_isort,
            "mypy": self._run_mypy,
            "ruff": self._run_ruff,
            "bandit": self._run_bandit,
            "flake8": self._run_flake8,
            "pylint": self._run_pylint,
        }

    async def analyze(self, path: str = ".", fix: bool = False) -> Dict[str, Any]:
        """Run comprehensive code analysis"""
        results = {
            "path": path,
            "timestamp": asyncio.get_event_loop().time(),
            "issues": {"critical": [], "warnings": [], "style": [], "info": []},
            "metrics": {},
            "auto_fixable": 0,
            "score": 10.0,
        }

        # Run all tools
        tool_results = {}
        for tool_name, tool_func in self.tools.items():
            try:
                tool_results[tool_name] = await tool_func(path, fix)
            except Exception as e:
                tool_results[tool_name] = {"error": str(e)}

        # Aggregate results
        for tool, result in tool_results.items():
            if "error" in result:
                results["issues"]["warnings"].append(f"{tool}: {result['error']}")
                continue

            # Collect issues based on severity
            if "issues" in result:
                for issue in result["issues"]:
                    severity = issue.get("severity", "info")
                    if severity == "critical":
                        results["issues"]["critical"].append(issue)
                        results["score"] -= 2.0
                    elif severity == "warning":
                        results["issues"]["warnings"].append(issue)
                        results["score"] -= 0.5
                    elif severity == "style":
                        results["issues"]["style"].append(issue)
                        results["score"] -= 0.1
                    else:
                        results["issues"]["info"].append(issue)

            # Count auto-fixable issues
            if "auto_fixable" in result:
                results["auto_fixable"] += result["auto_fixable"]

        # Ensure score doesn't go below 0
        results["score"] = max(0, results["score"])

        # Add summary
        results["summary"] = {
            "total_issues": sum(
                len(results["issues"][level]) for level in results["issues"]
            ),
            "tools_run": len([r for r in tool_results.values() if "error" not in r]),
            "tools_failed": len([r for r in tool_results.values() if "error" in r]),
        }

        return results

    async def _run_black(self, path: str, fix: bool) -> Dict[str, Any]:
        """Run Black formatter"""
        cmd = ["black", "--check"]
        if fix:
            cmd.remove("--check")
        cmd.append(path)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {"status": "clean", "issues": []}
            else:
                # Parse black output
                return {
                    "status": "needs_formatting",
                    "issues": [
                        {
                            "severity": "style",
                            "message": "Code needs formatting",
                            "tool": "black",
                        }
                    ],
                    "auto_fixable": 1 if not fix else 0,
                }
        except FileNotFoundError:
            return {"error": "Black not installed"}

    async def _run_isort(self, path: str, fix: bool) -> Dict[str, Any]:
        """Run isort for import sorting"""
        cmd = ["isort", "--check-only"]
        if fix:
            cmd.remove("--check-only")
        cmd.append(path)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {"status": "clean", "issues": []}
            else:
                return {
                    "status": "needs_sorting",
                    "issues": [
                        {
                            "severity": "style",
                            "message": "Imports need sorting",
                            "tool": "isort",
                        }
                    ],
                    "auto_fixable": 1 if not fix else 0,
                }
        except FileNotFoundError:
            return {"error": "isort not installed"}

    async def _run_mypy(self, path: str, fix: bool) -> Dict[str, Any]:
        """Run mypy type checker"""
        # Mypy doesn't have auto-fix
        cmd = ["mypy", path]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {"status": "clean", "issues": []}
            else:
                # Simple parsing of mypy output
                issues = []
                for line in result.stdout.splitlines():
                    if ": error:" in line:
                        issues.append(
                            {"severity": "warning", "message": line, "tool": "mypy"}
                        )

                return {"status": "type_errors", "issues": issues, "auto_fixable": 0}
        except FileNotFoundError:
            return {"error": "mypy not installed"}

    async def _run_ruff(self, path: str, fix: bool) -> Dict[str, Any]:
        """Run Ruff linter"""
        cmd = ["ruff", "check"]
        if fix:
            cmd.append("--fix")
        cmd.append(path)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {"status": "clean", "issues": []}
            else:
                # Count issues (simplified)
                issue_count = len(result.stdout.splitlines())
                return {
                    "status": "has_issues",
                    "issues": [
                        {
                            "severity": "warning",
                            "message": f"Found {issue_count} linting issues",
                            "tool": "ruff",
                        }
                    ],
                    "auto_fixable": issue_count if not fix else 0,
                }
        except FileNotFoundError:
            return {"error": "Ruff not installed"}

    async def _run_bandit(self, path: str, fix: bool) -> Dict[str, Any]:
        """Run Bandit security checker"""
        # Bandit doesn't have auto-fix
        cmd = ["bandit", "-r", path, "-f", "json"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {"status": "clean", "issues": []}
            else:
                # Simplified - would parse JSON in real implementation
                return {
                    "status": "security_issues",
                    "issues": [
                        {
                            "severity": "critical",
                            "message": "Security vulnerabilities detected",
                            "tool": "bandit",
                        }
                    ],
                    "auto_fixable": 0,
                }
        except FileNotFoundError:
            return {"error": "Bandit not installed"}

    async def _run_flake8(self, path: str, fix: bool) -> Dict[str, Any]:
        """Run Flake8 style checker"""
        # Flake8 doesn't have auto-fix
        cmd = ["flake8", path]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {"status": "clean", "issues": []}
            else:
                issue_count = len(result.stdout.splitlines())
                return {
                    "status": "style_issues",
                    "issues": [
                        {
                            "severity": "style",
                            "message": f"Found {issue_count} style issues",
                            "tool": "flake8",
                        }
                    ],
                    "auto_fixable": 0,
                }
        except FileNotFoundError:
            return {"error": "Flake8 not installed"}

    async def _run_pylint(self, path: str, fix: bool) -> Dict[str, Any]:
        """Run Pylint code quality checker"""
        # Pylint doesn't have auto-fix
        cmd = ["pylint", path, "--output-format=json"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Pylint returns non-zero even for warnings
            if not result.stdout:
                return {"status": "clean", "issues": []}
            else:
                # Simplified - would parse JSON in real implementation
                return {
                    "status": "quality_issues",
                    "issues": [
                        {
                            "severity": "warning",
                            "message": "Code quality issues detected",
                            "tool": "pylint",
                        }
                    ],
                    "auto_fixable": 0,
                }
        except FileNotFoundError:
            return {"error": "Pylint not installed"}
