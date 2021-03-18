# -*- coding: utf-8 -*-
"""
This module contains all the methods required to request the list data,
obtain it from the ESA NEOCC portal and parse it to show it properly.

* Project: NEOCC portal Python interface
* Property: European Space Agency (ESA)
* Developed by: Elecnor Deimos
* Author: C. Álvaro Arroyo Parejo
* Issue: 1.0
* Date: 26-02-2021
* Purpose: Module which request and parse list data from ESA NEOCC
* Module: lists.py
* History:

========   ===========   ================
Version    Date          Change History
========   ===========   ================
1.0        26-02-2021    Initial version
========   ===========   ================

© Copyright [European Space Agency][2021]
All rights reserved
"""

import io
from datetime import datetime as dt
import time
import pandas as pd
import requests

# Define the base URL for NEOCC
BASE_URL = 'http://neo.ssa.esa.int/PSDB-portlet/download?file='


def get_list_url(list_name):
    """Get url from requested list name.

    Parameters
    ----------
    list_name : str
        Name of the requested list. Valid names are: *nea_list,
        risk_list, risk_list_special, close_appr_upcoming,
        close_appr_recent, priority_list, priority_list_faint*.

    Returns
    -------
    url : str
        Final URL string.

    Raises
    ------
    KeyError
        If the requested list_name is not in the dictionary
    """
    # Define the parameters of each list
    lists_dict = {
        "nea_list": 'allneo.lst',
        "risk_list": 'esa_risk_list',
        "risk_list_special": 'esa_special_risk_list',
        "close_appr_upcoming": 'esa_upcoming_close_app',
        "close_appr_recent": 'esa_recent_close_app',
        "priority_list": 'esa_priority_neo_list',
        "priority_list_faint": 'esa_faint_neo_list',
        }
    # Raise error is input is not in dictionary
    if list_name not in lists_dict:
        raise KeyError('Valid list names are nea_list, risk_list, '
                       'risk_list_special, close_appr_upcoming, '
                       'close_appr_recent, priority_list, '
                       'priority_list_faint')
    # Get url
    url = lists_dict[list_name]

    return url


def get_list_data(url, list_name):
    """Get requested parsed list from url.

    Parameters
    ----------
    list_name : str
        Name of the requested list.
    url : str
        URL of the requested list.

    Returns
    -------
    neocc_lst : *pandas.Series* or *pandas.DataDrame*
        Data frame which contains the data of the requested list.
    """
    # Get data from URL
    data_list = requests.get(BASE_URL + url).content

    # Decode the data using UTF-8
    data_list_d = io.StringIO(data_list.decode('utf-8'))

    # Parse decoded data
    neocc_list = parse_list(list_name, data_list_d)

    return neocc_list


def get_dec_year(date):
    """Get decimal year from a date.

    Parameters
    ----------
    date : datetime
        Date in YYYY/MM/DD.dddd format.

    Returns
    -------
    decimal_year : float64
        Date in decimal year format YYYY.yyyyyy.
    """
    def since_epoch(date):
        """Convert time struct to time in seconds passed since epoch in
        local time

        Parameters
        ----------
         date : datetime
            Name of the requested list.

        Returns
        -------
        epoch_seconds : float64
            Seconds passed since epoch in local time.
        """
        epoch_seconds = time.mktime(date.timetuple())
        return epoch_seconds

    # Get current year and dt from init and end
    year = date.year
    year_start = dt(year=year, month=1, day=1)
    next_year = dt(year=year+1, month=1, day=1)

    # Get fraction of year from time elapsed and year duration
    year_elapsed = since_epoch(date) - since_epoch(year_start)
    year_duration = since_epoch(next_year) - since_epoch(year_start)
    fraction = year_elapsed/year_duration

    # Compute decimal year
    decimal_year = year + fraction

    return decimal_year


def parse_list(list_name, data_byte_d):
    """Switch function to select parse method.

    Parameters
    ----------
    list_name : str
        Name of the requested list.
    data_byte_d : object
        Decoded StringIO object.

    Returns
    -------
    neocc_lst : *pandas.Series* or *pandas.DataFrame*
        Data frame with data from the list parsed.
    """
    # Parse data for each type of list
    if list_name == "nea_list":
        neocc_lst = parse_nea(data_byte_d)

    elif list_name in ("risk_list", "risk_list_special"):
        neocc_lst = parse_risk(data_byte_d)

    elif list_name in ("close_appr_upcoming", "close_appr_recent"):
        neocc_lst = parse_clo(data_byte_d)

    elif list_name in ("priority_list", "priority_list_faint"):
        neocc_lst = parse_pri(data_byte_d)

    return neocc_lst


