.. _Usage :

Usage Notes
===========

Execution and the BIDS format
-----------------------------
The *bidsMReye* workflow takes as principal input the path of the dataset
that is to be processed.


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
   :module: bidsmreye.bidsmreye
   :func: common_parser
