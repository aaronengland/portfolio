import pandas as pd
import numpy as np 
import json
import pickle

# static table
def create_static_table(df):
	df = df.to_html(index=False, header='true', justify='left')
	return df

# sortable table
def create_sortable_table(df):
	df = df.to_html(classes='display', escape=False, index=False)
	return df

# read file
def read_file(str_local_path):
	try:
		dict_json_request = json.load(open(str_local_path))['request']
	except KeyError:
		dict_json_request = json.load(open(str_local_path))
	return dict_json_request

# load parser
def load_parser(str_local_path):
	cls_parse_payload = pickle.load(open(str_local_path, 'rb'))
	return cls_parse_payload