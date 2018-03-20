from __future__ import (absolute_import, division, print_function,
        unicode_literals)
from future.utils import iteritems
import numpy as np
import os
import re
import requests
import h5py
from mond_project.data_utils import data_read_utils


test_base_url = "http://www.illustris-project.org/api/"
test_hdf5_url = \
        "http://www.illustris-project.org/api/Illustris-3/snapshots/135/subhalos/1030/sublink/mpb.hdf5"


def test_get_fail():
    """Test fail cases for :function:`mond_test.data_read_utils.get`. This tests
    the cases when a bad URL or bad API key is given
    """
    # Set up a bad URL and a bad API key
    test_fail_url = list(test_base_url)
    test_fail_url[-2] = "s"
    test_fail_url = "".join(test_fail_url)
    
    # Try running with bad URL: should get an HTTPError
    with np.testing.assert_raises_regex(requests.exceptions.HTTPError, 
            "404 Client Error: NOT FOUND for url: " + test_fail_url):
        data_read_utils.get(test_fail_url)


def test_get_json():
    """Test getting json page with :function:`mond_test.data_read_utils.get`. In
    this case, we should successfully get a return dict
    """
    r = data_read_utils.get(test_base_url)

    # Check that the results are as expected
    ## Only key should be 'simulations'
    np.testing.assert_array_equal(list(r), ["simulations"],
            "Keys returned from base URL are not as expected")
    ## Check first simulation meta-data
    sim0_exp = {"name": "Illustris-1",
            "num_snapshots": 134,
            "url": "http://www.illustris-project.org/api/Illustris-1/"}
    sim0_get = r["simulations"][0]
    for key in sim0_exp:
        assert key in sim0_get, "Missing key %s in results" %(key)
    for (key, val) in iteritems(sim0_get):
        assert key in sim0_exp, "Extra key %s in results" %(key)
        np.testing.assert_string_equal(str(val), str(sim0_exp[key]))


def test_get_table():
    """Test getting table from data page with
    :function:`mond_test.data_read_utils.get`. In this case, we should
    successfully get a return astropy table
    """
    # Get data
    fname = data_read_utils.get(test_hdf5_url)
    ## Read in HDF5 data: just get the one field and close again
    f = h5py.File(fname, "r")
    snapnum_get = f["SnapNum"][:]
    f.close()

    # Get something to compare from the table
    snapnum_exp = list(np.arange(135, 31, -1))

    # Compare length and content of SnapNum
    np.testing.assert_equal(len(snapnum_get), len(snapnum_exp),
            "Length of 'SnapNum' not as expected")
    np.testing.assert_array_equal(snapnum_get, snapnum_exp,
            "'SnapNum' not as expected")
