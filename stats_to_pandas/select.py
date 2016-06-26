# coding: utf-8

# # stats-to-pandas

# A tool to make it easier to download data to a pandas dataframe from Statistics Norway (and other agencies) using json-stat to a Pandas dataframe. 

# Hans Olav Melberg, 9. June, 2016

#%% Required modules
from __future__ import print_function

import pandas as pd
import requests
import ast
from pyjstat import pyjstat
from collections import OrderedDict
from ipywidgets import widgets
from IPython.display import display
# todo: consider using jsonstat instead of pyjstat


def select(table_id = None, 
           language = 'en', 
           base_url = 'http://data.ssb.no/api/v0', 
           full_url = None):
    """
    Selects a table based on the table_id and returns a widget container 
    in which the user can select the set of variables and values to be 
    included in the final table.
    
    
    Example
    --------
    box = select(table_id = '10714')
    
    
    Parameters
    ----------    
    
        table_id : string 
            the id of the desired table
         
        language: string
            language for table
            'en' (default, English) 
            'no' (Norwegian): 
            language for table
        
        base_url: string.
            base url locating the table (not including table_id)
        
        full_url: string
            the full url to the table
    """
        
    # get table_id not full url was specified 
    if full_url is None:
        full_url = '{base_url}/{language}/table/{table_id}'.format(
                    base_url = base_url, 
                    language = language, 
                    table_id = table_id)
        
    table_info = pd.read_json(full_url)
    table_title = table_info.iloc[0,0]

    # get a list with dictionaries containing information about each variable
    variables = get_variables(table_id = table_id, 
                              language = language,
                              base_url = base_url,
                              full_url = full_url)
    
    # get number of variables (ok, childish approach, can be simplified!)
    nvars = len(variables)
    var_list = list(range(nvars))
    
    # a list of dictionaries of the values available for each variable
    option_list = [OrderedDict(zip(variables[var]['valueTexts'], 
                                   variables[var]['values'])) 
                   for var in var_list]
    
    # create a selection widget for each variable
    # todo: skip widget or make it invisible if there is only one option?
    # todo: make first alternative a default selection initially for all tables?
    # todo: add buttons for selecting "all", "latest" , "first" and "none"
                         
    selection_widgets = [widgets.widget_selection.SelectMultiple(
                            options = option_list[var], 
                            height = 400, 
                            width = 500) 
                         for var in var_list]
    
    # put all the widgets in a container
    variables_container = widgets.Tab(selection_widgets)

    # label each container with the variable label 
    for var in var_list:
        title = str(variables[var]['text'])
        variables_container.set_title(var, title)
    
    # build widgets and put in one widget container
    headline = widgets.Label(value = table_title, color = 'blue')
    
    endline = widgets.Label(value = '''Select category and click on elements 
        to be included in the table (CTRL-A selects "all")''')
    
    url_text = widgets.Label(value = full_url)
    
    selection_container = widgets.VBox([headline, 
                                        endline, 
                                        variables_container, 
                                        url_text])
    
    selection_container.layout.border = '3px grey solid'
    # may include a "click here when finished" just to make it more intuitive?
    return selection_container



#%% 
def get_json(box=None, 
             out = 'dict', 
             language = 'en'):
    """
    Takes a widget container as input (where the user has selected varables) 
    and returns a json dictionary or string that will fetch these variables. 
    
    The json follows the json-stat format.
    
    Parameters
    ----------
    
    box : widget container 
        name of widget box with the selected variables
    
    out : string 
        default: 'dict', options: 'str'
        
        The json can be returned as a dictionary or a string.
        The final end query should use a dict, but some may find it useful to
        get the string and revise it before transforming it back to a dict.
    
    
    Example
    -------
    
    json_query = get_json(box)
    
    """
        
    table_url = box.children[3].value
    variables = get_variables(full_url = table_url)
    nvars = len(box.children[2].children)
    var_list = list(range(nvars))
    query_element = {}
    
    # create a dict of strings, one for each variable that specifies 
    # the json-stat that selects the variables/values
    
    for x in var_list:
        value_list = str(list(box.children[2].children[x].value))
        query_element[x] = '{{"code": "{code}", "selection": {{"filter": "item", "values": {values} }}}}'.format(
            code = variables[x]['code'], 
            values = value_list)
        query_element[x] = query_element[x].replace("\'", '"')
    
    all_elements = str(list(query_element.values()))
    all_elements = all_elements.replace("\'", "")

    query = '{{"query": {all_elements} , "response": {{"format": "json-stat" }}}}'.format(all_elements = all_elements)
    
    if out == 'dict':
        query = ast.literal_eval(query)
    
  
    # todo: build it as a dictionary to start with (and not a string that is made into a dict as now)
    # todo: add error message if required variables are not selected
    # todo: avoid repeat downloading of same information 
    # eg. get_variables is sometimes used three times before a table is downloaded
    
    return query

#%%

def read_box(from_box):
    """
    Takes a widget container as input (where the user has selected varables) 
    and returns a pandas dataframe with the values for the selected variables.
    
    Example
    -------
    
    df = read_box(box)
    
    """
    query = get_json(from_box)
    url = from_box.children[3].value
    data = requests.post(url, json = query)
    results = pyjstat.from_json_stat(data.json(object_pairs_hook=OrderedDict))
    return results[0]



