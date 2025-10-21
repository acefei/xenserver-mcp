#!/usr/bin/env python3
"""
XenServer MCP Server - A Model Context Protocol server for XenServer/XCP-ng hypervisors.
Provides tools for querying XenServer objects via XenAPI.
"""

import contextlib
import logging
import os
from datetime import date
from typing import Any, Dict, Optional, Iterable

import XenAPI
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_environment() -> None:
    """Load environment variables from .env file in multiple possible locations."""
    env_paths = ['/app/.env', '.env', '../.env']
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            logger.info(f"Loaded environment from {env_path}")
            return
    logger.warning("No .env file found in any of the expected locations")


def get_xenserver_config() -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Get XenServer configuration from environment variables.
    
    Returns:
        Tuple of (host, user, password) - may contain None values if not configured
    """
    host = os.getenv('XENSERVER_HOST')
    user = os.getenv('XENSERVER_USER')
    password = os.getenv('XENSERVER_PASS')
    
    if not all([host, user, password]):
        logger.error("Missing required environment variables: XENSERVER_HOST, XENSERVER_USER, or XENSERVER_PASS")
    
    return host, user, password


# Initialize environment
load_environment()

# Get configuration
XENSERVER_HOST, XENSERVER_USER, XENSERVER_PASS = get_xenserver_config()
XENSERVER_URL = f"http://{XENSERVER_HOST}" if XENSERVER_HOST else None

# Create the XenServer MCP server with stateless HTTP
xenserver_mcp = FastMCP(name="XenServerMCP", stateless_http=True)


class XenServerClient:
    """XenServer API client for managing connections and operations."""
    
    def __init__(self, url: str, username: str, password: str) -> None:
        """
        Initialize XenServer client.
        
        Args:
            url: XenServer host URL
            username: XenServer username
            password: XenServer password
        """
        self.url = url
        self.username = username
        self.password = password
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @contextlib.contextmanager
    def session(self):
        """
        Context manager for XenAPI session management.
        
        Yields:
            XenAPI.Session: Active XenServer session
            
        Raises:
            XenAPI.Failure: If login fails
            Exception: For other connection errors
        """
        session = None
        try:
            self._logger.info(f"Connecting to XenServer at {self.url} with user {self.username}")
            session = XenAPI.Session(self.url)
            session.xenapi.login_with_password(self.username, self.password)
            self._logger.info("Successfully logged in to XenServer")
            yield session
        except XenAPI.Failure as xen_error:
            self._logger.error(f"XenAPI failure: {xen_error.details}")
            raise
        except Exception as e:
            self._logger.error(f"Failed to connect to XenServer: {e}")
            raise
        finally:
            if session:
                try:
                    session.xenapi.session.logout()
                    self._logger.debug("Successfully logged out from XenServer")
                except Exception as logout_error:
                    self._logger.warning(f"Error during logout: {logout_error}")


def _initialize_xenserver_client() -> Optional[XenServerClient]:
    """
    Initialize XenServer client if configuration is available.
    
    Returns:
        XenServerClient instance or None if configuration is missing
    """
    if all([XENSERVER_URL, XENSERVER_USER, XENSERVER_PASS]):
        logger.info(f"Initializing XenServer client for {XENSERVER_URL}")
        return XenServerClient(XENSERVER_URL, XENSERVER_USER, XENSERVER_PASS)
    else:
        logger.error("Cannot initialize XenServer client - missing configuration")
        return None


# Initialize XenServer client
xenserver_client = _initialize_xenserver_client()


def _get_host_memory_info(session: XenAPI.Session, host_ref: str, 
                          host_record: Dict[str, Any]) -> Dict[str, int]:
    """
    Get memory information for a host.
    
    Args:
        session: Active XenAPI session
        host_ref: Host reference
        host_record: Host record dictionary
        
    Returns:
        Dictionary with 'free' and 'total' memory in bytes
    """
    try:
        free_memory = session.xenapi.host.compute_free_memory(host_ref)
        metrics_ref = session.xenapi.host.get_metrics(host_ref)
        total_memory = session.xenapi.host_metrics.get_memory_total(metrics_ref)
    except Exception as e:
        logger.warning(f"Could not get memory metrics: {e}")
        free_memory = 0
        total_memory = host_record.get('memory_total', 0)
    
    return {
        "free": free_memory,
        "total": total_memory,
    }


CPU_KEYS: tuple[str, ...] = (
    "cpu_count",
    "socket_count",
    "threads_per_core",
    "vendor",
    "speed",
    "modelname",
)

BIOS_KEYS: tuple[str, ...] = (
    "bios-vendor",
    "bios-version",
    "system-manufacturer",
    "system-product-name",
    "system-version",
    "system-serial-number",
    "baseboard-manufacturer",
    "baseboard-product-name",
    "baseboard-version",
    "baseboard-serial-number",
)

LICENSE_KEYS: tuple[str, ...] = (
    "sku_type",
    "expiry",
    "grace",
    "license_type",
    "sku_marketing_name",
    "active_subscription",
    "css_expiry",
)


def _select_fields(source: Dict[str, Any], keys: Iterable[str]) -> Dict[str, Any]:
    """Return a dict containing only selected keys (missing -> empty string)."""
    result: Dict[str, Any] = {}
    for k in keys:
        v = source.get(k, "")
        if not isinstance(v, str):
            try:
                v = str(v)
            except Exception:
                v = ""
        result[k] = v
    return result


def _build_host_info(session: XenAPI.Session, host_ref: str) -> Dict[str, Any]:
    """Build tailored host information dictionary with filtered cpu/bios/license fields."""
    host_record = session.xenapi.host.get_record(host_ref)
    memory_info = _get_host_memory_info(session, host_ref, host_record)

    cpu_full = host_record.get('cpu_info', {}) or {}
    bios_full = host_record.get('bios_strings', {}) or {}
    license_full = host_record.get('license_params', {}) or {}

    cpu_filtered = _select_fields(cpu_full, CPU_KEYS)
    bios_filtered = _select_fields(bios_full, BIOS_KEYS)
    license_filtered = _select_fields(license_full, LICENSE_KEYS)

    return {
        "uuid": host_record.get('uuid', ''),
        "name": host_record.get('name_label', ''),
        "description": host_record.get('name_description', ''),
        "memory": memory_info,
        "cpu": cpu_filtered,
        "bios": bios_filtered,
        "version": host_record.get('software_version', {}),
        "license": license_filtered,
    }


@xenserver_mcp.tool()
def get_all_host_info(host_uuid: Optional[str] = None) -> Dict[str, Any]:
    """
    Get comprehensive host information for XenServer hosts in a pool.
    
    Args:
        host_uuid: Specific host UUID to get info for. If not provided, returns all hosts.
    
    Returns:
        Dictionary containing:
            - If host_uuid specified: Single host information dictionary
            - If host_uuid not specified: Dictionary with 'hosts' list and 'total_hosts' count
            
        Host information includes:
            - uuid: Host UUID
            - name: Host name (name_label)
            - description: Host description (name_description)
            - memory: Dictionary with 'free' and 'total' memory in bytes
            - cpu: CPU information dictionary
            - bios: BIOS strings dictionary
            - version: Software version dictionary
            - license: License information dictionary
    """
    if not xenserver_client:
        return {"error": "XenServer connection not configured"}
    
    try:
        with xenserver_client.session() as session:
            # Determine which hosts to process
            if host_uuid:
                try:
                    host_ref = session.xenapi.host.get_by_uuid(host_uuid)
                    hosts_to_process = [host_ref]
                except XenAPI.Failure:
                    return {"error": f"Host with UUID '{host_uuid}' not found"}
            else:
                hosts_to_process = session.xenapi.host.get_all()
            
            # Build host information list
            host_list = [_build_host_info(session, host_ref) 
                        for host_ref in hosts_to_process]
            
            # Return appropriate format based on query type
            if host_uuid:
                return host_list[0] if host_list else {"error": "Host not found"}
            
            return {
                "hosts": host_list,
                "total_hosts": len(host_list)
            }
            
    except XenAPI.Failure as xen_error:
        logger.error(f"XenAPI error: {xen_error.details}")
        return {"error": f"XenAPI error: {xen_error.details[0] if xen_error.details else 'Unknown error'}"}
    except Exception as e:
        logger.exception("Unexpected error getting host info")
        return {"error": f"Error getting host info: {str(e)}"}


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    """
    Manage the lifecycle of the XenServer MCP session manager.
    
    Args:
        app: Starlette application instance
        
    Yields:
        None - Context for application lifetime
    """
    async with xenserver_mcp.session_manager.run():
        yield


def create_app() -> Starlette:
    """
    Create and configure the Starlette application.
    
    Returns:
        Configured Starlette application instance
    """
    # Set the path to "/" so clients connect directly to root instead of /mcp
    xenserver_mcp.settings.streamable_http_path = "/"
    
    app = Starlette(
        routes=[
            Mount("/", xenserver_mcp.streamable_http_app()),
        ],
        lifespan=lifespan,
    )
    
    return app


# Create the application
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    # Server configuration
    HOST = "0.0.0.0"
    PORT = 8081
    LOG_LEVEL = "info"
    
    logger.info(f"Starting XenServer MCP server on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT, log_level=LOG_LEVEL)