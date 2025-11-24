"""XenServer MCP - Model Context Protocol implementation for XenServer/XCP-ng"""

__version__ = "0.1.0"

from .config import load_cluster_config
from .server import main

__all__ = [
    "main",
    "load_cluster_config",
]
