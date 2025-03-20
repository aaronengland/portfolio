# optimal learning rate
from sklearn.metrics import precision_score
import numpy as np
import matplotlib.pyplot as plt
from .algorithms import FIT_CATBOOST_MODEL
import pickle
from sklearn.metrics import (precision_score, roc_auc_score, mean_squared_error, confusion_matrix, accuracy_score, recall_score, 
							 balanced_accuracy_score, log_loss, f1_score, average_precision_score)
import numpy as np

# define function to tune lr
def TUNE_LEARNING_RATE(X_train, y_train, X_valid, y_valid, list_non_numeric,
						list_class_weights,
						int_iterations=1000, int_early_stopping_rounds=100,
						flt_learning_rate=0.1, flt_learning_rate_increment=0.1,
						str_filename_plot='./output/plt_lr_tuning.png',
						tpl_figsize=(12,10), str_eval_metric='Precision',
						int_n_rounds_no_improve_thresh=3, logger=None,
						str_filename_model='./output/model.sav',
						dict_monotone_constraints=None, str_task_type='GPU',
						bool_classifier=True, flt_rsm=None):
	# make sure flt_learning_rate < 1
	if flt_learning_rate > 1:
		raise Exception('flt_learning_rate must be less than 1.0')
	# if logger
	if logger:
		logger.warning('Beginning tuning learning rate')
	# empty lists and counter
	list_flt_learning_rate = []
	list_flt_metric = []
	list_model = []
	int_n_rounds_no_improve = 0
	# set a to 1 and use as counter
	a = 1
	while int_n_rounds_no_improve < int_n_rounds_no_improve_thresh:
		# raise exception if flt_learning_rate >= 1 or <= 0
		if (flt_learning_rate <= 0) or (flt_learning_rate >= 1):
			raise ValueError('flt_learning_rate must be >0 and <1')
		# append flt_learning_rate to list_flt_learning_rate
		list_flt_learning_rate.append(flt_learning_rate)
		# print model parameters
		print(f'Model {a}')
		print(f'Learning Rate: {flt_learning_rate}')
		print(f'Rounds no Improvement: {int_n_rounds_no_improve}')
		# fit a catboost model
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
		                           flt_learning_rate=flt_learning_rate,
		                           dict_monotone_constraints=dict_monotone_constraints,
		                           flt_rsm=flt_rsm)
		# append to list
		list_model.append(model)
		# if we need predicted classes
		if str_eval_metric in ['RMSE', 'Accuracy', 'Recall', 'Precision', 'BalancedAccuracy', 'F1']:
			# get predictions
			y_hat = model.predict(X_valid)
			# logic
			if str_eval_metric == 'RMSE':
				flt_metric = np.sqrt(mean_squared_error(y_true=y_valid, y_pred=y_hat))
				# make negative so less negative is better (i.e., so our logic works)
				flt_metric = -flt_metric
			elif str_eval_metric == 'Accuracy':
				# get accuracy
				flt_metric = accuracy_score(y_true=y_valid, y_pred=y_hat)
			elif str_eval_metric == 'Recall':
				flt_metric = recall_score(y_true=y_valid, y_pred=y_hat)
			elif str_eval_metric == 'Precision':
				flt_metric = precision_score(y_true=y_valid, y_pred=y_hat)
			elif str_eval_metric == 'BalancedAccuracy':
				flt_metric = balanced_accuracy_score(y_true=y_valid, y_pred=y_hat)
			elif str_eval_metric == 'F1':
				flt_metric = f1_score(y_true=y_valid, y_pred=y_hat)
		# if we need predicted probabilities
		elif (str_eval_metric in ['AUC', 'Logloss']) or (str_eval_metric.__name__ in ['PrecisionRecallAUC']):
			# get predictions
			y_hat = model.predict_proba(X_valid)[:,1]
			# logic
			if str_eval_metric == 'AUC':
				flt_metric = roc_auc_score(y_true=y_valid, y_score=y_hat)
			elif str_eval_metric == 'Logloss':
				flt_metric = log_loss(y_true=y_valid, y_pred=y_hat)
				# make negative so lower is better
				flt_metric = -flt_metric
			elif str_eval_metric.__name__ == 'PrecisionRecallAUC':
				flt_metric = average_precision_score(y_true=y_valid, y_score=y_hat)

		# append to list
		list_flt_metric.append(flt_metric)

		# if first iteration
		if a == 1:
			# set flt_metric_max
			flt_metric_max = flt_metric
			# set max learning rate
			flt_learning_rate_max = flt_learning_rate
			# add flt_learning_rate_increment to flt_learning_rate
			flt_learning_rate += flt_learning_rate_increment
		# if after first iteration and there was improvement from max         
		elif (a > 1) and (flt_metric > flt_metric_max):
			# save new value for flt_metric _max
			flt_metric_max = flt_metric
			# save new value for flt_learning_rate_max
			flt_learning_rate_max = flt_learning_rate
			# add 0.01 to flt_learning_rate
			flt_learning_rate += flt_learning_rate_increment
			# if flt_learning_rate > 1:
			if (flt_learning_rate > 1) or (flt_learning_rate <= 0):
				break
			# set int_n_rounds_no_improve to 0
			int_n_rounds_no_improve = 0
		# if after first iteration and there is no improvement from max
		elif (a > 1) and (flt_metric <= flt_metric_max):
			# get an average of the current flt_learning_rate and the previous learning_rate
			flt_learning_rate = np.mean([flt_learning_rate, flt_learning_rate_max])
			# make sure we don't repeat LR
			while flt_learning_rate in list_flt_learning_rate:
				flt_learning_rate -= (flt_learning_rate_increment/2) # might want to improve this logic later
			# add 1 to int_n_rounds_no_improve
			int_n_rounds_no_improve += 1

		# plot it
		fig, ax = plt.subplots(figsize=tpl_figsize)
		# plot
		ax.plot([str(lr)[0:7] for lr in list_flt_learning_rate], list_flt_metric)
		# x ticks
		ax.set_xticks([str(lr)[0:7] for lr in list_flt_learning_rate])
		# title
		ax.set_title(f'{str_eval_metric} by Learning Rate')
		# x
		ax.set_xlabel('Learning Rate')
		# y
		ax.set_ylabel(str_eval_metric)
		# save
		fig.savefig(str_filename_plot, bbox_inches='tight')
		# close
		plt.close()
		
		# get best model so far
		best_model = list_model[list_flt_metric.index(np.max(list_flt_metric))]
		# pickle best_model
		pickle.dump(best_model, open(str_filename_model, 'wb'))

		# add 1 to a
		a += 1

		# logic
		if (flt_learning_rate <= 0) or (flt_learning_rate >= 1):
			# if using logger
			if logger:
				logger.warning('Finished tuning learning rate')
			# end loop
			break

	# if using logger
	if logger:
		logger.warning('Finished tuning learning rate')
