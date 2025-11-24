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
    session = XenAPI.Session(cred["host"])
    session.xenapi.login_with_password(cred["username"], cred["password"])
    try:
        yield session
    finally:
        session.xenapi.session.logout()
