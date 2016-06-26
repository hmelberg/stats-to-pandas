
# coding: utf-8

# # stats-to-pandas

# A tool to make it easier to download data to a pandas dataframe from
# Statistics Norway (and other agencies) using json-stat to a Pandas dataframe.
# Hans Olav Melberg, 9. June, 2016

#%% Required modules
from __future__ import print_function

import pandas as pd
import requests
import ast
from pyjstat import pyjstat
from collections import OrderedDict

# todo: consider using jsonstat instead of pyjstat


#%% Defaults (not yet implemented)

# This is mainly to make the script flexible for future changes
# Makes it easier to use the same script for sources other than Statistics Norway
# The user can set a different source to be the default
# (note to self: is the extra complexity worth it? 
# more complex since functions now require defaults to be used easily)

#Statistics_Norway = {'base_url' : ['http://data.ssb.no/api/v0'], 
#                     'language' : ['en', 'no'], 
#                     'api_key' : [None]}

# Add more sources here Statistics_Sweden = {...} etc

# set a default
#default = Statistics_Norway

# make a list of the different sources
#sources = ['Statistics_Norway']



#%%

def search(phrase, 
           language = 'en', 
           base_url = 'http://data.ssb.no/api/v0'
           premade = False):
    """
        Search for tables that contain the phrase in Statistics Norway.
        Returns a pandas dataframe with the results.
            
        Example
        -------
        
            df = search("income")
        
        
        Parameters
        ----------
        
        phrase: string
            The phrase can contain several words (space separated): 
                search("export Norwegian parrot")
            
            It also supports trucation: 
                search("pharma*")
                
            Not case sensitive.
            Language sensitive (specified in the language option)
            
        language: string 
            default in Statistics Norway: 'en' (Search for English words) 
            optional in Statistics Norway: 'no' (Search for Norwegian words)
                   
        url: string
            default in Statistics Norway: 'http://data.ssb.no/api/v0'
            different defaults can be specified
        
        premade: boolean
            if True, searches only among the subset of premade tables
            if False searches all tables
            default: False
       
       Returns
       -------
       
       A pandas dataframe
       
        """
    # search among premade tables (only) if premade parameter is True
    url = 'http://data.ssb.no/api/v0/dataset'    
    if premade:        
        url = '{url}?lang={language}'.format(url = url,
                                             language = language)
        df = pd.read_html(url)
        df = df[0]
        df.index = df['ID']
        df = df.iloc[:,[0,1]]
        df = df.sort_index()
        phrase = phrase.lower()
        
        if phrase != '*':
            df = df[(df.iloc[:,0].str.lower().str.contains(phrase)) | 
                    (df.iloc[:,1].str.lower().str.contains(phrase)) ]
    
    # search among all tables (not premade) if premade parameter is False                
    if not premade:
        # todo: make converter part of the default specification only for statistics norway
        convert = {'æ' : '%C3%A6', 'Æ' : '%C3%86', 'ø' : '%C3%B8', 'Ø' : '%C3%98', 
                 'å' : '%C3%A5', 'Å' : '%C3%85',
                 '"' : '%22', '(' : '%28', ')' : '%29', ' ' : '%20'}
    
        search_str = '{base_url}/{language}/table/?query={phrase}'.format(
            base_url = base_url, 
            language = language, 
            phrase = phrase)
        
        for k, v in convert.items():
            search_str = search_str.replace(k, v)
        
        df = pd.read_json(search_str)
        
        if len(df) == 0:
            print("No match")
            return df
        
        # make the dataframe more readable
        # (is it worth it? increases vulnerability. formats may differ and change)
        # todo: make search and format conditional on the database being searched    
           
        # split the table name into table id and table text
        df['table_id'] = df['title'].str.split(':').str.get(0)
        df['table_title'] = df['title'].str.split(':').str.get(1)
        del df['title']
        
        # make table_id the index, visually more intuitive with id as first column
        df = df.set_index('table_id')
        
        # change order of columns to make it more intuitive (table_title is first) 
        cols = df.columns.tolist()
        cols.sort(reverse = True)
        df = df[cols[:-2]]

    return df


#%% 

def get_variables(
        table_id = None,
        source = None, 
        language = 'en',
        base_url = 'http://data.ssb.no/api/v0',
        full_url = None):
    """
        Returns a list. 
        
        Each element of the list is a dictionary that provides more 
        information about a variable. 
        
        For instance, one variable may contain information about the
        different years that are available.
        
        
        Parameters
        ----------
    
            table_id: string
                the unique table_id number, a string including leading zeros.
                                
            language: string
                default 'en' (default, English) 
                optional: 'no' (Norwegian)
            
            base_url: string
                base url locating the table (not including table identifier)
            
            full_url: string 
                The full url to the table.
                If full_url is specified, other paramaters are ignored.
                
    """
    
    if full_url is None:
          full_url = '{base_url}/{language}/table/{table_id}'.format(
            base_url = base_url, language = language, table_id = table_id)
    
    df = pd.read_json(full_url)
    variables = [dict(values) for values in df.iloc[:,1]]
    
    return variables


#%%

def to_dict(json_str):
    """
        Transforms a string to a dictionary.
        
        Note: Will fail if string is not correctly specified.
    """
    # OK, really unnecessary func, but a concession to less experienced users
    # todo: use json module instead, json.dumps()
    query = ast.literal_eval(json_str)
    return query
    

