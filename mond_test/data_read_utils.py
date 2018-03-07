import requests
from astropy.table import Table
import os


def get(path, api_key, params=None):
    """Make an HTTP request to get the data from path. Note that there are
    several possible returns with different types depending on the data received
    from the URL

    Parameters
    ----------
    :param path: The URL to request from
    :type path: str
    :param api_key: The key for accessing the Illustris API
    :type api_key: str
    :param params: Extra parameters to pass to `requests`. Default None
    :type params: dict or None

    Returns
    -------
    :return r: The :class:`Response` object from `requests`, if not JSON or binary data
    :rtype r: :class:`requests.Response`
    :return r.json(): JSON decoded response, if request was successful and 
    response is JSON
    :rtype r.json(): dict
    :return table: Data table read in, if request was successful and response is
    binary
    :rtype table: :class:`astropy.table.Table`
    """
    headers = {"api_key": api_key}

    r = requests.get(path, params=params, headers=headers)

    r.raise_for_status()

    if r.headers["content-type"] == "application/json":
        return r.json()

    if "content-disposition" in r.headers:
        filename = r.headers["content-disposition"].split("filename=")[1]
        with open(filename, "wb") as f:
            f.write(r.content)
        table = Table.read(filename)
        os.remove(filename)
        return table

    return r


