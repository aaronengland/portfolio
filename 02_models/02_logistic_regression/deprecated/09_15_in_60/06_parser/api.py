import pandas as pd
from tqdm import tqdm
import json
import numpy as np
from io import StringIO
import xml.etree.ElementTree as ET
import xmltodict
from functions_counters import CountersML, GetOffers
from functions_counters_pricing import PricingCounters

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
			# closed
			'flt_payment_closed': np.nan,
			'int_n_months_closed': np.nan,
			'list_pmt_hx_closed': np.nan,
			'flt_wtd_avg_closed': np.nan,
			'flt_avg_closed': np.nan,
			'int_30dpd_closed': np.nan,
			'int_60dpd_closed': np.nan,
			'int_90dpd_closed': np.nan,
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
	
	# get n payments
	df_tmp['n_months'] = df_tmp['str_pmt_hx__tu_pmthx'].apply(
		lambda x: len(x),
	)
	
	# convert str_pmt_hx__tu_pmthx to lists of 1 and 0
	df_tmp['str_pmt_hx__tu_pmthx'] = df_tmp['str_pmt_hx__tu_pmthx'].apply(
		lambda x: [1 if str_val == '1' else 0 for str_val in list(x)],
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
	else:
		flt_payment_open = np.nan
		int_n_months_open = np.nan
		list_pmt_hx_open = np.nan
		flt_wtd_avg_open = np.nan
		flt_avg_open = np.nan
		int_30dpd_open = np.nan
		int_60dpd_open = np.nan
		int_90dpd_open = np.nan
	
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
	else:
		flt_payment_closed = np.nan
		int_n_months_closed = np.nan
		list_pmt_hx_closed = np.nan
		flt_wtd_avg_closed = np.nan
		flt_avg_closed = np.nan
		int_30dpd_closed = np.nan
		int_60dpd_closed = np.nan
		int_90dpd_closed = np.nan
	
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
		# closed
		'flt_payment_closed': flt_payment_closed,
		'int_n_months_closed': int_n_months_closed,
		'list_pmt_hx_closed': list_pmt_hx_closed,
		'flt_wtd_avg_closed': flt_wtd_avg_closed,
		'flt_avg_closed': flt_avg_closed,
		'int_30dpd_closed': int_30dpd_closed,
		'int_60dpd_closed': int_60dpd_closed,
		'int_90dpd_closed': int_90dpd_closed,
	}
	# return
	return dict_output

