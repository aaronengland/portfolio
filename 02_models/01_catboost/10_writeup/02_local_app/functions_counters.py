import json
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import math

# naive - AE
class ProportionalECNLAE:
	# inititalize
	def __init__(self, df_tmp):
		self.df_tmp = df_tmp.copy()
	# get proportional ecnl
	def get_proportional_ecnls(self):
		# save values that will be changing
		flt_ecnl_mod = self.df_tmp['ecnl'].iloc[0]
		flt_amt_financed = self.df_tmp['amtfinanced__app'].iloc[0]

		# create a columns for original ecnl
		self.df_tmp['ecnl_mod_tmp'] = flt_ecnl_mod
		self.df_tmp['amtfinanced_tmp'] = flt_amt_financed

		# get ECNL in dollars using the new amt financed relative to the original model score
		self.df_tmp['ecnl_dollars_ae'] = self.df_tmp['amtfinanced__app'] * self.df_tmp['ecnl_mod_tmp']

		# get ecnl relative to the original amount financed
		self.df_tmp['ecnl_ae'] = self.df_tmp['ecnl_dollars_ae'] / self.df_tmp['amtfinanced_tmp']

		# drop
		self.df_tmp.drop(['ecnl_mod_tmp','amtfinanced_tmp'], axis=1, inplace=True)

		# return
		return self
	def plot_ecnl_by_cash_down(self):
		x = self.df_tmp['fltdowncash__app']
		y = self.df_tmp['ecnl_ae']
		# ax
		str_title = 'ECNL by Cash Down'
		fig, ax = plt.subplots(figsize=(9,5))
		ax.set_title(str_title)
		ax.set_xlabel('Cash Down')
		ax.set_ylabel('ECNL')
		# plot
		ax.plot(x, y)
		# show
		plt.show()

# naive - PT
class ProportionalECNLPT:
	# inititalize
	def __init__(self, df_tmp):
		self.df_tmp = df_tmp.copy()
	# get proportional ecnl
	def get_proportional_ecnls(self):
		# get original values
		flt_ecnl_mod = self.df_tmp['ecnl'].iloc[0]
		flt_amt_financed = self.df_tmp['amtfinanced__app'].iloc[0]
		flt_ecnl_dollars = flt_ecnl_mod * flt_amt_financed

		# assign original dollars lost
		self.df_tmp['ecnl_dollars_tmp'] = flt_ecnl_dollars

		# get min
		flt_min = self.df_tmp['fltdowncash__app'].min()
		# subtract min from cash down
		self.df_tmp['down_cash_diff_tmp'] = self.df_tmp['fltdowncash__app'] - flt_min

		# get ecnl in dollars
		self.df_tmp['ecnl_dollars_pt'] = self.df_tmp['ecnl_dollars_tmp'] - self.df_tmp['down_cash_diff_tmp']
		# get ecnl
		self.df_tmp['ecnl_pt'] = self.df_tmp['ecnl_dollars_pt'] / self.df_tmp['amtfinanced__app']

		# drop
		self.df_tmp.drop(['ecnl_dollars_tmp','down_cash_diff_tmp'], axis=1, inplace=True)

		# return
		return self
	def plot_ecnl_by_cash_down(self):
		x = self.df_tmp['fltdowncash__app']
		y = self.df_tmp['ecnl_pt']
		# ax
		str_title = 'ECNL by Cash Down'
		fig, ax = plt.subplots(figsize=(9,5))
		ax.set_title(str_title)
		ax.set_xlabel('Cash Down')
		ax.set_ylabel('ECNL')
		# plot
		ax.plot(x, y)
		# show
		plt.show()

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

