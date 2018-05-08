from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import numpy as np
import pandas as pd


# Gravitational constant in units of km^2 kpc / M_sun s^2
grav_constant = 4.301e-6


def _get_subhalo_ids(file_list):
    """A private function to be used behind the scenes for getting a list of
    the stored subhalo IDs given the list of file names

    Parameters
    ----------
    :param file_list: List of file names
    :type file_list: 1D array-like str

    Returns
    -------
    :return ids: Subhalo IDs found in the file names
    :rtype ids: 1D array int
    """
    ids = np.array([int(
          os.path.splitext(os.path.splitext(filei)[0])[0].split("subhalo", 1)[
              1]) for filei in file_list])
    return ids


def _get_subhalo_fbase(file_list):
    """A private function to be used behind the scenes for getting the file
    name base of the stored subhalo files given the list of file names

    Parameters
    ----------
    :param file_list: List of file names
    :type file_list: 1D array-like str

    Returns
    -------
    :return base: Base of the file names contained within :param:`file_list`
    :rtype base: str
    """
    base =\
    os.path.splitext(os.path.splitext(file_list[0])[0])[0].split("subhalo", 1)[
        0]
    return base


def calc_gobs(r, delta_r, list_file_loc, subhalo_id=None):
    """Calculate the observed gravitational acceleration, :math:`g_{obs}(r) =
    \frac{V_{obs}^2(r)}{r}`

    Parameters
    ----------
    :param r: Radius/radii at which to calculate the acceleration
    :type r: scalar or 1D array-like float
    :param delta_r: Radial bin size(s), for averaging. Accelerations for
    particles within :math:`r \pm 0.5 \cdot delta\_r` are averaged together
    for a given radius r. Note that :param:`delta_r` must be scalar if
    :param:`r` is scalar, can be scalar if using the same width for each bin
    when :param:`r` is array-like, but must be same size as :param:`r` if not
    scalar
    :type delta_r: scalar or 1D array-like float
    :param list_file_loc: Location of the list file for the simulation and
    snapshot being used
    :type list_file_loc: str
    :param subhalo_id: ID(s) of subhalos within snapshot for which to
    calculate, or None to calculate for all subhalos. Default None
    :type subhalo_id: scalar or 1D array-like int, optional

    Returns
    -------
    :return gobs: The observed gravitational acceleration for each halo
    averaged in each radial bin
    :rtype gobs: pandas DataFrame
    """
    r = np.atleast_1d(r)
    if r.ndim > 1:
        r = r.flatten()
    if hasattr(delta_r, "len"):
        delta_r = np.atleast_1d(delta_r)
        if delta_r.ndim > 1:
            delta_r = delta_r.flatten()
        if delta_r.size != r.size:
            raise ValueError(
                "Non-constant bin sizes must have same length as bin centers")
    r_low = r.copy() - 0.5 * delta_r
    r_upp = r.copy() + 0.5 * delta_r

    snap_dir = os.path.dirname(list_file_loc)
    file_list = np.load(list_file_loc)["arr_0"]
    saved_ids = _get_subhalo_ids(file_list)
    if subhalo_id is not None:
        subhalo_id = np.atleast_1d(subhalo_id)
        if subhalo_id.ndim > 1:
            subhalo_id = subhalo_id.flatten()
        if not np.all(np.isin(subhalo_id, saved_ids)):
            raise ValueError("One or more requested subhalos not found")
    else:
        subhalo_id = saved_ids
    gobs = pd.DataFrame(index=pd.Index(r, name="r"),
                        columns=pd.Index(subhalo_id, name="ID"))
    use_files = file_list[np.isin(saved_ids, subhalo_id)]
    for id, filei in zip(subhalo_id, use_files):
        shdf = pd.read_pickle(os.path.join(snap_dir, filei))
        for ri, rli, rui in zip(r, r_low, r_upp):
            shdfi = shdf.query("(r >= {}) & (r < {})".format(rli, rui))
            gobs[id].loc[ri] = shdfi["v"].pow(2).div(shdfi["r"]).mean()
    return gobs


def calc_gbar(r, delta_r, list_file_loc, subhalo_id=None):
    """Calculate the baryonic gravitational acceleration, :math:`g_{bar}(r) =
    \frac{G M(<r)}{r^2}`

    Parameters
    ----------
    :param r: Radius/radii at which to calculate the acceleration
    :type r: scalar or 1D array-like float
    :param delta_r: Radial bin size(s), for averaging. Accelerations for
    particles within :math:`r \pm 0.5 \cdot delta\_r` are averaged together
    for a given radius r. Note that :param:`delta_r` must be scalar if
    :param:`r` is scalar, can be scalar if using the same width for each bin
    when :param:`r` is array-like, but must be same size as :param:`r` if not
    scalar
    :type delta_r: scalar or 1D array-like float
    :param list_file_loc: Location of the list file for the simulation and
    snapshot being used
    :type list_file_loc: str
    :param subhalo_id: ID(s) of subhalos within snapshot for which to
    calculate, or None to calculate for all subhalos. Default None
    :type subhalo_id: scalar or 1D array-like int, optional

    Returns
    -------
    :return gbar: The baryonic gravitational acceleration for each halo
    averaged in each radial bin
    :rtype gbar: pandas DataFrame
    """
    r = np.atleast_1d(r)
    if r.ndim > 1:
        r = r.flatten()
    if hasattr(delta_r, "len"):
        delta_r = np.atleast_1d(delta_r)
        if delta_r.ndim > 1:
            delta_r = delta_r.flatten()
        if delta_r.size != r.size:
            raise ValueError(
                "Non-constant bin sizes must have same length as bin centers")
    r_low = r.copy() - 0.5 * delta_r
    r_upp = r.copy() + 0.5 * delta_r

    snap_dir = os.path.dirname(list_file_loc)
    file_list = np.load(list_file_loc)["arr_0"]
    saved_ids = _get_subhalo_ids(file_list)
    if subhalo_id is not None:
        subhalo_id = np.atleast_1d(subhalo_id)
        if subhalo_id.ndim > 1:
            subhalo_id = subhalo_id.flatten()
        if not np.all(np.isin(subhalo_id, saved_ids)):
            raise ValueError("One or more requested subhalos not found")
    else:
        subhalo_id = saved_ids
    gbar = pd.DataFrame(index=pd.Index(r, name="r"),
                        columns=pd.Index(subhalo_id, name="ID"))
    use_files = file_list[np.isin(saved_ids, subhalo_id)]
    for id, filei in zip(subhalo_id, use_files):
        shdf = pd.read_pickle(os.path.join(snap_dir, filei))
        for ri, rli, rui in zip(r, r_low, r_upp):
            shdf_in = shdf.query("r < {}".format(rli))
            m_in = shdf_in["M"].sum()
            shdfi = shdf.query("(r >= {}) & (r < {})".format(rli, rui))
            gbar[id].loc[ri] = (grav_constant * m_in / shdfi["r"]).mean()
    return gbar
