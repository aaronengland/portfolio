import pandas as pd
from io import StringIO
import numpy as np
import datetime as dt
import xml.etree.ElementTree as ET
import catboost as cb

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
def get_application_table(str_values):
	# convert str_values to df
	X = pd.read_csv(StringIO(str_values), delimiter=',')
	# add suffix
	list_cols = [f'{col.lower()}__app' for col in X.columns]
	# assign
	X.columns = list_cols
	# return X
	return X

# get income table
def get_income_table(str_values):
	# convert str_values to df
	X = pd.read_csv(
		StringIO(str_values),
		delimiter=',',
	)
	list_cols = [f'{col.lower()}' for col in X.columns]
	X.columns = list_cols
	# rm t/f
	X = X * 1
	# filter rows
	X = X[X['bitinvalid']==0].copy()
	X = X[X['bituse']==1].copy()
	# aggregate
	X_2 = pd.DataFrame()
	X_2['fltgrossmonthly__income_sum'] = [np.sum(X['fltgrossmonthly'])]
	X_2['fltgrossmonthly__income_count'] = [X.shape[0]]
	# return
	return X_2

# get ln table
def get_lexis_nexis_table(str_values):
	# convert str_values to df
	X = pd.read_csv(
		StringIO(str_values),
		delimiter=',',
	)
	# add suffix
	list_cols = [f'{col.lower()}__ln' for col in X.columns]
	# assign
	X.columns = list_cols
	# return
	return X

# TUXML
def get_transunion_table(str_values):
	# get root
	root = ET.fromstring(str_values)
	# empty dict
	dict_tuxml = {}
	# iterate through child branches
	for child in root.iter(tag='{http://www.transunion.com/namespace}characteristic'):
		# get col name
		str_col_name = child.find('{http://www.transunion.com/namespace}id').text.lower()
		# get value
		try:
			str_col_value = child.find('{http://www.transunion.com/namespace}value').text
		except AttributeError:
			str_col_value = np.nan
		# try to convert the value to integer
		try:
			str_col_value = int(str_col_value)
		except:
			# try to convert to float
			try:
				str_col_value = float(str_col_value)
			except:
				# leave as string
				pass
		# assign
		dict_tuxml[str_col_name] = str_col_value
	# make into df
	X = pd.DataFrame([dict_tuxml])
	
	# rename columns
	list_cols = list(X.columns)
	# add suffix
	list_cols = [f'{col.lower()}__tu' for col in X.columns]
	# assign
	X.columns = list_cols
	# return
	return X

# adverse action
def get_adverse_action(X_clean, cls_model_inference, dict_aa):
	# get the list of features in the model
	list_cols_in_model = list(cls_model_inference.feature_names_)
	# get cat feat indices
	list_idx_nonnumeric = cls_model_inference.get_cat_feature_indices()
	# get non-numeric features
	list_cols_nonnumeric = [list_cols_in_model[idx] for idx in list_idx_nonnumeric]
	# pool data
	X_pooled = cb.Pool(
		data=X_clean[list_cols_in_model],
		cat_features=list_cols_nonnumeric,
	)
	# get SHAP values
	df_shap_vals = pd.DataFrame(
		data=cls_model_inference.get_feature_importance(
			data=X_pooled,
			type='ShapValues',
			prettified=False,
			thread_count=-1,
			verbose=False,
		)
	).iloc[:, :-1]
	# assign col names
	df_shap_vals.columns = list_cols_in_model
	# set index
	df_shap_vals.index = X_clean.index
	# get reasons
	list_list_reasons = list(df_shap_vals.apply(lambda row: list(row.sort_values(ascending=False, inplace=False).index[:5].map(dict_aa)), axis=1))
	# return
	return df_shap_vals, list_list_reasons