# counters class
class CountersML:
	# initialize
	def __init__(self, df, cls_model_preprocessing, cls_model_inference_pd, cls_model_inference_lgd, flt_max_ltv, int_cash_down_increments, flt_factor_24_to_72):
		self.df = df # X raw
		self.cls_model_preprocessing = cls_model_preprocessing
		self.cls_model_inference_pd = cls_model_inference_pd
		self.cls_model_inference_lgd = cls_model_inference_lgd
		self.flt_max_ltv = flt_max_ltv
		self.int_cash_down_increments = int_cash_down_increments
		self.flt_factor_24_to_72 = flt_factor_24_to_72
	# get the important raw values
	def get_important_raw_values(self):
		# sales price
		flt_sales_price_original = self.df['fltsalesprice__app'].iloc[0]
		# book value
		flt_book_value_original = self.df['bookvalue__app'].iloc[0]
		if flt_book_value_original == 0:
			flt_book_value_original = 28125
		else:
			pass
		# down cash
		flt_down_cash_original = self.df['fltdowncash__app'].iloc[0]
		# down total
		flt_down_total_original = self.df['fltapproveddowntotal__app'].iloc[0]
		# difference in down total and down cash (i.e., trade-in value)
		flt_diff_original = flt_down_total_original - flt_down_cash_original
		# amount financed
		flt_amt_financed_original = self.df['amtfinanced__app'].iloc[0]
		if flt_amt_financed_original == 0:
			flt_amt_financed_original = 45000
		else:
			pass
		# bk type
		bk_type = self.df['intopenbktype__app'].iloc[0]
		# make boolean
		if pd.notnull(bk_type):
			bool_bk = True
		else:
			bool_bk = False
		# advance
		flt_advance_original = self.df['fltadvance__app'].iloc[0]
		# get front end
		flt_front_end_original = flt_advance_original * flt_book_value_original
		# vehicle class
		try:
			str_vehicle_class = self.df['vehicleclass__app'].iloc[0]
		except:
			str_vehicle_class = 'Class 2'
			print(f'No vehicle class in payload, default to {str_vehicle_class}')
		# dealer type
		str_dealer_type = self.df['strdealershiptrackertype__app'].iloc[0]
		# dealer state
		str_dealer_state = self.df['dealerstate__app'].iloc[0]
		
		# show original values
		dict_tmp = {
			'flt_sales_price_original': flt_sales_price_original,
			'flt_book_value_original': flt_book_value_original,
			'flt_down_cash_original': flt_down_cash_original,
			'flt_down_total_original': flt_down_total_original,
			'flt_diff_original': flt_diff_original,
			'flt_amt_financed_original': flt_amt_financed_original,
			'bool_bk': bool_bk,
			'flt_advance_original': flt_advance_original,
			'flt_front_end_original': flt_front_end_original,
			'str_vehicle_class': str_vehicle_class,
			'str_dealer_type': str_dealer_type,
			'str_dealer_state': str_dealer_state,
		}
		# save to self
		self.dict_tmp_raw = dict_tmp
		# return
		return self
	# preprocess and get ecnl
	def preprocess_and_get_predictions(self):
		# preprocess
		df = self.cls_model_preprocessing.transform(self.df)
		# set intopenbktype to string float
		df['intopenbktype__app'] = df['intopenbktype__app'].astype(float).astype(str)
		# predictions - pd
		list_cols = self.cls_model_inference_pd.feature_names_
		flt_pd = np.mean(self.cls_model_inference_pd.predict_proba(df[list_cols])[:,1])
		# predictions - lgd
		list_cols = self.cls_model_inference_lgd.feature_names_
		flt_lgd = np.mean(self.cls_model_inference_lgd.predict(df[list_cols]))
		# get ecnl
		flt_ecnl = flt_pd * flt_lgd
		# make 72 mo
		flt_ecnl_mod = flt_ecnl * self.flt_factor_24_to_72
		# save the number of rows
		int_nrows = df.shape[0]
		# save to self
		self.flt_ecnl_mod = flt_ecnl_mod
		self.df = df 
		self.int_nrows = int_nrows
		# return
		return self
	# get important clean values
	def get_important_clean_values(self):
		# book value
		flt_book_value = self.df['bookvalue__app'].iloc[0]
		# down cash
		flt_down_cash = self.df['fltdowncash__app'].iloc[0]
		# down total
		flt_down_total = self.df['fltapproveddowntotal__app'].iloc[0]
		# difference in down total and down cash (i.e., trade-in value)
		flt_diff = flt_down_total - flt_down_cash
		# amount financed
		flt_amt_financed = self.df['amtfinanced__app'].iloc[0]
		# advance
		flt_advance = self.df['fltadvance__app'].iloc[0]
		# factor
		flt_factor = self.df['factor'].iloc[0]		
		# show preprocessed values
		dict_tmp = {
			'flt_book_value': flt_book_value,
			'flt_down_cash': flt_down_cash,
			'flt_down_total': flt_down_total,
			'flt_diff': flt_diff,
			'flt_amt_financed': flt_amt_financed,
			'flt_advance': flt_advance,
			'flt_factor': flt_factor,
		}
		# save to self
		self.dict_tmp_clean = dict_tmp
		# return 
		return self
	# get values for cash down
	def get_vals_cash_down(self):
		# get flt_down_cash
		flt_down_cash = int(self.dict_tmp_raw['flt_down_cash_original'])
		# get flt_amt_financed
		flt_amt_financed = int(self.dict_tmp_raw['flt_amt_financed_original'])

		# get list of original cash down to amt financed in increments
		list_cash_down = list(range(
			flt_down_cash, # clean cash down
			flt_down_cash+flt_amt_financed+1, # to maximum amount financed
			self.int_cash_down_increments, # increments of x
		))

		# save to self
		self.list_cash_down = list_cash_down
		self.int_len_list = len(list_cash_down)
		# return
		return self
	# expand clean data
	def expand_clean_data(self):
		# make df large
		df_lg = self.df.iloc[np.tile(np.arange(self.int_nrows), self.int_len_list)].copy()
		# save to self
		self.df_lg = df_lg 
		# return
		return self
	# make a column to keep debtor and codebtor together
	def create_sample_column(self):
		# get number of rows
		list_sample = list(np.repeat(list(range(0, self.int_len_list)), self.int_nrows))
		# assign
		self.df_lg['sample'] = list_sample
		# return
		return self
	# assign cash down
	def assign_cash_down(self):
		list_cash_down = [int_val for int_val in self.list_cash_down for _ in range(self.int_nrows)]
		# save to object
		self.list_cash_down = list_cash_down
		# assign
		self.df_lg['fltdowncash__app'] = list_cash_down
		# get the difference from the original raw value value
		self.df_lg['diff'] = self.df_lg['fltdowncash__app'] - self.dict_tmp_raw['flt_down_cash_original']
		# return
		return self
	# assign book value
	def assign_book_value(self):
		self.df_lg['bookvalue__app'] = self.dict_tmp_raw['flt_book_value_original']
		# return
		return self
	# get the new down total
	def get_new_down_total(self):
		# get flt_down_diff
		flt_down_diff = self.dict_tmp_raw['flt_diff_original']
		# down cash plus trade in value
		list_down_total = list(self.df_lg['fltdowncash__app'] + flt_down_diff)
		self.list_down_total = list_down_total
		# assign
		self.df_lg['fltapproveddowntotal__app'] = list_down_total
		# return
		return self
	# get the new amount financed
	def get_new_amount_financed(self):
		# get flt_amt_financed
		flt_amt_financed = self.dict_tmp_raw['flt_amt_financed_original']
		# get flt_down_total
		flt_down_total = self.dict_tmp_raw['flt_down_total_original']
		# get the new amt financed
		list_amt_financed = list((flt_amt_financed + flt_down_total) - self.df_lg['fltapproveddowntotal__app'])
		self.list_amt_financed = list_amt_financed
		# assign
		self.df_lg['amtfinanced__app'] = list_amt_financed
		# return
		return self
	# get the new advance
	def get_new_advance(self):
		# get new front end
		self.df_lg['flt_front_end'] = self.dict_tmp_raw['flt_front_end_original'] - self.df_lg['diff']
		# get new advance
		self.df_lg['fltadvance__app'] = self.df_lg['flt_front_end'] / self.dict_tmp_raw['flt_book_value_original']
		# return
		return self
	# inflate/deflate
	def inflate_deflate_values(self):
		list_cols = [
			'fltdowncash__app',
			'fltapproveddowntotal__app',
			'amtfinanced__app',
			'bookvalue__app',
		]
		for col in tqdm(list_cols):
			self.df_lg[col] = self.df_lg[col] * self.dict_tmp_clean['flt_factor']
		# return
		return self
	# bin values
	def bin_values(self):
		dict_round = {
			'fltdowncash__app': 500,
			'fltapproveddowntotal__app': 500,
			'amtfinanced__app': 500,
			'fltadvance__app': 0.025,
			'bookvalue__app': 500,
		}
		for key, val in tqdm (dict_round.items()):
			self.df_lg[key] = val * round(pd.to_numeric(self.df_lg[key]) / val)
		# return
		return self
	# get new ltv
	def get_new_ltv(self):
		self.df_lg['ENG-loan_to_value'] = self.df_lg['amtfinanced__app'] / self.df_lg['bookvalue__app']
		# return
		return self
	# get predictions
	def get_predictions(self):
		# get pd model
		cls_model_pd = self.cls_model_inference_pd
		list_cols_pd = list(cls_model_pd.feature_names_)
		# get lgd model
		cls_model_lgd = self.cls_model_inference_lgd
		list_cols_lgd = list(cls_model_lgd.feature_names_)
		
		# get predictions pivoting on down
		self.df_lg['pd_down'] = cls_model_pd.predict_proba(self.df_lg[list_cols_pd])[:,1]
		self.df_lg['lgd_down'] = cls_model_lgd.predict(self.df_lg[list_cols_lgd])

		# rename
		dict_rename = {
			'fltdowncash__app': 'fltdowncash__app_tmp',
			'fltapproveddowntotal__app': 'fltapproveddowntotal__app_tmp',
		}
		self.df_lg.rename(columns=dict_rename, inplace=True)
		
		# assign the original values
		self.df_lg['fltdowncash__app'] = self.dict_tmp_clean['flt_down_cash']
		self.df_lg['fltapproveddowntotal__app'] = self.dict_tmp_clean['flt_down_total']

		# get predictions pivoting on amt financed
		self.df_lg['pd_amt'] = cls_model_pd.predict_proba(self.df_lg[list_cols_pd])[:,1]
		self.df_lg['lgd_amt'] = cls_model_lgd.predict(self.df_lg[list_cols_lgd])

		# re-assign
		self.df_lg['fltdowncash__app'] = self.df_lg['fltdowncash__app_tmp']
		self.df_lg['fltapproveddowntotal__app'] = self.df_lg['fltapproveddowntotal__app_tmp']
		
		# subset
		list_cols = [col for col in self.df_lg.columns if '__app_tmp' not in col]
		self.df_lg = self.df_lg[list_cols].copy()
		# return
		return self
	# group so we can get ECNL
	def group_by_sample(self):
		# group by the sample
		df_tmp = self.df_lg.groupby(by='sample', as_index=False).agg({
			'bookvalue__app': 'mean',
			'fltdowncash__app': 'mean',
			'diff': 'mean',
			'fltapproveddowntotal__app': 'mean',
			'amtfinanced__app': 'mean',
			'fltadvance__app': 'mean',
			'ENG-loan_to_value': 'mean',
			'pd_down': 'mean',
			'lgd_down': 'mean',
			'pd_amt': 'mean',
			'lgd_amt': 'mean',
		})
		# save to self
		self.df_tmp = df_tmp.copy()
		# return
		return self
	# get ecnl
	def get_ecnl(self):
		# calc ecnl - down
		self.df_tmp['ecnl_down'] = (self.df_tmp['pd_down'] * self.df_tmp['lgd_down']) * self.flt_factor_24_to_72
		# calc ecnl - amt financed
		self.df_tmp['ecnl_amt'] = (self.df_tmp['pd_amt'] * self.df_tmp['lgd_amt']) * self.flt_factor_24_to_72
		# return
		return self
	# get original app
	def get_original_app(self):
		# get original app
		df_tmp_0 = self.df_tmp[self.df_tmp['diff'] == 0].copy()
		# save to self
		self.df_tmp_0 = df_tmp_0.copy()
		# return
		return self
	# concat dfs
	def create_offer_column(self):
		# create offer column
		self.df_tmp['Offer'] = list(range(0, self.df_tmp.shape[0]))
		# sort
		self.df_tmp.sort_values(by='ENG-loan_to_value', ascending=False, inplace=True)
		# return
		return self
	# get original down cash
	def get_original_down_cash(self):
		# rm dups so it works for codebtors
		list_cash_down = list(dict.fromkeys(self.list_cash_down))
		self.df_tmp['Down Cash'] = list_cash_down
		# return
		return self
	# get original down total
	def get_original_down_total(self):
		# rm dups so it works for codebtors
		list_down_total = list(dict.fromkeys(self.list_down_total))
		# use the original + the diff
		self.df_tmp['Down Total'] = list_down_total
		# return
		return self
	# get original amount financed
	def get_original_amt_financed(self):
		# rm dups so it works for codebtors
		list_amt_financed = list(dict.fromkeys(self.list_amt_financed))
		self.df_tmp['Amount Financed'] = list_amt_financed
		# return
		return self
	# assign original book value
	def assign_original_book_value(self):
		# assign
		self.df_tmp['Book Value'] = self.dict_tmp_raw['flt_book_value_original']
		# return
		return self
	# get original ltv
	def get_original_ltv(self):
		# ltv
		self.df_tmp['Loan to Value'] = self.df_tmp['Amount Financed'] / self.df_tmp['Book Value']

		# get the original app
		df_tmp_original = self.df_tmp[self.df_tmp['Offer'] == 0].copy()

		# rm original app
		df_tmp = self.df_tmp[self.df_tmp['Offer'] != 0].copy()
		# subset
		df_tmp = df_tmp[df_tmp['Loan to Value'] <= self.flt_max_ltv].copy()

		# concatenate
		list_df = [
			df_tmp_original,
			df_tmp,
		]
		df_tmp = pd.concat(list_df)
		# sort
		df_tmp.sort_values(by='Offer', ascending=True, inplace=True)

		# save to object
		self.df_tmp = df_tmp.copy()
		# return
		return self
	# get sales price
	def get_sales_price(self):
		# assign original sales price
		self.df_tmp['Sales Price Original'] = self.dict_tmp_raw['flt_sales_price_original']
		# use the original - the diff
		self.df_tmp['Sales Price'] = self.dict_tmp_raw['flt_sales_price_original'] - self.df_tmp['diff']
		# return
		return self
	# assign original values
	def assign_original_values(self):
		# cash down
		self.df_tmp['Down Cash Original'] = self.dict_tmp_raw['flt_down_cash_original']
		# down total
		self.df_tmp['Down Total Original'] = self.dict_tmp_raw['flt_down_total_original']
		# return
		return self

