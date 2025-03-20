import pandas as pd
from tqdm import tqdm
import json
import numpy as np
from io import StringIO
import xml.etree.ElementTree as ET
import xmltodict

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

# class
class PayloadToDataFrame:
	# init
	def __init__(self):
		pass
	# get data
	def get_data(self, str_request):
		# convert to dictionary
		dict_request = json.loads(str_request)
		# get the rows
		list_dict_rows = dict_request['rows']

		# iterate through the rows
		list_df_tmp_concat = []
		for a, dict_row in enumerate(list_dict_rows):
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
		df_out = pd.concat(list_df_tmp_concat)
		# if there is no strdealershiptrackertype__app
		if 'strdealershiptrackertype__app' not in list(df_out.columns):
			df_out['strdealershiptrackertype__app'] = 'Franchise'
		else:
			pass
		# if there is no dealer state
		if 'dealerstate__app' not in list(df_out.columns):
			df_out['dealerstate__app'] = df_out['strname__app']
		else:
			pass
		# if there is no fltgrossmonthly__income_sum
		if 'fltgrossmonthly__income_sum' not in list(df_out.columns):
			df_out['fltgrossmonthly__income_sum'] = df_out['fltgrossmonthly__app']
		else:
			pass
		# if there is no amtfinanced__app
		if 'amtfinanced__app' not in list(df_out.columns):
			df_out['amtfinanced__app'] = df_out['fltamountfinanced__app']
		else:
			pass
		# if there is no bookvalue__app
		if 'bookvalue__app' not in list(df_out.columns):
			df_out['bookvalue__app'] = df_out['vehiclevalue__app']
		else:
			pass
		# return
		return df_out