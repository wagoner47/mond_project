from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import requests
import os
from configobj import ConfigObj
import h5py
import numpy as np
import pandas as pd

config = ConfigObj(
      os.path.join(os.path.dirname(__file__), "..", "mond_config.ini"))
api_key = config["ILL_KEY"]
hubble_param = config.as_float("ILL_h")


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
    :return r: The :class:`Response` object from `requests`, if not JSON or
    binary data
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
    >>> list(r)
    ['simulations']
    >>> len(r["simulations"])
    18
    >>> r["simulations"][0] == {'name': 'Illustris-1', 
    ...                         'num_snapshots': 134, 
    ...                         'url': 'http://www.illustris-project.org/api/'\
                                'Illustris-1/'}
    True

    Getting the data saved in a file with a specific URL:

    >>> table_url = "http://www.illustris-project.org/api/Illustris-3/"\
                    "snapshots/135/subhalos/1030/sublink/mpb.hdf5"
    >>> filename = get(table_url)
    >>> print(filename)
    sublink_mpb_1030.hdf5
    """
    headers = {"api-key":api_key}
    
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


def save_halos(simulation, save_loc, z=None, snapnum=None):
    """Save the info for each subhalo in :param:`sumulation` at redshift
    :param:`z`. The results are stored in one file per subhalo, with each
    file containing the radii, masses, and velocities of gas and stars
    associated with the subhalo. The files are stored at :param:`save_loc`,
    as well as a file containing a list of the subhalo file names. The file
    path for the list file will be returned for future use.
    
    Parameters
    ----------
    :param simulation: The name of the Illustris simulation to query,
    or an integer to reference one of 'Illustris-1', 'Illustris-2',
    or 'Illustris-3'
    :type simulation: str
    :param save_loc: The location in which to store the result files. Must be
    a valid path to an existing *directory*, **not a file name**
    :type save_loc: str
    :param z: The redshift at which to query the simulation, and the closest
    available redshift will be used. Does not need to be given if
    :param:`snapnum` is given. If both are provided, this will be preferred.
    Default None
    :type z: int or float, optional
    :param snapnum: The snapshot number at which to query the simulation.
    This must be a valid snapshot number. Does not need to be given if
    :param:`z` is given. If both are provided, :param:`z` will be preferred.
    Default None
    :type snapnum: int, optional
    
    Returns
    -------
    :return list_file: The path to the file created containing the list of
    output file names
    :rtype list_file: str
    
    :TODO: Decide on definition of subhalo as a 'galaxy'. Is :math:`M > 10^5
    M_\odot` good enough?
    """
    mass_cut = hubble_param * 10**-5
    query_params = {
        "stars":"Coordinates,Masses,Velocities",
        "gas"  :"Coordinates,Masses,Velocities"}
    base_url = "http://www.illustris-project.org/api/"
    base = get(base_url)
    valid_sims = [sim["name"] for sim in base["simulations"]]
    if isinstance(simulation, int):
        simulation = "Illustris-{}".format(simulation)
    if not simulation in valid_sims:
        raise ValueError("Invalid Illustris simulation: {}. Please use a valid "
                         "simulation!".format(simulation))
    sim = get(base["simulations"][valid_sims.index(simulation)]["url"])
    if z is None and snapnum is None:
        raise ValueError("At least one of z and snapnum MUST be given")
    if z is None:
        sim_snaps = get(sim["snapshots"])
        snapnum = int(snapnum)
        sim_snapnums = [snap["number"] for snap in sim_snaps]
        if not snapnum in sim_snapnums:
            raise ValueError(
                  "Invalid snapshot number for simulation {}: {}. Please use a "
                  "valid snapshot number for this simulation".format(simulation,
                        snapnum))
        snap_url = sim_snaps[sim_snapnums.index(snapnum)]["url"]
    else:
        snap_url = sim["snapshots"] + "z={}/".format(float(z))
    snap = get(snap_url)
    sub_url = "{}{{}}".format(snap["subhalos"])
    
    file_list = []
    fname_base = "{}_{}={}_subhalo{{}}.pickle.gz".format(simulation,
                                                         "z" if z is not None
                                                         else "snapnum",
                                                         z if z is not None
                                                         else snapnum)
    z = snap["redshift"]
    a = 1.0 / (1.0 + z)
    for i in range(snap["count"]):
        sub = get(sub_url.format(i))
        if sub["mass"] > mass_cut:
            saved_filename = get(sub["cutouts"]["subhalo"], query_params)
            with h5py.File(saved_filename, "r") as f:
                # Get gas data
                dx = f["PartType0"]["Coordinates"][:, 0] - sub["pos_x"]
                dy = f["PartType0"]["Coordinates"][:, 1] - sub["pos_y"]
                dz = f["PartType0"]["Coordinates"][:, 2] - sub["pos_z"]
                r_gas = np.sqrt(dx**2 + dy**2 + dz**2) * a / hubble_param
                vx = f["PartType0"]["Velocities"][:, 0] * np.sqrt(a) - sub[
                    "vel_x"]
                vy = f["PartType0"]["Velocities"][:, 1] * np.sqrt(a) - sub[
                    "vel_y"]
                vz = f["PartType0"]["Velocities"][:, 2] * np.sqrt(a) - sub[
                    "vel_z"]
                v_gas = np.sqrt(vx**2 + vy**2 + vz**2)
                m_gas = f["PartType0"]["Masses"] * 10**10 / hubble_param
                type_gas = np.full(m_gas.size, "gas")
                
                # Get star data
                dx = f["PartType4"]["Coordinates"][:, 0] - sub["pos_x"]
                dy = f["PartType4"]["Coordinates"][:, 1] - sub["pos_y"]
                dz = f["PartType4"]["Coordinates"][:, 2] - sub["pos_z"]
                r_stars = np.sqrt(dx**2 + dy**2 + dz**2) * a / hubble_param
                vx = f["PartType4"]["Velocities"][:, 0] * np.sqrt(a) - sub[
                    "vel_x"]
                vy = f["PartType4"]["Velocities"][:, 1] * np.sqrt(a) - sub[
                    "vel_y"]
                vz = f["PartType4"]["Velocities"][:, 2] * np.sqrt(a) - sub[
                    "vel_z"]
                v_stars = np.sqrt(vx**2 + vy**2 + vz**2)
                m_stars = f["PartType4"]["Masses"] * 10**10 / hubble_param
                type_stars = np.full(m_stars.size, "star")
                
                # Put in DataFrame
                df = pd.DataFrame.from_dict({
                                                "r":np.append(r_gas, r_stars),
                                                "M":np.append(m_gas, m_stars),
                                                "v":np.append(v_gas, v_stars),
                                                "type":np.append(type_gas,
                                                                 type_stars)})
                df.to_pickle(os.path.join(save_loc, fname_base.format(i)))
                file_list.append(fname_base.format(i))
            os.remove(saved_filename)
    list_file_loc = os.path.join(save_loc, "subhalo_list.npz")
    np.savez_compressed(list_file_loc, file_list)
    return list_file_loc


if __name__ == "__main__":
    import doctest
    
    doctest.testmod()
