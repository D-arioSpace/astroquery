from ESANEOCC import neocc
import io
import requests
import pandas as pd
from bs4 import BeautifulSoup
from parse import parse
from datetime import datetime
import logging
import time

#TODO include modes of testing
#TODO include requests all the tabs
#TODO include summary.log and try and except to check every set

start_time = time.time()
asteroid_set = neocc.query_list(list_name='nea_list')

logging.basicConfig(filename="physical_properties.log", level=logging.INFO)

for asteroid in asteroid_set:
        try:
                ast = neocc.query_object(name=asteroid, tab='physical_properties')
                #, observatory='500', start='2019-05-08 01:30', stop='2019-05-23 01:30', step='1', step_unit='days')
                logging.info('Object ' + str(asteroid) + ' gets physical properties')
        except:
                logging.error('Object ' + str(asteroid) + ' does NOT get physical properties file')
                continue

print("--- %s seconds ---" % (time.time() - start_time))