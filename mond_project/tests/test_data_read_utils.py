from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from future.utils import iteritems
import numpy as np
import os
import re
import requests
import h5py
import pandas as pd
from mond_project.data_utils import data_read_utils
from . import create_test_data

test_base_url = "http://www.illustris-project.org/api/"
test_hdf5_url = "http://www.illustris-project.org/api/Illustris-3/snapshots"\
                "/135/subhalos/1030/sublink/mpb.hdf5"
test_sim_url = "http://www.illustris-project.org/api/Illustris-1/snapshots/"
test_snap_url = "http://www.illustris-project.org/api/Illustris-1/snapshots"\
                "/135/subhalos/"
test_dir = os.path.dirname(__file__)


def test_get_fail():
    """Test fail cases for :function:`data_utils.data_read_utils.get`. This
    tests
    the cases when a bad URL or bad API key is given
    """
    # Set up a bad URL and a bad API key
    test_fail_url = list(test_base_url)
    test_fail_url[-2] = "s"
    test_fail_url = "".join(test_fail_url)
    
    # Try running with bad URL: should get an HTTPError
    with np.testing.assert_raises_regex(requests.exceptions.HTTPError,
                                        "404 Client Error: NOT FOUND for url:"
                                        " " + test_fail_url):
        data_read_utils.get(test_fail_url)


def test_get_json():
    """Test getting json page with
    :function:`data_utils.data_read_utils.get`. In
    this case, we should successfully get a return dict
    """
    r = data_read_utils.get(test_base_url)
    
    # Check that the results are as expected
    ## Only key should be 'simulations'
    np.testing.assert_array_equal(list(r), ["simulations"],
                                  "Keys returned from base URL are not as "
                                  "expected")
    ## Check first simulation meta-data
    sim0_exp = {
        "name":"Illustris-1", "num_snapshots":134,
        "url" :"http://www.illustris-project.org/api/Illustris-1/"}
    sim0_get = r["simulations"][0]
    for key in sim0_exp:
        assert key in sim0_get, "Missing key %s in results" % (key)
    for (key, val) in iteritems(sim0_get):
        assert key in sim0_exp, "Extra key %s in results" % (key)
        np.testing.assert_string_equal(str(val), str(sim0_exp[key]))


def test_get_table():
    """Test getting table from data page with
    :function:`data_utils.data_read_utils.get`. In this case, we should
    successfully get a string for a filename to be saved
    """
    # Get data
    fname = data_read_utils.get(test_hdf5_url)
    np.testing.assert_string_equal(fname, os.path.join(os.getcwd(), 
        "sublink_mpb_1030.hdf5"))
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


def test_save_halos_badz():
    """Test for expected error raised if no redshift or snapshot passed,
    or if an invalid value is passed in
    :function:`data_utils.data_read_utils.save_halos`
    """
    with np.testing.assert_raises_regex(ValueError,
                                        "At least one of z and snapnum MUST "
                                        "be given"):
        data_read_utils.save_halos(1, test_dir)
    with np.testing.assert_raises_regex(ValueError,
                                        "Invalid snapshot number for "
                                        "simulation Illustris-1: 136. Please "
                                        "use a valid snapshot number for this "
                                        "simulation"):
        data_read_utils.save_halos(1, test_dir, snapnum=136)


def test_save_halos_bad_sim():
    """Test trying to use an invalid simulation in Illustris with
    :function:`data_utils.data_read_utils.save_halos`
    """
    with np.testing.assert_raises_regex(ValueError,
                                        "Invalid Illustris simulation: {}. "
                                        "Please use a valid simulation!".format(
                                              "Illustris-0")):
        # Pass as bad integer
        data_read_utils.save_halos(0, test_dir, z=0)
        # Pass as bad string
        data_read_utils.save_halos("Illustris-0", os.path.dirname(__file__),
                                   z=0)


def test_save_halos():
    """Test pass case of :function:`data_utils.data_read_utils.save_halos`
    """
    test_exp_files = [os.path.join(test_dir, "test_data", "exp", filei) for
            filei in ["subhalo_list_z.npz", "subhalo_list_snapnum.npz",
            "Illustris-1_z=0_subhalo0.pickle.gz",
            "Illustris-1_snapnum=135_subhalo0.pickle.gz"]]
    if not np.all([os.path.isfile(filei) for filei in test_exp_files]):
        create_test_data.main()

    if not os.path.isdir(os.path.join(test_dir, "test_data", "obs")):
        os.makedirs(os.path.join(test_dir, "test_data", "obs"))
    # Test query by redshift
    list_file = data_read_utils.save_halos(1,
                                           os.path.join(test_dir, "test_data",
                                                        "obs"), z=0)
    file_list_z_exp = np.load(
        os.path.join(test_dir, "test_data", "exp",
        "subhalo_list_z.npz"))["arr_0"]
    file_list_z_obs = np.load(list_file)["arr_0"]
    # Compare saved file names
    np.testing.assert_array_equal(file_list_z_obs, file_list_z_exp,
                                  "Saved file name list different than "
                                  "expected for redshift query")
    # Compare the first saved file
    df_z_exp = pd.read_pickle(
        os.path.join(test_dir, "test_data", "exp", file_list_z_exp[0]))
    df_z_obs = pd.read_pickle(
        os.path.join(os.path.dirname(list_file), file_list_z_obs[0]))
    pd.testing.assert_index_equal(df_z_obs.columns, df_z_exp.columns,
                                  obj="Column names from redshift query")
    pd.testing.assert_frame_equal(df_z_obs, df_z_exp,
                                  obj="DataFrame from redshift query")
    
    # Test query by snapshot number
    list_file = data_read_utils.save_halos(1,
                                           os.path.join(test_dir, "test_data",
                                                        "obs"), snapnum=135)
    file_list_sn_exp = np.load(
        os.path.join(test_dir, "test_data", "exp",
        "subhalo_list_snapnum.npz"))["arr_0"]
    file_list_sn_obs = np.load(list_file)["arr_0"]
    # Compare saved file names
    np.testing.assert_array_equal(file_list_sn_obs, file_list_sn_exp,
                                  "Saved file name list different than "
                                  "expected for snapshot number query")
    # Compare the first saved file
    df_sn_exp = pd.read_pickle(
        os.path.join(test_dir, "test_data", "exp", file_list_sn_exp[0]))
    df_sn_obs = pd.read_pickle(
        os.path.join(os.path.dirname(list_file), file_list_sn_obs[0]))
    pd.testing.assert_index_equal(df_sn_obs.columns, df_sn_exp.columns,
                                  obj="Column names from snapshot number query")
    pd.testing.assert_frame_equal(df_sn_obs, df_sn_exp,
                                  obj="DataFrame from snapshot number query")