def parse_nea(data_byte_d):
    """Parse and arrange all NEA list.

    Parameters
    ----------
    data_byte_d : object
        Decoded StringIO object.
    Returns
    -------
    neocc_lst : *pandas.Series* or *pandas.DataFrame*
        Data frame with NEA list data parsed.
    """
    # Read data as csv
    neocc_lst = pd.read_csv(data_byte_d, header=None)

    # Remove redundant white spaces
    neocc_lst = neocc_lst[0].str.strip().replace(r'\s+', ' ',
                                                 regex=True)

    return neocc_lst


def parse_risk(data_byte_d):
    """Parse and arrange risk lists.

    Parameters
    ----------
    data_byte_d : object
        Decoded StringIO object.

    Returns
    -------
    neocc_lst : *pandas.Series* or *pandas.DataFrame*
        Data frame with risk list data parsed.
    """
    # Read data as csv
    neocc_lst = pd.read_csv(data_byte_d, sep='|', skiprows=[3],
                            header=2)

    # Remove redundant white spaces
    neocc_lst.columns = neocc_lst.columns.str.strip()
    neocc_lst = neocc_lst.replace(r'\s+', ' ', regex=True)
    df_obj = neocc_lst.select_dtypes(['object'])
    neocc_lst[df_obj.columns] = df_obj.apply(lambda x:
                                             x.str.strip())

    # Rename columns
    col_dict = {"Num/des.       Name": 'Object Name',
                "m": 'Diameter in m',
                "Vel km/s": 'Vel in km/s'}
    neocc_lst.rename(columns=col_dict, inplace=True)

    # Remove last column
    neocc_lst = neocc_lst.drop(neocc_lst.columns[-1], axis=1)

    # Convert column with date to datetime variable
    neocc_lst['Date/Time'] = pd.to_datetime(neocc_lst['Date/Time'])
    # Convert from datetime to YYYY.yyyyyy
    neocc_lst['Date/Time'] = neocc_lst['Date/Time'].map(get_dec_year)

    return neocc_lst


def parse_clo(data_byte_d):
    """Parse and arrange close approaches lists.

    Parameters
    ----------
    data_byte_d : object
        Decoded StringIO object.
    Returns
    -------
    neocc_lst : *pandas.Series* or *pandas.DataFrame*
        Data frame with close approaches list data parsed.
    """
    # Read data as csv
    neocc_lst = pd.read_csv(data_byte_d, sep='|', skiprows=[3],
                            header=2)
    # Check if there is server internal error
    if len(neocc_lst.columns) <= 1:
        raise ConnectionError('Internal Server Error. Please try '
                              'again.')
    # Remove redundant white spaces
    neocc_lst.columns = neocc_lst.columns.str.strip()
    neocc_lst = neocc_lst.replace(r'\s+', ' ', regex=True)
    df_obj = neocc_lst.select_dtypes(['object'])
    neocc_lst[df_obj.columns] = df_obj.apply(lambda x:
                                             x.str.strip())

    # Remove last column
    neocc_lst = neocc_lst.drop(neocc_lst.columns[-1], axis=1)

    # Rename columns
    neocc_lst.columns = ['Object Name', 'Date',
                         'Miss Distance in km', 'Miss Distance in au',
                         'Miss Distance in LD', 'Diameter in m',
                         '*=Yes', 'H', 'Max Bright',
                         'Rel. vel in km/s']

    # Convert column with date to datetime variable
    neocc_lst['Date'] = pd.to_datetime(neocc_lst['Date'])
    # Convert from datetime to YYYY.yyyyyy
    neocc_lst['Date'] = neocc_lst['Date'].map(get_dec_year)

    return neocc_lst


def parse_pri(data_byte_d):
    """Parse and arrange priority lists.

    Parameters
    ----------
    data_byte_d : object
        Decoded StringIO object.
    Returns
    -------
    neocc_lst : *pandas.Series* or *pandas.DataFrame*
        Data frame with priority list data parsed.
    """
    # Read as txt
    neocc_lst = pd.read_fwf(data_byte_d, skiprows=1, sep=' ',
                            header=None)

    # Merge second and first columns into 1
    neocc_lst[1] = neocc_lst[1] + " " + neocc_lst[2]
    neocc_lst = neocc_lst.drop(columns=2)
    # Removing white space from object number and designator
    neocc_lst[1] = neocc_lst[1].replace(r'\s+', '',
                                        regex=True)

    # Reindex columns
    neocc_lst.columns = range(neocc_lst.shape[1])

    # Remove quotes
    neocc_lst = neocc_lst.replace(to_replace='\"', value='',
                                  regex=True)

    # Convert column with date to datetime variable
    neocc_lst[7] = pd.to_datetime(neocc_lst[7])

    # Convert from datetime to YYYY.yyyyyy
    # False positive. pylint: disable=E1101
    neocc_lst[7] = neocc_lst[7].map(get_dec_year)

    # Rename columns
    neocc_lst.columns = ['Priority', 'Object',
                         'R.A. in arcsec', 'Decl. in deg',
                         'Elong. in deg', 'V in mag', 'Sky uncert.',
                         'End of Visibility']

    return neocc_lst