# new class
class GetOffers:
	# init
	def __init__(self, df, str_tiers, flt_prop_c, flt_pct_threshold):
		self.df = df
		self.str_tiers = str_tiers
		self.flt_prop_c = flt_prop_c
		self.flt_pct_threshold = flt_pct_threshold
	# get initial approval
	def get_initial_approval(self):
		# convert str_tier to dict_tier
		dict_tiers = eval(self.str_tiers)
		# get c threshold
		flt_threshold_c = dict_tiers['C']
		# get decline threshold
		flt_threshold_ecnl = dict_tiers['D']
		# get diff
		flt_diff = flt_threshold_ecnl - flt_threshold_c
		# multiply by flt_prop_c
		flt_c_padding = flt_diff * self.flt_prop_c
		# add to flt_threshold_c
		flt_threshold_ecnl_counter = flt_threshold_c + flt_c_padding
		print(f'Counter threshold: {flt_threshold_ecnl_counter}')

		# get initial ecnl
		flt_ecnl_initial = self.df[self.df['Offer'] == 0]['ecnl_amt'].iloc[0]
		print(f'Initial ECNL: {flt_ecnl_initial:0.4f}')
		# get boolean for approved or not
		if flt_ecnl_initial <= flt_threshold_ecnl:
			bool_approved = True
		else:
			bool_approved = False
		print(f'Approved (T/F): {bool_approved}')

		# get tier
		if flt_ecnl_initial <= dict_tiers['A1']:
			str_tier = 'A1'
		elif flt_ecnl_initial <= dict_tiers['A']:
			str_tier = 'A'
		elif flt_ecnl_initial <= dict_tiers['B']:
			str_tier = 'B'
		elif flt_ecnl_initial <= dict_tiers['C']:
			str_tier = 'C'
		elif flt_ecnl_initial <= dict_tiers['D']:
			str_tier = 'D'
		else:
			str_tier = 'Decline'
		print(f'Tier: {str_tier}')

		# save to object
		self.flt_ecnl_initial = flt_ecnl_initial
		self.flt_threshold_ecnl = flt_threshold_ecnl
		self.flt_threshold_ecnl_counter = flt_threshold_ecnl_counter
		self.bool_approved = bool_approved
		self.str_tier = str_tier
		# return object
		return self
	# get offers for decline to approval
	def get_offers_decline_to_approval(self):
		print(f'Initial offer Declined: {self.flt_ecnl_initial:0.4f}')

		# subset to counter offers
		df_tmp = self.df[self.df['Offer'] > 0].copy()

		# save to object
		self.df_all_offers = df_tmp.copy()

		# subset to approved offers on ECNL (LTV)
		str_ecnl = 'ecnl_amt'
		df_tmp_2 = df_tmp[df_tmp[str_ecnl] <= self.flt_threshold_ecnl_counter].copy()
		# rm negative fees
		df_tmp_2 = df_tmp_2[df_tmp_2['net_discount_amt'] >= 0].copy()

		# get n offers
		int_n_offers = df_tmp_2.shape[0]
		print(f'There are {int_n_offers} offers on {str_ecnl}')

		# logic
		if int_n_offers == 0: # if no offers on LTV
			# subset to approved offers on ECNL (Down)
			str_ecnl = 'ecnl_down'
			df_tmp_2 = df_tmp[df_tmp[str_ecnl] <= self.flt_threshold_ecnl_counter].copy()
			# rm negative fees
			df_tmp_2 = df_tmp_2[df_tmp_2['net_discount_down'] >= 0].copy()
			# get n offers
			int_n_offers = df_tmp_2.shape[0]
		else:
			pass
		# message
		print(f'There are {int_n_offers} offers on {str_ecnl}')

		# logic for n counters
		if int_n_offers == 0:
			int_offer_min = 0
		else:
			# get the first approved offer
			int_offer_min = df_tmp_2['Offer'].min()
		# get list of offers
		list_int_offers = [
			0,
			int_offer_min,
		]
		# subset
		self.df = self.df[self.df['Offer'].isin(list_int_offers)].copy()

		# save to object
		self.str_ecnl = str_ecnl
		# get the 
		return self
	# method for approval to approval
	def get_offers_approval_to_approval(self):
		print(f'Initial offer Approved: {self.flt_ecnl_initial:0.4f}')

		# get original values
		df_tmp = self.df[self.df['Offer'] == 0].copy()
		# make dictionary
		dict_original_values = {
			'LTV': df_tmp['Loan to Value'].iloc[0],
			'APR': df_tmp['apr_amt'].iloc[0],
			'Fees': df_tmp['net_discount_amt'].iloc[0],
			'Tier': self.str_tier,
		}
		print('Original Values:')
		print(dict_original_values)

		# get original LTV
		flt_ltv_original = dict_original_values['LTV']
		print(f'Original LTV: {flt_ltv_original:0.4f}')
		# get pct below
		flt_ltv_below = flt_ltv_original * self.flt_pct_threshold
		# lower limit
		flt_ltv_min = flt_ltv_original - flt_ltv_below
		print(f'Minimum LTV: {flt_ltv_min:0.4f}')

		# get the original APR
		flt_apr_original = dict_original_values['APR']
		print(f'Original APR: {flt_apr_original:0.4f}')

		# get the original Fees
		flt_fees = dict_original_values['Fees']
		print(f'Original Fees: {flt_fees:0.4f}')

		# get the logic for tier
		str_tier = dict_original_values['Tier']
		if str_tier in ['A1','A','B']:
			int_threshold = 100
		else:
			int_threshold = 200
		print(f'APR + Fees Threshold: {int_threshold}')

		# rm original offer
		df_tmp = self.df[self.df['Offer'] > 0].copy()

		# filter based on flt_ltv_min
		df_tmp = df_tmp[df_tmp['Loan to Value'] < flt_ltv_min].copy()

		# get diff - APR
		df_tmp['APR_diff_amt'] = flt_apr_original - df_tmp['apr_amt']
		df_tmp['APR_diff_down'] = flt_apr_original - df_tmp['apr_down']

		# convert to dollars
		df_tmp['APR_diff_amt_dollars'] = (df_tmp['APR_diff_amt'] / 0.1) * 50 # 0.1 APR == $50
		df_tmp['APR_diff_down_dollars'] = (df_tmp['APR_diff_down'] / 0.1) * 50 # 0.1 APR == $50

		# get diff - Fees
		df_tmp['Fees_diff_amt_dollars'] = flt_fees - df_tmp['net_discount_amt']
		df_tmp['Fees_diff_down_dollars'] = flt_fees - df_tmp['net_discount_down']

		# sum
		df_tmp['diff_amt_dollars_sum'] = df_tmp['APR_diff_amt_dollars'] + df_tmp['Fees_diff_amt_dollars']
		df_tmp['diff_down_dollars_sum'] = df_tmp['APR_diff_down_dollars'] + df_tmp['Fees_diff_down_dollars']

		# save to object
		self.df_all_offers = df_tmp.copy()

		# get the first offer value
		int_offer_tmp = df_tmp['Offer'].min()

		# subset to that offer
		df_tmp = df_tmp[df_tmp['Offer'] == int_offer_tmp].copy()

		# subset on counters threshold
		df_tmp_2 = df_tmp[df_tmp['ecnl_amt'] <= self.flt_threshold_ecnl_counter].copy()
		# subset on threshold - amt
		df_tmp_2 = df_tmp_2[df_tmp_2['diff_amt_dollars_sum'] >= int_threshold].copy()
		# rm anything with negative fees
		df_tmp_2 = df_tmp_2[df_tmp_2['net_discount_amt'] >= 0].copy()

		# get number of rows
		int_nrows_amt = df_tmp_2.shape[0]
		print(f'There are {int_nrows_amt} counters on amount financed')

		# logic
		if int_nrows_amt > 0: # if we have counters on amount financed
			# save ecnl type
			str_ecnl_type = 'amt'
			# save ecnl column name
			str_ecnl = 'ecnl_amt'
			# get the first offer
			int_offer_min = df_tmp_2['Offer'].min()
		else: # if there are no offers on amount financed
			print(f'Looking for counters on down')
			# save ecnl type
			str_ecnl_type = 'down'
			# save ecnl column name
			str_ecnl = 'ecnl_down'

			# subset on counters threshold
			df_tmp_2 = df_tmp[df_tmp['ecnl_down'] <= self.flt_threshold_ecnl_counter].copy()
			# try down
			df_tmp_2 = df_tmp_2[df_tmp_2['diff_down_dollars_sum'] >= int_threshold].copy()
			# rm anything with negative fees
			df_tmp_2 = df_tmp_2[df_tmp_2['net_discount_down'] >= 0].copy()

			# get number of rows
			int_nrows_down = df_tmp_2.shape[0]
			print(f'There are {int_nrows_down} counters on down')
			# logic
			if int_nrows_down > 0:
				# get the first offer
				int_offer_min = df_tmp_2['Offer'].min()
			else:
				int_offer_min = 0
		print(f'Best Counter Offer: {int_offer_min}')
		
		# get list of offers
		list_int_offers = [
			0,
			int_offer_min,
		]
		# rm dups
		list_int_offers = list(dict.fromkeys(list_int_offers))
		df_tmp = self.df[self.df['Offer'].isin(list_int_offers)].copy()

		# subset
		self.df = self.df[self.df['Offer'].isin(list_int_offers)].copy()

		# save to object
		self.str_ecnl_type = str_ecnl_type
		self.str_ecnl = str_ecnl
		# get the 
		return self
	# get offers
	def get_the_offers(self):
		# if the initial offer is an approval
		if self.bool_approved:
			self.get_offers_approval_to_approval()
		else:
			self.get_offers_decline_to_approval()
	# susbet to important columns
	def subset_and_rename_columns(self):
		# logic
		if self.str_ecnl == 'ecnl_amt':
			str_down_cash = 'Down Cash Original'
			str_sales_price = 'Sales Price'
			str_apr = 'apr_amt'
			str_net_discount = 'net_discount_amt'
		else:
			str_down_cash = 'Down Cash'
			str_sales_price = 'Sales Price Original'
			str_apr = 'apr_down'
			str_net_discount = 'net_discount_down'
		# subset
		list_cols = [
			'Offer',
			self.str_ecnl,
			str_down_cash,
			'Amount Financed',
			str_sales_price,
			str_apr,
			str_net_discount,
			'Loan to Value',
		]
		self.df = self.df[list_cols].copy()
		# rename
		dict_rename = {
			self.str_ecnl: 'ECNL',
			str_down_cash: 'Down Cash',
			str_sales_price: 'Sales Price',
			str_apr: 'APR',
			str_net_discount: 'Net Discount',
			'Loan to Value': 'Current LTV',
		}
		self.df.rename(columns=dict_rename, inplace=True)
		# return object
		return self
	# tag approve or decline
	def tag_approve_decline(self):
		# tag based on threshold from tiers
		self.df['Decision'] = self.df['ECNL'].apply(
			lambda x: 'Declined' if x > self.flt_threshold_ecnl else 'Approved',
		)
		# return
		return self
	# get max ltv and reorder columns
	def get_max_ltv_and_reorder(self):
		# subset to approvals
		df_tmp = self.df[self.df['Decision'] == 'Approved'].copy()
		# get maximum LTV
		flt_max_ltv = df_tmp['Current LTV'].max()
		# assign
		self.df['Max LTV'] = flt_max_ltv

		# reorder
		list_cols = [
			'Offer',
			'ECNL',
			'Decision',
			'Down Cash',
			'Amount Financed',
			'Sales Price',
			'APR',
			'Net Discount',
			'Current LTV',
			'Max LTV',
		]
		self.df = self.df[list_cols].copy()
		# rename
		dict_rename = {
			'Down Cash': 'DownCash',
			'Amount Financed': 'AmountFinanced',
			'Sales Price': 'SalesPrice',
			'Net Discount': 'NetDiscount',
			'Current LTV': 'CurrentLTV',
			'Max LTV': 'MaxLTV',
		}
		self.df.rename(columns=dict_rename, inplace=True)
		# return object
		return self