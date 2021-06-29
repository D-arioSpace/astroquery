.. NEOCC_lib documentation master file, created by
   sphinx-quickstart on Fri Feb  5 08:37:43 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

##########################################
ESA NEOCC Portal Python Interface Library
##########################################

This is the documentation for the ESA NEOCC Portal Python interface library.

===============
Introduction
===============

ESA NEOCC Portal Python interface library makes the data that `ESA NEOCC <http://neo.ssa.esa.int/>`_
provides easily accessible through a Python program.

The main functionality of this library is to allow a programmer to easily retrieve:

* All the NEAs
* Other data that the NEOCC provides (risk list, close approach list, etc.)
* All basic and advanced information regarding a NEA
* An ephemeris service for NEAs


.. toctree::
   :numbered:
   :maxdepth: 3
   :caption: Contents:

===============
Installation
===============

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
the dependencies is the following:

.. code-block:: bash

    $ pip install . --upgrade-strategy eager

In this case, dependencies are upgraded regardless of whether the currently
installed version satisfies the requirements of the upgraded package(s).

If you want to make sure none of your existing dependencies get upgraded, you
can also do::

   $ pip install . --no-deps

Note that, in the latter case, it is possible that some library functionalities
will not work if the dependencies do not satisfy the Requirements.

===============
Requirements
===============

ESA NEOCC Portal Python Interface Library works with Python 3.

The following packages are required for the library installation & use:

* `astropy <https://pypi.org/project/astropy/>`_ = 4.2.1
* `beautifulsoup4 <https://pypi.org/project/beautifulsoup4/>`_ = 4.9.3
* `lxml <https://pypi.org/project/lxml/>`_ = 4.6.3
* `pandas <https://pypi.org/project/pandas/>`_ = 1.2.4
* `parse <https://pypi.org/project/parse/>`_ = 1.19.0
* `requests <https://pypi.org/project/requests/>`_ = 2.25.1
* `scipy <https://pypi.org/project/scipy/>`_ = 1.6.3

For tests the following packages are required:

* `pytest <https://pypi.org/project/pytest/>`_

===============
Modules
===============

-------------------
ESANEOCC.core
-------------------
.. automodule:: ESANEOCC.core
   :members:

-------------------
ESANEOCC.lists
-------------------
.. automodule:: ESANEOCC.lists
   :members:

-------------------
ESANEOCC.tabs
-------------------
.. automodule:: ESANEOCC.tabs
   :members:

==============================
Library Examples
==============================

==============================
How to export data
==============================

-------------------
To JSON
-------------------

Most of the data obtained from ESANEOCC Python Interface is collected as *pandas.Series* or *pandas.DataFrame* and, therefore
it can be easily converted to JSON format. Here is a template that you may use in Python to export pandas DataFrame to JSON:

>>> df.to_json(r'Path to store the exported JSON file\File Name.json')

The complete use of this function can be found in `pandas.DataFrame.to_json <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html>`_, 
where different examples are shown. It also shows how to obtain the different types of JSON files.

>>> from ESANEOCC import neocc
>>> import json
>>> ast = neocc.query_object(name='99942', tab='physical_properties')
>>> ast.physical_properties
                  Property    Values Unit Source
0           Rotation Period     30.56    h    [4]
1                   Quality         3    -    [4]
2                 Amplitude       1.0  mag    [4]
3        Rotation Direction     RETRO    -    [1]
4              Spinvector L       250  deg    [1]
5              Spinvector B   -7.50E1  deg    [1]
6                  Taxonomy      S/Sq    -    [2]
7            Taxonomy (all)  Sq,Scomp    -    [3]
8    Absolute Magnitude (H)     19.09  mag    [5]
9       Slope Parameter (G)      0.24  mag    [1]
10                   Albedo     0.285    -    [8]
11                 Diameter       375    m    [9]
12  Color Index Information     0.362  R-I   [10]
13                Sightings   Radar R    -   [11]
>>> ast_json = ast.physical_properties.to_json(orient='split')
>>> parsed = json.loads(ast_json)
>>> print(json.dumps(parsed, indent=4))
{
    "columns": [
        "Property",
        "Values",
        "Unit",
        "Source"
    ],
    "index": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13
    ],
    "data": [
        [
            "Rotation Period",
            "30.56",
            "h",
            "[4]"
        ],
        [
            "Quality",
            "3",
            "-",
            "[4]"
        ],
        [
            "Amplitude",
            "1.0",
            "mag",
            "[4]"
        ],
        [
            "Rotation Direction",
            "RETRO",
            "-",
            "[1]"
        ],
        [
            "Spinvector L",
            "250",
            "deg",
            "[1]"
        ],
        [
            "Spinvector B",
            "-7.50E1",
            "deg",
            "[1]"
        ],
        [
            "Taxonomy",
            "S/Sq",
            "-",
            "[2]"
        ],
        [
            "Taxonomy (all)",
            "Sq,Scomp",
            "-",
            "[3]"
        ],
        [
            "Absolute Magnitude (H)",
            "19.09",
            "mag",
            "[5]"
        ],
        [
            "Slope Parameter (G)",
            "0.24",
            "mag",
            "[1]"
        ],
        [
            "Albedo",
            "0.285",
            "-",
            "[8]"
        ],
        [
            "Diameter",
            "375",
            "m",
            "[9]"
        ],
        [
            "Color Index Information",
            "0.362",
            "R-I",
            "[10]"
        ],
        [
            "Sightings",
            "Radar R",
            "-",
            "[11]"
        ]
    ]
}

