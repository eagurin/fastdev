"""
FastDEV - Intelligent MCP server for FastAPI
Because life is too short for "Address already in use"
"""

__version__ = "0.1.0"
__author__ = "FastDEV Contributors"
__email__ = "fastdev@example.com"

from .server import FastDEVServer

__all__ = ["FastDEVServer", "__version__"]
