# final model
import pandas as pd
from .algorithms import FIT_CATBOOST_MODEL
import pickle
from sklearn.metrics import f1_score, average_precision_score, precision_score, recall_score, roc_auc_score, precision_score, balanced_accuracy_score, log_loss
import matplotlib.pyplot as plt
import numpy as np

# define function for combining train and valid
def COMBINE_TRAIN_AND_VALID(df_train, df_valid, logger=None):
	# if using logger
	if logger:
		# log it
		logger.warning('Training and validation data combined')
	# return
	return pd.concat([df_train, df_valid])

# define function to fit models iterating through random state
def ITERATIVE_MODEL_FITTING(train_pool, valid_pool, X_valid, y_valid, list_class_weights, int_n_randstate=50, 
	                        int_iterations=10000, int_early_stopping_rounds=1000,
		                    str_filename='./output/df_randstates.csv', int_randstate_start=0, logger=None,
		                    str_eval_metric='F1', str_task_type='GPU', tpl_figsize=(12,10),
		                    str_filename_plot='./output/plt_randstates.png', str_filename_model='./output/cb_model.sav'):
	# create message
	str_message = f'Iterative model fitting for {int_n_randstate} rounds starting at random_state {int_randstate_start}'
	# print it
	print(str_message)
	# if using logger
	if logger:
		# log it
		logger.warning(str_message)
	# see if str_filename exists
	try:
		# read in str_filename
		df_empty = pd.read_csv(str_filename)
	except FileNotFoundError:
		# create empty df
		df_empty = pd.DataFrame()

	# empty lists
	list_random_state = []
	list_flt_evalmetric = []
	# iterate through random states
	counter = 0
	for int_random_state in range(int_randstate_start, (int_randstate_start+int_n_randstate)):
		# append
		list_random_state.append(int_random_state)
		# print message
		print(f'Fitting model {int_random_state+1}/{int_n_randstate}')
		# fit cb model
		model = FIT_CATBOOST_MODEL(train_pool=train_pool,
			                       valid_pool=valid_pool, 
		                           int_iterations=int_iterations, 
		                           str_eval_metric=str_eval_metric, 
		                           int_early_stopping_rounds=int_early_stopping_rounds, 
		                           str_task_type=str_task_type, 
		                           bool_classifier=True,
		                           list_class_weights=list_class_weights,
		                           int_random_state=int_random_state,
		                           bool_pool=False)
		# logic
		if str_eval_metric == 'F1':
			# get eval metric
			flt_evalmetric = f1_score(y_true=y_valid, y_pred=model.predict(X_valid))
		elif str_eval_metric == 'Precision':
			# get eval metric
			flt_evalmetric = precision_score(y_true=y_valid, y_pred=model.predict(X_valid))
		elif str_eval_metric == 'Recall':
			# get eval metric
			flt_evalmetric = recall_score(y_true=y_valid, y_pred=model.predict(X_valid))
		elif str_eval_metric == 'AUC':
			# get eval metric
			flt_evalmetric = roc_auc_score(y_true=y_valid, y_score=model.predict_proba(X_valid)[:,1])
		# append to list
		list_flt_evalmetric.append(flt_evalmetric)

		# ax
		fig, ax = plt.subplots(figsize=tpl_figsize)
		# plot
		ax.plot([str(rand_state) for rand_state in list_random_state], list_flt_evalmetric)
		# title
		ax.set_title(f'{str_eval_metric} by Random State')
		# x
		ax.set_xlabel('Random State')
		# xticks
		ax.set_xticks([str(rand_state) for rand_state in list_random_state])
		# y
		ax.set_ylabel(str_eval_metric)
		# save
		plt.savefig(str_filename_plot, bbox_inches='tight')
		# close
		plt.close()

		# if we are on first iteration
		if counter == 0:
			# save flt_evalmetric as the current high
			flt_evalmetric_curr_max = flt_evalmetric
			# pickle model
			pickle.dump(model, open(str_filename_model, 'wb'))
		# if we are not on the first iteration and we have a new high eval metric score
		if (counter > 0) and (flt_evalmetric > flt_evalmetric_curr_max):
			# save flt_evalmetric as the current high
			flt_evalmetric_curr_max = flt_evalmetric
			# pickle model
			pickle.dump(model, open(str_filename_model, 'wb'))

		# create dict
		dict_ = {'random_state': int_random_state,
		         'eval_metric': flt_evalmetric,
		         'list_feats': model.feature_names_,
		         'n_feats': len(model.feature_names_),
		         'n_iterations': int_iterations,
				 'n_early_stopping': int_early_stopping_rounds}
		# append to df_empty
		df_empty = df_empty.append(dict_, ignore_index=True)
		# wite to csv
		df_empty.to_csv(str_filename, index=False)
		# increase counter by 1
		counter += 1
	# return
	return df_empty

# define function for plotting df_randstates
def PLOT_DF_RANDSTATES(logger, df_randstates, tpl_figsize=(15,10), 
	                   str_filename='./output/plt_randstates.png', str_eval_metric='F1'):
	# find max eval_metric
	flt_max = np.max(df_randstates['eval_metric'])
	# find corresponding random_state
	int_rand_state = df_randstates[df_randstates['eval_metric']==flt_max]['random_state'].iloc[0]

	# create ax
	fig, ax = plt.subplots(figsize=tpl_figsize)
	# title
	ax.set_title(f'Best {str_eval_metric} ({flt_max:0.4}) at Random State {int_rand_state}')
	# plot it
	ax.plot(df_randstates['random_state'], df_randstates['eval_metric'], label=str_eval_metric)
	# plot the maximum eval metric
	ax.plot(df_randstates['random_state'], [flt_max for x in df_randstates['random_state']], linestyle=':', label=f'Max {str_eval_metric}')
	# xlabel
	ax.set_xlabel('Random State')
	# ylabel
	ax.set_ylabel(str_eval_metric)
	# legend
	ax.legend()
	# save
	plt.savefig(str_filename, bbox_inches='tight')
	# if logging
	if logger:
		# log it
		logger.warning(f'Plot of df_randstates.csv saved to {str_filename}')
	# return
	return fig