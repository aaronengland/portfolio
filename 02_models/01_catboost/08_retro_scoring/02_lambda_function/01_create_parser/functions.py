
import pandas as pd
from io import StringIO
import numpy as np
import datetime as dt
import xml.etree.ElementTree as ET

# helper for get data
def get_data_helper(dict_json_request):
    # get rows
    list_dict_data = dict_json_request['rows']
    # get id and tables
    list_unique_id = []
    dict_list_tables = {}
    for dict_data in list_dict_data:
        # get unique_id
        unique_id = dict_data['row_id']
        list_unique_id.append(unique_id)
        # assign tables
        dict_list_tables[unique_id] = dict_data['sources']
    # return
    return list_unique_id, dict_list_tables

# get application table
def get_application_table(str_values, unique_id, dict_list_errors):
    # convert str_values to a df
    X = pd.read_csv(
        StringIO(str_values), 
        delimiter=',', 
    )
    # if X is empty
    if X.empty:
        # append error
        dict_list_errors[unique_id].append('Missing Application Table')
        # create a single row df filled with NaN
        list_cols = [
            'app_was_empty',
        ]
        X = pd.DataFrame({col: np.nan for col in list_cols}, index=[0])
        # set date to today
        X['applicationdate'] = dt.datetime.today()
    else:
        # lower
        X.columns = [col.lower() for col in X.columns]
    # add suffix to end of column names
    X.columns = [f'{col}__app' for col in X.columns]
    # set index to unique id
    X.index = [unique_id]
    # return
    return X, dict_list_errors

# get income table
def get_income_table(str_values, unique_id, dict_list_errors):
    # list of columns for income
    list_cols = [
        'bitinvalid',
        'bituse',
        'fltgrossmonthly',
    ]
    # list of cols after aggregation
    list_cols_agg = [
        'fltgrossmonthly__income_sum',
        'fltgrossmonthly__income_count',
    ]
    # convert str_values to a df
    X = pd.read_csv(
        StringIO(str_values), 
        delimiter=',', 
    )
    # if X is empty
    if X.empty:
        # append error
        dict_list_errors[unique_id].append('Missing Income Table')
        X = pd.DataFrame({col: np.nan for col in list_cols_agg}, index=[0])
    else:
        # lower
        X.columns = [col.lower() for col in X.columns]
        # rm T/F
        X_tmp = X * 1
        # filter rows
        X_tmp = X_tmp[X_tmp['bitinvalid']==0] # False
        X_tmp = X_tmp[X_tmp['bituse']==1] # True
        # aggregate
        X = pd.DataFrame()
        X['fltgrossmonthly__income_sum'] = [np.sum(X_tmp['fltgrossmonthly'])]
        X['fltgrossmonthly__income_count'] = [X_tmp.shape[0]]
    # set index to unique id
    X.index = [unique_id]
    # return
    return X, dict_list_errors

# get ln table
def get_lexis_nexis_table(str_values, unique_id, dict_list_errors):
    # read str_values to a df
    X = pd.read_csv(
        StringIO(str_values), 
        delimiter=',', 
    )
    # if empty
    if X.empty:
        # append error
        dict_list_errors[unique_id].append('Missing Lexis Nexis Table')
        # create row with NaN
        list_cols = [
            'ln_was_empty',
        ]
        X = pd.DataFrame({col: np.nan for col in list_cols}, index=[0])
    else:
        # lower
        X.columns = [col.lower() for col in X.columns]
    # add suffix to end of column names
    X.columns = [f'{col}__ln' for col in X.columns]
    # set index to unique id
    X.index = [unique_id]
    # return
    return X, dict_list_errors

# define helper to convert to proper dtype
def helper_convert_dtype(str_col_value):
    # try converting to integer
    try:
        str_col_value = int(str_col_value)
    except:
        # try converting to float
        try:
            str_col_value = float(str_col_value)
        # leave as string
        except:
            pass
    # return
    return str_col_value

# define helper to parse tuxml
def helper_parse_tuxml(str_values):
    # get root
    root = ET.fromstring(str_values)
    # empty dict
    dict_tuxml = {}
    # iterate through child branches
    for child in root.iter(tag='{http://www.transunion.com/namespace}characteristic'):
        # get col name
        str_col_name = child.find('{http://www.transunion.com/namespace}id').text.lower()
        # get col val
        try:
            str_col_value = helper_convert_dtype(str_col_value=child.find('{http://www.transunion.com/namespace}value').text)
        # if its nonetype
        except AttributeError:
            str_col_value = np.nan
        # assign
        dict_tuxml[str_col_name] = str_col_value
    # convert dtype and return df
    return pd.DataFrame(dict_tuxml, index=[0])

# get tu table
def get_transunion_table(str_values, unique_id, dict_list_errors):
    # parse xml
    X = helper_parse_tuxml(
        str_values=str_values, 
    )
    # if empty
    if X.empty:
        # append error
        dict_list_errors[unique_id].append('Missing TU Table')
        list_cols = [
            'tu_was_empty',
        ]
        # create row with NaN
        X = pd.DataFrame({col: np.nan for col in list_cols}, index=[0])
    else:
        pass
    # add suffix to end of column names
    X.columns = [f'{col}__tu' for col in X.columns]
    # set index to unique id
    X.index = [unique_id]
    # return
    return X, dict_list_errors
