from tqdm import tqdm
import pandas as pd
import numpy as np

# silence warnings
import warnings
warnings.filterwarnings('ignore')

# helper
def get_nansum(list_vals):
	# if it is a list
	if isinstance(list_vals, list):
		flt_sum = np.nansum(list_vals)
	else:
		flt_sum = np.nan
	return flt_sum

class Preprocessing: 
	# initialize
	def __init__(self, dict_impute, dict_bins, flt_quantile=0.95, int_new_payment=600):
		self.dict_impute = dict_impute
		self.flt_quantile = flt_quantile
		self.dict_bins = dict_bins
		self.int_new_payment = int_new_payment
	# fit
	def fit(self, X):
		# get the 95% confidence interval
		print(f'Getting max income based on {self.flt_quantile} quantile...')
		ser_income = 1 * round(pd.to_numeric(X['fltgrossmonthly__income_sum']) / 1)
		flt_income_max = ser_income.quantile(self.flt_quantile)
		print(f'Max Income: {flt_income_max}')

		# save to object
		self.flt_income_max = flt_income_max
		# return
		return self
	def transform(self, X):
		# mask negatives
		print('Masking negative values to NaN...')
		list_cols_numeric = [col for col in X.columns if X[col].dtype in ['float64','int64']]
		list_cols_neg = [col for col in list_cols_numeric if np.min(X[col]) < 0]
		list_cols_tu = [col for col in list_cols_neg if '__tu' in col]
		list_cols_ln = [col for col in list_cols_neg if '__ln' in col]
		# combine
		list_cols = list_cols_tu + list_cols_ln
		# mask
		for col in tqdm(list_cols):
			try:
				X[col] = X[col].mask(X[col] < 0, np.nan)
			except TypeError:
				pass
			except ValueError:
				pass

		# cap income
		print('Capping income...')
		X['fltgrossmonthly__income_sum'] = X['fltgrossmonthly__income_sum'].clip(upper=self.flt_income_max)
		X['fltgrossmonthly__income_sum'] = X['fltgrossmonthly__income_sum'].replace([np.inf], np.nan)

		# replace zeros
		print('Replacing zeros...')
		dict_value_replace = {
			'amtfinanced__app': {0: np.nan},
			'bookvalue__app': {0: np.nan},
			'miles_odometer__app': {0: np.nan},
		}
		for key, val in tqdm(dict_value_replace.items()):
			X[key] = X[key].replace(0, val[0])

		# engineer int n months
		print('Engineering number of months...')
		X['ENG-int_n_months'] = X['int_n_months_open__tu_pmthx'].fillna(X['int_n_months_closed__tu_pmthx'])

		# engineer int n months total
		print('Engineering number of months total...')
		X['ENG-int_n_months_total'] = X[['int_n_months_open__tu_pmthx', 'int_n_months_closed__tu_pmthx']].sum(
			skipna=True,
			axis=1,
		)

		# engineer flt wtd avg
		print('Engineering weighted average...')
		X['ENG-wtd_avg'] = X['flt_wtd_avg_open__tu_pmthx'].fillna(X['flt_wtd_avg_closed__tu_pmthx'])

		# engineer tag for having an auto
		print('Engineering tag for has auto...')
		X['ENG-has_auto'] = X['ENG-wtd_avg'].apply(
			lambda x: 1 if pd.notnull(x) else 0,
		)

		# engineer tag if it has an open auto
		print('Engineering tag for open auto indicator...')
		X['ENG-open_auto'] = X['flt_wtd_avg_open__tu_pmthx'].apply(
			lambda x: 1 if pd.notnull(x) else 0,
		)

		# engineer tag if it has a closed auto
		print('Engineering tag for closed auto indicator...')
		X['ENG-closed_auto'] = X['flt_wtd_avg_closed__tu_pmthx'].apply(
			lambda x: 1 if pd.notnull(x) else 0,
		)

		# engineer tag if it has open and closed auto
		print('Engineering tag for open and closed auto indicator...')
		X['ENG-open_and_closed_auto'] = X.apply(
			lambda x: 1 if (x['ENG-open_auto'] == 1 and x['ENG-closed_auto'] == 1) else 0,
			axis=1,
		)

		# engineer 3 mo early delinquency
		print('Engineering 3 month early delinquency...')
		X['ENG-3mo_bad'] = X['int_bad_3mo_open__tu_pmthx'].fillna(X['int_bad_3mo_closed__tu_pmthx'])

		# engineer 6 mo early delinquency
		print('Engineering 6 month early delinquency...')
		X['ENG-6mo_bad'] = X['int_bad_6mo_open__tu_pmthx'].fillna(X['int_bad_6mo_closed__tu_pmthx'])

		# engineer 3 mo recent delinquency
		print('Engineering 3 month recent delinquency...')
		X['ENG-3mo_bad_end'] = X['int_bad_3mo_open_end__tu_pmthx'].fillna(X['int_bad_3mo_closed_end__tu_pmthx'])

		# engineer 6 mo recent delinquency
		print('Engineering 6 month recent delinquency...')
		X['ENG-6mo_bad_end'] = X['int_bad_6mo_open_end__tu_pmthx'].fillna(X['int_bad_6mo_closed_end__tu_pmthx'])

		# get the dti
		print('Engineering DTI...')
		try:
			X['ENG-debt'] = X['totaldebt__app'] + self.int_new_payment
		except KeyError:
			X['ENG-debt'] = 100000 + self.int_new_payment
			print('totaldebt__app not in data')
		X['ENG-dti'] = X['ENG-debt'] / X['fltgrossmonthly__income_sum']
		X['ENG-dti'] = X['ENG-dti'].replace([np.inf], np.nan)

		# engineer franchise
		print('Engineering franchise...')
		X['ENG-franchise'] = X['strdealershiptrackertype__app'].apply(
			lambda x: 1 if x != 'Independent' else 0,
		)

		# engineer has a codebtor
		print('Engineering has a codebtor...')
		# logic
		if 'bitdebtor' not in list(X.columns):
			X['bitdebtor'] = X['bitdebtor__app']
		else:
			pass
		# logic
		if 'accountid' not in list(X.columns):
			X['accountid'] = X['bigaccountid__app']
		else:
			pass
		list_accountid = list(X[X['bitdebtor'] == 0]['accountid'])
		X['ENG-has_codebtor'] = X['accountid'].apply(
			lambda x: 1 if x in list_accountid else 0,
		)

		# engineer vehicle age
		print('Engineering vehicle age...')
		X['applicationdate__app'] = pd.to_datetime(X['applicationdate__app'])
		X['ENG-vehicle_age'] = X['applicationdate__app'].dt.year - X['vehicleyear__app']
		X['ENG-vehicle_age'] = X['ENG-vehicle_age'].replace([np.inf], np.nan)

		# engineer pti
		print('Engineering PTI...')
		X['ENG-payment_to_income'] = X['flt_payment_open__tu_pmthx'] / X['fltgrossmonthly__income_sum']
		X['ENG-payment_to_income'] = X['ENG-payment_to_income'].replace([np.inf], np.nan)

		# engineer ltv
		print('Engineering LTV...')
		X['ENG-loan_to_value'] = X['amtfinanced__app'] / X['bookvalue__app']
		X['ENG-loan_to_value'] = X['ENG-loan_to_value'].replace([np.inf], np.nan)

		# engineer BK
		print('Engineering BK...')
		X['ENG-bk'] = X['intopenbktype__app'].apply(
			lambda x: 1 if pd.notnull(x) else 0,
		)

		# engineer perfect payment hx
		print('Engineering perfect payment history tag for most recent auto...')
		X['ENG-perfect_payment_hx'] = X['ENG-wtd_avg'].apply(
			lambda x: 1 if x == 1 else 0,
		)

		# engineer perfect payment hx - open
		print('Engineering perfect payment history tag for open auto...')
		X['ENG-perfect_payment_hx_open'] = X['flt_avg_open__tu_pmthx'].apply(
			lambda x: 1 if x == 1 else 0,
		)

		# engineer perfect payment hx - closed
		print('Engineering perfect payment history tag for closed auto...')
		X['ENG-perfect_payment_hx_closed'] = X['flt_avg_closed__tu_pmthx'].apply(
			lambda x: 1 if x == 1 else 0,
		)

		# interactions
		print('Engineering interactions...')
		X['ENG-bk_x_wtd_avg'] = X['ENG-bk'] * X['ENG-wtd_avg']
		
		# impute
		print('Imputing values...')
		for key, val in tqdm(self.dict_impute.items()):
			try:
				X[key] = X[key].fillna(val)
			except KeyError:
				pass

		# bin
		print('Binning values for scorecard...')
		for key, val in tqdm(self.dict_bins.items()):
			try:
				X[f'{key}_binned'] = val.transform(X[key])
			except:
				pass

		# return
		return X