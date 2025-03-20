# exploratory data analysis
import pandas as pd
import math
from pandas.api.types import is_numeric_dtype
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import os

# define function for histogram
def MAKE_AND_SAVE_HISTOGRAM(list_data, str_filename='./output/plt_histogram.png', str_name='lgdtarget', tpl_figsize=(10,10), logger=None):
	# fig
	fig, ax = plt.subplots(figsize=tpl_figsize)
	# title
	ax.set_title(f'Distribution of {str_name}')
	# plot
	sns.histplot(list_data, ax=ax, kde=True)
	# fix overlap
	fig.tight_layout()
	# save
	fig.savefig(str_filename, bbox_inches='tight')
	# log
	if logger:
		logger.warning(f'Saved plot to {str_filename}')
	# return
	return fig

# define class to make plot comparisons
class ContinuousTargetComparison:
	# get y
	def get_y(self, ser_y, str_df_name='train'):
		if str_df_name == 'train':
			self.y_train = ser_y
		elif str_df_name == 'valid':
			self.y_valid = ser_y
		else:
			self.y_test = ser_y
	# make plot
	def make_and_save_plot(self, str_filename='./output/plt_targetcompare.png', tpl_figsize=(12,8)):
		# make ax
		fig, ax = plt.subplots(figsize=tpl_figsize)
		# title
		ax.set_title('Target Distributions')
		# train
		sns.distplot(self.y_train, ax=ax, kde=True, label='Train', color='r')
		# valid
		sns.distplot(self.y_valid, ax=ax, kde=True, label='Valid', color='g')
		# test
		sns.distplot(self.y_test, ax=ax, kde=True, label='Test', color='b')
		# legend
		plt.legend()
		# save
		plt.savefig(str_filename, bbox_inches='tight')
		# close plot
		plt.close()

# create common cols class
class CommonColumChecker:
	# get cols
	def get_cols(self, list_cols, str_df_name):
		# logic for saving lists
		if str_df_name == 'train':
			self.list_train = list_cols[:]
		elif str_df_name == 'valid':
			self.list_valid = list_cols[:]
		elif str_df_name == 'test':
			self.list_test = list_cols[:]
		else:
			raise Exception('str_df_name must be "train", "valid", or "test"')
		# return
		return self
	# create table
	def create_table(self):
		# train and train
		int_train_train = len(self.list_train)
		# train and valid
		int_train_valid = len([col for col in self.list_train if col in self.list_valid])
		# train and test
		int_train_test = len([col for col in self.list_train if col in self.list_test])
		
		# valid and train
		int_valid_train = len([col for col in self.list_valid if col in self.list_train])
		# valid and valid
		int_valid_valid = len(self.list_valid)
		# valid and test
		int_valid_test = len([col for col in self.list_valid if col in self.list_test])
		
		# test and train
		int_test_train = len([col for col in self.list_test if col in self.list_train])
		# test and valid
		int_test_valid = len([col for col in self.list_test if col in self.list_valid])
		# test and test
		int_test_test = len(self.list_valid)
		
		# make data frame
		self.df_table = pd.DataFrame({'df':['train','valid','test'],
						   		      'train':[int_train_train, int_train_valid, int_train_test],
						   			  'valid':[int_valid_train, int_valid_valid, int_valid_test],
						   			  'test':[int_test_train, int_test_valid, int_test_test]})
		# return
		return self
	# save table
	def save_table(self, str_filename='./output/df_common_cols.csv'):
		# write to csv
		self.df_table.to_csv(str_filename, index=False)

