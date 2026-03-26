import pandas as pd
from tqdm import tqdm
import json
import numpy as np
from io import StringIO
import xml.etree.ElementTree as ET
import xmltodict
from datetime import datetime

# for LGD
def map_ltv_range_to_lgd_bin(flt_ltv, dict_bins_ltv):
	for flt_threshold, flt_val in dict_bins_ltv.items():
		if flt_ltv <= flt_threshold:
			return flt_val
	# else
	return np.max(list(dict_bins_ltv.values()))

# helper
def get_app_table(str_values):
	# convert str_values to df
	df_tmp = pd.read_csv(StringIO(str_values), delimiter=',')
	# rename columns
	list_cols = list(df_tmp.columns)
	# add suffix
	list_cols = [f'{col.lower()}__app' for col in list_cols]
	# assign
	df_tmp.columns = list_cols
	# return
	return df_tmp

# helper
def get_debt_table(str_values):
	# convert str_values to df
	df_tmp = pd.read_csv(
		StringIO(str_values),
		delimiter=',',
	)
	# rm t/f
	df_tmp = df_tmp * 1
	# lower
	list_cols = [col.lower() for col in df_tmp.columns]
	df_tmp.columns = list_cols
	# filter rows
	df_tmp = df_tmp[df_tmp['bitinvalid']==0].copy()
	df_tmp = df_tmp[df_tmp['bituse']==1].copy()
	# find rows where strcreditor containes exp
	df_tmp['exp'] = df_tmp['strcreditor'].apply(
		lambda x: 1 if 'exp' in str(x).lower() else 0,
	)
	# rm
	df_tmp = df_tmp[df_tmp['exp']==0].copy()
	# get sum of monthly payment
	flt_sum_monthly_payment = df_tmp['fltmonthlypayment'].sum()
	# get sum of current balance
	flt_sum_current_balance = df_tmp['fltbalancecurrent'].sum()
	# get sum of original balance
	flt_sum_original_balance = df_tmp['fltbalanceoriginal'].sum()
	# get number of sources
	int_count = df_tmp.shape[0]
	# aggregate
	df_tmp_2 = pd.DataFrame()
	df_tmp_2['fltmonthlypayment__debt_sum'] = [flt_sum_monthly_payment]
	df_tmp_2['fltbalancecurrent__debt_sum'] = [flt_sum_current_balance]
	df_tmp_2['fltbalanceoriginal__debt_sum'] = [flt_sum_original_balance]
	df_tmp_2['n_sources__debt_count'] = [int_count]
	# return
	return df_tmp_2

# helper
def get_income_table(str_values):
	# convert str_values to df
	df_tmp = pd.read_csv(
		StringIO(str_values),
		delimiter=',',
	)
	# rm t/f
	df_tmp = df_tmp * 1
	# lower
	list_cols = [col.lower() for col in df_tmp.columns]
	df_tmp.columns = list_cols
	# filter rows
	df_tmp = df_tmp[df_tmp['bitinvalid']==0].copy()
	df_tmp = df_tmp[df_tmp['bituse']==1].copy()
	# get sum
	int_sum = np.sum(df_tmp['fltgrossmonthly'])
	# get count
	int_count = df_tmp.shape[0]
	# aggregate
	df_tmp_2 = pd.DataFrame()
	df_tmp_2['fltgrossmonthly__income_sum'] = [int_sum]
	df_tmp_2['fltgrossmonthly__income_count'] = [int_count]
	# return
	return df_tmp_2

# helper
def get_ln_table(str_values):
	# convert str_values to df
	df_tmp = pd.read_csv(
		StringIO(str_values),
		delimiter=',',
	)
	# rename columns
	list_cols = list(df_tmp.columns)
	# add suffix
	list_cols = [f'{col.lower()}__ln' for col in list_cols]
	# assign
	df_tmp.columns = list_cols
	# return
	return df_tmp

# helper
def get_blackbook_table(str_values):
	# convert str_values to df
	df_tmp = pd.read_csv(StringIO(str_values), delimiter=',')
	# rename columns
	list_cols = list(df_tmp.columns)
	# add suffix
	list_cols = [f'{col.lower()}__bb' for col in list_cols]
	# assign
	df_tmp.columns = list_cols
	# return
	return df_tmp

