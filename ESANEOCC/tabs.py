# -*- coding: utf-8 -*-
"""
This module contains all the methods required to request the data from
a particular object, obtain it from the ESA NEOCC portal and parse it
to show it properly. The information of the object is shows in the
ESA NEOCC in different tabs that correspond to the different classes
within this module.

* Project: NEOCC portal Python interface
* Property: European Space Agency (ESA)
* Developed by: Elecnor Deimos
* Author: C. Álvaro Arroyo Parejo
* Issue: 1.0
* Date: 26-02-2021
* Purpose: Module which request and parse list data from ESA NEOCC
* Module: tabs.py
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
import logging
import time
import pandas as pd
from parse import parse
import requests
from bs4 import BeautifulSoup


# Define the base URL for NEOCC
BASE_URL = 'http://neo.ssa.esa.int/PSDB-portlet/download?file='
# Define specific URLs for parsing HTMLs and for ephemerides
PROPERTIES_URL = 'https://neo.ssa.esa.int/'\
                 'search-for-asteroids?tab=physprops&des='
EPHEM_URL = 'http://neo.ssa.esa.int/PSDB-portlet/ephemerides?des='
SUMMARY_URL = 'https://neo.ssa.esa.int/search-for-asteroids?sum=1&des='

def get_object_url(name, tab, **kwargs):
    """Get url from requested object and tab name.

    Parameters
    ----------
    name : str
        Name of the requested object.
    tab : str
        Name of the request tab. Valid names are: *summary,
        orbit_properties, physical_properties, observations,
        ephemerides, close_approaches and impacts*.
    **kwargs : str
        orbit_properties and ephemerides tabs required additional
        arguments to work:

        * *orbit_properties*: the required additional arguments are:

            * *orbit_element* : str (keplerian or equinoctial)
            * *orbit_epoch* : str (present or middle)

        * *ephemerides*: the required additional arguments are:

            * *observatory* : str (observatory code, e.g. '500', 'J04', etc.)
            * *start* : str (start date in YYYY-MM-DD HH:MM)
            * *stop* : str (end date in YYYY-MM-DD HH:MM)
            * *step* : str (time step, e.g. '2', '15', etc.)
            * *step_unit* : str (e.g. 'days', 'minutes', etc.)

    Returns
    -------
    url : string
        Final url from which data is requested.

    Raises
    ------
    KeyError
        If the requested tab is not in the dictionary.
    ValueError
        If the elements requested are not valid.
    """
    # Define the parameters of each list
    tab_dict = {"impacts": '.risk',
                "close_approaches": '.clolin',
                "observations": '.rwo',
                "orbit_properties": ['.ke0', '.ke1', '.eq0', '.eq1']}

    # Raise error is input is not in dictionary
    if tab not in tab_dict:
        raise KeyError('Valid list names are impacts, close_approaches'
                       ' observations and orbit_properties')

    # Check if orbit_elements is an input
    if 'orbit_elements' in kwargs:
        # Check if the elements are Keplerian or Equinoctial
        if kwargs['orbit_elements'] == "keplerian":
            #Check if the epoch is present day or middle obs. arch
            if kwargs['orbit_epoch'] == "present":
                url = str(name).replace(' ', '%20') + tab_dict[tab][1]
            elif kwargs['orbit_epoch'] == "middle":
                url = str(name).replace(' ', '%20') + tab_dict[tab][0]
        elif kwargs['orbit_elements'] == "equinoctial":
            if kwargs['orbit_epoch'] == "present":
                url = str(name).replace(' ', '%20') + tab_dict[tab][3]
            elif kwargs['orbit_epoch'] == "middle":
                url = str(name).replace(' ', '%20') + tab_dict[tab][2]
        else:
            raise ValueError('The introduced file type does not exist.'
                             'Check that orbit elements (keplerian or '
                             'equinoctial) and orbit epoch (present or '
                             'middle).')
    else:
        url = str(name).replace(' ', '%20') + tab_dict[tab]

    return url


def get_object_data(url):
    """Get object in byte format from requested url.

    Parameters
    ----------
    url : str
        URL of the requested data.

    Returns
    -------
    data_obj : object
        Object in byte format.
    """
    # Get data from URL
    data_obj = requests.get(BASE_URL + url).content
    # Parse data and assign attributes to object

    return data_obj


def get_indexes(dfobj, value):
    """Get a list with location index of a value or string in the
    DataFrame requested.

    Parameters
    ----------
    dfobj : pandas.DataFrame
        Data frame where the value will be searched.
    value : str, int, float
        String, integer or float to be searched.

    Returns
    -------
    listofpos : list
        List which contains the location of the value in the Data
        frame. The first elements will correspond to the index and
        the second element to the columns
    """
    # Empty list
    listofpos = []

    # isin() method will return a dataframe with boolean values,
    # True at the positions where element exists
    result = dfobj.isin([value])

    # any() method will return a boolean series
    seriesobj = result.any()

    # Get list of column names where element exists
    columnnames = list(seriesobj[seriesobj].index)

    # Iterate over the list of columns and extract the row index
    # where element exists
    for col in columnnames:
        rows = list(result[col][result[col]].index)

        for row in rows:
            listofpos.append((row, col))

    return listofpos


class Impacts:
    """This class contains information of object possible impacts.

    Attributes
    ---------
    impacts : pandas.DataFrame
        Data frame where are listed all the possible impactors.
    arc_start : str
        Starting date for optical observations.
    arc_end : str
        End date for optical observations.
    observations_accepted : int
        Total number of observations subtracting rejected
        observations.
    observations_rejected : int
        Number of observations rejected.
    computation : str
        Date of computation (in format YYYYMMDD MJD TimeSys)
    info : str
        Information from the footer of the requested file.
    additional_note : str
        Additional information. Some objects (e.g. 99942 Apophis)
        have an additional note after the main footer.

    """

    def __init__(self):
        """Initialization of class attributes
        """
        self.impacts = []
        self.arc_start = []
        self.arc_end = []
        self.observation_accepted = []
        self.observation_rejected = []
        self.computation = []
        self.info = []
        self.additional_note = []

    @staticmethod
    def _get_footer(data_obj):
        """Get footer information for impacts content.

        Parameters
        ----------
        data_obj : object
            Object in byte format.

        Returns
        -------
        obs : list
            Number of observations (total and rejected).
        arc : list
            Start and end dates.
        comp : str
            Computation date.
        info : str
            Additional information.
        add_note : str
            Addition note.
        """
        # Decode data using UTF-8 and store in new space of memory
        df_txt_d = io.StringIO(data_obj.decode('utf-8'))
        # Read data as txt
        df_txt = pd.read_fwf(df_txt_d, header=None)
        # Check that there is not additonal note
        index = get_indexes(df_txt, '<p> </p>')
        # Assign the index for obtaining the rest of attributes and
        # additional note value
        if not index:
            j = 0
            add_note = 'There is no additional note for this object'
        else:
            j = 6
            index = index[0][0]
            add_note = df_txt.iloc[index+1, 0] + '\n' +\
                df_txt.iloc[index+2, 0] + '\n' +\
                df_txt.iloc[index+3, 0] + '\n' +\
                df_txt.iloc[index+4, 0] + '\n' +\
                df_txt.iloc[index+5, 0]
            # Remove unnecessary words
            add_note = add_note.replace('<p>','').replace('</p>','').\
                replace('<span style="color: #0000CD;"><strong>','').\
                replace('</strong></span>','').replace('<sup>','^').\
                replace('</sup>','')

        # Drop NaN values if necessary
        df_txt = df_txt.dropna(how='all')
        # Template for observations data
        parse_txt_obs = "Based on {total} optical observations "\
                        "(of which {rejected} are rejected as "\
                        "outliers)"
        # Parse required data for attributes
        obs = parse(parse_txt_obs, df_txt.iloc[-7-j][0].split(' and')[0])
        # Template for date of observations
        parse_txt_arc = 'from {start} to {end}.'
        # Parse required data for attributes
        arc = parse(parse_txt_arc, df_txt.iloc[-6-j][0])
        # Computation date
        comp = df_txt.iloc[-1-j][0].split('=')[2].strip()
        # Get information text
        info = df_txt.iloc[-5-j][0] + '\n\n' + df_txt.iloc[-4-j][0] +\
            '\n' + df_txt.iloc[-3-j][0] + '\n\n' + df_txt.iloc[-2-j][0]

        return obs, arc, comp, info, add_note

    def _impacts_parser(self, data_obj):
        """Parse and arrange the possible impacts data

        Parameters
        ----------
        data_obj : object
            Object in byte format.

        Raises
        ------
        ValueError
            If there is not risk file available for requested
            object
        """
        # Check that there is not additonal note
        df_check_d = io.StringIO(data_obj.decode('utf-8'))
        # Read as txt file
        df_check = pd.read_fwf(df_check_d, engine='python')
        index = get_indexes(df_check, '<p> </p>')
        # Assign the skipfooter if there is or not additional note
        if not index:
            footer_num = 12
        else:
            footer_num = 21
        # Decode data using UTF-8 and store in memory
        df_impacts_d = io.StringIO(data_obj.decode('utf-8'))
        # Read data as csv
        df_impacts = pd.read_csv(df_impacts_d, skiprows=[0, 2, 3, 4],
                                 skipfooter=footer_num,
                                 delim_whitespace=True, engine='python')
        # Check if there are information for the object
        if len(df_impacts.index) == 0:
            logging.warning('Required risk file is not '
                            'available for this object')
            raise ValueError('Required risk file is not '
                             'available for this object')
        # The previous skipfooter allow strange cases to show proper
        # impacts table. For the rest of the cases an additional row
        # must be dropped
        if df_impacts.iloc[-1,0] == 'Based':
            # Drop last row
            df_impacts = df_impacts.iloc[:-1]
            # Reassign numeric types to columns
            df_impacts['MJD'] = pd.to_numeric(df_impacts['MJD'])
            df_impacts['sigimp'] = pd.to_numeric(df_impacts['sigimp'])
            df_impacts['dist'] = pd.to_numeric(df_impacts['dist'])
            df_impacts['width'] = pd.to_numeric(df_impacts['width'])
            df_impacts['p_RE'] = pd.to_numeric(df_impacts['p_RE'])
            df_impacts['exp.'] = pd.to_numeric(df_impacts['exp.'])
            df_impacts['en.'] = pd.to_numeric(df_impacts['en.'])
            df_impacts['PS'] = pd.to_numeric(df_impacts['PS'])

        # Add number of decimals
        df_impacts['dist'].map(lambda x: f"{x:.2f}")
        df_impacts['width'].map(lambda x: f"{x:.3f}")
        # Rename new column and drop duplicate columns
        col_dict = {'exp.': 'Exp. Energy in MT',
                    'en.': 'PS',
                    'PS': 'TS'}
        df_impacts = df_impacts.drop(columns=['+/-',
                                     'TS']).rename(
                                     columns=col_dict)
        # Assign Data structure to attribute
        self.impacts = df_impacts

        # Get info from footer
        footer = self._get_footer(data_obj)
        # Assign parsed data to attributes
        self.arc_start = footer[1]['start']
        self.arc_end = footer[1]['end']
        self.observation_accepted = int(footer[0]['total']) - \
            int(footer[0]['rejected'])
        self.observation_rejected = int(footer[0]['rejected'])
        self.computation = footer[2]
        self.additional_note = footer[4]
        # Assign info text from pandas
        self.info = footer[3]


class CloseApproaches:
    """This class contains information of object close approaches.
    """
    @staticmethod
    def clo_appr_parser(data_obj, name):
        """Parse and arrange the close approaches data.

        Parameters
        ----------
        data_obj : object
            Object in byte format.

        Returns
        -------
        df_close_appr : pandas.DataFrame
            Data frame with the close approaches information.

        Raises
        ------
        ValueError
            If file is empty.
        """
        # Decode data using UTF-8 and store in memory
        df_impacts_d = io.StringIO(data_obj.decode('utf-8'))
        # Check if the decoded data is empty before reading
        if not df_impacts_d.getvalue():
            logging.warning('Required close approach file is '
                            'empty for %s', name)
            raise ValueError('Required close approach file is '
                             'empty for ' + name)

        # Read data as csv
        df_close_appr = pd.read_csv(df_impacts_d,
                                    delim_whitespace=True)

        return df_close_appr


class PhysicalProperties:
    """
        This class contains information of asteroid physical properties

        Attributes
        ---------
        physical_properties : DataFrame
            Data structure containing property, value, units and source
            from the complete set of physical properties
        sources : DataFrame
            Data structure containing source number, name and
            additional information

        Raises
        ------
        ValueError
            If the name of the object is not found
    """
    def __init__(self):
        """
            Initialization of class attributes
        """
        # Physical properties
        self.physical_properties = []
        # Sources
        self.sources = []

    @staticmethod
    def _get_prop_sources(url):
        """
            Obtain the sources parsed

            Parameters
            ----------
            url : str
                Complete url for physical properties

            Returns
            -------
            sources : Data structure
                Data structure containing all property sources
        """
        # Read html for obtaining different tables from the portal
        try:
            df_p = pd.read_html(url, keep_default_na=False)
        except df_p.DoesNotExist as df_not_exist:
            logging.warning('Object not found: the name of the '
                            'object is wrong or misspelt')
            raise ValueError('Object not found: the name of the '
                             'object is wrong or misspelt') from df_not_exist

        # The obtaining data frame contains a list of different data
        # frames so the required is extracted
        sources = pd.DataFrame(df_p[2])

        return sources

    @staticmethod
    def _get_physical_props(url):
        """
            Obtain the physical properties from the portal

            Parameters
            ----------
            url : str
                Complete url for physical properties

            Returns
            -------
            physical_properties : Data structure
                Data structure containing the physical properties
        """
        # Get contents from url
        contents = requests.get(url).content
        # Parse html using BS
        parsed_html = BeautifulSoup(contents, 'lxml')
        # Search for property names using div and class
        props_names = parsed_html.find_all("div",
                                        {"class": "col-lg-3 font-weight-bold"
                                            " d-none d-lg-block"})
        # Create DataFrame with the obtained properties
        df_names = pd.DataFrame(props_names)
        # Since the parsing gets properties from other tabs it is
        # necessary to select the properties associated to Physical
        # Properties tab
        df_names = df_names[0][13:27]
        # Reindex and drop old indexes
        df_names = df_names.reset_index(drop=True)
        # Search for property values, units and sources
        props_value = parsed_html.find_all("div",
                                        {"class": "col-12"})
        # Convert to DataFrame and specify string type to avoid bad
        # object parsing
        df_values = pd.DataFrame(props_value, dtype='string')
        # Since the parsing is not as precises as needed remove/replace
        # unnecessary data
        df_values[0] = df_values[0].str.replace('<div class="col-12">',
                                                '')\
                    .str.replace('</div>', '').str.replace('\n', '')\
                    .str.strip()
        # Since the parsing gets properties from other tabs it is
        # necessary to select the properties associated to Physical
        # Properties tab
        df_values = df_values[0][0:42]
        # Diameter property is an exception, it is required to
        # introduce an additional parsing step searching for the
        # specific property
        diameter = parsed_html.find_all("span",
                                        {"id": "_NEOSearch_WAR_PSDBportlet_:"
                                        "j_idt10:j_idt639:diameter-value"})
        # Get the value from BS attribute
        diameter_parsed = BeautifulSoup(str(diameter), 'html.parser').\
                          span.text
        # Drop-down units needs to be specify. It has been chosen the
        # default unit
        df_values = df_values.replace(df_values[13], 'deg').\
                            replace(df_values[16], 'deg').\
                            replace(df_values[33], diameter_parsed).\
                            replace(df_values[34], 'm')
        # Create lists to used as columns for final frame
        # Initialize list
        values = []
        units = []
        sources = []
        for i in range(0, len(df_values), 3):
            # Append values for the lists
            values.append(df_values[i])
            units.append(df_values[i+1])
            sources.append(df_values[i+2])
        # Create frame structure for pandas
        frame = {'Property': df_names,
                'Values': values,
                'Unit': units,
                'Source': sources}
        # Create DataFrame using pandas
        physical_properties =  pd.DataFrame(frame)

        return physical_properties

    def _phys_prop_parser(self, name):
        """
            Parse and arrange the physical properties data

            Parameters
            ----------
            name : string
                Object name

            Raises
            ------
            ValueError
                If the name of the object is not encountered
        """
        # Final url = PROPERTIES_URL + desig in which white spaces,
        # if any, are replaced by %20 to complete the designator
        url = PROPERTIES_URL + str(name).replace(' ', '%20')

        # Sources
        self.physical_properties = self._get_physical_props(url)
        self.sources = self._get_prop_sources(url)


class AsteroidObservations:
    """This class contains information of asteroid observations.

    Attributes
    ----------
    version : int
        File version.
    errmod : str
        Error model for the data.
    rmsast : float
        Root Mean Square for asteroid observations.
    rmsmag : float
        Root Mean Square for magnitude.
    optical_observations : pandas.DataFrame
        Data frame which contains optical observations (without roving
        observer and satellite observation).
    radar_observations : pandas.DataFrame
        Data structure which contains radar observations.
    roving_observations : pandas.DataFrame
        Data structure which contains "roving observer" observations.
    sat_observations : pandas.DataFrame
        Data structure which contains satellite observations.

    """

    def __init__(self):
        """Initialization of class attributes
        """
        self.version = []
        self.errmod = []
        self.rmsast = []
        self.rmsmag = []
        self.optical_observations = []
        self.radar_observations = []
        self.roving_observations = []
        self.sat_observations = []

    @staticmethod
    def _get_head_obs(df_d):
        """Get and parse header of asteroid observations file.

        Parameters
        ----------
        df_d : object
            StringIO object with data.

        Returns
        -------
        ver : int
            File version.
        err : str
            Error model.
        ast : float
            Root Mean Square for asteroid observations.
        mag : float
            Root Mean Square for magnitude.
        """
        df_head = pd.read_csv(df_d, nrows=4, header=None)
        # Template for version
        parse_ver = 'version =   {ver}'
        # Parse required data for attributes
        ver = parse(parse_ver, df_head[0][0])
        ver = int(ver['ver'])
        # Template for errmod
        parse_err = "errmod  = '{err}'"
        # Parse required data for attributes
        err = parse(parse_err, df_head[0][1])
        err = err['err']
        # Template for RMSast
        parse_ast = "RMSast  =   {ast}"
        # Parse required data for attributes
        ast = parse(parse_ast, df_head[0][2])
        ast = float(ast['ast'])
        # Template for RMSast
        parse_mag = "RMSmag  =   {mag}"
        # Parse required data for attributes
        mag = parse(parse_mag, df_head[0][3])
        if mag is None:
            mag = 'No data for RMSmag'
        else:
            mag = float(mag['mag'])

        return ver, err, ast, mag

    @staticmethod
    def _get_opt_info(data_obj, diff, head):
        """Get optical information from asteroid observation file.

        Parameters
        ----------
        df_d : object
            Object in byte format with data decoded.
        diff : int
            Optical observations data frame length.
        head : list
            Header rows to be skipped.

        Returns
        -------
        df_optical_obs : pandas.DataFrame
            Parsed data frame for optical observations.
        df_roving_obs : pandas.DataFrame
            Parsed data frame for "roving observer" observations.
        df_sat_obs : pandas.DataFrame
            Parsed data frame for satellite observations.
        """
        # Decode data for check v and s optical observations
        df_check = io.StringIO(data_obj.decode('utf-8'))
        # Set attributes
        df_obs = pd.read_fwf(df_check, sep=' ', skiprows=[0,1,2,3,4,5],
                               engine='python', skipfooter=diff)
        # Check if there are "Roving Observer" observations
        df_index = df_obs.iloc[:,1:4]
        v_indexes = get_indexes(df_index, 'v')
        # Check if there are "Roving Observer" observations
        s_indexes = get_indexes(df_index, 's')
        # Initialization of a list which contain the row indexes
        v_rows = []
        s_rows = []

        # Roving Observations
        if not v_indexes:
            df_roving_obs = 'There are no "Roving Observer"' \
                            'observartions for this object'
        else:
            # Save a list with the row indexes that needs to be saved
            for v_index in v_indexes:
                # Add to the list in order to consider header lines
                v_rows =  v_rows + [v_index[0]+len(head)+1]
            # Decode data for final roving observations
            df_v = io.StringIO(data_obj.decode('utf-8'))
            # Define colspecs fwf
            cols_v = [(0,10), (11,12), (12,14), (15,16), (17,21),
                      (22,24), (25,34), (34,44), (45,55), (56,64),
                      (65,68)]
            # Usea pandas to read these rows
            df_roving_obs = pd.read_fwf(df_v, delim_whitespace=True,
                                        skiprows=lambda x: x not in v_rows,
                                        engine='python', header=None,
                                        colspecs=cols_v)
            # Rename columns as in file
            df_roving_obs.columns = ['Design.', 'K', 'T', 'N', 'YYYY',
                                     'MM', 'DD.dddddd', 'E longitude',
                                     'Latitude', 'Altitude', 'Obs Code']

        # Satellite Observations
        if not s_indexes:
            df_sat_obs = 'There are no Satellite observartions for '\
                         'this object'
        else:
            # Save a list with the row indexes that needs to be saved
            for s_index in s_indexes:
                # Number 7 is add to the list in order to consider
                # header lines
                s_rows =  s_rows + [s_index[0]+len(head)+1]
            # Decode data for final satellite observations
            df_s = io.StringIO(data_obj.decode('utf-8'))
            # Define colspecs fwf
            cols_s = [(0,10), (11,12), (12,15), (15,16), (17,21),
                     (22,24), (25,34), (34,35), (40,59), (64,83),
                     (88,107), (108,111)]
            # Usea pandas to read these rows
            df_sat_obs = pd.read_fwf(df_s, delim_whitespace=True,
                                     skiprows=lambda x: x not in s_rows,
                                     engine='python', header=None,
                                     colspecs=cols_s)
            # Rename columns as in file
            df_sat_obs.columns = ['Design.', 'K', 'T', 'N', 'YYYY',
                                  'MM', 'DD.dddddd',
                                  'Parallax info.', 'X', 'Y',
                                  'Z', 'Obs Code']
            # For satellite observations columns "T" contains
            # whitespacese. Strip them
            df_sat_obs['T'] = df_sat_obs['T'].str.strip()

        # Rest of optical observations
        df_opt = io.StringIO(data_obj.decode('utf-8'))
        # Define colspecs fwf
        cols = [(0,10), (11,12), (12,15), (15,16), (17,21), (22,24),
                (25,38), (40,49), (50,52), (53,55), (56,62), (64,73),
                (76,82), (83,84), (87,93), (96,102), (103,106),
                (107,109), (110,115), (117,126), (129,135), (136,137),
                (140,146), (149,155), (156,161), (161,162), (164,168),
                (170,175), (177,179), (180,183), (188,193), (194,195),
                (196,197)]
        # Read data using pandas as text, skiping header and footer
        # and v_rows and s_rows if any
        df_optical_obs = pd.read_fwf(df_opt, skipfooter=diff, colspecs=cols,
                                      engine='python',
                                      skiprows=head + v_rows + s_rows)
        # Replace NaN values for blank values
        df_optical_obs = df_optical_obs.fillna('')
        # Rename Columns as in file
        df_optical_obs.columns = ['Design.', 'K', 'T', 'N', 'YYYY',
                                  'MM', 'DD.dddddddddd',
                                  'Date Accuracy', 'RA HH',
                                  'RA MM', 'RA SS.sss', 'RA Accuracy',
                                  'RA RMS', 'RA F', 'RA Bias',
                                  'RA Resid', 'DEC sDD', 'DEC MM',
                                  'DEC SS.ss', 'DEC Accuracy',
                                  'DEC RMS', 'DEC F', 'DEC Bias',
                                  'DEC Resid', 'MAG Val', 'MAG B',
                                  'MAG RMS', 'MAG Resid', 'Ast Cat',
                                  'Obs Code', 'Chi', 'A', 'M']

        return df_optical_obs, df_roving_obs, df_sat_obs

    @staticmethod
    def _get_rad_info(df_d, index):
        """Get radar information from asteroid observations file

        Parameters
        ----------
        df_d : object
            stringIO object with data decoded.
        index : int
            Position at which radar information starts.

        Returns
        -------
        df_rad : pandas.DataFrame
            Parsed data frame for radar observations.
        """
        # Read decoded DataFrame and skip rows
        df_rad = pd.read_fwf(df_d, engine='python', sep=' ',
                             skiprows=index[0][0]+8)
        # Drop NaN columns and rename
        df_rad = df_rad.drop(['F', 'S'], axis=1)
        # Create Datetime column
        df_rad['YYYY'] = df_rad['YYYY'].apply(str) + '-' + \
            df_rad['MM'].apply(str) + '-' + df_rad['DD'].apply(str) + \
            '-' + df_rad['hh:mm:ss']
        df_rad['YYYY'] = pd.to_datetime(df_rad['YYYY'])
        # Dropping old name columns
        df_rad = df_rad.drop(['MM', 'DD', 'hh:mm:ss'], axis=1)
        # Check variable column data
        if 'rms' in df_rad.columns:
            # Rename columns
            cols_dict = {'! Design': 'Design',
                         'Unnamed: 11': 'F',
                         'Unnamed: 17': 'S',
                         'YYYY': 'Datetime'}
            df_rad.rename(columns=cols_dict, inplace=True)
        else:
            # Rename columns
            cols_dict = {'! Design': 'Design',
                         'Unnamed: 10': 'F',
                         'Unnamed: 16': 'S',
                         'YYYY': 'Datetime'}
            df_rad.rename(columns=cols_dict, inplace=True)
            # Splitting bad joined columns
            split1 = df_rad["Accuracy    rms"].str.split(" ", n=1,
                                                         expand=True)
            df_rad["Accuracy"] = split1[0]
            df_rad["rms"] = split1[1]
            # Dropping old Name columns
            df_rad.drop(columns=["Accuracy    rms"], inplace=True)

        # Splitting bad joined columns
        split2 = df_rad["TRX RCX"].str.split(" ", n=1, expand=True)
        # Making separate first name column from new Data structure
        df_rad["TRX"] = split2[0]
        # Making separate last name column from new Data structure
        df_rad["RCX"] = split2[1]
        # Dropping old Name columns
        df_rad.drop(columns=["TRX RCX"], inplace=True)

        # Reorder columns
        df_rad = df_rad[['Design', 'K', 'T', 'Datetime', 'Measure',
                         'Accuracy', 'rms', 'F', 'Bias', 'Resid',
                         'TRX', 'RCX', 'Chi', 'S']]

        return df_rad

    def _ast_obs_parser(self, data_obj):
        """Get asteroid observation properties parsed from object data

        Parameters
        ----------
        data_obj : object
            Object in byte format.

        Raises
        ------
        ValueError
            If the required observations file is empty or does not exist
        """
        # Decode data using UTF-8 and store in memory for header
        df_head_d = io.StringIO(data_obj.decode('utf-8'))
        # Check file exists or is not empty
        if not df_head_d.getvalue():
            logging.warning('Required data observations file is '
                            'empty for this object')
            raise ValueError('Required data observations file is '
                             'empty for this object')

        # Obtain header
        df_head = self._get_head_obs(df_head_d)
        self.version = df_head[0]
        self.errmod = df_head[1]
        self.rmsast = df_head[2]
        self.rmsmag = df_head[3]
        # Decode data using UTF-8 and store in memory for
        # observations
        df_d = io.StringIO(data_obj.decode('utf-8'))
        # Check there is valid data for RMS magnitude and set header
        # length
        if isinstance(self.rmsmag, str):
            head = [0, 1, 2, 3, 4]
        else:
            head = [0, 1, 2, 3, 4, 5]
        # Read data in fixed width format
        df_p = pd.read_fwf(df_d, delim_whitespace=True,
                           skiprows=head, engine='python')
        # Check if there is radar observations data
        if not get_indexes(df_p, '! Object'):
            # Set length of asteriod observations to zero
            diff = 0
            # Set attributes
            self.optical_observations = self._get_opt_info(data_obj, diff,
                                                          head)[0]
            self.radar_observations = 'There is no relevant radar '\
                                      'information'
            self.roving_observations = self._get_opt_info(data_obj, diff,
                                                         head)[1]
            self.sat_observations = self._get_opt_info(data_obj, diff,
                                                      head)[2]

        else:
            # # Decode data for optical and radar observations
            df_rad = io.StringIO(data_obj.decode('utf-8'))
            # Get position at which radar observations start
            index = get_indexes(df_p, '! Object')
            # Set lenght of radar obsrevations to remove footer
            diff = len(df_p) - index[0][0]
            # Set attributes
            self.optical_observations = self._get_opt_info(data_obj, diff,
                                                          head)[0]
            self.radar_observations = self._get_rad_info(df_rad, index)
            self.roving_observations = self._get_opt_info(data_obj, diff,
                                                         head)[1]
            self.sat_observations = self._get_opt_info(data_obj, diff,
                                                      head)[2]


class OrbitProperties:
    """This class contains information of asteroid orbit properties.

    Attributes
    ----------
    form : str
        File format.
    rectype : str
        Record type.
    refsys : str
        Default reference system.
    epoch : str
        Epoch in MJD format.
    mag : pandas.DataFrame
        Data frame which contains magnitude values.
    lsp : pandas.DataFrame
        Data structure with information about non-gravitational
        parameters (model, numer of parameters, dimension, etc.).
    ngr : pandas.DataFrame
        Data frame which contains non-gravitational parameters.

    """

    def __init__(self):
        """Initialization of class attributes
        """
        # Document info
        self.form = []
        self.rectype = []
        self.refsys = []
        # Orbit properties
        self.epoch = []
        self.mag = []
        self.lsp = []
        # Non-gravitational parameters
        self.ngr = []

    @staticmethod
    def _get_matrix(dfd, matrix_name, dimension, orbit_element, **kwargs):
        """Get covariance or correlaton matrix from df.

        Parameters
        ----------
        dfd : pandas.DataFrame
            Data frame with object data to be parsed.
        matrix_name : str
            Matrix name to be obtained.
        dimension : int
            Matrix dimension.
        orbit_element : str
            Orbit elements for the matrix.
        **kwargs : str
            If there is only one additional NGR parameter it should be
            introduced to show properly in the matrix.

        Returns
        -------
        mat : Data structure
            Data structure with matrix data

        Raises
        ------
        ValueError
            If the matrix name is not correct
        """
        # Define dictionary for types of matrices
        matrix_dict = {'cov': 'COV',
                       'cor': 'COR',
                       'nor': 'NOR'}
        # Define indexes and colunm namaes according to orbit element type
        mat_var = {'keplerian': ['a', 'e', 'i', 'long. node',
                                   'arg. peric', 'M'],
                   'equinoctial': ['a', 'e*sin(LP)', 'e*cos(LP)',
                                     'tan(i/2)*sin(LN)', 'tan(i/2)*cos(LN)',
                                     'mean long.']}
        # Get matrix location according to its name
        if matrix_name in matrix_dict:
            i = get_indexes(dfd, matrix_dict[matrix_name])[0][0]
            # Check if there is a matrix
            if not i:
                mat = 'There is no ' + matrix_dict[matrix_name]  +\
                    'matrix for this object'
                logging.warning('There is no %s matrix for this object',
                                matrix_dict[matrix_name])
            else:
                # Define the matrix according to its dimension
                if dimension == 6:
                    # Define matrix structure
                    mat_data = {mat_var[orbit_element][0]:
                                    [dfd.iloc[i, 1], dfd.iloc[i, 2],
                                    dfd.iloc[i, 3], dfd.iloc[i+1, 1],
                                    dfd.iloc[i+1, 2], dfd.iloc[i+1, 3]],
                                mat_var[orbit_element][1]:
                                    [dfd.iloc[i, 2], dfd.iloc[i+2, 1],
                                    dfd.iloc[i+2, 2], dfd.iloc[i+2, 3],
                                    dfd.iloc[i+3, 1], dfd.iloc[i+3, 2]],
                                mat_var[orbit_element][2]:
                                    [dfd.iloc[i, 3], dfd.iloc[i+2, 2],
                                    dfd.iloc[i+3, 3], dfd.iloc[i+4, 1],
                                    dfd.iloc[i+4, 2], dfd.iloc[i+4, 3]],
                                mat_var[orbit_element][3]:
                                    [dfd.iloc[i+1, 1], dfd.iloc[i+2, 3],
                                    dfd.iloc[i+4, 1], dfd.iloc[i+5, 1],
                                    dfd.iloc[i+5, 2], dfd.iloc[i+5, 3]],
                                mat_var[orbit_element][4]:
                                    [dfd.iloc[i+1, 2], dfd.iloc[i+3, 1],
                                    dfd.iloc[i+4, 2], dfd.iloc[i+5, 2],
                                    dfd.iloc[i+6, 1], dfd.iloc[i+6, 2]],
                                mat_var[orbit_element][5]:
                                    [dfd.iloc[i+1, 3], dfd.iloc[i+3, 2],
                                    dfd.iloc[i+4, 3], dfd.iloc[i+5, 3],
                                    dfd.iloc[i+6, 2], dfd.iloc[i+6, 3]]}
                    # Rename matrix indexes
                    matrix_indexes = mat_var[orbit_element]
                    # Build the matrix
                    mat = pd.DataFrame(mat_data, index=matrix_indexes)

                elif dimension == 7:
                    # Obtain from kwargs the non-gravitational parameter
                    ngr_parameter = kwargs['ngr']
                    # Define matrix structure
                    mat_data = {mat_var[orbit_element][0]:
                                    [dfd.iloc[i, 1], dfd.iloc[i, 2],
                                    dfd.iloc[i, 3], dfd.iloc[i+1, 1],
                                    dfd.iloc[i+1, 2], dfd.iloc[i+1, 3],
                                    dfd.iloc[i+2, 1]],
                                mat_var[orbit_element][1]:
                                    [dfd.iloc[i, 2], dfd.iloc[i+2, 2],
                                    dfd.iloc[i+2, 3], dfd.iloc[i+3, 1],
                                    dfd.iloc[i+3, 2], dfd.iloc[i+3, 3],
                                    dfd.iloc[i+4, 1]],
                                mat_var[orbit_element][2]:
                                    [dfd.iloc[i, 3], dfd.iloc[i+2, 3],
                                    dfd.iloc[i+4, 2], dfd.iloc[i+4, 3],
                                    dfd.iloc[i+5, 1], dfd.iloc[i+5, 2],
                                    dfd.iloc[i+5, 3]],
                                mat_var[orbit_element][3]:
                                    [dfd.iloc[i+1, 1], dfd.iloc[i+3, 1],
                                    dfd.iloc[i+4, 3], dfd.iloc[i+6, 1],
                                    dfd.iloc[i+6, 2], dfd.iloc[i+6, 3],
                                    dfd.iloc[i+7, 1]],
                                mat_var[orbit_element][4]:
                                    [dfd.iloc[i+1, 2], dfd.iloc[i+3, 2],
                                    dfd.iloc[i+5, 1], dfd.iloc[i+6, 2],
                                    dfd.iloc[i+7, 2], dfd.iloc[i+7, 3],
                                    dfd.iloc[i+8, 1]],
                                mat_var[orbit_element][5]:
                                    [dfd.iloc[i+1, 3], dfd.iloc[i+3, 3],
                                    dfd.iloc[i+5, 2], dfd.iloc[i+6, 3],
                                    dfd.iloc[i+7, 3], dfd.iloc[i+8, 2],
                                    dfd.iloc[i+8, 3]],
                                ngr_parameter: [dfd.iloc[i+2, 1],
                                                dfd.iloc[i+4, 1],
                                                dfd.iloc[i+5, 3],
                                                dfd.iloc[i+7, 1],
                                                dfd.iloc[i+8, 1],
                                                dfd.iloc[i+8, 3],
                                                dfd.iloc[i+9, 1]]}
                    # Rename matrix indexes
                    matrix_indexes = mat_var[orbit_element] + [ngr_parameter]
                    # Build the matrix
                    mat = pd.DataFrame(mat_data, index=matrix_indexes)

                elif dimension == 8:
                    # Define matrix structure
                    mat_data = {mat_var[orbit_element][0]:
                                    [dfd.iloc[i, 1], dfd.iloc[i, 2],
                                    dfd.iloc[i, 3], dfd.iloc[i+1, 1],
                                    dfd.iloc[i+1, 2], dfd.iloc[i+1, 3],
                                    dfd.iloc[i+2, 1], dfd.iloc[i+2, 2]],
                                mat_var[orbit_element][5]:
                                    [dfd.iloc[i, 2], dfd.iloc[i+2, 3],
                                    dfd.iloc[i+3, 1], dfd.iloc[i+3, 2],
                                    dfd.iloc[i+3, 3], dfd.iloc[i+4, 1],
                                    dfd.iloc[i+4, 2], dfd.iloc[i+4, 3]],
                                mat_var[orbit_element][5]:
                                    [dfd.iloc[i, 3], dfd.iloc[i+3, 1],
                                    dfd.iloc[i+5, 1], dfd.iloc[i+5, 2],
                                    dfd.iloc[i+5, 3], dfd.iloc[i+6, 1],
                                    dfd.iloc[i+6, 2], dfd.iloc[i+6, 3]],
                                mat_var[orbit_element][5]:
                                    [dfd.iloc[i+1, 1], dfd.iloc[i+3, 2],
                                    dfd.iloc[i+5, 2], dfd.iloc[i+7, 1],
                                    dfd.iloc[i+7, 2], dfd.iloc[i+7, 3],
                                    dfd.iloc[i+8, 1], dfd.iloc[i+8, 2]],
                                mat_var[orbit_element][5]:
                                    [dfd.iloc[i+1, 2], dfd.iloc[i+3, 3],
                                    dfd.iloc[i+5, 3], dfd.iloc[i+7, 2],
                                    dfd.iloc[i+8, 3], dfd.iloc[i+9, 1],
                                    dfd.iloc[i+9, 2], dfd.iloc[i+9, 3]],
                                mat_var[orbit_element][5]:
                                    [dfd.iloc[i+1, 3], dfd.iloc[i+4, 1],
                                    dfd.iloc[i+6, 1], dfd.iloc[i+7, 3],
                                    dfd.iloc[i+9, 1], dfd.iloc[i+10, 1],
                                    dfd.iloc[i+10, 2], dfd.iloc[i+10, 3]],
                                'Area-to-mass ratio':
                                    [dfd.iloc[i+2, 1], dfd.iloc[i+4, 2],
                                    dfd.iloc[i+6, 2], dfd.iloc[i+8, 1],
                                    dfd.iloc[i+9, 2], dfd.iloc[i+10, 2],
                                    dfd.iloc[i+11, 1], dfd.iloc[i+11, 2]],
                                'Yarkovsky parameter':
                                    [dfd.iloc[i+2, 2], dfd.iloc[i+4, 3],
                                    dfd.iloc[i+6, 3], dfd.iloc[i+8, 2],
                                    dfd.iloc[i+9, 3], dfd.iloc[i+10, 3],
                                    dfd.iloc[i+11, 2], dfd.iloc[i+11, 3]]}
                    # Rename matrix indexes
                    matrix_indexes = mat_var[orbit_element] +\
                        ['Area-to-mass ratio', 'Yarkovsky parameter']
                    # Build the matrix
                    mat = pd.DataFrame(mat_data, index=matrix_indexes)
        else:
            raise ValueError('Valid matrix name are cov, cor and nor')

        return mat

    @staticmethod
    def _get_head_orb(data_obj):
        """Get and parse header of orbit properties file.

        Parameters
        ----------
        data_obj : object
            Object data in byte format.

        Returns
        -------
        form : str
            Format file.
        rectype : str
            File record type.
        refsys : str
            Default reference system.
        """
        # Decode data using UTF-8 and store in memory for doc info
        df_info_d = io.StringIO(data_obj.decode('utf-8'))
        # Read as txt file
        df_info = pd.read_fwf(df_info_d, nrows=3, header=None)
        # Template for format data
        parse_format = "format  = '{format}'       ! file format"
        # Parse required data for attributes
        format_txt = parse(parse_format, df_info.iloc[0][0])
        form = format_txt['format']
        # Template for record type
        parse_rectype = "rectype = '{rectype}'           !"\
            " record type (1L/ML)"
        # Parse required data for attributes
        rectype = parse(parse_rectype, df_info.iloc[1][0])
        rectype = rectype['rectype']
        # Template for reference system
        parse_refsys = "refsys  = {refsys}     !"\
            " default reference system"
        # Parse required data for attributes
        refsys = parse(parse_refsys, df_info.iloc[2][0])
        refsys = refsys['refsys']

        return form, rectype, refsys

    def _orb_prop_parser(self, data_obj):
        """Get orbit properties parsed from object data

        Parameters
        ----------
        data_obj : object
            Object data in byte format.

        Raises
        ------
        ValueError
            If the orbit properties file is empty or does not exists
        """
        # Decode data using UTF-8 and store in memory for orb props
        df_orb_d = io.StringIO(data_obj.decode('utf-8'))
        # Check file exists or is not empty
        if not df_orb_d.getvalue():
            logging.warning('Required orbit properties file is '
                            'empty for this object')
            raise ValueError('Required orbit properties file is '
                             'empty for this object')

        # Obtain header
        df_head = self._get_head_orb(data_obj)
        self.form = df_head[0]
        self.rectype = df_head[1]
        self.refsys = df_head[2]
        # Check if there is an additional line
        df_check_d = io.StringIO(data_obj.decode('utf-8'))
        # Read as txt file
        df_check = pd.read_fwf(df_check_d, skiprows=[0,1,2,3,4],
                               header=None, engine='python',
                               delim_whitespace=True)
        if 'SOLUTION' in df_check.iloc[0][0]:
            last_skip_rows = [0,1,2,3,4,5,10]
        else:
            last_skip_rows = [0,1,2,3,4,9]
        # Read data as csv
        df_orb = pd.read_csv(df_orb_d, delim_whitespace=True,
                             skiprows=last_skip_rows,
                             engine='python')
        # Epoch in MJD
        self.epoch = df_orb.iloc[1, 1] + ' MJD'
        # MAG
        mag = df_orb.iloc[2:3, 1:3].reset_index(drop=True)
        # MAG - Rename columns and indexes
        mag.index = ['MAG']
        mag.columns = ['', '']
        self.mag = mag
        # LSP
        # Get LSP index
        lsp_index = get_indexes(df_orb, 'LSP')[0][0]
        # Check if there are additional non-gravitational parameters
        if int(df_orb.iloc[lsp_index,3]) == 7:
            lsp = df_orb.iloc[lsp_index:lsp_index+1, 1:5]
            lsp.columns = ['model used', 'number of model parameters',
                       'dimension', '']
            ngr = df_orb.iloc[lsp_index+3:lsp_index+4, 1:3]
            ngr.index = ['NGR']
            ngr.columns = ['Area-to-mass ratio in m^2/ton',
                           'Yarkovsky parameter in 1E-10au/day^2']
        elif int(df_orb.iloc[lsp_index,3]) == 8:
            lsp = df_orb.iloc[lsp_index:lsp_index+1, 1:6]
            lsp.columns = ['model used', 'number of model parameters',
                        'dimension', '', '']
            ngr = df_orb.iloc[lsp_index+3:lsp_index+4, 1:2]
            ngr.index = ['NGR']
            ngr.columns = ['Area-to-mass ratio in m^2/ton',
                           'Yarkov sky parameter in 1E-10au/day^2']
        else:
            lsp = df_orb.iloc[lsp_index:lsp_index+1, 1:4]
            lsp.columns = ['model used', 'number of model parameters',
                       'dimension']
            ngr = ('There are no gravitational parameters '
                        'calculated for this object')
        # Rename indexes
        lsp.index = ['LSP']
        self.lsp = lsp
        # Non-gravitational parameters
        self.ngr = ngr


class KeplerianOrbitProperties(OrbitProperties):
    """This class contains information of keplerian asteroid orbit
    properties. This class inherits the attributes from OrbitProperties.

    Attributes
    ----------
    kep : pandas.DataFrame
        Data frame which contains the keplerian elements information.
    perihelion : int
        Orbit perihelion in au.
    aphelion : int
        Orbit aphelion in au.
    anode : int
        Ascending node-Earth separation in au.
    dnode : int
        Descending node-Earth separation in au.
    moid : int
        Minimum Orbit Intersection distance in au.
    period : int
        Orbit period in days.
    pha : string
        Potential hazardous asteroid classification.
    vinfty : int
        Infinite velocity.
    u_par : int
        Uncertainty parameter as defined by MPC.
    rms : pandas.DataFrame
        Root mean square for keplerian elements
    cov : pandas.DataFrame
        Covariance matrix for keplerian elements
    cor : pandas.DataFrame
        Correlation matrix for keplerian elements

    """

    def __init__(self):
        """Initialization of class attributes
        """
        # Get attributes from paren OrbitProperties
        super().__init__()
        # Orbit properties
        self.kep = []
        self.perihelion = []
        self.aphelion = []
        self.anode = []
        self.dnode = []
        self.moid = []
        self.period = []
        self.pha = []
        self.vinfty = []
        self.u_par = []
        self.rms = []
        # Covariance and correlation matrices
        self.cov = []
        self.cor = []

    def _orb_kep_prop_parser(self, data_obj):
        """Get orbit properties parsed from object data

        Parameters
        ----------
        data_obj : object
            Object data in byte format.

        Raises
        ------
        ValueError
            If the required orbit properties file is empty or does not
            exist
        """
        # Assign parent attributes
        self._orb_prop_parser(data_obj)
        # Decode data using UTF-8 and store in memory for orb props
        df_orb_d = io.StringIO(data_obj.decode('utf-8'))
        # Check file exists or is not empty
        if not df_orb_d.getvalue():
            logging.warning('Required orbit properties file is '
                            'empty for this object')
            raise ValueError('Required orbit properties file is '
                            'empty for this object')
        # Read data as csv
        df_orb = pd.read_csv(df_orb_d, delim_whitespace=True,
                            skiprows=[0,1,2,3,4,9], engine='python')
        # Keplerian elements
        keplerian = df_orb.iloc[0:1, 1:7]
        # Kep - Rename columns and indexes
        keplerian.columns = ['a', 'e', 'i', 'long. node',
                            'arg.s peric.', 'mean anomaly']
        keplerian.index = ['KEP']
        self.kep = keplerian
        # Get perihelion index to provide location for rest of attributes
        perihelion_index = get_indexes(df_orb, 'PERIHELION')[0][0]
        # Perihelion
        self.perihelion = df_orb.iloc[perihelion_index, 2]
        # Aphelion
        self.aphelion = df_orb.iloc[perihelion_index+1, 2]
        # Ascending node - Earth Separation
        self.anode = df_orb.iloc[perihelion_index+2, 2]
        # Descending node - Earth Separation
        self.dnode = df_orb.iloc[perihelion_index+3, 2]
        # MOID (Minimum Orbit Intersection Distance)
        self.moid = df_orb.iloc[perihelion_index+4, 2]
        # Period
        self.period = df_orb.iloc[perihelion_index+5, 2]
        # PHA (Potential Hazardous Asteroid)
        self.pha = df_orb.iloc[perihelion_index+6, 2]
        # Vinfty
        self.vinfty = df_orb.iloc[perihelion_index+7, 2]
        # U_par
        check_upar = get_indexes(df_orb, 'U_PAR')
        # Check if U_par parameter is assigned
        if bool(check_upar) is False:
            self.u_par = 'There is no u_par assigned to this object'
        else:
            self.u_par = df_orb.iloc[check_upar[0][0], 2]

        # Get index for RMS
        rms_index = get_indexes(df_orb, 'RMS')[0][0]
        # Check the dimension of the matrix to give complete RMS
        matrix_dimension = int(self.lsp.iloc[0, 2])
        if matrix_dimension == 8:
            # RMS (Root Mean Square)
            rms = df_orb.iloc[rms_index:rms_index+1, 2:10]
            # Rename colums
            rms.columns = ['a', 'e', 'i', 'long. node', 'arg. peric.',
                       'mean anomaly', 'Area-to-mass ratio',
                       'Yarkovsky parameter']
            ngr_parameter = 'Yarkovsky parameter and Area-to-mass ratio'
        elif matrix_dimension == 7:
            # RMS (Root Mean Square)
            rms = df_orb.iloc[rms_index:rms_index+1, 2:9]
            # Check which of NGR parameters is 0 to rename cols
            if float(self.ngr.iloc[0][0]) == 0:
                ngr_parameter = 'Yarkovsky parameter'
            else:
                ngr_parameter = 'Area-to-mass ratio'
            # Rename columns
            rms.columns = ['a', 'e', 'i', 'long. node',
                               'arg. peric.', 'mean anomaly',
                               ngr_parameter]
        else:
            # RMS (Root Mean Square)
            rms = df_orb.iloc[rms_index:rms_index+1, 2:8]
            #Rename columns
            rms.columns = ['a', 'e', 'i', 'long. node', 'arg. peric.',
                       'mean anomaly']
            ngr_parameter = 'There are no additional NRG parameters'

        # RMS - Rename indexes
        rms.index = ['RMS']
        self.rms = rms
        # Covariance matrix
        self.cov = self._get_matrix(df_orb, 'cov', matrix_dimension,
                                   'keplerian', ngr=ngr_parameter)
        # Correlation matrix
        self.cor = self._get_matrix(df_orb, 'cor', matrix_dimension,
                                   'keplerian', ngr=ngr_parameter)


class EquinoctialOrbitProperties(OrbitProperties):
    """This class contains information of equinoctial asteroid orbit
    properties. This class inherits the attributes from OrbitProperties.

    Attributes
    ----------
    equinoctial : pandas.DataFrame
        Data frame which contains the equinoctial elements information.
    rms : DataFrame
        Root Mean Square for equinoctial elements.
    eig : pandas.DataFrame
        Eigenvalues for the covariance matrix.
    wea : pandas.DataFrame
        Eigenvector corresponding to the largest eigenvalue.
    cov : pandas.DataFrame
        Covariance matrix for equinoctial elements.
    nor : pandas.DataFrame
        Normalization matrix for equinoctial elements.

    """

    def __init__(self):
        """Initialization of class attributes
        """
        # Get attributes from paren OrbitProperties
        super().__init__()
        # Orbit properties
        self.equinoctial = []
        self.rms = []
        self.eig = []
        self.wea = []
        # Covariance and nor matrices
        self.cov = []
        self.nor = []

    def _orb_equi_prop_parser(self, data_obj):
        """Get orbit properties parsed from object data

        Parameters
        ----------
        data_obj : object
            Object data in byte format.

        Raises
        ------
        ValueError
            If the required orbit properties file is empty or does not
            exist
        """
        # Assign parent attributes
        self._orb_prop_parser(data_obj)
        # Decode data using UTF-8 and store in memory for orb props
        df_orb_d = io.StringIO(data_obj.decode('utf-8'))
        # Check file exists or is not empty
        if not df_orb_d.getvalue():
            logging.warning('Required orbit properties file is '
                            'empty for this object')
            raise ValueError('Required orbit properties file is '
                            'empty for this object')
        # Check if there is an additional line
        df_check_d = io.StringIO(data_obj.decode('utf-8'))
        # Read as txt file
        df_check = pd.read_fwf(df_check_d, skiprows=[0,1,2,3,4],
                               header=None, engine='python',
                               delim_whitespace=True)
        if 'SOLUTION' in df_check.iloc[0][0]:
            last_skip_rows = [0,1,2,3,4,5,10]
        else:
            last_skip_rows = [0,1,2,3,4,9]

        # Read data as csv
        df_orb = pd.read_csv(df_orb_d, delim_whitespace=True,
                            skiprows=last_skip_rows, engine='python')
        # Equinoctial elements
        equinoctial = df_orb.iloc[0:1, 1:7]
        # Equinoctial - Rename columns and indexes
        equinoctial.columns = ['a', 'e*sin(LP)', 'e*cos(LP)',
                               'tan(i/2)*sin(LN)', 'tan(i/2)*cos(LN)',
                               'mean long.']
        equinoctial.index = ['EQU']
        self.equinoctial = equinoctial
        # Get index for RMS
        rms_index = get_indexes(df_orb, 'RMS')[0][0]
        # Check the dimension of the matrix to give complete RMS
        matrix_dimension = int(self.lsp.iloc[0, 2])
        if matrix_dimension == 8:
            # RMS (Root Mean Square)
            rms = df_orb.iloc[rms_index:rms_index+1, 2:10]
            # EIG
            eig = df_orb.iloc[rms_index+1:rms_index+2, 2:10]
            # WEA
            wea = df_orb.iloc[rms_index+2:rms_index+3, 2:10]
            # Assign column names
            column_names = ['a', 'e*sin(LP)', 'e*cos(LP)',
                            'tan(i/2)*sin(LN)', 'tan(i/2)*cos(LN)',
                            'mean long.', 'Area-to-mass ratio',
                            'Yarkovsky parameter']
            ngr_parameter = 'Yarkovsky parameter and Area-to-mass ratio'

        elif matrix_dimension == 7:
            # RMS (Root Mean Square)
            rms = df_orb.iloc[rms_index:rms_index+1, 2:9]
            # EIG
            eig = df_orb.iloc[rms_index+1:rms_index+2, 2:9]
            # WEA
            wea = df_orb.iloc[rms_index+2:rms_index+3, 2:9]
            # Check which of NGR parameters is 0 to rename cols
            if float(self.ngr.iloc[0][0]) == 0:
                ngr_parameter = 'Yarkovsky parameter'
            else:
                ngr_parameter = 'Area-to-mass ratio'
            # Assign column names
            column_names = ['a', 'e*sin(LP)', 'e*cos(LP)',
                               'tan(i/2)*sin(LN)', 'tan(i/2)*cos(LN)',
                               'mean long.',
                               ngr_parameter]
        else:
            # RMS (Root Mean Square)
            rms = df_orb.iloc[rms_index:rms_index+1, 2:8]
            # EIG
            eig = df_orb.iloc[rms_index+1:rms_index+2, 2:8]
            # WEA
            wea = df_orb.iloc[rms_index+2:rms_index+3, 2:8]
            # Assign column names
            column_names = ['a', 'e*sin(LP)', 'e*cos(LP)',
                           'tan(i/2)*sin(LN)', 'tan(i/2)*cos(LN)',
                           'mean long.']
            ngr_parameter = 'There are no additional NRG parameters'

        # Rename columns
        rms.columns = eig.columns = wea.columns = column_names
        # RMS - Rename indexes
        rms.index = ['RMS']
        self.rms = rms
        # EIG - Rename indexes
        eig.index = ['EIG']
        self.eig = eig
        # EIG - Rename indexes
        wea.index = ['WEA']
        self.wea = wea
        # Covariance matrix
        self.cov = self._get_matrix(df_orb, 'cov', matrix_dimension,
                                   'equinoctial', ngr=ngr_parameter)
        # Correlation matrix
        self.nor = self._get_matrix(df_orb, 'nor', matrix_dimension,
                                   'equinoctial', ngr=ngr_parameter)


class Ephemerides:
    """This class contains information of object ephemerides.

    Attributes
    ----------
    observatory : str
        Name of the observatory from which ephemerides are obtained.
    tinit : str
        Start date from which ephemerides are obtained.
    tfinal : str
        End date from which ephemerides are obtained.
    tstep : str
        Time step and time unit used during ephemerides calculation.
    ephemerides : pandas.DataFrame
        Data frame which contains the information of the object
        ephemerides

    """

    def __init__(self):
        """Initialization of class attributes
        """
        # # Document info
        self.observatory = []
        self.tinit = []
        self.tfinal = []
        self.tstep = []
        # Orbit properties
        self.ephemerides = []

    @staticmethod
    def _get_head_ephem(data_obj):
        """Get and parse header of ephemerides file.

        Parameters
        ----------
        data_obj : object
            Object in bytes format.

        Returns
        -------
        obs : str
            Observatory name.
        idate : str
            Start date of the ephemerides.
        fdate : str
            Final date of the ephemerides.
        tstep : str
            Value and units for time step.
        """
        data_d = io.StringIO(data_obj.decode('utf-8'))
        head_ephe = pd.read_fwf(data_d, nrows=5, header=None)
        # Template for observatory
        parse_obs = 'Observatory: {observatory}'
        # Parse required data for attributes
        obs = parse(parse_obs, head_ephe[0][1])
        obs = obs['observatory']
        # Template for initial date
        parse_idate = 'Initial Date: {init_date}'
        # Parse required data for attributes
        idate = parse(parse_idate, head_ephe[0][2])
        idate = idate['init_date']
        # Template for initial date
        parse_fdate = 'Final Date: {final_date}'
        # Parse required data for attributes
        fdate = parse(parse_fdate, head_ephe[0][3])
        fdate = fdate['final_date']
        # Template for initial date
        parse_step = 'Time step: {step}'
        # Parse required data for attributes
        tstep = parse(parse_step, head_ephe[0][4])
        tstep = tstep['step']

        return obs, idate, fdate, tstep

    def _ephem_parser(self, name, observatory, start, stop, step, step_unit):
        """Parse and arrange the ephemeries data.

            Parameters
            ----------
            name : str
                Name of the requested object.
            observatory :
                Name of the observatory from which ephemerides are obtained.
            start : str
                Start date from which ephemerides are obtained.
            stop : str
                End date from which ephemerides are obtained.
            step : str
                Value for the time step (e.g. '1', '0.1', etc.)
            step_unit : str
                Units of the time step
            Raises
            ------
            KeyError
                Some of the parameters introduced in the method is not
                valid.
        """
        # Unique base url for asteroid properties
        url_ephe = EPHEM_URL + str(name).replace(' ', '%20') +\
            '&oc=' + str(observatory) + '&t0=' +\
            str(start).replace(' ', 'T') + 'Z&t1=' +\
            str(stop).replace(' ', 'T') + 'Z&ti=' + str(step) +\
            '&tiu=' + str(step_unit)

        # Request data two times if the first attempt fails
        try:
            # Get object data
            data_obj = requests.get(url_ephe).content

        except ConnectionError:
            print('Initial attempt to obtain object data failed. '
                  'Reattempting...')
            logging.warning('Initial attempt to obtain object data'
                           'failed.')
            # Wait 5 seconds
            time.sleep(5)
            # Get object data
            data_obj = requests.get(url_ephe).content

        # Check if file contains errors due to bad URL keys
        check = io.StringIO(data_obj.decode('utf-8'))
        check_r = pd.read_fwf(check, delimiter='"', header=None)
        if len(check_r) == 1:
            error = check_r[0][0]
            raise KeyError(error)

        # Get ephemerides if file is correct
        ephems_d = io.StringIO(data_obj.decode('utf-8'))
        # Since ephemerides col space is fixed, it is defined in order
        # to set the length (number of spaces) for each field
        col_space = [(1,12), (13,19), (20,32), (34,37), (37,40),
                     (40,47), (49,52), (52, 55), (55,61), (62,67),
                     (68,73), (74,82), (83, 89), (90,96), (97,103),
                     (104,110), (111,116), (116,122), (123,130),
                     (131,138), (140,148), (150,158), (160,168),
                     (170,178), (178,184)]
        # Read pandas as txt
        ephem = pd.read_fwf(ephems_d, header=None, skiprows=9,
                            engine='python', colspecs=col_space,
                            skipfooter=2)
        # Rename columns
        ephem.columns = ['Date', 'Hour', 'MJD', 'H', 'M', 'S', 'D',
                         '\'','"','Mag','Alt', 'Airmass', 'Sun elev.',
                         'SolEl (deg)', 'LunEl (deg)', 'Phase (deg)',
                         'Glat (deg)', 'Glon (deg)', 'R (au)',
                         'Delta (au)', 'Ra*cosDE ("/min)',
                         'DEC ("/min)', 'Err1', 'Err2', 'PA']
        # Convert Date to datetime format and show it as in portal
        ephem['Date'] = pd.to_datetime(ephem['Date'], format="%d %b %Y")
        ephem['Date'] = ephem['Date'].dt.strftime("%d %b %Y")
        # Remove mid whitespaces from declination, if any, and apply int
        # format
        if ephem['D'].dtype == str:
            ephem['D'] = ephem['D'].str.replace(' ','').astype(int)

        # Assign attributes
        self.ephemerides = ephem
        self.observatory = self._get_head_ephem(data_obj)[0]
        self.tinit = self._get_head_ephem(data_obj)[1]
        self.tfinal = self._get_head_ephem(data_obj)[2]
        self.tstep = self._get_head_ephem(data_obj)[3]


class Summary:
    """This class contains the information from the Summary tab.

    Attributes
    ----------
    physical_properties : pandas.DataFrame
        Data frame which contains the information of the object
        physical properties, their value and their units.
    discovery_date : str
        Provides the object discovery date
    observatory : str
        Provides the name of the observatory where object was discovered

    """

    def __init__(self):
        """Initialization of parameters
        """
        self.physical_properties = []
        self.discovery_date = []
        self.observatory = []

    def _summary_parser(self, name):
        """Parse and arrange the summary data

        Parameters
        ----------
        name : str
            Name of the requested object
        """
        # Final url = SUMMARY_URÑ + desig in which white spaces,
        # if any, are replaced by %20 to complete the designator
        url = SUMMARY_URL + str(name).replace(' ', '%20')

        # Read the url as html
        try:
            contents = requests.get(url).content
        except contents.DoesNotExist as contents_not_exist:
            logging.warning('Object not found: the name of the '
                            'object is wrong or misspelt')
            raise ValueError('Object not found: the name of the '
                             'object is wrong or misspelt') from\
                                 contents_not_exist
        # Parse html using BS
        parsed_html = BeautifulSoup(contents, 'lxml')
        # Summary properties are in </div>. Search for them:
        props = parsed_html.find_all("div",
                                     {"class": "simple-list__cell"})
        # Convert properties from BS to string type
        props_str = str(props).replace('<div class="simple-list__cell">',
                                    '').replace('</div>', '').\
                                        replace(',', '').strip()
        # Convert into bytes to allow pandas read
        props_byte = io.StringIO(props_str)
        props_df = pd.read_fwf(props_byte, engine='python', header=None)
        # Diameter property is an exception. Use BS to find and parse it
        diameter = parsed_html.find_all("span",
                                        {"id": "_NEOSearch_WAR_PSDBportlet_:"\
                                         "j_idt10:j_idt639:diameter-value"})
        # Obtain the text in the span location. Note that the diameter type
        # will be str since * can be given in the value
        diam_p = BeautifulSoup(str(diameter), 'html.parser').span.text
        # Get indexes to locate the required properties.
        # In this code only the location of Absolute Magnitude is obtained
        index = get_indexes(props_df, 'Absolute Magnitude (H)')
        index = index[0][0]
        # Adding a second index for Rotation Period since diameter can
        # change the dimensions of the line
        red_index = get_indexes(props_df, 'Rotation period (T)')
        red_index = red_index[0][0]
        physical_properties = {'Physical Properties':
                                ['Absolute Magnitude (H)',
                                 'Diameter', 'Taxonomic Type',
                                 'Rotation Period (T)'],
                               'Value': [props_df[0][index+1],
                                        diam_p,
                                        props_df[0][index+9],
                                        props_df[0][red_index+1]],
                               'Units': [props_df[0][index+2],
                                        props_df[0][index+7],
                                        ' ',
                                        props_df[0][red_index+2]]}
        # Create DataFrame
        physical_properties_df = pd.DataFrame(physical_properties)
        self.physical_properties = physical_properties_df
        # Assign attributes for discovery date and observatory
        discovery_date = props_df[0][red_index+4]
        self.discovery_date = discovery_date
        observatory = props_df[0][red_index+6]
        self.observatory = observatory