# create class
class PiePlotPropTrainValidTest:
	# get na info
	def get_na_info(self, df, str_df_name):
		# get total number missing
		n_missing = np.sum(df.isnull().sum())
		# get total observations
		n_observations = df.shape[0] * df.shape[1]
		# both into a list
		list_values = [n_missing, n_observations]
		# logic for organization
		if str_df_name == 'train':
			self.list_values_train = list_values
		elif str_df_name == 'valid':
			self.list_values_valid = list_values
		elif str_df_name == 'test':
			self.list_values_test = list_values
		else:
			raise Exception('Valid values for str_df_name include "train", "valid", "test"')
		# return object
		return self
	# make plot
	def make_plot(self, tpl_figsize=(20,10)):
		# create ax for suplots
		fig, ax = plt.subplots(ncols=3, figsize=tpl_figsize) # 3 = train, valid, test
		# create plot with loop
		for a, str_df in enumerate(['Train', 'Valid', 'Test']):
			# title
			ax[a].set_title(str_df)
			# plot
			if a == 0:
				# use train
				list_vals = self.list_values_train[:]
			elif a == 1:
				# use valid
				list_vals = self.list_values_valid[:]
			elif a == 2:
				# use test
				list_vals = self.list_values_test[:]
			# create plot
			ax[a].pie(x=list_vals, 
					  colors=['y', 'c'],
					  explode=(0, 0.1),
					  labels=['Missing', 'Non-Missing'], 
					  autopct='%1.1f%%')
		# fix overlap
		plt.tight_layout()
		# save fig to object
		self.fig = fig
		# return object
		return self
	# save plot
	def save_plot(self, str_filename='./output/plt_pie_na_compare.png'):
		# save fig
		plt.savefig(str_filename, bbox_inches='tight')

# pie chart of proportion NaN values
def PIE_PLOT_NA_OVERALL(df, str_filename='./output/plt_na_overall.png', tpl_figsize=(10,15), logger=None):
	# get total number missing
	n_missing = np.sum(df.isnull().sum())
	# get total observations
	n_observations = df.shape[0] * df.shape[1]
	# both into a list
	list_values = [n_missing, n_observations]
	# create axis
	fig, ax = plt.subplots(figsize=tpl_figsize)
	# title
	ax.set_title('Pie Chart of Missing Values')
	ax.pie(x=[n_missing, n_observations], 
	       colors=['y', 'c'],
	       explode=(0, 0.1),
	       labels=['Missing', 'Non-Missing'], 
	       autopct='%1.1f%%')
	# save fig
	plt.savefig(str_filename, bbox_inches='tight')
	# close plot
	plt.close()
	# logging
	if logger:
		logger.warning(f'Pie chart of NaN overall saved to {str_filename}')
	# return fig
	return fig

# plot binary frequency (i.e., target frequency using binary target)
def PLOT_BINARY_COMPARISON(ser_binary, str_filename='./output/target_freqplot.png', logger=None):
	# get value counts for each
	ser_val_counts = pd.value_counts(ser_binary)
	# get x
	x = ser_val_counts.index
	# get y
	y = ser_val_counts.values
	# get total
	int_total = len(ser_binary)
	# get pct negative class (i.e., when y == 0)
	flt_pct_negative = (y[0]/int_total)*100
	# get pct positive class (i.e., when y == 1)
	flt_pct_positive = (y[1]/int_total)*100
	# create axis
	fig, ax = plt.subplots(figsize=(15, 10))
	# title
	ax.set_title(f'{flt_pct_negative:0.4}% = 0, {flt_pct_positive:0.4}% = 1, (N = {int_total})')
	# frequency bar plot
	ax.bar(x, y)
	# ylabel
	ax.set_ylabel('Frequency')
	# xticks
	ax.set_xticks([0, 1])
	# xtick labels
	ax.set_xticklabels(['0','1'])
	# save
	plt.savefig(str_filename, bbox_inches='tight')
	# close plot
	plt.close()
	# log it
	if logger:
		logger.warning(f'Target frequency plot saved to {str_filename}')
	# return
	return fig

