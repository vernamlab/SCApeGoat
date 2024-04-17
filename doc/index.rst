SCApe Goat - Side Channel Analysis Library
===================================

Purpose
-------
Many years of cryptographic research have focused on the software security of different encryption algorithms.
One of the most well-known encryption algorithms, AES-128, would require billions of years to guess its 128-bit encryption key.
However, there exist hardware attacks that could extract this cryptography key in mere hours. A side-channel attack can use the
information received from device power consumption and electromagnetic emanation to guess a cryptographic key with immense accuracy.
Therefore, the field of side-channel analysis is of utmost importance if engineers want to design cryptographic devices that can withstand
even the most intense side-channel attacks. One of the research topics at Worcester Polytechnic Institute's Vernam Lab involves side-channel
analysis attacks and defense. In attacking encryption algorithms with different side-channel techniques, researchers can draw conclusions
about the security of different cryptographic implementations and develop better defenses against such attacks. However, Vernam Lab and
Worcester Polytechnic Institute as a whole, lack a unified repository of information and tools to help with side-channel analysis research
and education. The lab has access to the specialized equipment needed to conduct SCA research, however, there does not exist a
standardized interface for side-channel data collection, analysis, and data storage that the lab uses to conduct research.
Therefore, this necessitates an accessible set of tools that allow researchers and students alike to learn and contribute
to the ever-growing field of security analysis of side-channel attacks.

Library Features
---------------------
.. toctree::
   :maxdepth: 3

   fileformat.rst
   cwscope.rst
   metrics.rst
   leakagemodels.rst
   dpa.rst
   lecroy.rst