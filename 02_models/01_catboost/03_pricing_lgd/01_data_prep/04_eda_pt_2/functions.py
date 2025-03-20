# functions
import pandas as pd
import numpy as np
import json
from pprint import pprint
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

# get df info
def get_df_info(df, str_datecol, str_dirname_output, str_filename='dict_df_info.json'):
	# nrows/ncols
	int_nrows, int_ncols = df.shape
	# total obs
	int_obs_total = int_nrows * int_ncols
	# tot na
	int_n_missing = np.sum(df.isnull().sum())
	# create dict
	dict_df_info = {
		'int_nrows': int_nrows,
		'int_ncols': int_ncols,
		'int_obs_total': int_obs_total,
		'date_min': str(np.min(df[str_datecol])),
		'date_max': str(np.max(df[str_datecol])),
		'flt_mean_target': np.mean(df['target']),
		'flt_propna': int_n_missing / int_obs_total,
	}
	# write to .json
	json.dump(dict_df_info, open(f'{str_dirname_output}/{str_filename}', 'w'))
	# show
	#pprint(dict_df_info)

# get descriptives for each column
def get_descriptives_by_column(df, str_dirname_output, str_filename='df_descriptives.csv'):
	# get descriptives
	list_dict_row = []
	for col in tqdm (df.columns):
		# save as series
		ser_col = df[col]
		# get proportion nan
		flt_prop_na = ser_col.isnull().mean()
		if flt_prop_na == 1.0:
			# create row
			dict_row = {
				'feature': col,
				'dtype': np.nan,
				'propna': flt_prop_na,
				'min': np.nan,
				'max': np.nan,
				'range': np.nan,
				'std': np.nan,
				'mean': np.nan,
				'median': np.nan,
				'mode': np.nan,
				'n_unique': 0,
				'prop_unique': 0,
				'prop_negative': np.nan,
				'prop_min': np.nan,
				'prop_max': np.nan,
				'prop_zero': np.nan,
			}
			# append
			list_dict_row.append(dict_row)
			# skip the rest of the iteration
			continue
		# get data type
		str_dtype = ser_col.dtype
		# if value
		if str_dtype in ['float64', 'int64']:
			val_min, val_max, val_mean, val_std, val_median = ser_col.min(), ser_col.max(), ser_col.mean(), ser_col.std(), ser_col.median()
			val_range = val_max - val_min
			val_mode, int_n_unique = ser_col.mode().iloc[0], ser_col.nunique()
			flt_prop_unique = int_n_unique / len(ser_col.dropna())
			flt_prop_negative = len(ser_col[ser_col<0]) / len(ser_col.dropna())
			flt_prop_min = len(ser_col[ser_col==val_min]) / len(ser_col.dropna())
			flt_prop_max = len(ser_col[ser_col==val_max]) / len(ser_col.dropna())
			flt_prop_zero = len(ser_col[ser_col==0]) / len(ser_col.dropna())
		# if object
		if str_dtype == 'O':
			val_min, val_max, val_std, val_mean, val_median = np.nan, np.nan, np.nan, np.nan, np.nan
			val_range = np.nan
			val_mode, int_n_unique = ser_col.mode().iloc[0], ser_col.nunique()
			flt_prop_unique = int_n_unique / len(ser_col.dropna())
			flt_prop_negative = np.nan 
			flt_prop_min = np.nan
			flt_prop_max = np.nan
			flt_prop_zero = np.nan
		# if dtm
		if str_dtype == 'datetime64[ns]':
			val_min, val_max, val_mean, val_std, val_median = ser_col.min(), ser_col.max(), ser_col.mean(), np.nan, np.nan
			val_range = val_max - val_min
			val_mode, int_n_unique = ser_col.mode().iloc[0], ser_col.nunique()
			flt_prop_unique = int_n_unique / len(ser_col.dropna())
			flt_prop_negative = np.nan 
			flt_prop_min = len(ser_col[ser_col==val_min]) / len(ser_col.dropna())
			flt_prop_max = len(ser_col[ser_col==val_max]) / len(ser_col.dropna())
			flt_prop_zero = np.nan
		# create row
		dict_row = {
			'feature': col,
			'dtype': str_dtype,
			'propna': flt_prop_na,
			'min': val_min,
			'max': val_max,
			'range': val_range,
			'std': val_std,
			'mean': val_mean,
			'median': val_median,
			'mode': val_mode,
			'n_unique': int_n_unique,
			'prop_unique': flt_prop_unique,
			'prop_negative': flt_prop_negative,
			'prop_min': flt_prop_min,
			'prop_max': flt_prop_max,
			'prop_zero': flt_prop_zero,
		}
		# append
		list_dict_row.append(dict_row)
	# make df
	df_descriptives = pd.DataFrame(list_dict_row)
	# order cols
	df_descriptives.columns = [
		'feature',
		'dtype',
		'propna',
		'min',
		'max',
		'range',
		'std',
		'mean',
		'median',
		'mode',
		'n_unique',
		'prop_unique',
		'prop_negative',
		'prop_min',
		'prop_max',
		'prop_zero',
	]
	df_descriptives.sort_values(by='propna', ascending=False, inplace=True)
	df_descriptives.to_csv(f'{str_dirname_output}/{str_filename}', index=False)
	# return
	return df_descriptives

