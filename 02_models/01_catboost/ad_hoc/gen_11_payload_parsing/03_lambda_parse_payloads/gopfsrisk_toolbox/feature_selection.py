# feature selection
import numpy as np
import pandas as pd
from .algorithms import FIT_CATBOOST_MODEL
from .general import GET_NUMERIC_AND_NONNUMERIC
import ast
import pickle
from sklearn.metrics import (f1_score, roc_auc_score, mean_squared_error, accuracy_score, recall_score, 
							 precision_score, balanced_accuracy_score, log_loss, average_precision_score)
from scipy.special import expit
import matplotlib.pyplot as plt


# define function for importance threshold feat select
def ITER_IMP_THRESH_FEAT_SELECT(X_train, y_train, X_valid, y_valid, list_non_numeric,
								list_class_weights, flt_thresh_imp=0.0,
								int_iterations=1000, int_early_stopping_rounds=100,
								str_eval_metric='RMSE', int_random_state=42,
								str_filename='./output/df_output.csv',
								logger=None, tpl_figsize=(12,10), str_filename_plot='./output/plt_n_feats.png',
								flt_learning_rate=None, dict_monotone_constraints=None, str_task_type='GPU',
							 	bool_classifier=False, flt_rsm=None, list_feat_force=None):
	# set initial list_features
	list_features = list(X_train.columns)
	# set n_imp_thresh to 1
	n_imp_thresh = 1
	# list n features
	list_int_n_feats = []
	# list features
	list_list_features = []
	# list flt_metric
	list_flt_metric = []
	# while loop
	while n_imp_thresh > 0:
		# append to list
		list_int_n_feats.append(len(list_features[:]))
		# append to list
		list_list_features.append(list_features[:])
		# if using constraints
		if dict_monotone_constraints:
			# remove any monotone constraints not in list features
			for col in list(dict_monotone_constraints.keys()):
				if col not in list_features:
					del dict_monotone_constraints[col]
		# fit model
		model = FIT_CATBOOST_MODEL(X_train=X_train[list_features], 
								   y_train=y_train, 
					               X_valid=X_valid[list_features], 
					               y_valid=y_valid, 
					               list_non_numeric=[col for col in list_non_numeric if col in list_features], 
					               int_iterations=int_iterations, 
					               str_eval_metric=str_eval_metric, 
					               int_early_stopping_rounds=int_early_stopping_rounds, 
					               str_task_type=str_task_type, 
					               bool_classifier=bool_classifier,
					               list_class_weights=list_class_weights,
					               int_random_state=int_random_state,
					               flt_learning_rate=flt_learning_rate,
					               dict_monotone_constraints=dict_monotone_constraints,
					               flt_rsm=flt_rsm)
		# get metric
		if str_eval_metric in ['RMSE', 'Accuracy', 'Recall', 'Precision', 'BalancedAccuracy', 'F1']:
			# predict
			y_hat = model.predict(X_valid[list_features])
			# logic
			if str_eval_metric == 'RMSE':
				flt_metric = np.sqrt(mean_squared_error(y_true=y_valid, y_pred=y_hat))
			elif str_eval_metric == 'Accuracy':
				flt_metric = accuracy_score(y_true=y_valid, y_pred=y_hat)
			elif str_eval_metric == 'Recall':
				flt_metric = recall_score(y_true=y_valid, y_pred=y_hat)
			elif str_eval_metric == 'Precision':
				flt_metric = precision_score(y_true=y_valid, y_pred=y_hat)
			elif str_eval_metric == 'BalancedAccuracy':
				flt_metric = balanced_accuracy_score(y_true=y_valid, y_pred=y_hat)
			elif str_eval_metric == 'F1':
				flt_metric = f1_score(y_true=y_valid, y_pred=y_hat)
		elif (str_eval_metric in ['AUC', 'Logloss']) or (str_eval_metric.__name__ in ['PrecisionRecallAUC']):
			# predict
			y_hat = model.predict_proba(X_valid[list_features])[:,1]
			# logic
			if str_eval_metric == 'AUC':
				flt_metric = roc_auc_score(y_true=y_valid, y_score=y_hat)
			elif str_eval_metric == 'Logloss':
				flt_metric = log_loss(y_true=y_valid, y_pred=y_hat)
			elif str_eval_metric.__name__ == 'PrecisionRecallAUC':
				flt_metric = average_precision_score(y_true=y_valid, y_score=y_hat)

		# append to list
		list_flt_metric.append(flt_metric)
		# create a data frame
		df_output = pd.DataFrame({'n_feats': list_int_n_feats,
								  'eval_metric': list_flt_metric,
								  'list_features': list_list_features})
		# sort ascending by n_feats
		df_output.sort_values(by='n_feats', ascending=True, inplace=True)
		# write to csv
		df_output.to_csv(str_filename, index=False)

		# plot
		fig, ax = plt.subplots(figsize=tpl_figsize)
		# title
		ax.set_title(f'{str_eval_metric} by N Features')
		# y
		ax.set_ylabel(str_eval_metric)
		# x
		ax.set_xlabel('N Features')
		# plot
		ax.plot([str(feat) for feat in df_output['n_feats']], df_output['eval_metric'])
		# save plot
		plt.savefig(str_filename_plot, bbox_inches='tight')
		# close
		plt.close()

		# get importance
		list_feature_importance = list(model.feature_importances_)
		# put in df
		df_imp = pd.DataFrame({'feature': model.feature_names_,
		                       'importance': list_feature_importance})
		# subset to importance > threshold
		df_imp = df_imp[df_imp['importance']>flt_thresh_imp]
		# check how many were <= flt_thresh_imp
		n_imp_thresh = len(list_features) - df_imp.shape[0]
		# create list
		list_features = list(df_imp['feature'])
		# if we are forcing features
		if list_feat_force:
			for feat_force in list_feat_force:
				if feat_force not in list_features:
					list_features.append(feat_force)

