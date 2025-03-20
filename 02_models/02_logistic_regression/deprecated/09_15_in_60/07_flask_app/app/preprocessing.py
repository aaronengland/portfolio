from tqdm import tqdm
import pandas as pd
import numpy as np

# silence warnings
import warnings
warnings.filterwarnings('ignore')

class Preprocessing: 
	# initialize
	def __init__(self, dict_impute, dict_bins, flt_quantile=0.95):
		self.dict_impute = dict_impute
		self.flt_quantile = flt_quantile
		self.dict_bins = dict_bins
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
		list_cols = [
			're01s__tu', # top feature in PD
			'g990s__tu', # highest shap in PD
			'g106s__tu', # in all 4 scorecards
			'addrinputtimenewest__ln', # Time on file (in months) since the subject was most recently reported at the input address
			'linka029__tu', # checking account inquiries
			'au25s__tu', # pmt hx
			'au27s__tu', # pmt hx
			'g980s__tu',
			'bkc321__tu',
			'balmag01__tu',
			'at28b__tu',
			'addrlastmovetaxratiodiff__ln',
			'at35a__tu',
			'g232s__tu', # top feature when using all features
			'g306s__tu',
			'au21s__tu',
			'addrinputproblems__ln',
			'linka006__tu',
			'inquiryshortterm12month__ln',
			'g234s__tu',
			'cv15__tu',
			'at21s__tu',
			'inquirybanking12month__ln',
			'g242s__tu',
			'paymnt11__tu',
			'inquirytelcom12month__ln',
			's073b__tu',
			's064b__tu',
			'linka017__tu',
			'g213a__tu',
			'derogseverityindex__ln',
		]
		for col in tqdm(list_cols):
			X[col] = X[col].mask(X[col] < 0, np.nan)

		# replace zeros
		print('Replacing zeros...')
		dict_value_replace = {
			'amtfinanced__app': {0: 45000},
			'bookvalue__app': {0: 28125},    
		}
		for key, val in tqdm(dict_value_replace.items()):
			X[key] = X[key].replace(0, val[0])

		# round values
		print('Rounding values...')
		dict_round = {
			'amtfinanced__app': 1,
			'bookvalue__app': 1,
			'fltgrossmonthly__income_sum': 1,
		}
		for key, val in tqdm(dict_round.items()):
			X[key] = val * round(pd.to_numeric(X[key]) / val)

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

		# cap income
		print('Capping income...')
		X['fltgrossmonthly__income_sum'] = X['fltgrossmonthly__income_sum'].clip(upper=self.flt_income_max)
		X['fltgrossmonthly__income_sum'] = X['fltgrossmonthly__income_sum'].replace([np.inf], np.nan)

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
		X['ENG-bk'] = X['ENG-bk'].replace([np.inf], np.nan)

		# impute
		print('Imputing values...')
		if 'dti__app' not in list(X.columns):
			X['dti__app'] = 6.717
		else:
			pass
		for key, val in tqdm(self.dict_impute.items()):
			X[key] = X[key].fillna(val)

		# bin
		print('Binning values...')
		for key, val in tqdm(self.dict_bins.items()):
			X[f'{key}_binned'] = val.transform(X[key])

		# return
		return X