# define class to make plot comparisons
class BinaryTargetComparison:
	# get y
	def get_y(self, ser_y, str_df_name='train'):
		if str_df_name == 'train':
			self.y_train = ser_y
		elif str_df_name == 'valid':
			self.y_valid = ser_y
		else:
			self.y_test = ser_y
	# make plot
	def make_and_save_plot(self, str_filename='./output/plt_targetcompare.png', tpl_figsize=(12,8)):
		# iterate through y's and get vals into dict_
		dict_empty = {}
		for a, ser_y in enumerate([self.y_train, self.y_valid, self.y_test]):
			# get value counts for each
			y_val_counts = pd.value_counts(ser_y)
			# get x
			x = y_val_counts.index
			# logic
			if a == 0:
				dict_empty['train_x'] = x
			elif a == 1:
				dict_empty['valid_x'] = x
			else:
				dict_empty['test_x'] = x
			# get y
			y = y_val_counts.values
			# logic
			if a == 0:
				dict_empty['train_y'] = y
			elif a == 1:
				dict_empty['valid_y'] = y
			else:
				dict_empty['test_y'] = y
		# create axis
		fig, ax = plt.subplots(nrows=1, ncols=3, figsize=tpl_figsize)
		# main title
		#fig.suptitle('Target Frequencies', fontsize=14)
		counter=0
		for x, y in ([(dict_empty['train_x'], dict_empty['train_y']),
			          (dict_empty['valid_x'], dict_empty['valid_y']),
					  (dict_empty['test_x'], dict_empty['test_y'])]):
			if counter == 0:
				str_df_name = 'Train'
			elif counter == 1:
				str_df_name = 'Valid'
			else:
				str_df_name = 'Test'
			# title
			ax[counter].set_title(f'{str_df_name}')
			# frequency bar plot
			ax[counter].bar(x, y)
			# logic
			if counter == 0:
				# ylabel
				ax[counter].set_ylabel('Frequency')
			# xticks
			ax[counter].set_xticks([0, 1])
			# xtick labels
			ax[counter].set_xticklabels(['0','1'])
			# increase counter
			counter += 1
		# fix overlap
		plt.tight_layout()
		# save
		plt.savefig(str_filename, bbox_inches='tight')
		# close plot
		plt.close()

# define function to create dtype frequ plot
def PLOT_DTYPE(df, str_filename='./output/plt_dtype.png', tpl_figsize=(10,10), logger=None):
	# get frequency of numeric and non-numeric
	counter_numeric = 0
	counter_non_numeric = 0
	for col in df.columns:
		if is_numeric_dtype(df[col]):
			counter_numeric += 1
		else:
			counter_non_numeric += 1
	# number of cols
	int_n_cols = len(list(df.columns))
	# % numeric
	flt_pct_numeric = (counter_numeric / int_n_cols) * 100
	# % non-numeric
	flt_pct_non_numeric = (counter_non_numeric / int_n_cols) * 100
	# create ax
	fig, ax = plt.subplots(figsize=tpl_figsize)
	# title
	ax.set_title(f'{flt_pct_numeric:0.4}% Numeric, {flt_pct_non_numeric:0.4}% Non-Numeric (N = {int_n_cols})')
	# y label
	ax.set_ylabel('Frequency')
	# bar plot
	ax.bar(['Numeric','Non-Numeric'], [counter_numeric, counter_non_numeric])
	# save plot
	plt.savefig(str_filename, bbox_inches='tight')
	# close plot
	plt.close()
	# log
	if logger:
		logger.warning(f'Data type frequency plot saved to {str_filename}')
	# return
	return fig

# define function to log df info
def LOG_DF_INFO(df, str_dflogname='df_train', str_datecol='dtmStampCreation__app', str_bin_target='TARGET__app', 
	            logger=None, bool_low_memory=True):
	# get rows
	int_nrows = df.shape[0]
	# get columns
	int_ncols = df.shape[1]
	# logic
	if bool_low_memory:
		int_n_missing_all = 0
		# iterate through cols
		for a, col in enumerate(df.columns):
			# print message
			print(f'Checking NaN: {a+1}/{int_ncols}')
			# get number missing per col
			int_n_missing_col = df[col].isnull().sum()
			# add to int_n_missing_all
			int_n_missing_all += int_n_missing_col
		# get proportion NaN
		flt_prop_nan = int_n_missing_all/(int_nrows*int_ncols)
	else:
		# get proportion NaN
		flt_prop_nan = np.sum(df.isnull().sum())/(int_nrows*int_ncols)
	# get min str_datecol
	min_ = np.min(df[str_datecol])
	# get max dtmstampCreation__app
	max_ = np.max(df[str_datecol])
	# get deliquency rate
	flt_prop_delinquent = np.mean(df[str_bin_target])
	# if logging
	if logger:
		logger.warning(f'{str_dflogname}: {int_nrows} rows, {int_ncols} columns')
		logger.warning(f'{str_dflogname}: {flt_prop_nan:0.4} NaN')
		logger.warning(f'{str_dflogname}: Min {str_datecol} = {min_}')
		logger.warning(f'{str_dflogname}: Max {str_datecol} = {max_}')
		logger.warning(f'{str_dflogname}: Target Proportion = {flt_prop_delinquent:0.4}')