# define function for iterative feature selection
def ITERATIVE_FEAT_SELECTION(X_train, y_train, X_valid, y_valid, list_non_numeric, 
							 list_class_weights, int_n_models=50,
							 int_iterations=1000, int_early_stopping_rounds=100,
							 str_eval_metric='F1', int_random_state=42,
							 str_filename='./output/list_bestfeats.pkl',
							 logger=None, tpl_figsize=(12,10), str_filename_plot='./output/plt_n_feats.png',
							 flt_learning_rate=None, dict_monotone_constraints=None, str_task_type='GPU',
							 bool_classifier=True, flt_rsm=None):
	# instantiate empty list
	list_empty = []
	# instantiate lists for plotting
	list_idx = []
	list_n_feats = []
	# build n models
	for a in range(int_n_models):
		# append a+1 to list_idx
		list_idx.append(a+1)
		# print message
		print(f'Fitting model {a+1}/{int_n_models}')
		# fit model
		model = FIT_CATBOOST_MODEL(X_train=X_train, 
								   y_train=y_train, 
					               X_valid=X_valid, 
					               y_valid=y_valid, 
					               list_non_numeric=list_non_numeric, 
					               int_iterations=int_iterations, 
					               str_eval_metric=str_eval_metric, 
					               int_early_stopping_rounds=int_early_stopping_rounds, 
					               str_task_type=str_task_type, 
					               bool_classifier=bool_classifier,
					               list_class_weights=list_class_weights,
					               int_random_state=int_random_state,
					               flt_learning_rate=flt_learning_rate,
					               dict_monotone_constraints=dict_monotone_constraints,
					               flt_rsm=flt_rsm)
		# get model features
		list_model_features = model.feature_names_
		# get importance
		list_feature_importance = list(model.feature_importances_)
		# put in df
		df_imp = pd.DataFrame({'feature': list_model_features,
		                       'importance': list_feature_importance})
		# subset to > 0
		list_imp_feats = list(df_imp[df_imp['importance']>0]['feature'])
		# append new feats to list_empty
		for feat in list_imp_feats:
			if feat not in list_empty:
				list_empty.append(feat)
		# pickle list
		pickle.dump(list_empty, open(str_filename, 'wb'))

		# append length of list_empty to list_n_feats
		list_n_feats.append(len(list_empty))

		# ax
		fig, ax = plt.subplots(figsize=tpl_figsize)
		# plot
		ax.plot([str(idx) for idx in list_idx], list_n_feats)
		# title
		ax.set_title('N Features by N Models')
		# x
		ax.set_xlabel('N Models')
		# x ticks
		ax.set_xticks([str(idx) for idx in list_idx])
		# y
		ax.set_ylabel('N Features')
		# save
		plt.savefig(str_filename_plot, bbox_inches='tight')
		# close
		plt.close()
	# if using logger
	if logger:
		logger.warning(f'Completed iterative feature selection after fitting {int_n_models} models.')
		logger.warning(f'List of {len(list_empty)} features pickled to {str_filename}')

