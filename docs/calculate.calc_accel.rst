.. _calculate.calc_accel:

***************************************************
Calculate accelerations in data (:mod:`calc_accel`)
***************************************************

.. currentmodule:: mond_project

The :mod:`calc_accel` module contains the functions needed to find accelerations in the Illustris data. The data is assumed to have been read already using :func:`data_read_utils.save_halos`, although the user could also get the data themselves and store with the same assumed structure. There are two accelerations that need to be calculated, and they are found very differently.

Observed acceleration
=====================

The observed acceleration is calculated from the velocities of stars and gas in a given galaxy or subhalo:

.. math::

    g_{obs}(R) = \frac{V_{obs}^2(R)}{R}

This can be calculated in the data rather simply by averaging over the value of :math:`g_{obs}(R)` for all star/gas particles within a bin at :math:`R`.

Baryonic acceleration
=====================

The expected (or baryonic) acceleration is found by calculating the expected gravitational force given the mass of stars and gas within some radius, or alternatively by solving for the gradient of the gravitational potential due to stars and gas from the Poisson equation. As we have masses of stars and gas at different radii, we here use the force due to the sum of masses within the radius of interest:

.. math::

    M_{bar}(r < R) = \sum_{r_i < R} M_{stars}(r_i) + M_{gas}(r_i)

    g_{bar}(R) = \frac{G M_{bar}(r < R)}{R^2}

.. automodule:: calculate.calc_accel
   :members:
   :undoc-members:
