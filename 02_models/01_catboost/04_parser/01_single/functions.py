import pandas as pd
from io import StringIO
import numpy as np
import datetime as dt
import xml.etree.ElementTree as ET
import catboost as cb
import xmltodict

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

# get the payment history
def get_pmt_history(str_values):
	# suffix
	str_suffix = '__tu_pmthx'
	# bool
	bool_trades = False

	# make into dictionary
	dict_data = xmltodict.parse(str_values)
	
	# get tradelines
	try:
		list_trades = dict_data['creditBureau']['product']['subject']['subjectRecord']['custom']['credit']['trade']
		bool_trades = True
	except (KeyError, TypeError):
		bool_trades = False
		# create empty df
		df_tmp = pd.DataFrame({
			'str_institution': [],
			'str_dtm_opened': [],
			'str_dtm_closed': [],
			'str_closed_indicator': [],
			'flt_current_balance': [],
			'flt_payment': [],
			'flt_past_due': [],
			'flt_30_dpd': [],
			'flt_60_dpd': [],
			'flt_90_dpd': [],
			'str_loan_type': [],
			'str_pmt_hx': [],
			'str_dtm_most_recent_pmt': [],
			'str_method': [],
			'auto': [],
		})
	# logic
	if bool_trades:
		# get the pmt hx
		list_dict_row = []
		for dict_trade in list_trades:
			# institution
			try:
				str_institution = dict_trade['subscriber']['name']['unparsed']
			except:
				str_institution = np.nan
			# date opened
			try:
				str_dtm_opened = dict_trade['dateOpened']['#text']
			except:
				str_dtm_opened = np.nan
			# date closed
			try:
				str_dtm_closed = dict_trade['dateClosed']['#text']
			except:
				str_dtm_closed = np.nan
			# closed indicator
			try:
				str_closed_indicator = dict_trade['closedIndicator']
			except:
				str_closed_indicator = np.nan
			# current balamce
			try:
				flt_current_balance = float(dict_trade['currentBalance'])
			except:
				flt_current_balance = np.nan
			# payment
			try:
				flt_payment = float(dict_trade['terms']['scheduledMonthlyPayment'])
			except:
				flt_payment = np.nan
			# past due
			try:
				flt_past_due = float(dict_trade['pastDue'])
			except:
				flt_past_due = np.nan
			# 30 dpd
			try:
				flt_30_dpd = float(dict_trade['paymentHistory']['historicalCounters']['late30DaysTotal'])
			except:
				flt_30_dpd = np.nan
			# 60 dpd
			try:
				flt_60_dpd = float(dict_trade['paymentHistory']['historicalCounters']['late60DaysTotal'])
			except:
				flt_60_dpd = np.nan
			# 90 dpd
			try:
				flt_90_dpd = float(dict_trade['paymentHistory']['historicalCounters']['late90DaysTotal'])
			except:
				flt_90_dpd = np.nan
			# pmt hx
			try:
				str_pmt_hx = dict_trade['paymentHistory']['paymentPattern']['text']
			except:
				str_pmt_hx = np.nan
			# loan type
			try:
				str_loan_type = dict_trade['account']['type']
			except:
				str_loan_type = np.nan
			# most recent pmt
			try:
				str_dtm_most_recent_pmt = dict_trade['mostRecentPayment']['date']['#text']
			except:
				str_dtm_most_recent_pmt = np.nan
			# method
			try:
				str_method = dict_trade['updateMethod']
			except:
				str_method = np.nan
			# dict row
			dict_row = {
				'str_institution': str_institution,
				'str_dtm_opened': str_dtm_opened,
				'str_dtm_closed': str_dtm_closed,
				'str_closed_indicator': str_closed_indicator,
				'flt_current_balance': flt_current_balance,
				'flt_payment': flt_payment,
				'flt_past_due': flt_past_due,
				'flt_30_dpd': flt_30_dpd,
				'flt_60_dpd': flt_60_dpd,
				'flt_90_dpd': flt_90_dpd,
				'str_loan_type': str_loan_type,
				'str_pmt_hx': str_pmt_hx,
				'str_dtm_most_recent_pmt': str_dtm_most_recent_pmt,
				'str_method': str_method,
			}
			list_dict_row.append(dict_row)
		# make df
		df_tmp = pd.DataFrame(list_dict_row)
		# tag auto
		df_tmp['auto'] = df_tmp['str_loan_type'].apply(
			lambda x: 1 if str(x).lower() in ['au','al','ar'] else 0,
		)
		# condense
		df_tmp['group'] = 1
		df_tmp = df_tmp.groupby(by='group', as_index=False).agg(lambda x: list(x))
		df_tmp.drop('group', axis=1, inplace=True)
	else:
		pass
	
	# add suffix
	list_cols = [f'{col}{str_suffix}' for col in df_tmp.columns]
	# assign
	df_tmp.columns = list_cols
	# return
	return df_tmp