# class
class ParsePayload:
	# init
	def __init__(self, cls_model_preprocessing, cls_model_inference, arr_quantiles_model, arr_score_quantiles_pricing, dict_aa, str_tiers):
		self.cls_model_preprocessing = cls_model_preprocessing
		self.cls_model_inference = cls_model_inference
		self.arr_quantiles_model = arr_quantiles_model
		self.arr_score_quantiles_pricing = arr_score_quantiles_pricing
		self.dict_aa = dict_aa
		self.str_tiers = str_tiers
	# get data
	def get_data(self, str_request):
		print('Getting data...')
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
		df = pd.concat(list_df_tmp_concat)
		# get unique ids
		list_unique_id = list(df['uniqueid__app'])
		# save to object
		self.df_raw = df.copy()
		self.list_unique_id = list_unique_id
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
		# save to object
		self.df_raw = df.copy()
		# return
		return self
	# preprocessing
	def preprocessing(self):
		print(f'{self.list_unique_id}: Preprocessing data...')
		# preprocess
		df = self.cls_model_preprocessing.transform(self.df_raw.copy())
		# save to object
		self.df_clean = df.copy()
		# return
		return self
	# predict
	def get_predictions(self):
		print(f'{self.list_unique_id}: Getting predictions...')
		df = self.df_clean.copy()
		# predict
		list_cols_model = list(self.cls_model_inference.feature_names_in_)
		df['yhat'] = self.cls_model_inference.predict_proba(df[list_cols_model])[:,1]
		# get the mean prediction
		flt_mean_score = df['yhat'].mean()
		# make into list for interpolation
		list_model_scores = list(df['yhat'])
		# save to object
		self.df_clean = df.copy()
		self.flt_mean_score = flt_mean_score
		self.list_model_scores = list_model_scores
		# return
		return self
	# interpolate
	def interpolate(self):
		print(f'{self.list_unique_id}: Interpolating...')
		df = self.df_clean.copy()
		# map quantiles and transform data
		list_mapped_data = list(np.interp(
			x=[self.flt_mean_score],
			xp=self.arr_quantiles_model,
			fp=self.arr_score_quantiles_pricing,
		))
		# get score
		flt_mean_score_mapped = list_mapped_data[0]
		# assign
		df['yhat_mapped_ecnl'] = flt_mean_score_mapped
		# save to object
		self.flt_mean_score_mapped = flt_mean_score_mapped
		self.df_clean = df.copy()
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
	# counter offers
	def counter_offers(self):
		print(f'{self.list_unique_id}: Getting counter offers...')
		# constants
		flt_pct_threshold = 0.10
		int_dollars_round_fees = 1
		flt_avg_life = 2.3
		flt_equity_intercept = 0.04
		flt_equity_slope = 0.80
		flt_securitization = 0.0595
		flt_late_fee_income = 0.0042
		flt_state_rate_cap = 1.0
		flt_cnl_scaler = 0.8039
		flt_prop_c = 0.5

		# init
		cls_model_counters = CountersML(
			df=self.df_clean.copy(),
			cls_model_preprocessing=self.cls_model_preprocessing,
			cls_model_inference=self.cls_model_inference,
			arr_quantiles_model=self.arr_quantiles_model,
			arr_score_quantiles_pricing=self.arr_score_quantiles_pricing,
		)
		# run methods
		cls_model_counters.get_important_values()
		cls_model_counters.get_vals_ltv()
		cls_model_counters.expand_clean_data()
		cls_model_counters.create_sample_column()
		cls_model_counters.assign_ltv()
		cls_model_counters.get_predictions()
		cls_model_counters.create_sample_column()
		cls_model_counters.group_by_sample()
		cls_model_counters.get_ecnl()
		cls_model_counters.create_offer_column()

		# get df_tmp
		df_tmp = cls_model_counters.df_tmp.copy()

		# get bool bk
		bool_bk = cls_model_counters.dict_tmp_raw['bool_bk']
		print(f'BK: {bool_bk}')
		# get vehicle class
		str_vehicle_class = cls_model_counters.dict_tmp_raw['str_vehicle_class']
		print(f'Vehicle Class: {str_vehicle_class}')
		# get dealer type
		str_dealer_type = cls_model_counters.dict_tmp_raw['str_dealer_type']
		print(f'Dealer Type: {str_dealer_type}')
		# get dealer state
		str_dealer_state = cls_model_counters.dict_tmp_raw['str_dealer_state']
		print(f'Dealer State: {str_dealer_state}')
		
		# init pricing class
		print(f'{self.list_unique_id}: Pricing counter offers...')
		cls_model_pricing = PricingCounters(
			df=df_tmp,
			bool_bk=bool_bk,
			str_tiers=self.str_tiers,
			flt_cnl_scaler=flt_cnl_scaler,
			flt_avg_life=flt_avg_life, 
			flt_equity_intercept=flt_equity_intercept, 
			flt_equity_slope=flt_equity_slope, 
			flt_securitization=flt_securitization, 
			flt_late_fee_income=flt_late_fee_income, 
			flt_state_rate_cap=flt_state_rate_cap,
			int_dollars_round_fees=int_dollars_round_fees,
			str_vehicle_class=str_vehicle_class,
			str_dealer_type=str_dealer_type,
			str_dealer_state=str_dealer_state,
		)
		# run methods
		cls_model_pricing.pricing_test_logic()
		cls_model_pricing.map_to_tier()
		cls_model_pricing.get_equity()
		cls_model_pricing.get_profit()
		cls_model_pricing.get_discount()
		cls_model_pricing.get_late_fee()
		cls_model_pricing.get_funding_cost()
		cls_model_pricing.get_adjusted_ecnl()
		cls_model_pricing.get_expected_losses()
		cls_model_pricing.get_buy_rate()
		cls_model_pricing.get_raw_apr()
		cls_model_pricing.get_raw_discount_adjustment()
		cls_model_pricing.get_raw_apr_adjustment()
		cls_model_pricing.get_rate_cap_handicap()
		cls_model_pricing.get_additional_discount_needed()
		cls_model_pricing.get_apr()
		cls_model_pricing.get_net_discount()

		# get df_tmp
		df_tmp = cls_model_pricing.df.copy()

		# init get offers class
		print(f'{self.list_unique_id}: Showing counter offers...')
		cls_model_get_offers = GetOffers(
			df=df_tmp,
			str_tiers=self.str_tiers,
			flt_prop_c=flt_prop_c,
			flt_pct_threshold=flt_pct_threshold,
		)
		# run methods
		cls_model_get_offers.get_initial_approval()
		cls_model_get_offers.get_the_offers()
		cls_model_get_offers.subset_columns()
		cls_model_get_offers.tag_approve_decline()
		cls_model_get_offers.get_max_ltv_and_reorder()

		# get df
		df_tmp = cls_model_get_offers.df.copy()

		# make copy
		df_counters = df_tmp.copy()
		list_dict_counters = df_counters.to_dict('records')

		# get the original APR and Net Discount
		df_tmp = df_tmp[df_tmp['Offer'] == 0].copy()

		# get the original APR and Net Discount
		df_tmp = df_tmp[df_tmp['Offer'] == 0].copy()
		flt_apr = df_tmp['APR'].iloc[0]
		if str(flt_apr) == 'nan':
			flt_apr = 'NaN'
		print(f'Original APR: {flt_apr}')
		flt_net_discount = df_tmp['NetDiscount'].iloc[0]
		if str(flt_net_discount) == 'nan':
			flt_net_discount = 'NaN'
		print(f'Original Net Discount: {flt_net_discount}')

		# save to dict_output
		self.df_counters = df_counters
		self.list_dict_counters = list_dict_counters
		self.flt_apr = flt_apr
		self.flt_net_discount = flt_net_discount
		# return object
		return self
	# generate response
	def generate_response(self):
		print(f'{self.list_unique_id}: Generating response...')

		# get n debtors
		int_n_debtors = self.df_clean.shape[0]

		# create df
		df = pd.DataFrame({
			'Row_id': self.list_unique_id,
			'Score_pd': self.list_model_scores,
			'Score_ecnl_mod': [self.flt_mean_score_mapped] * int_n_debtors,
			'APR': [self.flt_apr] * int_n_debtors,
			'Net_discount': [self.flt_net_discount] * int_n_debtors,
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
				'Model_name': 'prestige-gen-xiii',
				'Model_version': 'v1',
				'Results': list_output,
				'Errors': [],
				'CounterOffers': self.list_dict_counters,
			}]
		}

		# save to object
		self.dict_response = dict_response
		# return
		return self