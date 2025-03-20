# general
import logging
import os
import time
import pandas as pd
import pickle
from pandas.api.types import is_numeric_dtype
import json
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import datetime as dt
import git

# define function for logging
def LOG_EVENTS(str_filename='./logs/db_pull.log'):
	# set logging format
	FORMAT = '%(name)s:%(levelname)s:%(asctime)s:%(message)s'
	# get logger
	logger = logging.getLogger(__name__)
	# try making log
	try:
		# reset any other logs
		handler = logging.FileHandler(str_filename, mode='w')
	except FileNotFoundError:
		os.mkdir('./logs')
		# reset any other logs
		handler = logging.FileHandler(str_filename, mode='w')
	# change to append
	handler = logging.FileHandler(str_filename, mode='a')
	# set the level to info
	handler.setLevel(logging.INFO)
	# set format
	formatter = logging.Formatter(FORMAT)
	# format the handler
	handler.setFormatter(formatter)
	# add handler
	logger.addHandler(handler)
	# return logger
	return logger

# define function for rm keys of dictionary not in list
def RM_KEYS_NOT_IN_LIST(dict_, list_):
	# make list of keys
	list_keys = list(dict_.keys())
	# rm key val pairs not in list_
	for col in list_keys:
		if col not in list_:
			del dict_[col]
	# return dict_
	return dict_

# define function for loadin#g from pickle
def LOAD_FROM_PICKLE(logger=None, str_filename='../06_preprocessing/output/dict_imputations.pkl'):
	# get file
	pickled_file = pickle.load(open(str_filename, 'rb'))
	# if using logger
	if logger:
		# log it
		logger.warning(f'Imported file from {str_filename}')
	# return
	return pickled_file

# define function to read csv
def CSV_TO_DF(logger=None, str_filename='../output_data/df_raw.csv', list_usecols=None, list_parse_dates=None, int_nrows=None,
	          list_skiprows=None, str_sep=',', lambda_date_parser=None, str_encoding=None):
	# start timer
	time_start = time.perf_counter()
	# read json file
	df = pd.read_csv(str_filename, parse_dates=list_parse_dates, usecols=list_usecols, nrows=int_nrows, 
		             skiprows=list_skiprows, sep=str_sep, date_parser=lambda_date_parser,
		             encoding=str_encoding)
	# if we are using a logger
	if logger:
		# log it
		logger.warning(f'Data imported from {str_filename} in {(time.perf_counter()-time_start)/60:0.4} min.')
	# return
	return df

# define function to convert date col to datetime and sort
def SORT_DF(df, str_colname='dtmStmpCreation__app', logger=None, bool_dropcol=False):
	# get series of str_colname
	ser_ = df[str_colname]
	# sort ascending
	ser_sorted = ser_.sort_values(ascending=True)
	# get the index as a list
	list_ser_sorted_index = list(ser_sorted.index)
	# order df
	df = df.reindex(list_ser_sorted_index)
	# if dropping str_colname
	if bool_dropcol:
		# drop str_colname
		del df[str_colname]
	# if using a logger
	if logger:
		# log it
		logger.warning(f'df sorted ascending by {str_colname}.')
	# return df
	return df

# define function to get numeric and non-numeric cols
def GET_NUMERIC_AND_NONNUMERIC(df, list_columns, logger=None):
	# instantiate empty lists
	list_numeric = []
	list_non_numeric = []
	# iterate through list_columns
	for col in list_columns:
		# if its numeric
		if is_numeric_dtype(df[col]):
			# append to list_numeric
			list_numeric.append(col)
		else:
			# append to list_non_numeric
			list_non_numeric.append(col)
	# if using logger
	if logger:
		logger.warning(f'{len(list_numeric)} numeric columns identified, {len(list_non_numeric)} non-numeric columns identified')
	# return both lists
	return list_numeric, list_non_numeric

# define function for writing to pickle
def PICKLE_TO_FILE(item_to_pickle, str_filename='./output/transformer.pkl', logger=None):
	# pickle file
	pickle.dump(item_to_pickle, open(str_filename, 'wb'))
	# if using logger
	if logger:
		# log it
		logger.warning(f'Pickled {item_to_pickle.__class__.__name__} to {str_filename}')

# write dictionary to text
def DICT_TO_TEXT(dict_, str_filename='./output/dict_evalmetrics.txt', logger=None):
	# write dictionary to text
	with open(str_filename, 'w') as file:
		file.write(json.dumps(dict_))
	# if using logger
	if logger:
		logger.warning(f'Wrote dictionary to {str_filename}')

# define function for computing list of class weights
def GET_LIST_CLASS_WEIGHTS(y_train, logger=None):
	# get list of class weights
	list_class_weights = list(compute_class_weight(class_weight='balanced', 
	                                               classes=np.unique(y_train), 
	                                               y=y_train))
	# if using logger
	if logger:
		# log it
		logger.warning(f'List of class weights {list_class_weights} computed')
	# return
	return list_class_weights

# define function for pushing code to github
def PUSH_TO_REPO(str_path_of_git_repo=f'{os.getcwd()}\.git', 
				 str_commit_message=f'ran on {dt.datetime.now()}',
				 str_add='.',
				 logger=None):
	# create repo object
	repo = git.Repo(str_path_of_git_repo)
	# pull
	print('git pull')
	repo.git.pull()
	# add
	print(f'git add {str_add}')
	if str_add == '.':
		repo.git.add(all=True)
	else:
		repo.git.add(str_add)
	# commit
	print(f'git commit -m "{str_commit_message}"')
	repo.index.commit(str_commit_message)
	# get origin
	origin = repo.remote(name='origin')
	# push to origin
	print('git push origin main')
	origin.push()
	# get url of origin
	str_url_origin = git.cmd.Git(str_path_of_git_repo).execute('git remote get-url origin')
	# print message
	print(f'Push to {str_url_origin} complete')
	# if using logger
	if logger:
		logger.warning(f'Pushed all files to {str_url_origin}')