# define function to save proportion NaN by column
def SAVE_NAN_BY_COL(df, str_filename='./output/df_propna.csv', logger=None, bool_low_memory=True):
	# logic
	if bool_low_memory:
		# empty list
		list_empty = []
		# iterate through cols
		for a, col in enumerate(df.columns):
			# print message
			print(f'Checking NaN: {a+1}/{df.shape[1]}')
			# get prop missing
			flt_prop_nan = df[col].isnull().sum()/len(df[col])
			# create dict
			dict_ = {'column': col,
			         'prop_nan': flt_prop_nan}
			# append to list_empty
			list_empty.append(dict_)
		# make df
		df = pd.DataFrame(list_empty)
	else:
		# get proportion missing by col
		ser_propna = df.isnull().sum()/df.shape[0]
		# put into df
		df = pd.DataFrame({'column': ser_propna.index,
	                       'prop_nan': ser_propna})
	# sort
	df.sort_values(by='prop_nan', ascending=False, inplace=True)
	# save to csv
	df.to_csv(str_filename, index=False)
	# if using logger
	if logger:
		logger.warning(f'csv file of proportion NaN by column generated and saved to {str_filename}')

# define function to get training only
def CHRON_GET_TRAIN(df, flt_prop_train=0.5, logger=None):
	# get n_rows in df
	n_rows_df = df.shape[0]
	# get last row in df_train
	n_row_end_train = math.floor(n_rows_df * flt_prop_train)
	# get training data
	df = df.iloc[:n_row_end_train, :]
	# if using logger
	if logger:
		# log it
		logger.warning(f'Subset df to first {flt_prop_train} rows for training')
	# return
	return df

# define class to find/drop features with 100% NaN
class DropAllNaN(BaseEstimator, TransformerMixin):
	# initialize
	def __init__(self, list_cols, bool_low_memory=True):
		self.list_cols = list_cols
		self.bool_low_memory = bool_low_memory
	# fit
	def fit(self, X, y=None):
		# logic
		if self.bool_low_memory:
			# empty list
			list_cols_allnan = []
			# iterate through cols
			for a, col in enumerate(X[self.list_cols]):
				# print message
				print(f'Checking NaN: {a+1}/{len(self.list_cols)}')
				# get proportion nan
				flt_prop_nan = X[col].isnull().sum()/X.shape[0]
				# logic
				if flt_prop_nan == 1:
					# append to list
					list_cols_allnan.append(flt_prop_nan)
		else:
			# get proportion missing per column
			ser_propna = X[self.list_cols].isnull().sum()/X.shape[0]
			# subset to 1.0
			list_cols_allnan = list(ser_propna[ser_propna==1.0].index)
		# save into object
		self.list_cols_allnan = list_cols_allnan
		# return object
		return self
	# transform
	def transform(self, X):
		# make sure all cols in self.list_cols_allnan are in X
		list_cols = [col for col in self.list_cols_allnan if col in list(X.columns)]
		# drop features
		X.drop(list_cols, axis=1, inplace=True)
		# return
		return X

# define function to log df shape
def LOG_DF_SHAPE(df, logger=None):
	# get rows
	int_nrows = df.shape[0]
	# get columns
	int_ncols = df.shape[1]
	# if logging
	if logger:
		logger.warning(f'df: {int_nrows} rows, {int_ncols} columns')

