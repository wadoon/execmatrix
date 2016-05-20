execmatrix
=============

*Exec*ute *Matrix* provides an easy way to benchmark a bunch of programs under
a combination of possible environments. It measures the runtime out-of-the-box
and provides various facility for documentation purpose.

    License: MIT
    Author: Alexaner Weigl <weigl@kit.edu>

How to use
------------

1. Download `execmatrix.py`.
1. Create a Python script that uses `from execmatrix import *` and creates an
    `Environment` and `Runner` object. `Environment` objects describe the
    possible combinations of environments. `Runner` executes the given programs
    under each setting from the environment.
1. Call your script.


TODO
-----



Changelog
-----------

* *[0.1]* -- 2016-05-20
  * First release
