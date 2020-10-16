# stats-to-pandas
Download data from statistical agencies to pandas dataframes and easily get the json-stat query required to download different types of tables. 

[Demo on YouTube](https://www.youtube.com/watch?v=hhj7ITIU3F8)

## Installation

    pip install stats_to_pandas

## Requirements
    - pandas
    - requests
    - pyjstat
    - Jupyter notebook, IPython, ipywidgets

## Overview

##### 0. Import package

    import stats_to_pandas as stp
    
##### 1. Search for tables based on keywords

    stp.search('cows')

##### 2. Select a table id from the dataframe and create a gui-box to select the variables to be included
(Works when the user is in a jupyter notebook and has widgets installed)

    box = stp.select(table_id = '10714')

##### 3. Read the variable selection from the gui-box and download the data from Statistics Norway

    df = stp.read_box(box)

##### Or just get the json query that specify the data selected in the gui-box 

    query = stp.get_json(box)

## 4. More
##### Read all values for all variables for table with id 10714
(Avoid having to select variables, step 2 above, but may result in large tables)

    df = stp.read_all(table_id = '10714')

##### Get the json string for a full query of table number 10714

    query = stp.full_json(table_id = '10714', out = 'str')

##### Get the json dict for a full query of table number 10714

    query = stp.full_json(table_id = '10714', out = 'dict')

##### Get the json dict associated with the current selection from a widget box

    query = stp.get_json(box)

##### Read data from Statistics Ireland

    irl_url = 'http://www.cso.ie/StatbankServices/StatbankServices.svc/jsonservice/responseinstance/CNA31'
    
    df = stp.read_url(full_url = irl_url)