# define DropNoVariance
class DropNoVariance(BaseEstimator, TransformerMixin):
	# initialize class
	def __init__(self, list_cols, bool_low_memory=True):
		self.list_cols = list_cols
		self.bool_low_memory = bool_low_memory
	# fit to X
	def fit(self, X, y=None):
		# if we have low memory
		if self.bool_low_memory:
			# instantiate empty list
			list_novar = []
			# iterate through cols
			for a, col in enumerate(self.list_cols):
				# print message
				print(f'Checking col {a+1}/{len(self.list_cols)}')
				# get number of unique
				n_unique = len(pd.value_counts(X[col]))
				# logic to identify no variance cols
				if n_unique == 1:
					list_novar.append(col)
		else:
			# define helper function
			def GET_NUNIQUE(ser_):
				n_unique = len(pd.value_counts(ser_))
				return n_unique
			# apply function to every column
			ser_nunique = X[self.list_cols].apply(lambda x: GET_NUNIQUE(ser_=x), axis=0)
			# get the cols with nunique == 1
			list_novar = list(ser_nunique[ser_nunique==1].index)
		# save to object
		self.list_novar = list_novar
		# return self
		return self
	# transform X
	def transform(self, X):
		# make sure all cols in self.list_novar are in X
		list_cols = [col for col in self.list_novar if col in list(X.columns)]
		# drop list_cols
		X.drop(list_cols, axis=1, inplace=True)
		# return
		return X

# define class
class DropRedundantFeatures(BaseEstimator, TransformerMixin):
	# initialize class
	def __init__(self, list_cols, int_n_rows_check=10000):
		self.list_cols = list_cols
		self.int_n_rows_check = int_n_rows_check
	# fit
	def fit(self, X, y=None):
		# instantiate empty list
		list_redundant_cols = []
		for a, cola in enumerate(self.list_cols):
			# status message
			print(f'Currently, there are {len(list_redundant_cols)} redundant columns.')
			# status message
			print(f'Checking column {a+1}/{len(self.list_cols)}')
			# logic
			if cola not in list_redundant_cols:
				# iterate through the other cols
				for colb in self.list_cols[a+1:]:
					# check if subset of cola == colb
					if X[cola].iloc[:self.int_n_rows_check].equals(X[colb].iloc[:self.int_n_rows_check]):
						# print message
						print(f'First {self.int_n_rows_check} rows in {colb} are redundant with {cola}')
						# check if the whole column is redundant
						if X[cola].equals(X[colb]):
							# print message
							print(f'After checking all rows, {colb} is redundant with {cola}')
							list_redundant_cols.append(colb)
						else:
							print(f'After checking all rows, {colb} is not redundant with {cola}')
		# save to object
		self.list_redundant_cols = list_redundant_cols
		# return
		return self
	# transform
	def transform(self, X):
		# make sure all cols in self.list_redundant_cols are in X
		list_cols = [col for col in self.list_redundant_cols if col in list(X.columns)]
		# drop list_cols
		X.drop(list_cols, axis=1, inplace=True)
		# return
		return X

