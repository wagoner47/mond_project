.. _data_utils.data_read_utils:

***************************************************
Utilities for reading data (:mod:`data_read_utils`)
***************************************************

.. currentmodule:: mond_project

The :mod:`data_read_utils` module is the main interface point for accessing the data from the `Illustris simulations`_. The primary function :func:`get` can be used recursively to access deeper levels of the data from the Illustris API, or can be used to access a table directly if the URL is already known. Once a table level page is reached, the data is stored in an HDF5_ table, which can then be read in by the user using their favorite HDF5 reader in python, such as h5py_.

.. todo:: Add function for reading the HDF5 table? Or is that too much since that is already available in other modules?

One potential gotcha for using this is that the user must have an environment variable with the API key they will use to `access the data from Illustris`_. To get this key, you must complete the registration through Illustris. The API key environment variable should be named "ILL_KEY", and can be set by adding to the appropriate user profile file for the system or by using the appropriate command line utility. For Linux/Unix based systems, for instance, to set and check the value:

..code-block:: console
        
        $ export ILL_KEY=insert-your-assigned-api-key
        $ echo $ILL_KEY

.. automodule:: data_utils.data_read_utils
   :members:
   :undoc-members:

.. _Illustris simulations: http://www.illustris-project.org/
.. _HDF5: https://support.hdfgroup.org/HDF5/
.. _h5py: http://www.h5py.org/
.. _access the data from Illustris: http://www.illustris-project.org/data/
