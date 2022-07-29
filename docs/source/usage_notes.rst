.. _Usage :

Usage Notes
===========

Execution and the BIDS format
-----------------------------
The *bidsMReye* workflow takes as principal input the path of the dataset
that is to be processed.
.. The input dataset is required to be in valid :abbr:`BIDS (Brain Imaging Data
.. Structure)` format, and it must include at least one T1w structural image and
.. (unless disabled with a flag) a BOLD series.
.. We highly recommend that you validate your dataset with the free, online
.. `BIDS Validator <http://bids-standard.github.io/bids-validator/>`_.

The exact command to run *bidsMReye* depends on the :ref:`installation` method.
The common parts of the command follow the `BIDS-Apps
<https://github.com/BIDS-Apps>`_ definition.
Example: ::

    bidsmreye data/bids_root/ out/ participant

Further information about BIDS and BIDS-Apps can be found at the
`NiPreps portal <https://www.nipreps.org/apps/framework/>`__.

Command-Line Arguments
----------------------
.. argparse::
   :prog: bidsmreye
   :module: bidsmreye.run
   :func: common_parser