# define class for automating distribution plot analysis
class DistributionAnalysis(BaseEstimator, TransformerMixin):
	# initialiaze
	def __init__(self, list_cols, int_nrows=10000, int_random_state=42, flt_thresh_upper=0.95, tpl_figsize=(10,10), 
		         str_dirname='./output/distplots'):
		self.list_cols = list_cols
		self.int_nrows = int_nrows
		self.int_random_state = int_random_state
		self.flt_thresh_upper = flt_thresh_upper
		self.tpl_figsize = tpl_figsize
		self.str_dirname = str_dirname
	# random sample
	def get_random_sample(self, X, str_df_name='train'):
		# logic
		if str_df_name == 'train':
			self.df_train_sub = X.sample(n=self.int_nrows, random_state=self.int_random_state)
		elif str_df_name == 'valid':
			self.df_valid_sub = X.sample(n=self.int_nrows, random_state=self.int_random_state)
		else:
			self.df_test_sub = X.sample(n=self.int_nrows, random_state=self.int_random_state)
	# compare each col
	def fit(self, X, y=None):
		# iterate through cols
		list_sig_diff = []
		for a, col in enumerate(self.list_cols):
			# print
			print(f'Currently {len(list_sig_diff)} columns with a significant difference')
			# print
			print(f'Evaluating col {a+1}/{len(self.list_cols)}')
			# create a df with just the cols
			df_col = pd.DataFrame({'train': list(self.df_train_sub[col]),
				                   'valid': list(self.df_valid_sub[col]),
				                   'test': list(self.df_test_sub[col])})
			# get number of rows per sample
			int_len_sample = int(self.int_nrows/100) # always doing 100 samples
			# create list to use for sample
			list_empty = []
			for b in range(100): # always doing 100 samples
				# create list containing value for b the same length as a samplel
				list_ = list(itertools.repeat(b, int_len_sample))
				# extend list_empty
				list_empty.extend(list_)
			# create a dictionary to use for grouping
			dict_ = dict(zip(list(df_col.columns), ['median' for col in list(df_col.columns)]))
			# make list_empty into a column in df_col
			df_col['sample'] = list_empty
			# group df_col by sample and get median for each of 100 samples
			df_col = df_col.groupby('sample', as_index=False).agg(dict_)
			# TRAIN VS. VALID
			# first test (train > valid)
			flt_avg = np.mean(df_col.apply(lambda x: 1 if x['train'] > x['valid'] else 0, axis=1))
			# logic for significance
			if (flt_avg >= self.flt_thresh_upper):
				# print
				print(f'Significant difference in {col} between train and valid ({flt_avg:0.4})')
				# append to list
				list_sig_diff.append(col)
				# make distribution plot
				fig, ax = plt.subplots(figsize=self.tpl_figsize)
				# title
				ax.set_title(f'{col} - Train > Test')
				# plot train
				sns.distplot(df_col['train'], kde=True, color="r", ax=ax, label='Train')
				# plot valid
				sns.distplot(df_col['valid'], kde=True, color="g", ax=ax, label='Valid')
				# plot test
				sns.distplot(df_col['test'], kde=True, color="b", ax=ax, label='Test')
				# legend
				plt.legend()
				# save plot
				plt.savefig(f'{self.str_dirname}/{col}.png', bbox_inches='tight')
				# close plot
				plt.close()
				# move to next col
				continue
			else:
				# second test (valid > train)
				flt_avg = np.mean(df_col.apply(lambda x: 1 if x['valid'] > x['train'] else 0, axis=1))
				# logic for significance
				if (flt_avg >= self.flt_thresh_upper):
					# print
					print(f'Significant difference in {col} between train and valid ({flt_avg:0.4})')
					# append to list
					list_sig_diff.append(col)
					# make distribution plot
					fig, ax = plt.subplots(figsize=self.tpl_figsize)
					# title
					ax.set_title(f'{col} Valid > Train')
					# plot train
					sns.distplot(df_col['train'], kde=True, color="r", ax=ax, label='Train')
					# plot valid
					sns.distplot(df_col['valid'], kde=True, color="g", ax=ax, label='Valid')
					# plot test
					sns.distplot(df_col['test'], kde=True, color="b", ax=ax, label='Test')
					# legend
					plt.legend()
					# save plot
					plt.savefig(f'{self.str_dirname}/{col}.png', bbox_inches='tight')
					# close plot
					plt.close()
					# move to next col
					continue
			# TRAIN VS. TEST
			# first test (train > test)
			flt_avg = np.mean(df_col.apply(lambda x: 1 if x['train'] > x['test'] else 0, axis=1))
			# logic for significance
			if (flt_avg >= self.flt_thresh_upper):
				# print
				print(f'Significant difference in {col} between train and test ({flt_avg:0.4})')
				# append to list
				list_sig_diff.append(col)
				# make distribution plot
				fig, ax = plt.subplots(figsize=self.tpl_figsize)
				# title
				ax.set_title(f'{col} - Train > Test')
				# plot train
				sns.distplot(df_col['train'], kde=True, color="r", ax=ax, label='Train')
				# plot valid
				sns.distplot(df_col['valid'], kde=True, color="g", ax=ax, label='Valid')
				# plot test
				sns.distplot(df_col['test'], kde=True, color="b", ax=ax, label='Test')
				# legend
				plt.legend()
				# save plot
				plt.savefig(f'{self.str_dirname}/{col}.png', bbox_inches='tight')
				# close plot
				plt.close()
				# move to next col
				continue
			else:
				# second test (test > train)
				flt_avg = np.mean(df_col.apply(lambda x: 1 if x['test'] > x['train'] else 0, axis=1))
				# logic for significance
				if (flt_avg >= self.flt_thresh_upper):
					# print
					print(f'Significant difference in {col} between train and test ({flt_avg:0.4})')
					# append to list
					list_sig_diff.append(col)
					# make distribution plot
					fig, ax = plt.subplots(figsize=self.tpl_figsize)
					# title
					ax.set_title(f'{col} - Test > Train')
					# plot train
					sns.distplot(df_col['train'], kde=True, color="r", ax=ax, label='Train')
					# plot valid
					sns.distplot(df_col['valid'], kde=True, color="g", ax=ax, label='Valid')
					# plot test
					sns.distplot(df_col['test'], kde=True, color="b", ax=ax, label='Test')
					# legend
					plt.legend()
					# save plot
					plt.savefig(f'{self.str_dirname}/{col}.png', bbox_inches='tight')
					# close plot
					plt.close()
					# move to next col
					continue
			# VALID VS. TEST
			# first test (valid > test)
			flt_avg = np.mean(df_col.apply(lambda x: 1 if x['valid'] > x['test'] else 0, axis=1))
			# logic for significance
			if (flt_avg >= self.flt_thresh_upper):
				# print
				print(f'Significant difference in {col} between valid and test ({flt_avg:0.4})')
				# append to list
				list_sig_diff.append(col)
				# make distribution plot
				fig, ax = plt.subplots(figsize=self.tpl_figsize)
				# title
				ax.set_title(f'{col} - Valid > Test')
				# plot train
				sns.distplot(df_col['train'], kde=True, color="r", ax=ax, label='Train')
				# plot valid
				sns.distplot(df_col['valid'], kde=True, color="g", ax=ax, label='Valid')
				# plot test
				sns.distplot(df_col['test'], kde=True, color="b", ax=ax, label='Test')
				# legend
				plt.legend()
				# save plot
				plt.savefig(f'{self.str_dirname}/{col}.png', bbox_inches='tight')
				# close plot
				plt.close()
			else:
				# second test (test > valid)
				flt_avg = np.mean(df_col.apply(lambda x: 1 if x['test'] > x['valid'] else 0, axis=1))
				# logic for significance
				if (flt_avg >= self.flt_thresh_upper):
					# print
					print(f'Significant difference in {col} between test and valid ({flt_avg:0.4})')
					# append to list
					list_sig_diff.append(col)
					# make distribution plot
					fig, ax = plt.subplots(figsize=self.tpl_figsize)
					# title
					ax.set_title(f'{col} - Test > Valid')
					# plot train
					sns.distplot(df_col['train'], kde=True, color="r", ax=ax, label='Train')
					# plot valid
					sns.distplot(df_col['valid'], kde=True, color="g", ax=ax, label='Valid')
					# plot test
					sns.distplot(df_col['test'], kde=True, color="b", ax=ax, label='Test')
					# legend
					plt.legend()
					# save plot
					plt.savefig(f'{self.str_dirname}/{col}.png', bbox_inches='tight')
					# close plot
					plt.close()	
		# save to object
		self.list_sig_diff = list_sig_diff
		# delete the objects we don't want
		del self.df_train_sub, self.df_valid_sub, self.df_test_sub, df_col
		# return self
		return self
	# drop columns
	def transform(self, X):
		# make sure all cols in self.list_sig_diff are in X
		list_cols = [col for col in self.list_sig_diff if col in list(X.columns)]
		# drop list_cols
		X.drop(list_cols, axis=1, inplace=True)
		# return
		return X