# define function for feature selection
def STEPWISE_SENSITIVITY_SELECTION(X_train, y_train, X_valid, y_valid, list_feats_all, str_task_type='GPU',
	                               str_eval_metric='F1', list_non_numeric=None, list_class_weights=None, 
	                               int_iterations=10000, int_early_stopping_rounds=1000, str_dirname='./output', 
	                               int_n_rounds_no_increase=10, bool_skip_bl_sens=False, int_counter_start=0, 
	                               int_random_state=None, logger=None):
	# try importng df_feats.csv
	try:
		# import as df_empty
		df_empty = pd.read_csv(f'{str_dirname}/df_feats.csv')
		# if using logger
		if logger:
			logger.warning('df_feats.csv found, importing and continuing analysis...')
	# if the file is not in the directory
	except FileNotFoundError:
		# create a df for which to append
		df_empty = pd.DataFrame()
		# if using logger
		if logger:
			logger.warning('df_feats.csv not found, creating empty df and continuing analysis...')
	
	# instantiate a counter
	counter = int_counter_start
	# while True
	while True:
		# only if we don't want to skip the first sensititivty analysis
		if not bool_skip_bl_sens:
			# -----------------------------------------------------------------------------
			# SENSITIVITY ANALYSIS
			# -----------------------------------------------------------------------------
			# create message
			str_message = f'Beginning sensitivity analysis {counter+1}'
			# if using logger
			if logger:
				# log it
				logger.warning(str_message)
			# print message
			print(str_message)

			# iterate through each feature, removing them 1 by 1 and getting f1
			list_flt_evalmetric_sensitivity = []
			for a, feat in enumerate(list_feats_all):
				# print message
				print(f'Dropping {feat} and fitting model - {a+1}/{len(list_feats_all)}')
				# copy list
				list_feats_all_copy = list_feats_all[:]
				# remove feat
				list_feats_all_copy.remove(feat)
				# get the non_numeric features
				list_non_numeric_copy = GET_NUMERIC_AND_NONNUMERIC(df=X_train, 
												   				   list_columns=list_feats_all_copy)[1]
				# fit cb model
				model = FIT_CATBOOST_MODEL(X_train=X_train[list_feats_all_copy], 
				                           y_train=y_train, 
				                           X_valid=X_valid[list_feats_all_copy], 
				                           y_valid=y_valid, 
				                           list_non_numeric=list_non_numeric_copy, 
				                           int_iterations=int_iterations, 
				                           str_eval_metric=str_eval_metric, 
				                           int_early_stopping_rounds=int_early_stopping_rounds, 
				                           str_task_type=str_task_type, 
				                           bool_classifier=True,
				                           list_class_weights=list_class_weights,
				                           int_random_state=int_random_state)
				# get eval metric
				if str_eval_metric == 'F1':
					flt_evalmetric_sensitivity = f1_score(y_true=y_valid, y_pred=model.predict(X_valid[list_feats_all_copy]))
				elif str_eval_metric == 'AUC':
					flt_evalmetric_sensitivity = roc_auc_score(y_true=y_valid, y_score=model.predict_proba(X_valid[list_feats_all_copy])[:,1])
				# create dictionary
				dict_ = {'list_feats': model.feature_names_,
				         'eval_metric': flt_evalmetric_sensitivity,
				         'analysis_type': 'sensitivity',
				         'counter': counter,
				         'n_feats': len(model.feature_names_),
				         'model_number': a+1,
				         'random_state': int_random_state,
				         'n_iterations': int_iterations,
				         'n_early_stopping': int_early_stopping_rounds}
				# append to df_empty
				df_empty = df_empty.append(dict_, ignore_index=True)
				# write to csv
				df_empty.to_csv(f'{str_dirname}/df_feats.csv', index=False)
				# print message
				print(f'After dropping {feat}, {str_eval_metric} = {flt_evalmetric_sensitivity:0.4}')
				# append to list_flt_evalmetric_sensitivity
				list_flt_evalmetric_sensitivity.append(flt_evalmetric_sensitivity)
			# put features and eval metric into df_sensitivity
			df_sensitivity = pd.DataFrame({'feature':list_feats_all,
			                               'eval_metric':list_flt_evalmetric_sensitivity}).sort_values(by='eval_metric',
			                                                                                           ascending=True)
			# save df_sensitivity
			df_sensitivity.to_csv(f'{str_dirname}/df_sensitivity__{counter+1}.csv', index=False)
		else:
			# create message
			str_message = f'Loading sensitivity analysis {counter+1} from file'
			# print message
			print(str_message)
			# if using logger
			if logger:
				logger.warning(str_message)
			# load in df_sensitivity
			df_sensitivity = pd.read_csv(f'{str_dirname}/df_sensitivity__{counter+1}.csv')
			# set bool_skip_bl_sens = False so the sensitivity analysis will continue in the next iteration
			bool_skip_bl_sens = False

		# -----------------------------------------------------------------------------
		# STEPWISE FEATURE SELECTION
		# -----------------------------------------------------------------------------
		# create message
		str_message = f'Beginning stepwise feature selection {counter+1}'
		# print message
		print(str_message)
		# if using logger
		if logger:
			logger.warning(str_message)
		# instantiate empty lists
		list_feats_stepwise = []
		list_list_feats_stepwise = []
		list_flt_evalmetric_stepwise = []
		# stepwise add each feature 1 by 1 from df_sensitivity
		for a, feat in enumerate(df_sensitivity['feature']):
			# print message
			print(f'Adding {feat} and fitting model {a+1}/{len(df_sensitivity["feature"])}')
			# append to list_feats_stepwise
			list_feats_stepwise.append(feat)

			# get the non_numeric features
			list_non_numeric_copy = GET_NUMERIC_AND_NONNUMERIC(df=X_train, 
												   			   list_columns=list_feats_stepwise)[1]
			# fit cb model
			model = FIT_CATBOOST_MODEL(X_train=X_train[list_feats_stepwise], 
			                           y_train=y_train, 
			                           X_valid=X_valid[list_feats_stepwise], 
			                           y_valid=y_valid, 
			                           list_non_numeric=list_non_numeric_copy, 
			                           int_iterations=int_iterations, 
			                           str_eval_metric=str_eval_metric, 
			                           int_early_stopping_rounds=int_early_stopping_rounds, 
			                           str_task_type=str_task_type, 
			                           bool_classifier=True,
			                           list_class_weights=list_class_weights,
			                           int_random_state=int_random_state)
			# append list of model feats to list_list_feats_stepwise
			list_list_feats_stepwise.append(model.feature_names_)
			# get eval metric
			if str_eval_metric == 'F1':
				flt_evalmetric_sensitivity = f1_score(y_true=y_valid, y_pred=model.predict(X_valid[list_feats_stepwise]))
			elif str_eval_metric == 'AUC':
				flt_evalmetric_sensitivity = roc_auc_score(y_true=y_valid, y_score=model.predict_proba(X_valid[list_feats_stepwise])[:,1])
			# create dictionary
			dict_ = {'list_feats': model.feature_names_,
			         'eval_metric': flt_evalmetric_stepwise,
			         'analysis_type': 'stepwise',
			         'counter': counter,
			         'n_feats': len(model.feature_names_),
			         'model_number': a+1,
			         'random_state': int_random_state,
			         'n_iterations': int_iterations,
				     'n_early_stopping': int_early_stopping_rounds}
			# append to df_empty
			df_empty = df_empty.append(dict_, ignore_index=True)
			# write to csv
			df_empty.to_csv(f'{str_dirname}/df_feats.csv', index=False)
			# print message
			print(f'After adding {feat}, {str_eval_metric} = {flt_evalmetric_stepwise:0.4}')
			# append flt_evalmetric_stepwise to list
			list_flt_evalmetric_stepwise.append(flt_evalmetric_stepwise)

			# if we are on first iteration
			if a == 0:
				# assign flt_evalmetric_stepwise to flt_evalmetric_stepwise_currmax
				flt_evalmetric_stepwise_currmax = flt_evalmetric_stepwise
				# set counter_n_rounds_no_increase to 0
				counter_n_rounds_no_increase = 0
			# if we are not on first iteration and latest flt_evalmetric_stepwise > flt_evalmetric_stepwise_currmax
			elif (a > 0) and (flt_evalmetric_stepwise > flt_evalmetric_stepwise_currmax):
				# assign flt_evalmetric_stepwise to flt_evalmetric_stepwise_currmax
				flt_evalmetric_stepwise_currmax = flt_evalmetric_stepwise
				# reset counter_n_rounds_no_increase
				counter_n_rounds_no_increase = 0
			# if we are not on the firs iteration and there was no improvemment
			elif (a > 0) and (flt_evalmetric_stepwise <= flt_evalmetric_stepwise_currmax):
				# increase counter_n_rounds_no_increase by 1
				counter_n_rounds_no_increase += 1
				# print message
				print(f'No improvement in {counter_n_rounds_no_increase} rounds')

			# if we have gone int_n_rounds_no_increase with no increase
			if counter_n_rounds_no_increase == int_n_rounds_no_increase:
				# break inside loop and continue outer loop
				break

		# put lists into a df
		df_stepwise = pd.DataFrame({'list_feats':list_list_feats_stepwise,
		                            'eval_metric':list_flt_evalmetric_stepwise})
		# create a feature depicting number of items in each list of features
		df_stepwise['n_feats'] = df_stepwise['list_feats'].apply(lambda x: len(x))
		# sort by eval metric (decending) and n_feats (ascending)
		df_stepwise = df_stepwise.sort_values(by=['eval_metric', 'n_feats'], ascending=[False, True])
		# save df_stepwise
		df_stepwise.to_csv(f'{str_dirname}/df_stepwise__{counter+1}.csv', index=False)
		# get best score
		flt_evalmetric_max_stepwise = df_stepwise['eval_metric'].iloc[0]

		# if we are on the first iteration
		if counter == 0:
			# save flt_evalmetric_max_stepwise as our baseline
			flt_eval_metric_baseline = flt_evalmetric_max_stepwise
			# create message
			str_message = f'Baseline {str_eval_metric} established: {flt_eval_metric_baseline:0.4}'
			# log it
			logger.warning(str_message)
			# print it
			print(str_message)
			# save best list of features as list_feats_all so loop will continue to sensitivity analysis
			list_feats_all = df_stepwise['list_feats'].iloc[0]
		# if we are not on the first iteration and flt_evalmetric_max_stepwise improved from previous round
		elif (counter > 0) and (flt_evalmetric_max_stepwise > flt_eval_metric_baseline):
			# save flt_evalmetric_max_stepwise as our baseline
			flt_eval_metric_baseline = flt_evalmetric_max_stepwise
			# create message
			str_message = f'Max {str_eval_metric} from stepwise ({flt_evalmetric_max_stepwise:0.4}) is greater than {str_eval_metric} from baseline ({flt_eval_metric_baseline:0.4}), loop will continue'
			# print it
			print(str_message)
			# if using logger
			if logger:
				logger.warning(str_message)
			# save best list of features as list_feats_all so loop will continue to sensitivity analysis
			list_feats_all = df_stepwise['list_feats'].iloc[0]
		# if we are not on the first iteration and flt_evalmetric_max_stepwise did not improve from previous round
		elif (counter > 0) and (flt_evalmetric_max_stepwise <= flt_eval_metric_baseline):
			# create message
			str_message = f'Max {str_eval_metric} from stepwise ({flt_evalmetric_max_stepwise:0.4}) is not greater than PR-AUC from baseline ({flt_eval_metric_baseline:0.4}), loop will not continue'
			# print it
			print(str_message)
			# if using logger
			if logger:
				logger.warning(str_message)
			# end function
			return df_empty
		# increase counter by 1 because we are starting another round
		counter += 1
	# return
	return df_empty

