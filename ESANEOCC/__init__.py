"""

@author: C. Álvaro Arroyo
@contact: carlos.arroyo@deimos-space.com

European Space Agency (ESA)

Created on 16 Jun. 2021
Last update 02 Nov. 2021

"""
import os
from astropy import config as _config

class Conf(_config.ConfigNamespace):
    """
    Configuration parameters for 'ESANEOCC'
    """
    BASE_URL = 'https://' + os.getenv('NEOCC_PORTAL_IP')

    API_URL = _config.ConfigItem(BASE_URL +
                                 '/PSDB-portlet/download?file=')

    EPHEM_URL = _config.ConfigItem(BASE_URL +
                                   '/PSDB-portlet/ephemerides?des=')

    SUMMARY_URL = _config.ConfigItem(BASE_URL +
                                     '/search-for-asteroids?sum=1&des=')

    TIMEOUT = 60

conf = Conf()

from .core import neocc, ESAneoccClass

__all__ = ['neocc', 'ESAneoccClass', 'Conf', 'conf']
