# -*- coding: utf-8 -*-
"""
This module contains all the methods required to request the list data,
obtain it from the ESA NEOCC portal and parse it to show it properly.

* Project: NEOCC portal Python interface
* Property: European Space Agency (ESA)
* Developed by: Elecnor Deimos
* Author: C. Álvaro Arroyo Parejo
* Issue: 1.2
* Date: 17-05-2021
* Purpose: Module which request and parse list data from ESA NEOCC
* Module: lists.py
* History:

========   ===========   ==========================================
Version    Date          Change History
========   ===========   ==========================================
1.0        26-02-2021    Initial version
1.1        26-03-2021    New docstrings and lists
1.2        17-05-2021    Adding *help* property for dataframes.\n
                         Adding timeout of 90 seconds.
========   ===========   ==========================================

© Copyright [European Space Agency][2021]
All rights reserved
"""

import io
from datetime import datetime as dt
import time
import pandas as pd
import requests

# Define the base URL for NEOCC
BASE_URL = 'https://neo.ssa.esa.int/PSDB-portlet/download?file='


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
        "updated_nea": 'updated_nea.lst',
        "monthly_update": 'monthly_update.done',
        "risk_list": 'esa_risk_list',
        "risk_list_special": 'esa_special_risk_list',
        "close_appr_upcoming": 'esa_upcoming_close_app',
        "close_appr_recent": 'esa_recent_close_app',
        "priority_list": 'esa_priority_neo_list',
        "priority_list_faint": 'esa_faint_neo_list',
        "close_encounter" : 'close_encounter2.txt',
        "impacted_objects" : 'impactedObjectsList.txt'
        }
    # Raise error is input is not in dictionary
    if list_name not in lists_dict:
        raise KeyError('Valid list names are nea_list, updated_nea, '
                       'monthly_update, risk_list, risk_list_special, '
                       'close_appr_upcoming, close_appr_recent, '
                       'priority_list, priority_list_faint, '
                       'close_encounter and impacted_objects')
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
    data_list = requests.get(BASE_URL + url, timeout=90).content

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
    if list_name in ("nea_list", "updated_nea", "monthly_update"):
        neocc_lst = parse_nea(data_byte_d)

    elif list_name in ("risk_list", "risk_list_special"):
        neocc_lst = parse_risk(data_byte_d)

    elif list_name in ("close_appr_upcoming", "close_appr_recent"):
        neocc_lst = parse_clo(data_byte_d)

    elif list_name in ("priority_list", "priority_list_faint"):
        neocc_lst = parse_pri(data_byte_d)
    elif list_name == "close_encounter":
        neocc_lst = parse_encounter(data_byte_d)
    elif list_name == "impacted_objects":
        neocc_lst = parse_impacted(data_byte_d)

    return neocc_lst


