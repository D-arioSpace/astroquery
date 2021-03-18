from ESANEOCC import neocc
import io
import requests
import pandas as pd
from bs4 import BeautifulSoup
from parse import parse
from datetime import datetime
import logging
import time



start_time = time.time()
asteroid_set = neocc.query_list(list_name='nea_list')

logging.basicConfig(filename="logephemerides.log", level=logging.INFO)

for asteroid in asteroid_set:
        try:
                orbit_prop = neocc.query_object(name=asteroid, tab='ephemerides', observatory='500', start='2019-05-08 01:30', stop='2019-05-23 01:30', step='1', step_unit='days')
                logging.info('Asteroid ' + str(asteroid) + ' get ephemerides file')
        except:
                logging.error('Asteroid ' + str(asteroid) + ' does NOT get ephemerides file')
                continue

print("--- %s seconds ---" % (time.time() - start_time))