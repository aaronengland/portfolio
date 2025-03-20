import json
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import math

# counters class
class CountersML:
	# initialize
	def __init__(self, df, cls_model_preprocessing, cls_model_inference, arr_quantiles_model, arr_score_quantiles_pricing):
		self.df = df # clean data
		self.cls_model_preprocessing = cls_model_preprocessing
		self.cls_model_inference = cls_model_inference
		self.arr_quantiles_model = arr_quantiles_model
		self.arr_score_quantiles_pricing = arr_score_quantiles_pricing
	# get the important raw values
	def get_important_values(self):
		# bk type
		bk_type = self.df['intopenbktype__app'].iloc[0]
		# make boolean
		if pd.notnull(bk_type):
			bool_bk = True
		else:
			bool_bk = False
		
		# dealer type
		str_dealer_type = self.df['strdealershiptrackertype__app'].iloc[0]
		# dealer state
		str_dealer_state = self.df['dealerstate__app'].iloc[0]
		# ltv
		flt_ltv = self.df['ENG-loan_to_value'].iloc[0]
		# vehicle class
		str_vehicle_class = self.df['vehicleclass__app'].iloc[0]
		# book value
		flt_book_value = self.df['bookvalue__app'].iloc[0]
		
		# show original values
		dict_tmp = {
			'bool_bk': bool_bk,
			'str_dealer_type': str_dealer_type,
			'str_dealer_state': str_dealer_state,
			'flt_ltv': flt_ltv,
			'str_vehicle_class': str_vehicle_class,
			'flt_book_value': flt_book_value,
		}
		# save to self
		self.dict_tmp_raw = dict_tmp
		# return
		return self
	# get values for ltv
	def get_vals_ltv(self):
		# set the number of counters
		int_n = 100
		# set the minimum LTV
		flt_ltv_min = 0
		# get the original ltv (clean)
		flt_ltv_max = self.dict_tmp_raw['flt_ltv']
		# create list of possible LTV
		list_flt_ltv = list(np.linspace(flt_ltv_min, flt_ltv_max, int_n))
		# save to self
		self.list_flt_ltv = list_flt_ltv
		self.int_len_list = int_n
		# return
		return self
	# expand clean data
	def expand_clean_data(self):
		# inference model
		cls_model_inference = self.cls_model_inference
		# list of columns in the model
		list_cols_model = list(cls_model_inference.feature_names_in_)
		# get raw names
		list_cols_model_raw = [col.split('_binned')[0] for col in list_cols_model]
		# get the ids
		list_cols_id = ['uniqueid__app', 'bigaccountid__app', 'bitdebtor__app']
		# create list
		list_cols = list_cols_id + list_cols_model_raw + list_cols_model
		# get df
		df = self.df.copy()
		# get number of rows
		int_nrows = df.shape[0]
		# subset
		df = df[list_cols].copy()
		# make df large
		df_lg = df.iloc[np.tile(np.arange(int_nrows), self.int_len_list)].copy()
		# save to self
		self.int_nrows = int_nrows
		self.df_lg = df_lg.copy()
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
	# assign LTV
	def assign_ltv(self):
		list_flt_ltv = [int_val for int_val in self.list_flt_ltv for _ in range(self.int_nrows)]
		# save to object
		self.list_flt_ltv = list_flt_ltv
		# assign
		self.df_lg['ENG-loan_to_value'] = list_flt_ltv
		# return
		return self
	# get predictions
	def get_predictions(self):
		# bin LTV
		dict_bins = self.cls_model_preprocessing.dict_bins
		cls_binner = dict_bins['ENG-loan_to_value']
		self.df_lg['ENG-loan_to_value_binned'] = cls_binner.transform(self.df_lg['ENG-loan_to_value'])
		# get predictions
		cls_model_inference = self.cls_model_inference
		list_cols_model = list(cls_model_inference.feature_names_in_)
		self.df_lg['yhat'] = cls_model_inference.predict_proba(self.df_lg[list_cols_model])[:,1]
		# return
		return self
	# group so we can get ECNL
	def group_by_sample(self):
		# group by the sample
		df_tmp = self.df_lg.groupby(by='sample', as_index=False).agg({
			'ENG-loan_to_value': 'mean',
			'yhat': 'mean',
		})
		# get max LTV by ecnl
		df_tmp = df_tmp.loc[df_tmp.groupby('yhat')['ENG-loan_to_value'].idxmax()].copy()
		# sort
		df_tmp.sort_values(by='ENG-loan_to_value', ascending=False, inplace=True)
		# save to self
		self.df_tmp = df_tmp.copy()
		# return
		return self
	# get ecnl
	def get_ecnl(self):
		# interpolate
		self.df_tmp['ecnl'] = list(np.interp(
			x=list(self.df_tmp['yhat']),
			xp=self.arr_quantiles_model,
			fp=self.arr_score_quantiles_pricing,
		))
		# return
		return self
	# concat dfs
	def create_offer_column(self):
		# create offer column
		self.df_tmp['Offer'] = list(range(0, self.df_tmp.shape[0]))
		# sort
		self.df_tmp.sort_values(by='ENG-loan_to_value', ascending=False, inplace=True)
		# solve for amt financed
		self.df_tmp['book_value'] = self.dict_tmp_raw['flt_book_value']
		self.df_tmp['amt_financed'] = self.df_tmp['ENG-loan_to_value'] * self.dict_tmp_raw['flt_book_value']
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
		flt_ecnl_initial = self.df[self.df['Offer'] == 0]['ecnl'].iloc[0]
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

		# subset to approved offers
		df_tmp_2 = df_tmp[df_tmp['ecnl'] <= self.flt_threshold_ecnl_counter].copy()
		# rm negative fees
		df_tmp_2 = df_tmp_2[df_tmp_2['net_discount'] >= 0].copy()

		# get n offers
		int_n_offers = df_tmp_2.shape[0]
		print(f'There are {int_n_offers} offers')

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
		# get the object
		return self
	# method for approval to approval
	def get_offers_approval_to_approval(self):
		print(f'Initial offer Approved: {self.flt_ecnl_initial:0.4f}')

		# get original values
		df_tmp = self.df[self.df['Offer'] == 0].copy()
		# make dictionary
		dict_original_values = {
			'LTV': df_tmp['ENG-loan_to_value'].iloc[0],
			'APR': df_tmp['apr'].iloc[0],
			'Fees': df_tmp['net_discount'].iloc[0],
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
		df_tmp = df_tmp[df_tmp['ENG-loan_to_value'] < flt_ltv_min].copy()

		# get diff - APR
		df_tmp['APR_diff'] = flt_apr_original - df_tmp['apr']

		# convert to dollars
		df_tmp['APR_diff_dollars'] = (df_tmp['APR_diff'] / 0.1) * 50 # 0.1 APR == $50

		# get diff - Fees
		df_tmp['Fees_diff_dollars'] = flt_fees - df_tmp['net_discount']

		# sum
		df_tmp['diff_dollars_sum'] = df_tmp['APR_diff_dollars'] + df_tmp['Fees_diff_dollars']

		# save to object
		self.df_all_offers = df_tmp.copy()

		# get the first offer value
		int_offer_tmp = df_tmp['Offer'].min()

		# subset to that offer
		df_tmp = df_tmp[df_tmp['Offer'] == int_offer_tmp].copy()

		# subset on counters threshold
		df_tmp_2 = df_tmp[df_tmp['ecnl'] <= self.flt_threshold_ecnl_counter].copy()
		# subset on threshold - amt
		df_tmp_2 = df_tmp_2[df_tmp_2['diff_dollars_sum'] >= int_threshold].copy()
		# rm anything with negative fees
		df_tmp_2 = df_tmp_2[df_tmp_2['net_discount'] >= 0].copy()

		# get number of rows
		int_nrows = df_tmp_2.shape[0]
		print(f'There are {int_nrows} counters')

		# logic
		if int_nrows > 0: # if we have counters
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
	def subset_columns(self):
		# subset
		list_cols = [
			'Offer',
			'ecnl',
			'apr',
			'net_discount',
			'ENG-loan_to_value',
		]
		self.df = self.df[list_cols].copy()
		# return object
		return self
	# tag approve or decline
	def tag_approve_decline(self):
		# tag based on threshold from tiers
		self.df['Decision'] = self.df['ecnl'].apply(
			lambda x: 'Declined' if x > self.flt_threshold_ecnl else 'Approved',
		)
		# return
		return self
	# get max ltv and reorder columns
	def get_max_ltv_and_reorder(self):
		# subset to approvals
		df_tmp = self.df[self.df['Decision'] == 'Approved'].copy()
		# get maximum LTV
		flt_max_ltv = df_tmp['ENG-loan_to_value'].max()
		# assign
		self.df['ltv_max'] = flt_max_ltv

		# reorder
		list_cols = [
			'Offer',
			'ecnl',
			'Decision',
			'apr',
			'net_discount',
			'ENG-loan_to_value',
			'ltv_max',
		]
		self.df = self.df[list_cols].copy()
		# rename
		dict_rename = {
			'ecnl': 'ECNL',
			'apr': 'APR',
			'net_discount': 'NetDiscount',
			'ENG-loan_to_value': 'CurrentLTV',
			'ltv_max': 'MaxLTV',
		}
		self.df.rename(columns=dict_rename, inplace=True)
		# return object
		return self