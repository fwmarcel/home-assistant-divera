"""Utils Module for Divera Integration."""

from yarl import URL


def remove_params_from_url(url: URL):
    """Remove parameters from a URL.

    Args:
        url (str): The URL from which parameters need to be removed.

    Returns:
        str: URL without the parameters part.

    """
    url.with_query()
    url_str: str = url.human_repr()
    return url_str
