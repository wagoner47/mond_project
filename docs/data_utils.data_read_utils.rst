.. _data_utils.data_read_utils:

***************************************************
Utilities for reading data (:mod:`data_read_utils`)
***************************************************

.. currentmodule:: mond_project

The :mod:`data_read_utils` module is the main interface point for accessing the data from the `Illustris simulations`_. The primary function :func:`get` can be used recursively to access deeper levels of the data from the Illustris API, or can be used to access a table directly if the URL is already known. Once a table level page is reached, the data is stored in an HDF5_ table, which can then be read in by the user using their favorite HDF5 reader in python, such as h5py_.

A slightly higher level function for accessing the Illustris data can also be used, :func:`save_halos`. This function is built on the :func:`get` function, but it does the recursive calls for the user, and also only stores the relevant entries for the MOND calculations from the Illustris API. With this function, the user specifies a simulation (either the full name or the number for the base Illustris simulations), a snapshot number or redshift, and a directory in which to save the data. Any subhalo within the snapshot that qualifies as a galaxy is then queried for coordinates, velocities, and masses of all gas and star particles. The coordinates are used to calculate a radius within the galaxy, and the velocities are used to calculate a velocity dispersion (with respect to the galaxy), and the results are then stored into a single file per galaxy, with tags identifying each entry as "gas" or "star". The files are compressed pickle files which can be read with :mod:`pandas`, with names based upon the simulation, snapshot/redshift, and subhalo ID. File names are also stored in a "list file" in the same directory, saved as a numpy compressed binary file, and the file path for this list file is returned for future use. The columns and units for each subhalo file are as follows:

+-------------+-----------------+---------------------------+
| Column Name | Unit            | Description               |
+=============+=================+===========================+
| r           | kpc             | Radius, in physical units |
+-------------+-----------------+---------------------------+
| M           | :math:`M_\odot` | Mass                      |
+-------------+-----------------+---------------------------+
| v           | km/s            | Speed relative to galaxy, |
|             |                 | in physical units         |
+-------------+-----------------+---------------------------+
| type        |        -        | Type of particle, either  |
|             |                 | "gas" or "star"           |
+-------------+-----------------+---------------------------+

.. todo:: Make sure we like our galaxy definition!
.. todo:: Do we need anything else to be saved for each subhalo?

One potential gotcha for using this is that the user must have an environment variable with the API key they will use to `access the data from Illustris`_. To get this key, you must complete the registration through Illustris. The API key environment variable should be named "ILL_KEY", and can be set by adding to the appropriate user profile file for the system or by using the appropriate command line utility. For Linux/Unix based systems, for instance, to set and check the value:

.. code-block:: console
        
        $ export ILL_KEY=insert-your-assigned-api-key
        $ echo $ILL_KEY

.. automodule:: data_utils.data_read_utils
   :members:
   :undoc-members:

.. _Illustris simulations: http://www.illustris-project.org/
.. _HDF5: https://support.hdfgroup.org/HDF5/
.. _h5py: http://www.h5py.org/
.. _access the data from Illustris: http://www.illustris-project.org/data/
