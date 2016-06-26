
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
           base_url = 'http://data.ssb.no/api/v0'):
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
       
        """
    
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
    
    #print(search_str)    
    
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


#%% 

def read_with_json(table_id = None, 
              query = None, 
              language = 'en', 
              base_url = 'http://data.ssb.no/api/v0', 
              full_url = None):
    """
    Returns a pandas dataframe with the values for the table specified by 
    table_id and an explicit json string (in json-stat format).
    
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
    if full_url is None:
        
        full_url = '{base_url}/{language}/table/{table_id}'.format(
            base_url = base_url, 
            language = language, 
            table_id = table_id)
        
    data = requests.post(full_url, json = query)
    results = pyjstat.from_json_stat(data.json(object_pairs_hook=OrderedDict))
    return results[0]



#%%

def read_url(full_url = None, 
             table_format = 'json'):
    """
    Returns a pandas dataframe of the premade table indicated by the premade 
    table_id or the full_url.
    
    Note: The premade table id may be different from the normal table id.
    """
      
    if table_format == 'json':
        data = requests.get(full_url)
        df = pyjstat.from_json_stat(data.json(object_pairs_hook=OrderedDict))
        df = df[0]
        
    elif table_format == 'csv':
        df = pd.read_csv(full_url)
    else:
        print("""Table_format is incorrectly specified. 
              It must be 'json-stat' or 'csv'""")
        df = None
    return df



#%%

def search_premade(phrase = '*',
                   language = 'en',
                   url = 'http://data.ssb.no/api/v0/dataset'):
    
    """
    Returns a pandas dataframe with the tables matching the tags specified in the search.
    
    Note that the function does not search in the headline of the tables, but in the tags.
    
    The search is exact, so it may be better to get a list of all tables 
    (use phrase = '*' or just leave it unspecified)
    
    The ID column contains a special table id for premade tables 
    (use this is when specifying the table to be downloaded)
    
    Example:
        
        tables = search_url_tables('population')
    
    
    """
    url = '{url}?lang={language}'.format(
        url = url,
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
    return df

# to do: merge the two search functions?
# make premade an bool arg in the search. 
# also allow full_url



#%%

def read_premade(premade_id = None, 
            language = 'en', 
            base_url = 'http://data.ssb.no/api/v0/dataset', 
            full_url = None, 
            table_format = 'json'):
    """
    Returns a pandas dataframe of the premade table indicated by the premade 
    table_id or the full_url.
    
    Note: The premade table id may be different from the normal table id.
    """
    
    if full_url is None:
        full_url = '{base_url}/{premade_id}.{table_format}?lang={language}'.format(
                base_url = base_url,
                premade_id = str(premade_id), 
                language = language,
                table_format = table_format)
    #print(full_url)
    
    if table_format == 'json':
        data = requests.get(full_url)
        df = pyjstat.from_json_stat(data.json(object_pairs_hook=OrderedDict))
        df = df[0]
        
    elif table_format == 'csv':
        df = pd.read_csv(full_url)
    else:
        print("""Table_format is incorrectly specified. 
              It must be 'json-stat' or 'csv'""")
        df = None
    return df


#%%

def full_json(table_id = None, 
              out = 'dict', 
              language = 'en', 
              full_url = None):
    """
    Returns the json query for getting all the values for all options for a table.
    Useful if
        - you do not want to use the widgets/notebook to build the query
        - but want a starting point to revise and specify a the query instead of building it from the ground.
    
    Note
        - The json is a dictionary. You may want to edit the content of the dictionary directly,
        or make it a string, edit it as a string, and retransform it to a dictionary.
        
        To transform a string to a dict, use the function:
        
            query = to_dict(json_str)
        
    Example
    -------
    
    query = full_json(table_id = '10714', out = 'string')
    
    """
    
    variables = get_variables(table_id, language = language, full_url = full_url)
    nvars = len(variables)
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
    
    return query


#%%

def read_all(table_id = None, 
             language = 'en',
             base_url = 'http://data.ssb.no/api/v0', 
             full_url = None):
    """
    Returns a pandas dataframe with all values for all options 
    for the table specified by table_id
    
    Warning: The table may be large
    
    Useful if 
        - you know exactly what you are looking for and
        - you do not want to use the notebook/widgets/box to specify the json query)
    
    Example
    
    df = read_all(table_id = '10714')
    
    """
    
     
    if full_url is None:        
        full_url = '{base_url}/{language}/table/{table_id}'.format(
            base_url = base_url,
            language = language, 
            table_id = table_id)
        
    query = full_json(full_url = full_url)
    data = requests.post(full_url, json = query)
    results = pyjstat.from_json_stat(data.json(object_pairs_hook=OrderedDict))
    
    # maybe this need not be its own function, 
    # but an option in read_json? json = 'all'
    
    # other functions(options include: read_recent to get only the 
    # most recent values (defined as x), json = 'recent')
    
    return results[0]


