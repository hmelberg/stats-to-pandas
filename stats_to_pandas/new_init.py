# coding: utf-8

# # stats-to-pandas

# A tool to make it easier to download data to a pandas dataframe from Statistics Norway (and other agencies) using json-stat to a Pandas dataframe. 

# Hans Olav Melberg, 9. June, 2016




"""
Download data from Statistics Norway and other json-stat sources to a dataframe
===============================================================================

Functions: General Use
----------------------
:func:`search`
    returns a pandas dataframe with the tables containing a phrase or keyword
:func:`read_url`
    reads the table at the specified url using the json-stat format
:func:`read_with_json`
    reads the table_id and extracts the information specified in the json dict
:func:`read_premade`
    reads the premade table specified by table_id
:func:`read_premade`
    reads the premade table specified by table_id 
:func:`get_json`
    return the json-stat query that specifies a data download
:func:`get_variables`
    return a dictionary of the variables and values that can be selected in a specified table
:func:`to_dict`
    converts a string to a dictionary
    
    
Functions: Jupyter Notebook
---------------------------
:func:`show`
    show and select variables and values in widget gui
:func:`read(box = box)`
    download the data as specified in the gui box to a pandas dataframe
"""

__all__ = ["__version__",
           "get_json", "get_variables", "read", "search", "select", "to_dict"]

__title__ = 'stats_to_pandas'
__version__ = '0.0.8'
__author__ = 'Hans Olav Melberg'
__license__ = 'MIT'


from . import urls
from ._display import *