# helper
def get_tu_table(str_values):
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
		# try to convert to float
		try:
			str_col_value = float(str_col_value)
		except ValueError:
			pass
		# assign
		dict_tuxml[str_col_name] = str_col_value
	# make into df
	df_tmp = pd.DataFrame([dict_tuxml])
	
	# rename columns
	list_cols = list(df_tmp.columns)
	# add suffix
	list_cols = [f'{col.lower()}__tu' for col in list_cols]
	# assign
	df_tmp.columns = list_cols
	# return
	return df_tmp

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

# list of chime tags
list_str_inst = [
	# from ben: 2025-02-21
	'CURRENT',
	'SELF',
	# key words
	'CHIME-STRIDE',
	'CHIMEFINAL',
	# from dustin: 2025-02-24
	'SELF FIN',
	'SELF/LEAD',
	'SELFINC/LEAD',
	'SBNASELFLNDR',
	'SBNA SELF',
	'CHIME',
	'CLEO',
	'CLEO AI',
	'VARO',
	'ATLAS',
	'ATLCAPBKSELF',
	'POSSIBLE',
	'POSSIBLE FIN',
	'KIKOFF',
	'SUPER.COM',
	'STEP',
	'STEP MOBILE',
	'BRIGHT',
	'BRIGHT BLDR',
	'FIG TECH INC',
	'SELF/RENT',
	'SELFBILLSE',
	'PROGRESSRES',
	'FLEX',
	'FLEXFINANCE',
]