# define function to get inertia by n_clusters
def PLOT_INERTIA(df, int_n_max_clusters=20, tpl_figsize=(20,15), str_filename='./output/plt_inertia.png', logger=None):
	# instatiate list_inertia
	list_inertia = []
	# iterate through a range of clusters
	for n_clusters in np.arange(1, int_n_max_clusters+1):
		# print message
		print(f'KMeans - n_clusters {n_clusters}/{int_n_max_clusters}')
		# instantiate model
		model = KMeans(n_clusters=n_clusters)
		# fit model to df_cluster
		model.fit(df)
		# get inertia and append to list
		list_inertia.append(model.inertia_)
	# create axis
	fig, ax = plt.subplots(figsize=tpl_figsize)
	# generate title
	ax.set_title('Inertia by n Clusters', fontsize=20)
	# x label
	ax.set_xlabel('n Clusters', fontsize=15)
	# y label
	ax.set_ylabel('Inertia', fontsize=15)
	# plot inertia by n_clusters
	ax.plot(list(np.arange(1, int_n_max_clusters+1)), list_inertia)
	# xticks
	ax.set_xticks(list(np.arange(1, int_n_max_clusters+1)))
	# save figures
	plt.savefig(f'{str_filename}', bbox_inches='tight')
	# if using logger
	if logger:
		logger.warning(f'Inertia plot generated and saved to {str_filename}')
	# return fig
	return fig

