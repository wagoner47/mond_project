from __future__ import (absolute_import, division, print_function,
        unicode_literals)
import requests
import os
from configobj import ConfigObj


config = ConfigObj(os.path.join(os.path.dirname(__file__), "..",
    "mond_config.ini"))
api_key = config["ILL_KEY"]


def get(path, params=None):
    """Make an HTTP request to get the data from path. Note that there are
    several possible returns with different types depending on the data received
    from the URL

    Parameters
    ----------
    :param path: The URL to request from
    :type path: str
    :param params: Extra parameters to pass to `requests`. Default None
    :type params: dict or None

    Returns
    -------
    :return r: The :class:`Response` object from `requests`, if not JSON or binary data
    :rtype r: :class:`requests.Response`
    :return r.json(): JSON decoded response, if request was successful and 
    response is JSON
    :rtype r.json(): dict
    :return filename: Filename for stored HDF5 table, if request was successful
    and response is binary
    :rtype filename: str

    Examples
    --------
    Getting JSON data from a higher level API page:

    >>> from mond_project import get
    >>> import os
    >>> base_url = "http://www.illustris-project.org/api/"
    >>> r = get(base_url)
    >>> r.keys()
    ['simulations']
    >>> len(r["simulations"])
    18
    >>> r["simulations"][0]
    {'name': 'Illustris-1',
     'num_snapshots': 134,
     'url': 'http://www.illustris-project.org/api.Illustris-1/'}

    Getting the data saved in a file with a specific URL:

    >>> table_url = "http://www.illustris-project.org/api/Illustris-3/snapshots/135/subhalos/1030/sublink/mpb.hdf5"
    >>> filename = get(table_url)
    >>> print(filename)
    'sublink_mpb_1030.hdf5'
    """
    headers = {"api-key": api_key}

    r = requests.get(path, params=params, headers=headers)

    r.raise_for_status()

    if r.headers["content-type"] == "application/json":
        return r.json()

    if "content-disposition" in r.headers:
        filename = r.headers["content-disposition"].split("filename=")[1]
        with open(filename, "wb") as f:
            f.write(r.content)
        return filename

    return r


if __name__ == "__main__":
    import doctest
    doctest.testmod()
