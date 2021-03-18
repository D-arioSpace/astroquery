from ESANEOCC import neocc
import pandas as pd
import urllib.request
import string
import random
import requests
import io

def test_get_list_url():
    """!
    """
    lists = ["nea_list", "risk_list_n", "risk_list_s", "clo_app_u",
    "clo_app_r", "pri_list_n", "pri_list_f"]
    lists_dict = {
        "nea_list": 'allneo.lst',
        "risk_list_n": 'esa_risk_list',
        "risk_list_s": 'esa_special_risk_list',
        "clo_app_u": 'esa_upcoming_close_app',
        "clo_app_r": 'esa_recent_close_app',
        "pri_list_n": 'esa_priority_neo_list',
        "pri_list_f": 'esa_faint_neo_list',
        }
    for element in lists:
        assert neocc.lists.get_list_url(element) == lists_dict[element]

def test_parse_nea():
    """!
    """
    base_url = 'http://neo.ssa.esa.int/PSDB-portlet/download?file='
    url = neocc.lists.get_list_url('nea_list')
    # Get data from URL
    data_list = requests.get(base_url + url).content

    # Decode the data using UTF-8
    data_list_d = io.StringIO(data_list.decode('utf-8'))

    assert type(neocc.lists.parse_nea(data_list_d)) == pd.Series
    
def test_parse_risk():
    """!
    """
    base_url = 'http://neo.ssa.esa.int/PSDB-portlet/download?file='
    risks = ['risk_list_n', 'risk_list_s']
    risk_columns = ['Object Name', 'Diameter [m]', 'Date/Time', 'IP max', 'PS max', 'TS',
       'Vel [km/s]', 'Years', 'IP cum', 'PS cum']
    for element in risks:
        url = neocc.lists.get_list_url(element)
        # Get data from URL
        data_list = requests.get(base_url + url).content

        # Decode the data using UTF-8
        data_list_d = io.StringIO(data_list.decode('utf-8'))
        output = neocc.lists.parse_risk(data_list_d)
        assert type(output) == pd.DataFrame

def test_parse_clo():
    """!
    """
    base_url = 'http://neo.ssa.esa.int/PSDB-portlet/download?file='
    clos = ['clo_app_u', 'clo_app_r']
    for element in clos:
        url = neocc.lists.get_list_url(element)
        # Get data from URL
        data_list = requests.get(base_url + url).content

        # Decode the data using UTF-8
        data_list_d = io.StringIO(data_list.decode('utf-8'))

        assert type(neocc.lists.parse_clo(data_list_d)) == pd.DataFrame

def test_parse_pri():
    """!
    """
    base_url = 'http://neo.ssa.esa.int/PSDB-portlet/download?file='
    clos = ['pri_list_n', 'pri_list_f']
    for element in clos:
        url = neocc.lists.get_list_url(element)
        # Get data from URL
        data_list = requests.get(base_url + url).content

        # Decode the data using UTF-8
        data_list_d = io.StringIO(data_list.decode('utf-8'))

        assert type(neocc.lists.parse_pri(data_list_d)) == pd.DataFrame

def test_parse_list():
    """!
    """
    base_url = 'http://neo.ssa.esa.int/PSDB-portlet/download?file='
    lists = ["nea_list", "risk_list_n", "risk_list_s", "clo_app_u",
    "clo_app_r", "pri_list_n", "pri_list_f"]
    lists_dict = {
        "nea_list": pd.Series,
        "risk_list_n": pd.DataFrame,
        "risk_list_s": pd.DataFrame,
        "clo_app_u": pd.DataFrame,
        "clo_app_r": pd.DataFrame,
        "pri_list_n": pd.DataFrame,
        "pri_list_f": pd.DataFrame,
        }
    for element in lists:
        url = neocc.lists.get_list_url(element)
        # Get data from URL
        data_list = requests.get(base_url + url).content

        # Decode the data using UTF-8
        data_list_d = io.StringIO(data_list.decode('utf-8'))
        assert type(neocc.lists.parse_list(element, data_list_d)) == lists_dict[element]
    
