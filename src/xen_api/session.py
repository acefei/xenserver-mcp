import ssl
import xmlrpc.client
import os
from contextlib import contextmanager

import XenAPI


@contextmanager
def xapi_session(_id: str, get_xs_clusters: dict):
    """Context manager for XenAPI session.

    Args:
        _id: Cluster identifier
        get_xs_clusters: Dictionary containing cluster credentials

    Yields:
        XenAPI.Session: Authenticated session object
    """
    xs_clusters = get_xs_clusters
    cred = xs_clusters[_id]

    # Ensure host has a protocol prefix (default to https)
    host = cred["host"]
    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"https://{host}"

    # Honor verify_ssl config (default: True)
    verify_ssl = cred.get("verify_ssl", True)

    # Allow disabling SSL verification via environment variable
    if os.environ.get("PYTHONHTTPSVERIFY") == "0":
        verify_ssl = False

    if not verify_ssl:
        # Pass ignore_ssl=True to disable verification
        # This relies on XenAPI handling the SSL context correctly
        try:
            session = XenAPI.Session(host, ignore_ssl=True)
        except TypeError:
            # Fallback for older XenAPI versions that don't support ignore_ssl
            # In this case we must manually create a context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            transport = xmlrpc.client.SafeTransport(context=ssl_context)
            session = XenAPI.Session(host, transport=transport)
    else:
        session = XenAPI.Session(host)

    session.xenapi.login_with_password(cred["username"], cred["password"])  # type: ignore
    try:
        yield session
    finally:
        session.xenapi.session.logout()  # type: ignore