# plot proportion NaN overall
def plot_proportion_nan(df, str_dirname_output, str_filename='plt_prop_nan.png'):
	# get int_n_missing
	int_n_missing = np.sum(df.isnull().sum())
	# get int_obs_total
	int_obs_total = df.shape[0] * df.shape[1]
	# create axis
	fig, ax = plt.subplots(figsize=(9,5))
	# title
	ax.set_title('Pie Chart of Missing Values')
	ax.pie(
		x=[int_n_missing, int_obs_total], 
		colors=['y', 'c'],
		explode=(0, 0.1),
		labels=['Missing', 'Non-Missing'], 
		autopct='%1.1f%%',
	)
	# save fig
	plt.savefig(f'{str_dirname_output}/{str_filename}', bbox_inches='tight')
	# close
	plt.close()

# plot data type frequency
def plot_data_type_frequency(df, str_dirname_output, str_filename='plt_dtype.png'):
	# get numeric
	list_cols_numeric = []
	for col in tqdm (df.columns):
		if df[col].dtype in ['int64', 'float64']:
			list_cols_numeric.append(col)
	# get non-numeric
	list_cols_non_numeric = [col for col in df.columns if col not in list_cols_numeric]
	# get number of columns
	int_ncols = df.shape[1]
	# % numeric
	flt_pct_numeric = (len(list_cols_numeric) / int_ncols) * 100
	# % non-numeric
	flt_pct_non_numeric = (len(list_cols_non_numeric) / int_ncols) * 100
	# create ax
	fig, ax = plt.subplots(figsize=(9,5))
	# title
	ax.set_title(f'{flt_pct_numeric:0.4}% Numeric, {flt_pct_non_numeric:0.4}% Non-Numeric (N = {int_ncols})')
	# y label
	ax.set_ylabel('Frequency')
	# bar plot
	ax.bar(['Numeric','Non-Numeric'], [len(list_cols_numeric), len(list_cols_non_numeric)])
	# save plot
	plt.savefig(f'{str_dirname_output}/{str_filename}', bbox_inches='tight')
	# close
	plt.close()

# plot target
def plot_target(ser_target, str_dirname_output, str_filename='plt_target.png'):
	# get min/max
	flt_min = ser_target.min()
	flt_max = ser_target.max()
	# show distribution
	fig, ax = plt.subplots(figsize=(9,5))
	ax.set_title(f'Distribution of Target (N = {len(ser_target)}; Min = {flt_min:0.2f}; Max = {flt_max:0.2f})')
	sns.distplot(list(ser_target), ax=ax)
	# save
	plt.savefig(f'{str_dirname_output}/{str_filename}', bbox_inches='tight')
	# show
	plt.show()

# df info summary table
def get_df_info_summary_table(dict_df_info_train, dict_df_info_valid, dict_df_info_test, str_dirname_output):
	# create df
	df_info_summary = pd.DataFrame({
		'Data Set': ['Train','Valid','Test'],
		'Rows': [dict_df_info_train['int_nrows'], dict_df_info_valid['int_nrows'], dict_df_info_test['int_nrows']],
		'Columns': [dict_df_info_train['int_ncols'], dict_df_info_valid['int_ncols'], dict_df_info_test['int_ncols']],
		'Total Obs.': [dict_df_info_train['int_obs_total'], dict_df_info_valid['int_obs_total'], dict_df_info_test['int_obs_total']],
		'Min. Date': [dict_df_info_train['date_min'], dict_df_info_valid['date_min'], dict_df_info_test['date_min']],
		'Max. Date': [dict_df_info_train['date_max'], dict_df_info_valid['date_max'], dict_df_info_test['date_max']],
		'Prop. NaN': [dict_df_info_train['flt_propna'], dict_df_info_valid['flt_propna'], dict_df_info_test['flt_propna']],
		'Target Mean': [dict_df_info_train['flt_mean_target'], dict_df_info_valid['flt_mean_target'], dict_df_info_test['flt_mean_target']],
	})
	# save
	df_info_summary.to_csv(f'{str_dirname_output}/df_info_summary.csv', index=False)
	# return df_info_summary
	return df_info_summary