def parse_nea(data_byte_d):
    """Parse and arrange NEA lists.

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
                                                 regex=True)\
                                        .str.replace('# ', '')

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
    # Adding metadata
    neocc_lst.help = ('Risk lists contain a data frame with the '
                      'following information:\n'
                      '-Object Name: name of the NEA\n'
                      '-Diamater in m: approximate diameter in meters\n'
                      '-*=Y: recording an asterisk if the value has '
                      'been estimated from the absolute magnitude\n'
                      '-Date/Time: predicted impact date in YYYY.yyyyyy '
                      'format\n'
                      '-IP max: Maximum Impact Probability\n'
                      '-PS max: Palermo scale rating\n'
                      '-Vel in km/s: Impact velocity at atmospheric entry'
                      ' in km/s\n'
                      '-Years: Time span of detected impacts\n'
                      '-IP cum: Cumulative Impact Probability\n'
                      '-PS cum: Cumulative Palermo Scale')

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
    # Adding metadata
    neocc_lst.help = ('Close approches lists contain a data frame with'
                      ' the following information:\n'
                      '-Object Name: name of the NEA\n'
                      '-Date: close approach date in YYYY.yyyyyy '
                      'format\n'
                      '-Miss distance in km: miss distance in kilometers'
                      ' with precision of 1 km\n'
                      '-Miss distance in au: miss distance in astronomical'
                      ' units (1 au  = 149597870.7 km)\n'
                      '-Miss distance in LD: miss distance in Lunar '
                      'Distance (1 LD = 384399 km)\n'
                      '-Diamater in m: approximate diameter in meters\n'
                      '-*=Yes: recording an asterisk if the value has '
                      'been estimated from the absolute magnitude\n'
                      '-H: Absolute Magnitude\n'
                      '-Max Bright: Maximum brightness at close approach\n'
                      '-Rel. vel in km/s: relative velocity in km/s')

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
    neocc_lst[7] = neocc_lst[7].map(get_dec_year)

    # Rename columns
    neocc_lst.columns = ['Priority', 'Object',
                         'R.A. in arcsec', 'Decl. in deg',
                         'Elong. in deg', 'V in mag', 'Sky uncert.',
                         'End of Visibility']
    # Adding metadata
    neocc_lst.help = ('Priority lists contain a data frame with'
                      ' the following information:\n'
                      '-Priority: 0=UR: Urgent, 1=NE: Necessary, '
                      '2=US: Useful, 3=LP: Low Priority\n'
                      '-Object: designator of the object\n'
                      '-R.A. in arcsec: current right ascension on '
                      'the sky, Geocentric equatorial, in arcseconds\n'
                      '-Decl. in deg: current declination on the sky'
                      ', in sexagesimal degrees\n'
                      '-Elong. in deg: current Solar elongation, in '
                      'sexagesimal degrees\n'
                      '-V in mag: current observable brightness, V '
                      'band, in magnitudes\n'
                      '-Sky uncert.: uncertainty in the plane of the '
                      'sky, in arcseconds\n'
                      '-End of Visibility: expected date of end of '
                      'visibility as YYYY.yyyyyy format')

    return neocc_lst


def parse_encounter(data_byte_d):
    """Parse and arrange close encounter lists.

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
    neocc_lst = pd.read_csv(data_byte_d, sep='|', skiprows=[0,2])
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

    neocc_lst.help = ('Close encounter list contains a data frame with'
                      ' the following information:\n'
                      '-Name/design: designator of the NEA\n'
                      '-Planet:  planet or massive asteroid is '
                      'involved in the close approach\n'
                      '-Date: close encounter date in YYYY.yyyyyy '
                      'format\n'
                      '-Time approach: close encounter date in '
                      'MJD2000\n'
                      '-Time uncert: time uncertainty in MJD2000\n'
                      '-Distance: Nominal distance at the close '
                      'approach in au\n'
                      '-Minimum distance: minimum possible distance at'
                      ' the close approach in au\n'
                      '-Distance uncertainty: distance uncertainty in '
                      'in au\n'
                      '-Width: width of the strechin in au\n'
                      '-Stretch: stretching. It indicates how much the '
                      'confidence region at the epoch has been '
                      'stretched by the time of the approach. This is '
                      'a close cousin of the Lyapounov exponent\n'
                      '-Probability: close approach probability. A '
                      'value of 1 indicates a certain close approach\n'
                      '-Velocity: velocity in km/s\n'
                      '-Max Mag: maximum brightness magnitude at close'
                      'approach')

    return neocc_lst

def parse_impacted(data_byte_d):
    """Parse impacted objects list.

    Parameters
    ----------
    data_byte_d : object
        Decoded StringIO object.
    Returns
    -------
    neocc_lst : *pandas.DataFrame*
        Data frame with impacted objects list data parsed.
    """
    # Read data as csv
    neocc_lst = pd.read_csv(data_byte_d, header=None,
                            delim_whitespace=True)

    return neocc_lst
