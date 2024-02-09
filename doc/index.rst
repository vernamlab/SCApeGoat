SCApe Goat - Side Channel Analysis Library
===================================

Purpose
-------
One of the research topics at Worcester Polytechnic Institute's Vernam Lab involves side-channel analysis attacks and defence.
In attacking encryption algorithms with different side channel techniques, researchers are able to draw conclusions about the
security of different cryptographic implementations and develop better defences against such attacks. However, Vernam Lab and
Worcester Polytechnic Institute as a whole, lack a unified repository of information and tools to help with side-channel analysis
research and education. The lab has access to the specialized equipment needed to conduct SCA research, however, there does not
exist a standardized interface for side-channel data collection, analysis, and data storage that the lab uses to conduct research.
Therefore, this necessitates an accessible set of tools that allow for researchers and students alike to learn and contribute to
the ever growing field of security analysis of side-channel attacks.

Installation
------------
This set of side channel analysis tools was developed in Python and can be installed just like any Python library.

Library Documentation
---------------------
.. toctree::
   :maxdepth: 3

   fileformat.rst
   scope.rst
   metrics.rst
   leakagemodels.rst
   about_project.rst