# class to create kmeans feature
class CreateKMeansFeature(BaseEstimator, TransformerMixin):
	# initialize class
	def __init__(self, int_n_clusters=7):
		self.int_n_clusters = int_n_clusters
	# fit
	def fit(self, X, y=None):
		# instantiate class
		cls_kmeans = KMeans(n_clusters=self.int_n_clusters)
		# fit to X
		cls_kmeans.fit(X)
		# save to object
		self.cls_kmeansv = cls_kmeans
		# return
		return self
	# transform
	def transform(self, X):
		# create feature
		X[f'clusters_{self.int_n_clusters}'] = self.cls_kmeansv.predict(X)
		# return
		return X

# define function to find optimal n_components for PCA
def PLOT_PCA_EXPLAINED_VARIANCE(df, int_n_components_min=1, int_n_components_max=259,
								tpl_figsize=(12,10), str_filename='./output/plt_pca.png',
								logger=None):
	# list to append to
	list_flt_expl_var = []
	# iterate through n_components
	for n_components in range(int_n_components_min, int_n_components_max+1):
		# print status
		print(f'PCA - n_components {n_components}/{int_n_components_max}')
		# instantiate class
		cls_pca = PCA(n_components=n_components, 
				      copy=True, 
					  whiten=False, 
				      svd_solver='auto', 
				      tol=0.0, 
				      iterated_power='auto', 
				      random_state=42)
		# fit to df
		cls_pca.fit(df)
		# get explained variance
		flt_expl_var = np.sum(cls_pca.explained_variance_ratio_)
		# append to list
		list_flt_expl_var.append(flt_expl_var)
	# create empty canvas
	fig, ax = plt.subplots(figsize=tpl_figsize)
	# title
	ax.set_title('Explained Variance by n_components (PCA)')
	# x axis
	ax.set_xlabel('n_components')
	# y axis
	ax.set_ylabel('Explained Variance')
	# plot it
	ax.plot([item for item in range(int_n_components_min, int_n_components_max+1)] , list_flt_expl_var)
	# save fig
	plt.savefig(str_filename, bbox_inches='tight')
	# if using logging
	if logger:
		logger.warning(f'PCA explained variance plot generated and saved to {str_filename}')
	# return
	return fig

# class to create pca features
class CreatePCAFeatures(BaseEstimator, TransformerMixin):
	# initialize class
	def __init__(self, int_n_components=50):
		self.int_n_components = int_n_components
	# fit
	def fit(self, X, y=None):
		# instantiate class
		cls_pca = PCA(n_components=self.int_n_components, 
		              copy=True, 
					  whiten=False, 
		              svd_solver='auto', 
		              tol=0.0, 
		              iterated_power='auto', 
		              random_state=42)
		# fit
		cls_pca.fit(X)
		# save to object
		self.cls_pca = cls_pca
		# return
		return self
	# transform
	def transform(self, X):
		# transform
		arr_X_pca = self.cls_pca.transform(X)
		# convert array to df
		df_X_pca = pd.DataFrame(arr_X_pca)
		# rename columns
		df_X_pca.columns = [f'pca_{col}' for col in df_X_pca.columns]
		# make sure index matches X
		df_X_pca.index = X.index
		# concatenate
		df_concat = pd.concat([X, df_X_pca], axis=1)
		# return
		return df_concat