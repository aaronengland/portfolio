# functions
import pandas as pd
import numpy as np
import json
import os
import pickle
import gzip
import boto3
import time
from io import StringIO
from tqdm import tqdm

# import parser
def import_parser(str_local_path):
	# import and return
	return pickle.load(open(str_local_path,'rb'))

# define function to get tier
def get_tier(flt_score, dict_tiers):
	if flt_score <= dict_tiers['A1']:
		return 'A1'
	elif flt_score <= dict_tiers['A']:
		return 'A'
	elif flt_score <= dict_tiers['B']:
		return 'B'
	elif flt_score <= dict_tiers['C']:
		return 'C'
	elif flt_score <= dict_tiers['D']:
		return 'D'
	else:
		return 'Decline'

# create hyperlinks
def create_hyperlinks(df_show):
	df_show['Download'] = df_show['ROW'].apply(
		lambda x: f'<a href="download_json/{x-1}">Download JSON</a>'
	)
	# return
	return df_show

# sortable table
def create_sortable_table(df):
	df = df.to_html(
		classes='display', 
		escape=False, 
		index=False,
	)
	# return
	return df

# get selected requests
def get_selected_requests(df, int_row_1, int_row_2):
	df_tmp = df[df['Row']==int_row_1]
	json_str_request_1 = json.loads(df_tmp['REQUEST_JSON'].iloc[0])
	print(f'Selected row payload from row {int_row_1}')
	df_tmp = df[df['Row']==int_row_2]
	json_str_request_2 = json.loads(df_tmp['REQUEST_JSON'].iloc[0])
	print(f'Selected row payload from row {int_row_2}')
	# return
	return json_str_request_1, json_str_request_2

# parse both requests
def parse_both_requests(cls_parse_payload, json_str_request_1, json_str_request_2):
	# parse json_str_request_1
	cls_parse_payload.get_data(json_str_request_1)
	# engineer pmt hx
	cls_parse_payload.engineer_pmt_hx()
	# preprocess
	cls_parse_payload.preprocessing()
	# get X
	X_file1 = cls_parse_payload.df_clean.copy()

	# parse json_str_request_2
	cls_parse_payload.get_data(json_str_request_2)
	# engineer pmt hx
	cls_parse_payload.engineer_pmt_hx()
	# preprocess
	cls_parse_payload.preprocessing()
	# get X
	X_file2 = cls_parse_payload.df_clean.copy()

	# return
	return X_file1, X_file2

# define function to find differences
def find_differences(X_first, X_last, int_row_1, int_row_2):
	list_cols_ignore = [
		'ENG-debt',
		'ENG-dti',
	]
	# only look at debtor
	str_idx = 0
	# make empty list
	list_dict_row = []
	# iterate through each X and see where the discrepancies are
	for col in X_first.columns:
		# get first value
		val_first = X_first[col].iloc[str_idx]
		# get last value
		val_last = X_last[col].iloc[str_idx]
		# check if vals are not equal
		if col in list_cols_ignore:
			pass
		elif pd.isnull(val_first) and pd.isnull(val_last):
			pass
		elif val_first != val_last:
			# dict_row
			dict_row = {
				'Feature Name': col,
				f'Row {int_row_1}': val_first,
				f'Row {int_row_2}': val_last,
			}
			list_dict_row.append(dict_row)
		else:
			pass
	# make df
	df = pd.DataFrame(list_dict_row)
	# return
	return df

# get definitions
def get_descriptions(df, str_local_path):
	# import descriptions
	df_tmp = pd.read_csv(str_local_path)
	# get reason
	dict_map = dict(zip(df_tmp['feature'], df_tmp['reason']))
	df['Reason'] = df['Feature Name'].map(dict_map)
	# get description
	dict_map = dict(zip(df_tmp['feature'], df_tmp['description']))
	df['Description'] = df['Feature Name'].map(dict_map)
	# return
	return df