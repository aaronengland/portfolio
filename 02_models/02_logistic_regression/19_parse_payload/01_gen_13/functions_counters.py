import pandas as pd 
import numpy as np
from functions_pricing import get_tier

# for LGD
def map_ltv_range_to_lgd_bin(flt_ltv, dict_bins_ltv):
	for flt_threshold, flt_val in dict_bins_ltv.items():
		if flt_ltv <= flt_threshold:
			return flt_val
	# else
	return np.max(list(dict_bins_ltv.values()))

# counters
class CounterOffers:
	# initialize
	def __init__(self, flt_ltv_original, int_n_offers, df_clean, cls_parser, flt_threshold_counters, dict_tiers):
		self.flt_ltv_original = flt_ltv_original
		self.int_n_offers = int_n_offers
		self.df_clean = df_clean
		self.cls_parser = cls_parser
		self.flt_threshold_counters = flt_threshold_counters
		self.dict_tiers = dict_tiers
	# get the new list of LTV
	def get_vals_ltv(self):
		list_flt_ltv = list(np.linspace(
			0.01,
			self.flt_ltv_original,
			self.int_n_offers,
		))
		# round to 2 decimal places
		#list_flt_ltv = [round(flt_ltv, 2) for flt_ltv in list_flt_ltv]
		# rm dups
		#list_flt_ltv = list(dict.fromkeys(list_flt_ltv))
		# get len of list
		int_len_of_list = len(list_flt_ltv)
		# save to object
		self.list_flt_ltv = list_flt_ltv
		self.int_len_of_list = int_len_of_list
		# return
		return self
	# expand the clean data set
	def expand_clean_data(self):
		# make copy
		df = self.df_clean.copy()
		# get nrows
		int_nrows = df.shape[0]
		# expand
		df_lg = df.iloc[np.tile(np.arange(int_nrows), self.int_len_of_list)].copy()
		# create offer
		list_int_offer = list(np.repeat(list(range(0, self.int_len_of_list)), int_nrows))
		df_lg['Offer'] = list_int_offer
		# assign LTV
		list_flt_ltv = [flt_val for flt_val in self.list_flt_ltv for _ in range(int_nrows)]
		df_lg['ENG-loan_to_value'] = list_flt_ltv
		# save to object
		self.df_lg = df_lg.copy()
		# return
		return self
	# bin and predict
	def bin_and_predict(self):
		# make copy
		df = self.df_lg.copy()
		# recalc amt financed (for pricing)
		df['amtfinanced__app'] = df['ENG-loan_to_value'] * df['bookvalue__app']
		# subset
		#df = df[df['ENG-loan_to_value'] < self.flt_ltv_original].copy()
		# bin ltv
		cls_binner = self.cls_parser.cls_model_preprocessing.dict_bins['ENG-loan_to_value']
		df['ENG-loan_to_value_binned'] = cls_binner.transform(df['ENG-loan_to_value'])
		# predict PD
		cls_model_inference = self.cls_parser.cls_model_inference
		flt_intercept = cls_model_inference.intercept_[0]
		list_cols_model = list(cls_model_inference.feature_names_in_)
		list_coef = list(cls_model_inference.coef_[0])
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
		# get pd
		df['PD'] = np.exp(df['log_odds']) / (1 + np.exp(df['log_odds']))
		#df['PD'] = cls_model_inference.predict_proba(df[list_cols_model])[:,1]
		# get lgd
		dict_bins_ltv = self.cls_parser.dict_bins_ltv
		df['LGD'] = df['ENG-loan_to_value'].apply(
			lambda x: map_ltv_range_to_lgd_bin(
				flt_ltv=x,
				dict_bins_ltv=dict_bins_ltv,
			)
		)
		# group
		df = df.groupby(by='Offer', as_index=False).agg({
			'ENG-loan_to_value': 'mean',
			'PD': 'mean',
			'LGD': 'mean',
			'amtfinanced__app': 'mean',
		})
		# sort
		df.sort_values(by='Offer', ascending=False, inplace=True)
		# make new offer col
		df['Offer'] = list(range(0, df.shape[0]))
		# get ecnl
		df['ecnl_24'] = df['PD'] * df['LGD'] 
		# get ecnl mod
		df['ecnl'] = df['ecnl_24'] * 2.36
		# get tier
		df['Tier'] = df['ecnl'].apply(
			lambda x: get_tier(
				flt_ecnl=x,
				dict_tiers=self.dict_tiers,
			)
		)
		# rm declines
		#df = df[df['ecnl'] <= self.flt_threshold_counters].copy()
		# subset
		list_cols = [
			'Offer',
			'PD',
			'ENG-loan_to_value',
			'LGD',
			'ecnl_24',
			'ecnl',
			'Tier',
			'amtfinanced__app',
		]
		df = df[list_cols].copy()
		# save to object
		self.df = df.copy()
		# return
		return df