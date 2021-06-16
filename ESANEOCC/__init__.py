"""

@author: C. Álvaro Arroyo
@contact: carlos.arroyo@deimos-space.com

European Space Agency (ESA)

Created on 16 Jun. 2021

"""
from astropy import config as _config

class Conf(_config.ConfigNamespace):
    """
    Configuration parameters for 'ESANEOCC'
    """

    BASE_URL = _config.ConfigItem('https://neo.ssa.esa.int/'
                                  'PSDB-portlet/download?file=')

    PROPERTIES_URL = _config.ConfigItem('https://neo.ssa.esa.int/'
                                        'search-for-asteroids?tab='
                                        'physprops&des=')

    EPHEM_URL = _config.ConfigItem('https://neo.ssa.esa.int/'
                                   'PSDB-portlet/ephemerides?des=')

    SUMMARY_URL = _config.ConfigItem('https://neo.ssa.esa.int/'
                                     'search-for-asteroids?sum=1&des=')

    TIMEOUT = 60

conf = Conf()

from .core import neocc, ESAneoccClass

__all__ = ['neocc', 'ESAneoccClass', 'Conf', 'conf']
