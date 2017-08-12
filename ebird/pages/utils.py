import requests


def get_content(url: str) -> str:
    """
    Get the content from eBird web page.

    :param url: the URL for the API call.
    :type url: str

    :raises request.exceptions.ConnectionError if there is an error with
    the connection to the eBird site.

    :raises request.exceptions.Timeout if the eBird site takes too long
    to respond.

    :raises requests.exceptions.HTTPError any errors was returned by the
    eBird site.

    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text