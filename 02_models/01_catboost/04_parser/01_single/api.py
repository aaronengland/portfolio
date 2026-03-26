from functions import *
from functions_counters import *
from functions_counters_pricing import *
import time
from datetime import datetime

# define class
class ParsePayload:
	# init
	def __init__(self, 
		list_cols_raw,
		list_cols_all, 
		cls_model_preprocessing,
		cls_model_inference_ad, cls_model_inference_pd, cls_model_inference_lgd,
		dict_aa,
		str_tiers,
		dtm_effective_date1,
		dtm_effective_date2):
		self.list_cols_raw = list_cols_raw
		self.list_cols_all = list_cols_all
		self.cls_model_preprocessing = cls_model_preprocessing
		self.cls_model_inference_ad = cls_model_inference_ad
		self.cls_model_inference_pd = cls_model_inference_pd
		self.cls_model_inference_lgd = cls_model_inference_lgd
		self.dict_aa = dict_aa
		self.str_tiers = str_tiers
		self.dtm_effective_date1 = dtm_effective_date1
		self.dtm_effective_date2 = dtm_effective_date2
		self.dict_output = {'str_tiers': str_tiers}
	# get data
	def get_data(self, dict_json_request):
		# start time
		time_start = time.perf_counter()

		# get the rows
		list_dict_rows = dict_json_request['rows']

		# iterate through the rows
		list_X_concat = []
		for a, dict_row in enumerate(list_dict_rows):
			# get the tables
			list_dict_table = dict_row['sources']
			# iterate through the tables
			list_X = []
			for b, dict_table in enumerate(list_dict_table):
				# get the name
				str_name = dict_table['name']
				# get the values
				str_values = dict_table['values']
				# logic
				if str_name == 'Application':
					# get table
					X = get_application_table(str_values=str_values)
					# append
					list_X.append(X)
				elif str_name == 'Incomes':
					# get table
					X = get_income_table(str_values=str_values)
					# append
					list_X.append(X)
				elif str_name == 'Lexis Nexis Risk View 5':
					# get table
					X = get_lexis_nexis_table(str_values=str_values)
					# append
					list_X.append(X)            
				elif str_name == 'TUXML':
					# get table
					X = get_transunion_table(str_values=str_values)
					# get pmt hx
					X_2 = get_pmt_history(str_values=str_values)
					# concat horizontally
					X = pd.concat([X, X_2], axis=1)
					# append
					list_X.append(X)
				else:
					pass
			# concatenate horizontally
			X_concat = pd.concat(list_X, axis=1)
			# append
			list_X_concat.append(X_concat)
		# concatenate vertically
		X = pd.concat(list_X_concat)

		# make sure all raw values needed for preprocessing are in the data
		for col in self.list_cols_raw:
			if col not in list(X.columns):
				X[col] = np.nan

		# get the unique ID
		list_unique_id = list(X['uniqueid__app'])

		# get the applicationdate
		str_dtm_app_date = X['applicationdate__app'].iloc[0]
		dtm_app_date = datetime.strptime(str_dtm_app_date, '%m/%d/%Y %H:%M:%S')
		print(f'Application Date: {dtm_app_date}')

		# show effective dates
		print(f'Effective Date Policy: {self.dtm_effective_date1}')
		print(f'Effective Date Chime: {self.dtm_effective_date2}')

		# get boolean for policy
		if dtm_app_date < self.dtm_effective_date1:
			bool_apply_policy = False
		else:
			bool_apply_policy = True
		print(f'Apply Policy: {bool_apply_policy}')

		# get boolean for chime
		if dtm_app_date < self.dtm_effective_date2:
			bool_apply_chime = False
		else:
			bool_apply_chime = True
		print(f'Apply Chime: {bool_apply_chime}')

		# flt_sec
		flt_sec = time.perf_counter() - time_start
		# print
		print(f'{list_unique_id}: Get Data: {flt_sec:0.5f} sec.')

		# save to object
		self.dict_json_request = dict_json_request
		# save to dict_output
		self.dict_output['bool_apply_policy'] = bool_apply_policy
		self.dict_output['bool_apply_chime'] = bool_apply_chime
		self.dict_output['dtm_app_date'] = dtm_app_date
		self.dict_output['list_unique_id'] = list_unique_id
		self.dict_output['flt_sec_get_data'] = flt_sec
		self.dict_output['X_raw'] = X.copy()
		# return object
		return self
	# pmt hx
	def engineer_pmt_hx(self):
		print(f'{self.dict_output["list_unique_id"]}: Engineering payment history...')
		df = self.dict_output['X_raw'].copy()
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
			bool_has_chime = True
		else:
			bool_has_chime = False
		print(f'Chime: {bool_has_chime}')

		# save to object
		self.dict_output['bool_has_chime'] = bool_has_chime
		self.dict_output['X_raw'] = df.copy()
		# return
		return self
	# shared preprocessing
	def shared_preprocessing(self):
		# start time
		time_start = time.perf_counter()

		# make copy of X_raw
		X_raw_copy = self.dict_output['X_raw'].copy()

		# ensure applicationdate__app is datetime
		X_raw_copy['applicationdate__app'] = pd.to_datetime(X_raw_copy['applicationdate__app'])

		# list of id cols
		list_cols_id = [
			'uniqueid__app',
			'bigaccountid__app',
			'bigdebtorid__app',
			'flt_wtd_avg_open__tu_pmthx',
			'flt_wtd_avg_closed__tu_pmthx',
		]
		X_id = X_raw_copy[list_cols_id].copy()
		X_id['ENG-wtd_avg'] = X_id['flt_wtd_avg_open__tu_pmthx'].fillna(X_id['flt_wtd_avg_closed__tu_pmthx'])

		# if policy
		if self.dict_output['bool_apply_policy']:
			# fillna
			X_raw_copy['rp01s__tu'] = X_raw_copy['rp01s__tu'].fillna(999)
			X_raw_copy['g232s__tu'] = X_raw_copy['g232s__tu'].fillna(999)
		else:
			pass

		# transform
		X_clean = self.cls_model_preprocessing.transform(X=X_raw_copy[self.list_cols_raw]).copy()

		# concat
		X_clean = pd.concat([X_id, X_clean], axis=1)

		# ensure there is a field for every feature
		for col in self.list_cols_all:
			if col not in list(X_clean.columns):
				X_clean[col] = np.nan

		# flt_sec
		flt_sec = time.perf_counter() - time_start
		# print()
		print(f'{self.dict_output["list_unique_id"]}: Shared Preprocessing: {flt_sec:0.5f} sec.')

		# save to dict_output
		self.dict_output['flt_sec_preprocessing'] = flt_sec
		self.dict_output['X_clean'] = X_clean.copy()
		# return object
		return self
	# generate predictions
	def generate_predictions(self):
		# start time
		time_start = time.perf_counter()

		# make copy of X_clean
		df_tmp = self.dict_output['X_clean'].copy()

		# force bk type to be string float
		df_tmp['intopenbktype__app'] = df_tmp['intopenbktype__app'].astype(float).astype(str)

		# AD
		y_hat_ad = pd.Series(self.cls_model_inference_ad.predict_proba(df_tmp[self.cls_model_inference_ad.feature_names_])[:,1])
		# PD
		y_hat_pd = pd.Series(self.cls_model_inference_pd.predict_proba(df_tmp[self.cls_model_inference_pd.feature_names_])[:,1])
		# LGD
		y_hat_lgd = pd.Series(self.cls_model_inference_lgd.predict(df_tmp[self.cls_model_inference_lgd.feature_names_]))

		# Approved/Declined Score
		flt_ad = np.mean(y_hat_ad)
		# Pricing - PD Score
		flt_pd = np.mean(y_hat_pd)
		# Pricing - LGD -- model and constant
		flt_lgd = np.mean(y_hat_lgd)

		# Calculate ECNL
		flt_ecnl = flt_pd * flt_lgd

		# get modified ecnl
		flt_ecnl_mod = flt_ecnl * 2.36 # takes loss at 24 to loss at 72

		# flt_sec
		flt_sec = time.perf_counter() - time_start
		# print()
		print(f'{self.dict_output["list_unique_id"]}: Generate Predictions: {flt_sec:0.5f} sec.')

		# save to dict_output
		self.dict_output['flt_sec_predictions'] = flt_sec
		self.dict_output['y_hat_ad'] = y_hat_ad
		self.dict_output['mean_ad'] = flt_ad
		self.dict_output['y_hat_pd'] = y_hat_pd
		self.dict_output['mean_pd'] = flt_pd
		self.dict_output['y_hat_lgd'] = y_hat_lgd
		self.dict_output['mean_lgd'] = flt_lgd
		self.dict_output['ecnl'] = flt_ecnl
		self.dict_output['ecnl_mod'] = flt_ecnl_mod
		# return object
		return self
	# policy
	def apply_policies(self):
		# if applying policy
		if self.dict_output['bool_apply_policy']:
			# start time
			time_start = time.perf_counter()

			# get flt_ecnl_mod from dict_output
			flt_ecnl_mod = self.dict_output['ecnl_mod']
			flt_ecnl_mod_original = flt_ecnl_mod

			# get df
			df_tmp = self.dict_output['X_clean'].copy()

			# force bk type to be string float
			df_tmp['intopenbktype__app'] = df_tmp['intopenbktype__app'].astype(float).astype(str)

			# ltv
			flt_ltv = df_tmp['ENG-loan_to_value'].iloc[0]
			print(f'Current LTV: {flt_ltv}')
			# rp01s
			flt_max_rp01s = df_tmp['rp01s__tu'].max()
			print(f'Maximum rp01s__tu: {flt_max_rp01s}')
			# g232s
			flt_max_g232s = df_tmp['g232s__tu'].max()
			print(f'Maximum g232s__tu: {flt_max_g232s}')
			# get bk
			str_bk = df_tmp['intopenbktype__app'].iloc[0]
			if str_bk == 'nan':
				int_bk = 0
			else:
				int_bk = 1
			print(f'BK: {int_bk}')

			# if there is payment history
			if df_tmp['ENG-wtd_avg'].isnull().mean() != 1.0:
				int_bool_pmt_hx = 1
			else:
				int_bool_pmt_hx = 0
			print(f'Boolean has auto payment history: {int_bool_pmt_hx}')

			# get mean of wtd avg
			flt_wtd_avg_mean = df_tmp['ENG-wtd_avg'].mean()
			print(f'ENG-wtd_avg mean: {flt_wtd_avg_mean}')

			# policy declines

			# if there has been more than 1 repo for debtor or codebtor
			if flt_max_rp01s > 1:
				print('Too many repos')
				flt_ecnl_mod = 1.0
				int_policy_decline = 1
			# if there are too many inquiries
			elif flt_max_g232s > 31:
				print('Too many inquiries')
				flt_ecnl_mod = 1.0
				int_policy_decline = 1
			# if there is pmt hx and its bad and its a nonbk
			elif (int_bool_pmt_hx == 1) and (flt_wtd_avg_mean < 0.5) and (int_bk == 0):
				print('Bad payment history')
				flt_ecnl_mod = 1.0
				int_policy_decline = 1
			# else
			else:
				print('No policy decline')
				int_policy_decline = 0

			# policy approvals (these can override policy declines)

			# if its a bk with low ltv and the ecnl is greater than the middle of A1
			if (int_bk == 1) and (flt_ltv <= 0.6) and (flt_ecnl_mod_original > 0.04):
				print('Policy approval for BK')
				flt_ecnl_mod = 0.04
				int_policy_approval = 1
			# if its a non bk with low ltv and ecnl is greater than the middle of A1
			elif (int_bk == 0) and (flt_ltv <= 0.6) and (flt_ecnl_mod_original > 0.04):
				print('Policy approval for non-BK')
				flt_ecnl_mod = 0.04
				int_policy_approval = 1
			# else
			else:
				print('No policy approval')
				int_policy_approval = 0

			# flt_sec
			flt_sec = time.perf_counter() - time_start
			# print()
			print(f'{self.dict_output["list_unique_id"]}: Apply Policy: {flt_sec:0.5f} sec.')

			# save to dict_output
			self.dict_output['ecnl_mod'] = flt_ecnl_mod
			self.dict_output['int_policy_decline'] = int_policy_decline
			self.dict_output['int_policy_approval'] = int_policy_approval
		else:
			print('No policy applied')
		# return object
		return self
	# chime
	def apply_chime(self):
		# if applying chime
		if self.dict_output['bool_apply_chime']:
			# start time
			time_start = time.perf_counter()

			# get flt_ecnl_mod from dict_output
			flt_ecnl_mod = self.dict_output['ecnl_mod']

			# if has chime
			if self.dict_output['bool_has_chime']:
				# apply factor
				flt_ecnl_mod = 1.0
			else:
				pass

			# flt_sec
			flt_sec = time.perf_counter() - time_start
			# print()
			print(f'{self.dict_output["list_unique_id"]}: Apply Chime: {flt_sec:0.5f} sec.')

			# save to dict_output
			self.dict_output['ecnl_mod'] = flt_ecnl_mod
		else:
			print('No chime rules applied')
		
		# return object
		return self

	# adverse action
	def adverse_action(self):
		# start time
		time_start = time.perf_counter()

		# logic
		if self.dict_output['mean_ad'] > 1.0:
			cls_model_inference = self.cls_model_inference_ad
		else:
			cls_model_inference = self.cls_model_inference_pd

		# get adverse action
		df_shap_vals, list_list_reasons = get_adverse_action(
			X_clean=self.dict_output['X_clean'], 
			cls_model_inference=cls_model_inference, 
			dict_aa=self.dict_aa,
		)

		# flt_sec
		flt_sec = time.perf_counter() - time_start
		# print()
		print(f'{self.dict_output["list_unique_id"]}: Adverse Action: {flt_sec:0.5f} sec.')

		# save to dict_output
		self.dict_output['flt_sec_adverse_action'] = flt_sec
		self.dict_output['df_shap_vals'] = df_shap_vals
		self.dict_output['list_list_reasons'] = list_list_reasons
		# return object
		return self
	# counter offers
	def counter_offers(self):
		# start time
		time_start = time.perf_counter()

		# constants
		flt_max_ltv = 1.6
		int_cash_down_increments = 500
		flt_factor_24_to_72 = 2.36
		flt_pct_threshold = 0.10

		# init
		cls_counters_ml = CountersML(
			df=self.dict_output['X_raw'].copy(),
			cls_model_preprocessing=self.cls_model_preprocessing,
			cls_model_inference_pd=self.cls_model_inference_pd,
			cls_model_inference_lgd=self.cls_model_inference_lgd,
			flt_max_ltv=flt_max_ltv,
			int_cash_down_increments=int_cash_down_increments,
			flt_factor_24_to_72=flt_factor_24_to_72,
		)
		# run methods
		cls_counters_ml.get_important_raw_values()
		cls_counters_ml.preprocess_and_get_predictions()
		cls_counters_ml.get_important_clean_values()
		cls_counters_ml.get_vals_cash_down()
		cls_counters_ml.expand_clean_data()
		cls_counters_ml.create_sample_column()
		cls_counters_ml.assign_cash_down()
		cls_counters_ml.assign_book_value()
		cls_counters_ml.get_new_down_total()
		cls_counters_ml.get_new_amount_financed()
		cls_counters_ml.get_new_advance()
		cls_counters_ml.inflate_deflate_values()
		cls_counters_ml.bin_values()
		cls_counters_ml.get_new_ltv()
		cls_counters_ml.get_predictions()
		cls_counters_ml.group_by_sample()
		cls_counters_ml.get_ecnl() # referencing preprocessed vals...need to be converted to original

		# if applying policy
		if self.dict_output['bool_apply_policy']:
			print('Applying policy to counters')

			# get the data set
			df_tmp = cls_counters_ml.df_tmp.copy()

			# get ecnl
			flt_ecnl_mod = self.dict_output['ecnl_mod']

			# logic for policy declines that were not policy approvals
			if (self.dict_output['int_policy_decline'] == 1) and (self.dict_output['int_policy_approval'] == 0):
				df_tmp['ecnl_down'] = flt_ecnl_mod
				df_tmp['ecnl_amt'] = flt_ecnl_mod
			else:
				pass

			# logic for policy approvals
			if self.dict_output['int_policy_approval'] == 1:
				df_tmp['ecnl_down'] = df_tmp['ecnl_down'].apply(
					lambda x: flt_ecnl_mod if x > flt_ecnl_mod else x,
				)
				df_tmp['ecnl_amt'] = df_tmp['ecnl_amt'].apply(
					lambda x: flt_ecnl_mod if x > flt_ecnl_mod else x,
				)
			else:
				pass

			# reassign
			cls_counters_ml.df_tmp = df_tmp.copy()
		else:
			print('Not applying policy to counters')

		# if applying chime
		if self.dict_output['bool_apply_chime']:
			print('Applying chime to counter offers')

			# get the data set
			df_tmp = cls_counters_ml.df_tmp.copy()

			# logic for those with chime
			if self.dict_output['bool_has_chime']:
				df_tmp['ecnl_down'] = 1.0
				df_tmp['ecnl_amt'] = 1.0
			else:
				pass

			# reassign
			cls_counters_ml.df_tmp = df_tmp.copy()
		else:
			print('Not applying chime to counters')

		cls_counters_ml.get_original_app()
		cls_counters_ml.create_offer_column()
		cls_counters_ml.get_original_down_cash()
		cls_counters_ml.get_original_down_total()
		cls_counters_ml.get_original_amt_financed()
		cls_counters_ml.assign_original_book_value()
		cls_counters_ml.get_original_ltv()
		cls_counters_ml.get_sales_price()
		cls_counters_ml.assign_original_values()

		# get df_tmp
		df_tmp = cls_counters_ml.df_tmp.copy()

		# get bool bk
		bool_bk = cls_counters_ml.dict_tmp_raw['bool_bk']
		print(f'BK: {bool_bk}')

		# get vehicle class
		str_vehicle_class = cls_counters_ml.dict_tmp_raw['str_vehicle_class']
		print(f'Vehicle Class: {str_vehicle_class}')

		# get dealer type
		str_dealer_type = cls_counters_ml.dict_tmp_raw['str_dealer_type']
		print(f'Dealer Type: {str_dealer_type}')

		# get dealer state
		str_dealer_state = cls_counters_ml.dict_tmp_raw['str_dealer_state']
		print(f'Dealer State: {str_dealer_state}')
		
		# constants
		int_dollars_round_fees = 1
		flt_avg_life = 2.3
		flt_equity_intercept = 0.04
		flt_equity_slope = 0.80
		flt_securitization = 0.0595
		flt_late_fee_income = 0.0042
		flt_state_rate_cap = 1.0
		flt_cnl_scaler = 0.8039

		# get df_tmp
		df_tmp = cls_counters_ml.df_tmp.copy()

		# init pricing class
		cls_pricing = PricingCounters(
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
		cls_pricing.pricing_test_logic()
		cls_pricing.map_to_tier()
		cls_pricing.get_equity()
		cls_pricing.get_profit()
		cls_pricing.get_discount()
		cls_pricing.get_late_fee()
		cls_pricing.get_funding_cost()
		cls_pricing.get_adjusted_ecnl()
		cls_pricing.get_expected_losses()
		cls_pricing.get_buy_rate()
		cls_pricing.get_raw_apr()
		cls_pricing.get_raw_discount_adjustment()
		cls_pricing.get_raw_apr_adjustment()
		cls_pricing.get_rate_cap_handicap()
		cls_pricing.get_additional_discount_needed()
		cls_pricing.get_apr()
		cls_pricing.get_net_discount()

		# constants
		flt_prop_c = 0.5

		# get df_tmp
		df_tmp = cls_pricing.df.copy()

		# init get offers class
		cls_get_offers = GetOffers(
			df=df_tmp,
			str_tiers=self.str_tiers,
			flt_prop_c=flt_prop_c,
			flt_pct_threshold=flt_pct_threshold,
		)
		# run methods
		cls_get_offers.get_initial_approval()
		cls_get_offers.get_the_offers()
		cls_get_offers.subset_and_rename_columns()
		cls_get_offers.tag_approve_decline()
		cls_get_offers.get_max_ltv_and_reorder()

		# get df
		df_tmp = cls_get_offers.df.copy()

		# make copy
		X_lg_grouped = df_tmp.copy()
		print(X_lg_grouped)

		# get the original APR and Net Discount
		df_tmp = df_tmp[df_tmp['Offer'] == 0].copy()

		# get the original APR and Net Discount
		df_tmp = df_tmp[df_tmp['Offer'] == 0].copy()
		flt_apr = df_tmp['APR'].iloc[0]
		if str(flt_apr) == 'nan':
			flt_apr = 'NaN'
		print(flt_apr)
		flt_net_discount = df_tmp['NetDiscount'].iloc[0]
		if str(flt_net_discount) == 'nan':
			flt_net_discount = 'NaN'
		print(flt_net_discount)

		# time
		flt_sec = time.perf_counter() - time_start
		print(f'{self.dict_output["list_unique_id"]}: Counter Offers: {flt_sec:0.5f} sec.')

		# save to dict_output
		self.dict_output['flt_sec_counters'] = flt_sec
		self.dict_output['df_counter_offers'] = X_lg_grouped
		self.dict_output['flt_apr'] = flt_apr
		self.dict_output['flt_net_discount'] = flt_net_discount
		# return object
		return self
	# generate output
	def generate_output(self):
		# start time
		time_start = time.perf_counter()

		# get n debtors
		int_n_debtors = len(self.dict_output['list_unique_id'])
		print(int_n_debtors)
		# create df
		df_output = pd.DataFrame({
			'Row_id': self.dict_output['list_unique_id'],
			'Score_ad': self.dict_output['y_hat_ad'],
			'Score_pd': self.dict_output['y_hat_pd'],
			'Score_lgd': self.dict_output['y_hat_lgd'],
			'Score_ecnl': [self.dict_output['ecnl']] * int_n_debtors,
			'Score_ecnl_mod': [self.dict_output['ecnl_mod']] * int_n_debtors,
			'APR': [self.dict_output['flt_apr']] * int_n_debtors,
			'Net_discount': [self.dict_output['flt_net_discount']] * int_n_debtors,
			'Key_factors': self.dict_output['list_list_reasons'],
			'Outlier_score': [0.0] * int_n_debtors,
			'Dict_tiers': [self.str_tiers] * int_n_debtors,
		})
		print(df_output)

		# convert to json
		str_json_output = df_output.to_json(orient='records')
		print(str_json_output)

		# convert to list
		list_output = eval(str_json_output)

		# convert df_counter_offers to list of dictionaries
		try:
			list_dict_counters = self.dict_output['df_counter_offers'].to_dict('records')

			# create final output
			dict_output_final = {
				'Request_id': '',
				'Zaml_processing_id': '',
				'Response': [{
					'Model_name': 'gen-xii',
					'Model_version': 'v1',
					'Results': list_output,
					'Errors': [],
					'CounterOffers': list_dict_counters,
				}]
			}
		# if we did not run counter offer method in the API
		except KeyError:
			# create final output
			dict_output_final = {
				'Request_id': '',
				'Zaml_processing_id': '',
				'Response': [{
					'Model_name': 'gen-xii',
					'Model_version': 'v1',
					'Results': list_output,
					'Errors': [],
				}]
			}

		# flt_sec
		flt_sec = time.perf_counter() - time_start
		# print()
		print(f'{self.dict_output["list_unique_id"]}: Generate Output: {flt_sec:0.5f} sec.')

		# save to dict_output
		self.dict_output['flt_sec_generate_output'] = flt_sec
		self.dict_output['output_final'] = dict_output_final
		# return object
		return self