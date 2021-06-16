from ESANEOCC import neocc
import io
import requests
import pandas as pd
from bs4 import BeautifulSoup
from parse import parse
from datetime import datetime, timedelta
import logging
import time
from multiprocessing import Process
import asyncio
import concurrent.futures
from multiprocessing.pool import ThreadPool
from astropy.table import QTable

start_time = time.time()

BASE_URL = 'https://neo.ssa.esa.int/PSDB-portlet/download?file='
PROPERTIES_URL = 'https://neo.ssa.esa.int/search-for-asteroids?tab=physprops&des='


contents = requests.get('https://dummyimage.com/300x250/000/fff.png', timeout=90).content
print(contents)
# name1 = 'impactedObjectsList.txt'
# url1 = BASE_URL + str(name1)
# data_list = requests.get(url1).content
# data_list_d = io.StringIO(data_list.decode('utf-8'))
# a = pd.read_(data_list_d, header=None, delim_whitespace=True)
# print(a)

a = neocc.query_list(list_name='close_encounter')
print(a.info())
# a['Date'] = datetime.strptime(a['Date'][0][0], '%Y/%m/%d')
# a['Date'][0][1] = timedelta(days=(float(a['Date'][0][1])/1e5))
# a['Date'][0][0] = a['Date'][0][0]+a['Date'][0][1]
# a['Date'][0] = a['Date'][0][0]
# print(a['Date'][0])

# df = neocc.query_object(name='2009BD', tab='physical_properties')
# print(df.physical_properties)
# a.to_json(r'/home/caap/Desktop/ESANEOCC/neocc-python-interface/test/433.json', orient="columns")
# t2 = QTable.from_pandas(a)
# print(t2.info)
# print(a.physical_properties)
# # Get data from URL
# data_list = requests.get(url1).content
# # Decode the data using UTF-8
# data_list_d = io.StringIO(data_list.decode('utf-8'))
# # Read data as csv
# neocc_lst = pd.read_csv(data_list_d, header=None)

# # Remove redundant white spaces
# neocc_lst = neocc_lst[0].str.strip().replace(r'\s+', ' ',
#                                              regex=True)\
#                                     .str.replace('# ', '')
# print(neocc_lst)

# name2 = 'monthly_update.done'
# url2 = BASE_URL + str(name2)
# # Get data from URL
# data_list2 = requests.get(url2).content
# # Decode the data using UTF-8
# data_list_d2 = io.StringIO(data_list2.decode('utf-8'))
# # Read data as csv
# neocc_lst2 = pd.read_csv(data_list_d2, header=None)
# print(neocc_lst2[0])

# name3 = 'close_encounter2.txt'
# url3 = BASE_URL + str(name3)
# # Get data from URL
# data_list3 = requests.get(url3).content
# # Decode the data using UTF-8
# data_list_d3 = io.StringIO(data_list3.decode('utf-8'))
# # Read data as csv
# neocc_lst3 = pd.read_csv(data_list_d3, skiprows=[0,2], sep='|', engine='python')
# neocc_lst3.columns = neocc_lst3.columns.str.strip()
# neocc_lst3['Planet'] = neocc_lst3['Planet'].str.strip()
# neocc_lst3['Name/desig'] = neocc_lst3['Name/desig'].str.strip()
# neocc_lst3['Date'] = neocc_lst3['Date'].str.strip()
# print(neocc_lst3)