# define function to load df_feats.csv and convert string lists to lists
def LOAD_DF_FEATS(logger=None, str_filename='./output/df_feats.csv'):
	# load in df_feats
	df_feats = pd.read_csv(str_filename)
	# if each list is a string
	if type(df_feats['list_feats'].iloc[0]) == str:
		# convert them to lists
		df_feats['list_feats'] = df_feats['list_feats'].apply(lambda x: ast.literal_eval(x))
	# if using logger
	if logger:
		# log it
		logger.warning('df_feats.csv loaded to generate plot')
	# return
	return df_feats

# define function for plotting f1 by features
def PLOT_METRIC_BY_LIST_FEATURES(logger, df_feats, str_evalname='PR-AUC', tpl_figsize=(20,10), str_filename='./output/plt_fwd_prauc.png'):
	# subset df_feats to only stepwise
	df_feats = df_feats[df_feats['analysis_type']=='stepwise']
	# get max eval_metric
	flt_max_f1 = np.max(df_feats['eval_metric'])  
	# get number of feats in best model
	int_n_feats = df_feats[df_feats['eval_metric']==flt_max_f1]['n_feats'].iloc[0]
	# create axis
	fig, ax = plt.subplots(figsize=tpl_figsize)
	# title
	ax.set_title(f'Highest {str_evalname} ({flt_max_f1:0.4}) using {int_n_feats} features')
	# x label
	ax.set_xlabel('Iteration')
	# y label
	ax.set_ylabel(str_evalname)
	# plot
	ax.plot([str(x) for x in df_feats.index], df_feats['eval_metric'], label='F1')
	# plot max 
	ax.plot([str(x) for x in df_feats.index], [flt_max_f1 for x in df_feats.index], linestyle=':', label='Max F1')
	# remove x tick labels
	ax.set_xticklabels([])
	# legend
	ax.legend()
	# save plot
	plt.savefig(str_filename, bbox_inches='tight')
	# if using logger
	if logger:
		# log it
		logger.warning(f'Plot of {str_evalname} by feature list saved to {str_filename}')
	# return
	return fig