# get pmt hx
def make_auto_pmt_hx_df(ser_row):
	# make string
	ser_row = ser_row.astype(str)
	# replace nan with None
	ser_row = ser_row.str.replace('nan', 'None')
	# convert to lists
	ser_row = ser_row.apply(eval)
	# make into dictionary
	dict_ser_row = dict(ser_row)
	# make df
	try:
		df_tmp = pd.DataFrame(dict_ser_row)
	except ValueError:
		print('ERROR1')
		dict_output = {
			# overall
			'flt_mean_months_to_first_bad': np.nan,
			# open
			'flt_payment_open': np.nan,
			'int_n_months_open': np.nan,
			'list_pmt_hx_open': np.nan,
			'flt_wtd_avg_open': np.nan,
			'flt_avg_open': np.nan,
			'int_30dpd_open': np.nan,
			'int_60dpd_open': np.nan,
			'int_90dpd_open': np.nan,
			'int_bad_3mo_open': np.nan,
			'int_bad_6mo_open': np.nan,
			'int_bad_3mo_open_end': np.nan,
			'int_bad_6mo_open_end': np.nan,
			# closed
			'flt_payment_closed': np.nan,
			'int_n_months_closed': np.nan,
			'list_pmt_hx_closed': np.nan,
			'flt_wtd_avg_closed': np.nan,
			'flt_avg_closed': np.nan,
			'int_30dpd_closed': np.nan,
			'int_60dpd_closed': np.nan,
			'int_90dpd_closed': np.nan,
			'int_bad_3mo_closed': np.nan,
			'int_bad_6mo_closed': np.nan,
			'int_bad_3mo_closed_end': np.nan,
			'int_bad_6mo_closed_end': np.nan,
		}
		# return
		return dict_output
	
	# get only auto
	df_tmp = df_tmp[df_tmp['auto__tu_pmthx'] == 1].copy()
	
	# columns
	list_cols = [
		'str_dtm_opened__tu_pmthx',
		'str_dtm_closed__tu_pmthx',
		'str_dtm_most_recent_pmt__tu_pmthx',
	]
	# make dtm
	for col in list_cols:
		# make str_dtm_opened__tu_pmthx a datetime
		df_tmp[col] = pd.to_datetime(df_tmp[col])
	# sort
	df_tmp.sort_values(by='str_dtm_opened__tu_pmthx', ascending=False, inplace=True)
	
	# tag open
	df_tmp['tag_open'] = df_tmp['str_dtm_closed__tu_pmthx'].apply(
		lambda x: 1 if pd.isnull(x) else 0,
	)
	
	# fillna
	df_tmp['str_pmt_hx__tu_pmthx'] = df_tmp['str_pmt_hx__tu_pmthx'].fillna('')

	# remove Y from payment hx
	df_tmp['str_pmt_hx__tu_pmthx'] = df_tmp['str_pmt_hx__tu_pmthx'].apply(
		lambda x: [str_val for str_val in list(x) if str_val != 'Y'],
	)
	
	# get n payments
	df_tmp['n_months'] = df_tmp['str_pmt_hx__tu_pmthx'].apply(
		lambda x: len(x),
	)

	# convert str_pmt_hx__tu_pmthx to lists of 1 and 0
	df_tmp['str_pmt_hx__tu_pmthx'] = df_tmp['str_pmt_hx__tu_pmthx'].apply(
		lambda x: [1 if str_val in ['1','E'] else 0 for str_val in list(x)],
	)

	# reverse the order of the lists
	df_tmp['str_pmt_hx__tu_pmthx'] = df_tmp['str_pmt_hx__tu_pmthx'].apply(
		lambda x: x[::-1] if isinstance(x, list) else x,
	)
	
	# first month of bad event
	df_tmp['month_first_bad'] = df_tmp['str_pmt_hx__tu_pmthx'].apply(
		 lambda x: pd.Series(list(x))[pd.Series(list(x)) != 1].index.min()+1,
	)
	# months to first bad
	df_tmp['months_to_first_bad'] = df_tmp['month_first_bad'].fillna(df_tmp['n_months'])
	# make it a proportion
	df_tmp['months_to_first_bad'] = df_tmp['months_to_first_bad'] / df_tmp['n_months']
	
	# get mean proportion months to first bad overall open and closed - all
	flt_mean_months_to_first_bad = df_tmp['months_to_first_bad'].mean()
	
	# logic if there is no payment history
	if pd.isnull(flt_mean_months_to_first_bad):
		flt_mean_months_to_first_bad = 0 # lower is worse it means you have early delinquency
	else:
		pass
	
	# get df open
	df_tmp_open = df_tmp[df_tmp['tag_open'] == 1].copy()
	int_nrows = df_tmp_open.shape[0]
	if int_nrows > 0:
		# get mayment
		flt_payment_open = df_tmp_open['flt_payment__tu_pmthx'].iloc[0]
		# get n months
		int_n_months_open = df_tmp_open['n_months'].iloc[0]
		# get the most recent open pmt hx
		list_pmt_hx_open = df_tmp_open['str_pmt_hx__tu_pmthx'].iloc[0]
		# get weighted average
		list_weights = list(range(1, len(list_pmt_hx_open)+1))
		try:
			flt_wtd_avg_open = np.average(list_pmt_hx_open, weights=list_weights)
		except ZeroDivisionError:
			flt_wtd_avg_open = np.nan # lower is worse
		# get normal average
		flt_avg_open = np.mean(list_pmt_hx_open)
		# get DPD
		int_30dpd_open = df_tmp_open['flt_30_dpd__tu_pmthx'].iloc[0]
		int_60dpd_open = df_tmp_open['flt_60_dpd__tu_pmthx'].iloc[0]
		int_90dpd_open = df_tmp_open['flt_90_dpd__tu_pmthx'].iloc[0]

		# bad tags
		int_len_list_pmt_hx_open = len(list_pmt_hx_open)
		
		# if they dont have 3 months on file
		if int_len_list_pmt_hx_open < 3:
			int_bad_3mo_open = 1
		elif (int_len_list_pmt_hx_open >= 3) and (np.sum(list_pmt_hx_open[:3]) < 3):
			int_bad_3mo_open = 1
		else:
			int_bad_3mo_open = 0
		
		# if they dont have 6 months on file
		if int_len_list_pmt_hx_open < 3:
			int_bad_6mo_open = 1
		elif (int_len_list_pmt_hx_open >= 6) and (np.sum(list_pmt_hx_open[:6]) < 6):
			int_bad_6mo_open = 1
		else:
			int_bad_6mo_open = 0
		
		# if they dont have 3 months on file
		if int_len_list_pmt_hx_open < 3:
			int_bad_3mo_open_end = 1
		elif (int_len_list_pmt_hx_open >= 3) and (np.sum(list_pmt_hx_open[-3:]) < 3):
			int_bad_3mo_open_end = 1
		else:
			int_bad_3mo_open_end = 0
		
		# if they dont have 6 months on file
		if int_len_list_pmt_hx_open < 3:
			int_bad_6mo_open_end = 1
		elif (int_len_list_pmt_hx_open >= 6) and (np.sum(list_pmt_hx_open[-6:]) < 6):
			int_bad_6mo_open_end = 1
		else:
			int_bad_6mo_open_end = 0
	else:
		flt_payment_open = np.nan
		int_n_months_open = np.nan
		list_pmt_hx_open = np.nan
		flt_wtd_avg_open = np.nan
		flt_avg_open = np.nan
		int_30dpd_open = np.nan
		int_60dpd_open = np.nan
		int_90dpd_open = np.nan
		int_bad_3mo_open = np.nan
		int_bad_6mo_open = np.nan
		int_bad_3mo_open_end = np.nan
		int_bad_6mo_open_end = np.nan
	
	# get df closed
	df_tmp_closed = df_tmp[df_tmp['tag_open'] == 0].copy()
	int_nrows = df_tmp_closed.shape[0]
	if int_nrows > 0:
		# get mayment
		flt_payment_closed = df_tmp_closed['flt_payment__tu_pmthx'].iloc[0]
		# get n months
		int_n_months_closed = df_tmp_closed['n_months'].iloc[0]
		# get the most recent open pmt hx
		list_pmt_hx_closed = df_tmp_closed['str_pmt_hx__tu_pmthx'].iloc[0]
		# get weighted average
		list_weights = list(range(1, len(list_pmt_hx_closed)+1))
		try:
			flt_wtd_avg_closed = np.average(list_pmt_hx_closed, weights=list_weights)
		except ZeroDivisionError:
			flt_wtd_avg_closed = np.nan
		# get normal average
		flt_avg_closed = np.mean(list_pmt_hx_closed)
		# get DPD
		int_30dpd_closed = df_tmp_closed['flt_30_dpd__tu_pmthx'].iloc[0]
		int_60dpd_closed = df_tmp_closed['flt_60_dpd__tu_pmthx'].iloc[0]
		int_90dpd_closed = df_tmp_closed['flt_90_dpd__tu_pmthx'].iloc[0]

		# bad tags
		int_len_list_pmt_hx_closed = len(list_pmt_hx_closed)
		
		# if they dont have 3 months on file
		if int_len_list_pmt_hx_closed < 3:
			int_bad_3mo_closed = 1
		elif (int_len_list_pmt_hx_closed >= 3) and (np.sum(list_pmt_hx_closed[:3]) < 3):
			int_bad_3mo_closed = 1
		else:
			int_bad_3mo_closed = 0
		
		# if they dont have 6 months on file
		if int_len_list_pmt_hx_closed < 3:
			int_bad_6mo_closed = 1
		elif (int_len_list_pmt_hx_closed >= 6) and (np.sum(list_pmt_hx_closed[:6]) < 6):
			int_bad_6mo_closed = 1
		else:
			int_bad_6mo_closed = 0
			
		# if they dont have 3 months on file
		if int_len_list_pmt_hx_closed < 3:
			int_bad_3mo_closed_end = 1
		elif (int_len_list_pmt_hx_closed >= 3) and (np.sum(list_pmt_hx_closed[-3:]) < 3):
			int_bad_3mo_closed_end = 1
		else:
			int_bad_3mo_closed_end = 0
		
		# if they dont have 6 months on file
		if int_len_list_pmt_hx_closed < 3:
			int_bad_6mo_closed_end = 1
		elif (int_len_list_pmt_hx_closed >= 6) and (np.sum(list_pmt_hx_closed[-6:]) < 6):
			int_bad_6mo_closed_end = 1
		else:
			int_bad_6mo_closed_end = 0
	else:
		flt_payment_closed = np.nan
		int_n_months_closed = np.nan
		list_pmt_hx_closed = np.nan
		flt_wtd_avg_closed = np.nan
		flt_avg_closed = np.nan
		int_30dpd_closed = np.nan
		int_60dpd_closed = np.nan
		int_90dpd_closed = np.nan
		int_bad_3mo_closed = np.nan
		int_bad_6mo_closed = np.nan
		int_bad_3mo_closed_end = np.nan
		int_bad_6mo_closed_end = np.nan
	
	# dict output
	dict_output = {
		# overall
		'flt_mean_months_to_first_bad': flt_mean_months_to_first_bad,
		# open
		'flt_payment_open': flt_payment_open,
		'int_n_months_open': int_n_months_open,
		'list_pmt_hx_open': list_pmt_hx_open,
		'flt_wtd_avg_open': flt_wtd_avg_open,
		'flt_avg_open': flt_avg_open,
		'int_30dpd_open': int_30dpd_open,
		'int_60dpd_open': int_60dpd_open,
		'int_90dpd_open': int_90dpd_open,
		'int_bad_3mo_open': int_bad_3mo_open,
		'int_bad_6mo_open': int_bad_6mo_open,
		'int_bad_3mo_open_end': int_bad_3mo_closed_end,
		'int_bad_6mo_open_end': int_bad_6mo_closed_end,
		# closed
		'flt_payment_closed': flt_payment_closed,
		'int_n_months_closed': int_n_months_closed,
		'list_pmt_hx_closed': list_pmt_hx_closed,
		'flt_wtd_avg_closed': flt_wtd_avg_closed,
		'flt_avg_closed': flt_avg_closed,
		'int_30dpd_closed': int_30dpd_closed,
		'int_60dpd_closed': int_60dpd_closed,
		'int_90dpd_closed': int_90dpd_closed,
		'int_bad_3mo_closed': int_bad_3mo_closed,
		'int_bad_6mo_closed': int_bad_6mo_closed,
		'int_bad_3mo_closed_end': int_bad_3mo_closed_end,
		'int_bad_6mo_closed_end': int_bad_6mo_closed_end,
	}
	# return
	return dict_output

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

# add chime tags
list_str_inst = [
	'PROGRESSRES',
    'STEP MOBILE',
    'CHIME-STRIDE',
    'ATLCAPBKSELF',
]