#%%
def read(box = None, 
         table_id = None,
         premade = False, 
         language = 'en', 
         query = None, 
         base_url = 'http://data.ssb.no/api/v0/dataset', 
         full_url = None):
             
    """
    Returns a pandas dataframe with data for the specified table.
    
    Parameters
    ----------    
    box : widget container
        the name of the widget container that contains the specification
            of which variables and values to use to create the table

        If box is specified, no other parameter is needed since the widget
        contains all the information needed to create and download a table.
    
    table_id : string
        the table_id for the table to be downloaded. 
        
        If table_id is given, the user also has to specify one or more 
        arguments to indicate what variables and values that should be used.
        The following arguments can be used:
            - premade : boolean
                if False (default), read builds a table based on the other 
                    arguments
                
                if True, read downloads the data for table_id from the
                (limited) set of premade tables that do not need further 
                specifications.
            - language                
        
        
        
        
        
    
    Useful if 
        - you know exactly what you are looking for and
        - can specify the json yourself (as a dictionary)
        - you do not want to use the notebook/widgets/box to specify the json query
        
    Hints
    -----
        - use full_json(table_id = '10714', out = 'string') to get a query string and edit it
        - use to_dict(str) to get a dict from an edited json string
            
    Example
    -------
    json_query = {'response': {'format': 'json-stat'}, 
        'query': [
        {'selection': {'values': ['0'], 'filter': 'item'}, 'code': 'Region'}, 
        {'selection': {'values': ['KufjolsIAlt'], 'filter': 'item'}, 'code': 'ContentsCode'}, 
        {'selection': {'values': ['1999', '2013'], 'filter': 'item'}, 'code': 'Tid'}]}
        }
    
    df = read_with_json(table_id = '10714', query = json_query)
    """
    if box:
        query = get_json(from_box)
        url = from_box.children[3].value
        data = requests.post(url, json = query)
        results = pyjstat.from_json_stat(data.json(object_pairs_hook=OrderedDict))
        return results[0]

    elif premade:
        base_url = 'http://data.ssb.no/api/v0/dataset'
        full_url = '{base_url}/{table_id}.json?lang={language}'.format(
                                            base_url = base_url,
                                            table_id = str(table_id), 
                                            language = language)
        data = requests.get(full_url)
        df = pyjstat.from_json_stat(data.json(object_pairs_hook=OrderedDict))
        df = df[0]
       
    elif query:
        if query = 'all':
            query = full_json(table_id = None, 
                              out = 'dict', 
                              language = 'en',
                              full_url = None)
        else:
            full_url = '{base_url}/{language}/table/{table_id}'.format(
                                            base_url = base_url, 
                                            language = language, 
                                            table_id = table_id)
                    
                data = requests.post(full_url, json = query)
                df = pyjstat.from_json_stat(data.json(object_pairs_hook=OrderedDict))
                df = df[0]

    elif full_url:
        data = requests.get(full_url)
        df = pyjstat.from_json_stat(data.json(object_pairs_hook=OrderedDict))
        df = df[0]
            
    return df

#%% 
def get_json(box = None, 
             out = 'dict', 
             language = 'en',
             table_id = None,
             values = 'box',
             full_url = None):
        
    """
    Returns a json query used to selects variables and values.
    
  
    Parameters
    ----------
    
    box : widget container 
        name of widget box with the selected variables
        
    out : string 
        default: 'dict', options: 'str'
        
        The json can be returned as a dictionary or a string.
        The final query should use a dict, but some may find it useful to
        get the string and edit it before transforming it back to a dict.
    
    table_id: string
        the table_id of the table you want to query 
    
    values : string
        a general description of the variables you want to select from table_id 
        with the query. Alternatives
          'box' (default): the variables and values selected in the widget box
          'all' : all values for all variables
          'recent' : only the most recent value for all variables
          'first n'
          'last n'
             
    If box is specified, no table_id need to be specified (and will be ignored)
    
    Examples
    --------
    
    json_query = get_json(box)
    
    json_query = get_json(table_id = '10714', values = 'all')
    
    json_query = get_json(table_id = '10714', values = 'all', out = 'string')  
    
    
    Note
    ----
    
    The function is useful if
        - you do not want to use the widget gui/notebook to build the query
        - but want a starting point to revise and specify a query 
    
    You may want to edit the content of the query as a dictionary, or as a 
    string, edit it, and retransform it to a dictionary.
        
    To transform a string to a dict, use the function:
        
            query = to_dict(json_str)
        
    
    """
    if values = 'box':            
        table_url = box.children[3].value
        variables = get_variables(full_url = table_url)
        nvars = len(box.children[2].children)
        
     
    elif values = 'all':
        variables = get_variables(table_id, language = language, full_url = full_url)
        nvars = len(variables)
        
    # todo: add other options 'recent' (i.e. top) etc
    
    var_list = list(range(nvars))           
    query_element = {}
    
    for x in var_list:
        query_element[x] ='{{"code": "{code}", "selection": {{"filter": "item", "values": {values} }}}}'.format(
                code = variables[x]['code'], 
                values = variables[x]['values']) 
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