# define function for getting list of best features
def GET_LIST_BEST_FEATURES_FROM_FEATS(df_feats, logger=None, str_filename='./output/list_bestfeats.pkl'):
	# get number of features in each list
	df_feats['n_feats'] = df_feats['list_feats'].apply(lambda x: len(x))
	# sort descending by eval metric and ascending by n_feats
	df_feats_sorted = df_feats.sort_values(by=['eval_metric','n_feats'], 
	                                       ascending=[False, True])
	# get top list
	list_feats = df_feats_sorted['list_feats'].iloc[0]
	# make sure it is a list and not a string
	if type(list_feats) == str:
		list_feats = ast.literal_eval(list_feats)
	# pickle the list
	with open(str_filename, 'wb') as file_out:
		pickle.dump(list_feats, file_out)
	# if using logger
	if logger:
		# log it
		logger.warning(f'List of best features pickled to {str_filename}')
	# return
	return list_feats







# define pr-AUC custom eval metric
class PrecisionRecallAUC:
	# define a static method to use in evaluate method
	@staticmethod
	def get_pr_auc(y_true, y_pred):
		# fit predictions to logistic sigmoid function
		y_pred = expit(y_pred).astype(float)
		# actual values should be 1 or 0 integers
		y_true = y_true.astype(int)
		# calculate average precision
		flt_pr_auc = average_precision_score(y_true=y_true, y_score=y_pred)
		# return flt_pr_auc
		return flt_pr_auc
	# define a function to tell catboost that greater is better (or not)
	def is_max_optimal(self):
		# greater is better
		return True
	# get the score
	def evaluate(self, approxes, target, weight):
		# make sure length of approxes == 1
		assert len(approxes) == 1
		# make sure length of target is the same as predictions
		assert len(target) == len(approxes[0])
		# set target to integer and save as y_true
		y_true = np.array(target).astype(int)
		# save predictions
		y_pred = approxes[0]
		# generate score
		score = self.get_pr_auc(y_true=y_true, y_pred=y_pred)
		# return the prediction and the calculated weight
		return score, 1
	# get the final score
	def get_final_error(self, error, weight):
		# return error
		return error