>>> ast_json = ast.physical_properties.to_json(r'Path to store the exported JSON file/ast.json',orient='split')

----------------------
To Tables (VO Tables)
----------------------

Virtual Observatory (VO) tables are a new format developed by the International Virtual Observatory Alliance to store one or more tables. 
This format is included within `ATpy <https://atpy.readthedocs.io/en/stable/index.html>`_ library. However, most of ATpy’s functionalities has now been incorporated 
into Astropy library and the developers recommended to use the `Astropy Tables <https://docs.astropy.org/en/stable/table/>`_

Astropy documentation details how to interface with the Pandas library, i.e., how to convert data in *pandas.Series* or *pandas.DataFrame* formats into Astropy Tables and vice versa.

>>> from ESANEOCC import neocc
>>> from astropy.table import Table
>>> ast = neocc.query_object(name='99942', tab='physical_properties')
>>> ast.physical_properties
                  Property    Values Unit Source
0           Rotation Period     30.56    h    [4]
1                   Quality         3    -    [4]
2                 Amplitude       1.0  mag    [4]
3        Rotation Direction     RETRO    -    [1]
4              Spinvector L       250  deg    [1]
5              Spinvector B   -7.50E1  deg    [1]
6                  Taxonomy      S/Sq    -    [2]
7            Taxonomy (all)  Sq,Scomp    -    [3]
8    Absolute Magnitude (H)     19.09  mag    [5]
9       Slope Parameter (G)      0.24  mag    [1]
10                   Albedo     0.285    -    [8]
11                 Diameter       375    m    [9]
12  Color Index Information     0.362  R-I   [10]
13                Sightings   Radar R    -   [11]
>>> ast_astropy = Table.from_pandas(ast.physical_properties)
>>> ast_astropy
<Table length=14>
        Property         Values  Unit Source
         str23            str8   str3  str4 
----------------------- -------- ---- ------
        Rotation Period    30.56    h    [4]
                Quality        3    -    [4]
              Amplitude      1.0  mag    [4]
     Rotation Direction    RETRO    -    [1]
           Spinvector L      250  deg    [1]
           Spinvector B  -7.50E1  deg    [1]
               Taxonomy     S/Sq    -    [2]
         Taxonomy (all) Sq,Scomp    -    [3]
 Absolute Magnitude (H)    19.09  mag    [5]
    Slope Parameter (G)     0.24  mag    [1]
                 Albedo    0.285    -    [8]
               Diameter      375    m    [9]
Color Index Information    0.362  R-I   [10]
              Sightings  Radar R    -   [11]

Visit `Interfacing with the Pandas Package <https://docs.astropy.org/en/stable/table/pandas.html>`_ for further information.

##########################################
ESANEOCC Change Log
##########################################

==============================
Version 1.3.1
==============================

----------------------
Bug Fixes
----------------------
* Fixed bug where *risk_list* and *risk_list_special* were not displaying Torino Scale and Velocity.

==============================
Version 1.3
==============================

----------------------
Changes
----------------------

* `astropy <https://pypi.org/project/astropy/>`_ library has been added as required package.
* *neocc.py* module has been renamed to *core.py* in order to be consistent with Astroquery.
* *core.py* has been modified in order to be consistent with Astroquery (main class and static methods).
* Dates/time columns or data have been converted to datetime ISO format.
* Abbreviations contain now complete expressions (e.g., *close_appr_upcoming* to *close approaches_upcoming*)
* The documentation explains how to obtain JSON and Table format from data retrieved from the library.
* Time performance improvement in obtaining physical properties.

----------------------
Bug Fixes
----------------------

* Fixed two-points ephemerides generation fails
* Fixed physical properties generation for objects with Area-to-mass ratio and Yarkovsky parameter.
* Fixed orbit properties generation for objects with Area-to-mass ratio and Yarkovsky parameter.
