.. NEOCC_lib documentation master file, created by
   sphinx-quickstart on Fri Feb  5 08:37:43 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ESA NEOCC Portal Python Interface Library
=========================================
This is the documentation for the ESA NEOCC Portal Python interface library.

Introduction
-------------------
ESA NEOCC Portal Python interface library makes the data that `ESA NEOCC <http://neo.ssa.esa.int/>`_
provides easily accessible through a Python program.

The main functionality of this library is to allow a programmer to easily retrieve:

* All the NEAs
* Other data that the NEOCC provides (risk list, close approach list, etc.)
* All basic and advanced information regarding a NEA
* An ephemeris service for NEAs

The complete library documentation can be found in PDF file.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Installation
-------------------
The library is contained in ESANEOCC folder. In order to install the library:

#. Navigate to the proper directory where the *setup.py* is located.
#. The installation is doable through *pip install* command:

.. code-block:: bash

    $ pip install .

#. Additionaly, the following command can be applied to install directly the requirements:

.. code-block:: bash

    $ pip install . && pip install -r requirements.txt

Requirements
-------------------
ESA NEOCC Portal Python Interface Library works with Python 3.

The following packages are required for the library installation & use:

* `astropy <https://pypi.org/project/astropy/>`_ = 4.3.1
* `beautifulsoup4 <https://pypi.org/project/beautifulsoup4/>`_ = 4.10.0
* `lxml <https://pypi.org/project/lxml/>`_ = 4.6.3
* `pandas <https://pypi.org/project/pandas/>`_ = 1.3.4
* `parse <https://pypi.org/project/parse/>`_ = 1.19.0
* `requests <https://pypi.org/project/requests/>`_ = 2.26.0
* `scipy <https://pypi.org/project/scipy/>`_ = 1.7.1

For tests the following packages are required:

* `pytest <https://pypi.org/project/pytest/>`_ = 6.2.1
* `astroquery <https://pypi.org/project/astroquery/>`_ = 0.4.3