# class
class ParsePayload:
	# init
	def __init__(self, cls_model_preprocessing, cls_model_inference, dict_aa, str_tiers, list_cols_necessary, dict_bins_ltv_bk, dict_bins_ltv_nobk, dtm_effective_date1):
		self.cls_model_preprocessing = cls_model_preprocessing
		self.cls_model_inference = cls_model_inference
		self.dict_aa = dict_aa
		self.str_tiers = str_tiers
		self.list_cols_necessary = list_cols_necessary
		self.dict_bins_ltv_bk = dict_bins_ltv_bk
		self.dict_bins_ltv_nobk = dict_bins_ltv_nobk
		self.dtm_effective_date1 = dtm_effective_date1
	# get data
	def get_data(self, str_request):
		print('Getting data...')
		# convert to dictionary
		#dict_request = json.loads(str_request)

		# str_request seems already a dictionary
		dict_request = str_request

		# get the rows
		try:
			list_dict_rows = dict_request['rows']
		except:
			dict_request = json.loads(str_request)
			list_dict_rows = dict_request['rows']

		# empty list for unique id
		list_unique_id = []
		# iterate through the rows
		list_df_tmp_concat = []
		for a, dict_row in enumerate(list_dict_rows):
			# get unique ids
			int_uniquid = dict_row['row_id']
			list_unique_id.append(int_uniquid)
			# get the tables
			list_dict_table = dict_row['sources']
			# iterate through tables
			list_df_tmp = []
			for b, dict_table in enumerate(list_dict_table):
				# get the name
				str_name = dict_table['name']
				# get the values
				str_values = dict_table['values']
				
				# logic
				if str_name in ['Application','Everything Else']:
					# get table
					df_tmp = get_app_table(str_values=str_values)
					# append
					list_df_tmp.append(df_tmp)
				elif str_name == 'Debts':
					# get table
					df_tmp = get_debt_table(str_values=str_values)
					# append
					list_df_tmp.append(df_tmp)
				elif str_name == 'Incomes':
					# get table
					df_tmp = get_income_table(str_values=str_values)
					# append
					list_df_tmp.append(df_tmp)
				elif str_name == 'Lexis Nexis Risk View 5':
					# get table
					df_tmp = get_ln_table(str_values=str_values)
					# append
					list_df_tmp.append(df_tmp)
				elif str_name == 'Blackbook':
					# get table
					df_tmp = get_blackbook_table(str_values=str_values)
					# append
					list_df_tmp.append(df_tmp)            
				elif str_name == 'TUXML':
					# get table
					df_tmp = get_tu_table(str_values=str_values)
					# get pmt hx
					df_tmp_2 = get_pmt_history(str_values=str_values)
					# concatenate horizontally
					df_tmp = pd.concat([df_tmp, df_tmp_2], axis=1)
					# append
					list_df_tmp.append(df_tmp)
				else:
					pass
			# concatenate horizontally
			df_tmp_concat = pd.concat(list_df_tmp, axis=1)
			# append
			list_df_tmp_concat.append(df_tmp_concat)
		# concatenate vertically
		df = pd.concat(list_df_tmp_concat)
		print([col for col in df.columns if 'uniqueid' in col.lower()])
		# get unique ids
		try:
			list_unique_id = list(df['uniqueid__app'])
		except:
			# already made above
			pass
		# if there is no accountid__app
		if 'bigaccountid__app' not in list(df.columns):
			list_bigaccountid = [int_id.split('__')[0] for int_id in list_unique_id]
			df['bigaccountid__app'] = list_bigaccountid
		else:
			pass
		# if there is no strdealershiptrackertype__app
		if 'strdealershiptrackertype__app' not in list(df.columns):
			df['strdealershiptrackertype__app'] = 'Franchise'
		else:
			pass
		# if there is no dealerstate__app
		if 'dealerstate__app' not in list(df.columns):
			df['dealerstate__app'] = df['strname__app']
		else:
			pass
		# if there is no fltgrossmonthly__income_sum
		if 'fltgrossmonthly__income_sum' not in list(df.columns):
			df['fltgrossmonthly__income_sum'] = df['fltgrossmonthly__app']
		else:
			pass
		# if there is no amtfinanced__app
		if 'amtfinanced__app' not in list(df.columns):
			df['amtfinanced__app'] = df['fltamountfinanced__app']
		else:
			pass
		# if there is no bookvalue__app
		if 'bookvalue__app' not in list(df.columns):
			df['bookvalue__app'] = df['vehiclevalue__app']
		else:
			pass

		# get the applicationdate
		str_dtm_app_date = df['applicationdate__app'].iloc[0]
		dtm_app_date = datetime.strptime(str_dtm_app_date, '%m/%d/%Y %H:%M:%S')
		print(f'Application Date: {dtm_app_date}')

		# show effective dates
		print(f'Effective Date Payment History: {self.dtm_effective_date1}')

		# boolean for payment history
		if dtm_app_date < self.dtm_effective_date1:
			bool_apply_pmt_hx_decline = False
		else:
			bool_apply_pmt_hx_decline = True
		print(f'Apply Payment History - Decline: {bool_apply_pmt_hx_decline}')

		# save to object
		self.df_raw = df.copy()
		self.list_unique_id = list_unique_id
		self.bool_apply_pmt_hx_decline = bool_apply_pmt_hx_decline
		# return
		return self
	# pmt hx
	def engineer_pmt_hx(self):
		print(f'{self.list_unique_id}: Engineering payment history...')
		df = self.df_raw.copy()
		# pmt history columns
		list_cols_pmt_hx = [col for col in df.columns if '__tu_pmthx' in col]
		# get pmt hx
		df['pmt_hx'] = df[list_cols_pmt_hx].apply(
			lambda x: make_auto_pmt_hx_df(ser_row=x),
			axis=1,
		)
		# get the pmt hx
		df_tmp = pd.DataFrame(list(df['pmt_hx']))
		list_cols = [f'{col}__tu_pmthx' for col in df_tmp.columns]
		df_tmp.columns = list_cols

		# reset index
		df = df.reset_index(drop=True)
		df_tmp = df_tmp.reset_index(drop=True)
		# concat
		df = pd.concat([df, df_tmp], axis=1)

		# create list of institutions
		df['list_institutions'] = df['str_institution__tu_pmthx'].apply(
			lambda x: x if isinstance(x, list) else [],
		)
		
		# create tags for institutions
		list_str_col_new = []
		for str_inst in tqdm(list_str_inst):
			str_col_new = f'{str_inst}_tag'
			df[str_col_new] = df['list_institutions'].apply(
				lambda x: 1 if str_inst in x else 0,
			)
			list_str_col_new.append(str_col_new)
		# get the sum
		df['sum'] = df[list_str_col_new].sum(axis=1)
		# tag
		df['has_inst_tag'] = df['sum'].apply(
			lambda x: 1 if x > 0 else 0,
		)
		# get number of debtors with chime tag
		int_sum_chime = df['has_inst_tag'].sum()
		# logic
		if int_sum_chime >= 1:
			bool_chime = True
		else:
			bool_chime = False
		print(f'Chime: {bool_chime}')

		# pmt hx logic for payment history - decline
		int_n_payments = 4
		list_str_pmt_hx = [
			'list_pmt_hx_closed__tu_pmthx',
			'list_pmt_hx_open__tu_pmthx',
		]
		# make sure they are lists
		for str_pmt_hx in list_str_pmt_hx:
			df[str_pmt_hx] = df[str_pmt_hx].apply(
				lambda x: x if isinstance(x, list) else [],
			)
			print(df[str_pmt_hx])
		# create one long list
		df['list_pmt_hx'] = df.apply(
		    lambda x: x['list_pmt_hx_closed__tu_pmthx'] + x['list_pmt_hx_open__tu_pmthx'],
			axis=1,
		)
		print(df['list_pmt_hx'])
		# get length of list
		df['n_pmts'] = df['list_pmt_hx'].apply(
			lambda x: len(x),
		)
		print(df['n_pmts'])
		# tag
		df['tag_min_pmts'] = df['n_pmts'].apply(
			lambda x: 1 if x >= int_n_payments else 0,
		)
		print(df['tag_min_pmts'])
		# sum of last n payments
		df['list_last_n_pmts'] = df['list_pmt_hx'].apply(
			lambda x: x[-int_n_payments:],
		)
		print(df['list_last_n_pmts'])
		# get length of list n pmts
		df['len_last_n_pmts'] = df['list_last_n_pmts'].apply(
			lambda x: len(x),
		)
		print(df['len_last_n_pmts'])
		# get sum
		df['sum_last_n_pmts'] = df['list_last_n_pmts'].apply(
			lambda x: np.sum(x),
		)
		print(df['sum_last_n_pmts'])
		# tag bk
		df['tag_bk'] = df['intopenbktype__app'].apply(
			lambda x: 1 if pd.notnull(x) else 0,
		)
		print(df['tag_bk'])
		# tag if sum = 0 and non-bk
		df['tag_bad_pmt_hx'] = df.apply(
			lambda x: 1 if (x['len_last_n_pmts'] >= int_n_payments) and (x['sum_last_n_pmts'] == 0) and (x['tag_bk'] == 0) else 0,
			axis=1,
		)
		print(df['tag_bad_pmt_hx'])
		# get the optimistic view
		flt_bad_pmt_hx = df['tag_bad_pmt_hx'].min()

		# logic
		if flt_bad_pmt_hx == 1:
			bool_bad_pmt_hx = True 
		else:
			bool_bad_pmt_hx = False
		print(f'Bad payment history: {bool_bad_pmt_hx}')

		# save to object
		self.bool_chime = bool_chime
		self.bool_bad_pmt_hx = bool_bad_pmt_hx
		self.df_raw = df.copy()
		# return
		return self
	# preprocessing
	def preprocessing(self):
		print(f'{self.list_unique_id}: Preprocessing data...')
		df_tmp = self.df_raw.copy()

		# make sure all features we need are in there
		for col in tqdm(self.list_cols_necessary):
			if col not in list(df_tmp.columns):
				df_tmp[col] = np.nan 
			else:
				pass
		# subset
		df_tmp = df_tmp[self.list_cols_necessary].copy()

		# preprocess
		df = self.cls_model_preprocessing.transform(df_tmp.copy())

		# get value for ENG-bk
		int_bk = df['ENG-bk'].iloc[0]
		# logic
		if int_bk == 1:
			self.dict_bins_ltv = self.dict_bins_ltv_bk.copy()
		else:
			self.dict_bins_ltv = self.dict_bins_ltv_nobk.copy()

		# save to object
		self.df_clean = df.copy()
		# return
		return self
	# predict
	def get_predictions(self):
		print(f'{self.list_unique_id}: Getting predictions...')
		df = self.df_clean.copy()
		# get intercept
		flt_intercept = self.cls_model_inference.intercept_[0]
		# get cols in model
		list_cols_model = list(self.cls_model_inference.feature_names_in_)
		# get the coef
		list_coef = list(self.cls_model_inference.coef_[0])
		# make dict
		dict_coef = dict(zip(list_cols_model, list_coef))
		# get contribution
		list_str_contribution = []
		for key, val in dict_coef.items():
			str_contribution = f'{key}_contribution'
			df[str_contribution] = df[key] * val 
			list_str_contribution.append(str_contribution)
		# get the sum
		df['sum'] = df[list_str_contribution].apply(sum, axis=1)
		# get the log odds
		df['log_odds'] = df['sum'] + flt_intercept
		# get the pd
		df['PD'] = np.exp(df['log_odds']) / (1 + np.exp(df['log_odds']))
		#df['PD'] = self.cls_model_inference.predict_proba(df[list_cols_model])[:,1]
		list_scores_pd = list(df['PD'])
		flt_mean_pd = df['PD'].mean()
		df['LGD'] = df['ENG-loan_to_value'].apply(
			lambda x: map_ltv_range_to_lgd_bin(
				flt_ltv=x,
				dict_bins_ltv=self.dict_bins_ltv,
			),
		)
		list_scores_lgd = list(df['LGD'])
		flt_mean_lgd = df['LGD'].mean()
		# get the mean prediction
		flt_mean_score = flt_mean_pd * flt_mean_lgd
		# get loss at 72
		flt_mean_score_mapped = flt_mean_score * 2.36

		# chime logic
		if self.bool_chime:
			flt_mean_score_mapped = flt_mean_score_mapped * 1.203 # chime penalty
		else:
			flt_mean_score_mapped = flt_mean_score_mapped * 0.936 # non chime bonus

		# bool_bad_pmt_hx
		if (self.bool_apply_pmt_hx_decline) and (self.bool_bad_pmt_hx):
			flt_mean_score_mapped = 1.0 
		else:
			pass

		# save to object
		self.df_clean = df.copy()
		self.list_scores_pd = list_scores_pd
		self.list_scores_lgd = list_scores_lgd
		self.flt_mean_pd = flt_mean_pd 
		self.flt_mean_lgd = flt_mean_lgd
		self.flt_mean_score = flt_mean_score
		self.flt_mean_score_mapped = flt_mean_score_mapped
		# return
		return self
	# adverse action
	def adverse_action(self):
		print(f'{self.list_unique_id}: Getting adverse action...')
		# copy df
		df = self.df_clean.copy()

		# create a coefficient dictionary
		list_cols_model = list(self.cls_model_inference.feature_names_in_)
		list_flt_coef = list(self.cls_model_inference.coef_[0])
		dict_coef = dict(zip(list_cols_model, list_flt_coef))

		# get each features contribution to score
		for key, val in tqdm(dict_coef.items()):
			df[f'{key}_contribution'] = df[key] * val
		# get the features
		list_cols = [col for col in df.columns if '_contribution' in col]
		# subset
		df = df[list_cols].copy()

		# get the aa columns
		list_list_cols_positive = []
		for a, ser_row in tqdm(df.iterrows()):
			# sort
			ser_row = ser_row.sort_values(ascending=False)
			# get the top 5 positive features
			list_cols_positive = list(ser_row.index)[:5]
			# get back to original name
			list_cols_positive = [col.split('_binned')[0] for col in list_cols_positive]
			# append
			list_list_cols_positive.append(list_cols_positive)

		# map to reason
		list_list_reasons = []
		for list_cols_positive in tqdm(list_list_cols_positive):
			# map to reason
			list_reasons = [self.dict_aa[col] for col in list_cols_positive]
			# append
			list_list_reasons.append(list_reasons)

		# save to object
		self.list_list_reasons = list_list_reasons
		# return
		return self
	# generate response
	def generate_response(self):
		print(f'{self.list_unique_id}: Generating response...')

		# get n debtors
		int_n_debtors = self.df_clean.shape[0]

		# create df
		df = pd.DataFrame({
			'Row_id': self.list_unique_id,
			'Score_pd': self.list_scores_pd,
			'Score_lgd': self.list_scores_lgd,
			'Score_ecnl': [self.flt_mean_score] * int_n_debtors,
			'Score_ecnl_mod': [self.flt_mean_score_mapped] * int_n_debtors,
			'Key_factors': self.list_list_reasons,
			'Outlier_score': [0.0] * int_n_debtors,
			'Dict_tiers': [self.str_tiers] * int_n_debtors,
		})

		# convert to json
		str_json_output = df.to_json(orient='records')

		# convert to list
		list_output = eval(str_json_output)

		# formulate response
		dict_response = {
			'Request_id': '',
			'Zaml_processing_id': '',
			'Response': [{
				'Model_name': 'gen-xiii',
				'Model_version': 'v1',
				'Results': list_output,
				'Errors': [],
				'CounterOffers': [],
			}]
		}

		# save to object
		self.dict_response = dict_response
		# return
		return self