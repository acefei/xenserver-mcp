"""Configuration management for XenServer MCP"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("XenServerMCPServer.config")

# Get the project root directory (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_CONFIG_PATH = str(PROJECT_ROOT / "config" / "clusters.json")


def load_cluster_config() -> dict[str, dict[str, str]]:
    """Load XenServer cluster configurations from JSON file
    
    Configuration file path is determined by:
    1. XENSERVER_CONFIG environment variable (if set)
    2. Default path: config/clusters.json in project root
    """
    try:
        # Check for environment variable first
        config_path = os.getenv("XENSERVER_CONFIG", DEFAULT_CONFIG_PATH)
        config_file = Path(config_path)
        
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_path}")
            return {}

        with config_file.open() as f:
            config = json.load(f)
            logger.info(f"Loaded {len(config)} cluster configurations from {config_path}")
            return config
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return {}
