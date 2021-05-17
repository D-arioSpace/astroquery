.. NEOCC_lib documentation master file, created by
   sphinx-quickstart on Fri Feb  5 08:37:43 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
##########################################
ESA NEOCC Portal Python Interface Library
##########################################

This is the documentation for the ESA NEOCC Portal Python interface library.

***************
Introduction
***************

ESA NEOCC Portal Python interface library makes the data that `ESA NEOCC <http://neo.ssa.esa.int/>`_
provides easily accessible through a Python program.

The main functionality of this library is to allow a programmer to easily retrieve:

* All the NEAs
* Other data that the NEOCC provides (risk list, close approach list, etc.)
* All basic and advanced information regarding a NEA
* An ephemeris service for NEAs


.. toctree::
   :maxdepth: 3
   :caption: Contents:

***************
Installation
***************

The library is contained in ESANEOCC folder. In order to install the library:

#. Navigate to the proper directory where the *setup.py* is located.
#. The installation is doable through *pip install* command:

.. code-block:: bash

    $ pip install .

.. note:: 

   Consider installing ``ESANEOCC`` library into a `virtualenv
   <https://docs.python.org/3/tutorial/venv.html>`_. This will avoid problems
   with previous installed dependencies.

The previous installation will install the library and its dependencies, but
the dependencies will not be updated in case they are previously installed.
In order to asssure that the packages version is the one determined in the
Requirements the following command must be written:

.. code-block:: bash

    $ pip install -r requirements.txt

This can be done in one command line:

.. code-block:: bash

    $ pip install . && pip install -r requirements.txt

.. warning::

   The previous command will force to install the package version of the
   requirements. This will upgrade/downgrade the version of any previous
   installed package that ``ESANEOCC`` library depends on.

Another installation method that will install the library and will update
the dependencies is the follwing:

.. code-block:: bash

    $ pip install . --upgrade-strategy eager

In this case, dependencies are upgraded regardless of whether the currently
installed version satisfies the requirements of the upgraded package(s).

If you want to make sure none of your existing dependencies get upgraded, you
can also do::

   $ pip install . --no-deps

Note that, in the latter case, it is possible that some library functionalities
will not work if the dependencies do not satisfy the Requirements.

***************
Requirements
***************

ESA NEOCC Portal Python Interface Library works with Python 3.

The following packages are required for the library installation & use:

* `beautifulsoup4 <https://pypi.org/project/beautifulsoup4/>`_ = 4.9.3
* `lxml <https://pypi.org/project/lxml/>`_ = 4.6.3
* `pandas <https://pypi.org/project/pandas/>`_ = 1.2.4
* `parse <https://pypi.org/project/parse/>`_ = 1.19.0
* `requests <https://pypi.org/project/requests/>`_ = 2.25.1
* `scipy <https://pypi.org/project/scipy/>`_ = 1.6.3

For tests the following packages are required:

* `pytest <https://pypi.org/project/pytest/>`_

***************
Modules
***************

ESANEOCC.neocc
-------------------
.. automodule:: ESANEOCC.neocc
   :members:

ESANEOCC.lists
-------------------
.. automodule:: ESANEOCC.lists
   :members:

ESANEOCC.tabs
-------------------
.. automodule:: ESANEOCC.tabs
   :members:
