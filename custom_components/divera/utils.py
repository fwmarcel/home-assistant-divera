"""Utils Module for Divera Integration."""


def remove_params_from_url(url):
    """Remove parameters from a URL.

    Args:
        url (str): The URL from which parameters need to be removed.

    Returns:
        str: URL without the parameters part.

    """
    url_str: str = str(url)
    return url_str[:url_str.find('?')]
