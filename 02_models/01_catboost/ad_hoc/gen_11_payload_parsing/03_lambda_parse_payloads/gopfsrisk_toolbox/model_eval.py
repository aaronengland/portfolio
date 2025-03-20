# model eval
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from ast import literal_eval
from itertools import chain
from sklearn.metrics import (accuracy_score, fowlkes_mallows_score, precision_score,
                             recall_score, f1_score, roc_auc_score, average_precision_score,
                             log_loss, brier_score_loss, precision_recall_curve, auc,
	                         roc_curve, confusion_matrix)
from sklearn.metrics import (explained_variance_score, mean_absolute_error, mean_squared_error)
from scipy.stats import zscore
from .general import GET_NUMERIC_AND_NONNUMERIC
from .algorithms import FIT_CATBOOST_MODEL
import statsmodels.api as sm

# define function to make QQ plot
def QQ_PLOT(arr_yhat, ser_actual, str_filename='./output/plt_qq.png', logger=None, tpl_figsize=(10,10)):
	# get residuals
	res = arr_yhat - ser_actual
	# make ax
	fig, ax = plt.subplots(figsize=tpl_figsize)
	# title
	ax.set_title('Q-Q Plot')
	# create plot
	sm.qqplot(res, line='45', fit=True, ax=ax)
	# save it
	plt.savefig(str_filename, bbox_inches='tight')
	# close it
	plt.close()
	# log it
	if logger:
		logger.warning(f'QQ plot saved to {str_filename}')
	# return fig
	return fig

# define function to get continuous eval metrics
def CONTINUOUS_EVAL_METRICS(model_regressor, X, y, logger=None):
	# generate predictions
	y_hat = model_regressor.predict(X[model_regressor.feature_names_])
	# explained variance
	exp_var = explained_variance_score(y_true=y, y_pred=y_hat)
	# MAE
	mae = mean_absolute_error(y_true=y, y_pred=y_hat)
	# MSE
	mse = mean_squared_error(y_true=y, y_pred=y_hat)
	# RMSE
	rmse = np.sqrt(mse)
	# put into dictionary
	dict_ = {'exp_var': exp_var,
			 'mae': mae,
			 'mse': mse,
			 'rmse': rmse}
	# if using logger
	if logger:
		logger.warning('Dictionary of continuous eval metrics generated')
	# return dict_
	return dict_

# define function to get binary eval metrics
def BIN_CLASS_EVAL_METRICS(y, X=None, model_classifier=None, y_hat_class=None, y_hat_proba=None, logger=None):
	# if starting with model
	if model_classifier:
		# generate predicted class
		y_hat_class = model_classifier.predict(X[model_classifier.feature_names_])
		# generate predicted probabilities
		y_hat_proba = model_classifier.predict_proba(X[model_classifier.feature_names_])[:,1]
	# accuracy
	accuracy = accuracy_score(y_true=y, y_pred=y_hat_class)
	# geometric mean
	geometric_mean = fowlkes_mallows_score(labels_true=y, labels_pred=y_hat_class)
	# precision
	precision = precision_score(y_true=y, y_pred=y_hat_class)
	# recall
	recall = recall_score(y_true=y, y_pred=y_hat_class)
	# f1
	f1 = f1_score(y_true=y, y_pred=y_hat_class)
	# roc auc
	roc_auc = roc_auc_score(y_true=y, y_score=y_hat_proba)
	# precision recall auc
	pr_auc = average_precision_score(y_true=y, y_score=y_hat_proba)
	# log loss
	log_loss_ = log_loss(y_true=y, y_pred=y_hat_proba)
	# brier 
	brier = brier_score_loss(y_true=y, y_prob=y_hat_proba)
	# get confusion matrix
	tn, fp, fn, tp = confusion_matrix(y_true=y, y_pred=y_hat_class).ravel()
	# true positive rate
	tpr = tp / (tp + fn)
	# true negative rate
	tnr = tn / (tn + fp)
	# diagnostic odds ratio
	dor = (tp / fn) / (fp / tn)
	# discriminatory power
	disc_pwr = (np.sqrt(3) / np.pi) * (np.log(tpr / (1 - tnr)) + np.log(tnr / (1 - tpr)))
	# gilberts skill score
	# get c
	c = ((tp + fp) * (tp + fn)) / len(y)
	# get gs
	gilb_score = (tp - c) / (tp - c + fn + fp)
	# put into dictionary
	dict_ = {'accuracy': accuracy,
	         'geometric_mean': geometric_mean,
	         'precision': precision,
	         'recall': recall,
	         'f1': f1,
	         'roc_auc': roc_auc,
	         'pr_auc': pr_auc,
	         'log_loss': log_loss_,
	         'brier': brier,
	         'tpr': tpr,
	         'tnr': tnr,
	         'dor': dor,
	         'disc_pwr': disc_pwr,
	         'gilb_score': gilb_score}
	# if using logger
	if logger:
		logger.warning('Dictionary of binary eval metrics generated')
	# return dict_
	return dict_

# define function to get feat imp
def SAVE_FEAT_IMP(model, str_filename='./output/df_featimp.csv', logger=None):
	# get model features
	list_model_features = model.feature_names_
	# get importance
	list_feature_importance = list(model.feature_importances_)
	# put in df
	df_imp = pd.DataFrame({'feature': list_model_features,
	                       'importance': list_feature_importance})
	# sort descending
	df_imp.sort_values(by='importance', ascending=False, inplace=True)
	# try saving it
	try:
		# save it
		df_imp.to_csv(str_filename, index=False)
	except FileNotFoundError:
		# make output directory
		os.mkdir('./output')
		# save it
		df_imp.to_csv(str_filename, index=False)
	# if using logger
	if logger:
		# log it
		logger.warning(f'Feature importance saved to {str_filename}')

# define function for splitting into X and y
def X_Y_SPLIT(df_train, df_valid, df_test, logger=None, str_targetname='TARGET__app'):
	# train
	y_train = df_train[str_targetname]
	del df_train[str_targetname]
	# valid
	y_valid = df_valid[str_targetname]
	del df_valid[str_targetname]
	# test
	y_test = df_test[str_targetname]
	del df_test[str_targetname]
	# if using logger
	if logger:
		# log it
		logger.warning('Train, valid, and test dfs split into X and y')
	# return
	return df_train, y_train, df_valid, y_valid, df_test, y_test

# define function for combining train and valid
def COMBINE_TRAIN_AND_VALID(X_train, X_valid, y_train, y_valid, logger=None):
	# combine train and valid dfs
	X_train = pd.concat([X_train, X_valid])
	y_train = pd.concat([y_train, y_valid])
	# if using logger
	if logger:
		# log it
		logger.warning('Training and validation data combined')
	# return
	return X_train, y_train

# define function for PR Curve
def PR_CURVE(y_true, y_hat_prob, y_hat_class, tpl_figsize=(10,10), logger=None, str_filename='./output/plt_prcurve.png'):
	# get precision rate and recall rate
	precision_r, recall_r, thresholds = precision_recall_curve(y_true, y_hat_prob)
	# get F1
	flt_f1 = f1_score(y_true, y_hat_class)
	# get auc
	flt_auc = auc(recall_r, precision_r)
	# get the value of chance (i.e., deliquency rate)
	flt_chance = np.sum(y_true)/len(y_true)
	# create ax
	fig, ax = plt.subplots(figsize=tpl_figsize)
	# title
	ax.set_title(f'PR Curve: F1 = {flt_f1:0.4}; AUC = {flt_auc:0.4}')
	# xlabel
	ax.set_xlabel('Recall')
	# ylabel
	ax.set_ylabel('Precision')
	# pr curve
	ax.plot(recall_r, precision_r, label='PR Curve')
	# chance
	ax.plot(recall_r, [flt_chance for x in recall_r], color='red', linestyle=':', label='Chance')
	# legend
	ax.legend()
	# save fig
	plt.savefig(str_filename, bbox_inches='tight')
	# log for logging
	if logger:
		# log it
		logger.warning(f'Precsion-recall curve saved to {str_filename}')
	# return
	return fig

# function for ROC curves
def ROC_AUC_CURVE(y_true, y_hat, tpl_figsize=(10,10), logger=None, str_filename='.output/plt_rocauc.png'):
	# get roc auc
	auc = roc_auc_score(y_true=y_true,
		                y_score=y_hat)
	# get false positive rate, true positive rate
	fpr, tpr, thresholds = roc_curve(y_true=y_true, 
		                             y_score=y_hat)
	# set up subplots
	fig, ax = plt.subplots(figsize=tpl_figsize)
	# set title
	ax.set_title('ROC Plot - (AUC: {0:0.4f})'.format(auc))
    # set x axis label
	ax.set_xlabel('False Positive Rate (Sensitivity)')
    # set y axis label
	ax.set_ylabel('False Negative Rate (1 - Specificity)')
    # set x lim
	ax.set_xlim([0,1])
    # set y lim
	ax.set_ylim([0,1])
    # create curve
	ax.plot(fpr, tpr, label='Model')
    # plot diagonal red, dotted line
	ax.plot([0,1], [0,1], color='red', linestyle=':', label='Chance')
    # create legend
	ax.legend(loc='lower right')
	# fix overlap
	plt.tight_layout()
	# save fig
	plt.savefig(str_filename, bbox_inches='tight')
	# if using logger
	if logger:
		# log it
		logger.warning(f'ROC AUC curve saved in {str_filename}')
	# return fig
	return fig

# define function for residual plot
def RESIDUAL_PLOT(arr_yhat, ser_actual, str_filename, tpl_figsize=(10,10), logger=None):
	# get residuals
	ser_residuals = arr_yhat - ser_actual
	# get the norm
	norm = np.linalg.norm(ser_residuals)
	# normalize residuals
	ser_residuals = ser_residuals / norm
	# create ax
	fig, ax = plt.subplots(figsize=tpl_figsize)
	# title
	ax.set_title('Residual Plot (predicted - actual)')
	# distplot
	sns.distplot(ser_residuals, ax=ax)
	# save fig
	plt.savefig(str_filename, bbox_inches='tight')
	# if using logger
	if logger:
		# log it
		logger.warning(f'residual plot saved to {str_filename}')
	# return
	return fig

# define function for pd plots
def PARTIAL_DEPENDENCE_PLOTS(model, X_train, y_train, list_cols, tpl_figsize=(15,10), 
	                         str_dirname='./output/pd_plots', str_filename='./output/df_trends.csv', logger=None):
	# generate predictions
	try:
		y_hat_train = model.predict_proba(X_train[model.feature_names_])[:,1]
	except AttributeError:
		y_hat_train = model.predict(X_train[model.feature_names_])
	# create dataframe
	X_train['predicted'] = y_hat_train
	X_train['actual'] = y_train
	# create empty df
	df_empty = pd.DataFrame()
	# generate plots
	for a, col in enumerate(list_cols):
		# print meessage
		print(f'Creating plot {a+1}/{len(list_cols)}')
		# group df
		X_train_grouped = X_train.groupby(by=col, as_index=False).agg({'predicted': 'mean',
		                                                               'actual': 'mean'})
		# incase we have inf -inf or nan
		X_train_grouped = X_train_grouped[~X_train_grouped.isin([np.nan, np.inf, -np.inf]).any(1)]

		# sort
		X_train_grouped = X_train_grouped.sort_values(by=col, ascending=True)
		
		# make z score col name
		str_z_col = f'{col}_z'
		# get z score
		X_train_grouped[str_z_col] = zscore(X_train_grouped[col])
		# subset to only those with z >= 3 and <= -3 (i.e., remove outliers)
		X_train_grouped = X_train_grouped[(X_train_grouped[str_z_col] < 3) & (X_train_grouped[str_z_col] > -3)]

		# calculate trendlines
		# predicted
		z_pred = np.polyfit(X_train_grouped[col], X_train_grouped['predicted'], 1)
		p_pred = np.poly1d(z_pred)
		# actual
		z_act = np.polyfit(X_train_grouped[col], X_train_grouped['actual'], 1)
		p_act = np.poly1d(z_act)

		# create predicted array train
		arr_trend_pred = p_pred(X_train_grouped[col])
		# create array for actual
		arr_trend_actual = p_act(X_train_grouped[col])

		# calculate run
		run_ = np.max(X_train_grouped[col]) - np.min(X_train_grouped[col])

		# calculate slope predicted
		flt_trend_pred = (arr_trend_pred[-1] - arr_trend_pred[0]) / run_
		# calculate slope actual
		flt_trend_actual = (arr_trend_actual[-1] - arr_trend_actual[0]) / run_

		# make dictionary
		dict_ = {'feature':col, 'trend_pred':flt_trend_pred, 'trend_act':flt_trend_actual}
		# append to df_empty
		df_empty = df_empty.append(dict_, ignore_index=True)
		# write to csv
		df_empty.to_csv(str_filename, index=False)

		# create ax
		fig, ax = plt.subplots(figsize=tpl_figsize)
		# plot trendline
		# predicted
		ax.plot(X_train_grouped[col], arr_trend_pred, color='green', label=f'Trend - Predicted ({flt_trend_pred:0.4})')
		# actual
		ax.plot(X_train_grouped[col], arr_trend_actual, color='orange', label=f'Trend - Actual ({flt_trend_actual:0.4})')
		# plot it
		ax.set_title(col)
		# predicted
		ax.plot(X_train_grouped[col], X_train_grouped['predicted'], color='blue', label='Predicted')
		# actual
		ax.plot(X_train_grouped[col], X_train_grouped['actual'], color='red', linestyle=':', label='Actual')
		# legend
		ax.legend(loc='upper right')
		# save fig
		plt.savefig(f'{str_dirname}/{col}.png', bbox_inches='tight')
		# close plot
		plt.close()
	# delete the predicted and actual columns
	del X_train['predicted'], X_train['actual']
	# if logging
	if logger:
		logger.warning(f'Predicted and actual trends generated and saved to {str_filename}')
		logger.warning(f'{len(list_cols)} partial dependence plots generated and saved to {str_dirname}')

# class for sensitivity analysis
class SensitivityAnalysis:
	# initialize
	def __init__(self, str_eval_metric='F1', logger=None):
		self.str_eval_metric = str_eval_metric
		self.logger = logger
	# define function for sensitivity analysis
	def sensitivity_analysis(self,
		                     X_train, 
							 X_valid, 
							 y_train, 
							 y_valid, 
							 list_cols, 
							 list_class_weights=None, 
	                         str_filename_df='./output/df_sensitivity.csv', 
	                         int_iterations=1000, 
	                         int_early_stopping_rounds=100,
	                         str_task_type='CPU', 
	                         bool_classifier=True, 
	                         int_random_state=42,
	                         flt_learning_rate=None, 
	                         dict_monotone_constraints=None): 
		# create empty df
		df_sensitivity = pd.DataFrame(columns=['feature_removed', self.str_eval_metric]) 
		# iterate through columns in X_train
		for a, col in enumerate(list_cols):
			# print message
			print(f'Feature {a+1}/{len(list_cols)}')
			# create list of columns
			list_columns = [x for x in list_cols if x != col]
			# get non-numeric feats
			list_non_numeric = GET_NUMERIC_AND_NONNUMERIC(df=X_train, 
				                                          list_columns=list_columns, 
				                                          logger=None)[1]
			# if using monotone constraints
			if dict_monotone_constraints:
				# make copy of dict_monotone constraints
				dict_monotone_constraints_copy = dict_monotone_constraints.copy()
				# list keys
				list_keys = list(dict_monotone_constraints_copy.keys())
				# rm keys not in list_columns
				for key in list_keys:
					if key not in list_columns:
						del dict_monotone_constraints_copy[key]
				# save to alias
				dict_monotone_constraints_for_model = dict_monotone_constraints_copy.copy()
			else:
				# save to alias
				dict_monotone_constraints_for_model = None
			# fit cb model
			model = FIT_CATBOOST_MODEL(X_train=X_train[list_columns],
		                       		   y_train=y_train,
		                       		   X_valid=X_valid[list_columns],
		                       		   y_valid=y_valid,
		                       		   list_non_numeric=list_non_numeric,
		                       		   int_iterations=int_iterations,
		                       		   str_eval_metric=self.str_eval_metric,
		                       		   int_early_stopping_rounds=int_early_stopping_rounds,
		                       		   str_task_type=str_task_type,
		                       		   bool_classifier=bool_classifier,
		                       		   list_class_weights=list_class_weights,
		                       		   int_random_state=int_random_state,
		                       		   dict_monotone_constraints=dict_monotone_constraints_for_model)
			# get eval metric
			if self.str_eval_metric in ['RMSE', 'Accuracy', 'Recall', 'Precision', 'F1']:
				# predictions
				y_hat = model.predict(X_valid[list_columns])
				# logic
				if self.str_eval_metric == 'RMSE':
					metric_ = np.sqrt(mean_squared_error(y_true=y_valid, y_pred=y_hat))
				elif self.str_eval_metric == 'Accuracy':
					metric_ = accuracy_score(y_true=y_valid, y_pred=y_hat)
				elif self.str_eval_metric == 'Recall':
					metric_ = recall_score(y_true=y_valid, y_pred=y_hat)
				elif self.str_eval_metric == 'Precision':
					metric_ = precision_score(y_true=y_valid, y_pred=y_hat)
				elif self.str_eval_metric == 'F1':
					metric_ = f1_score(y_true=y_valid, y_pred=y_hat)
			elif self.str_eval_metric in ['AUC', 'Logloss', 'MAP']:
				# predictions
				y_hat = model.predict_proba(X_valid[list_columns])[:,1]
				# logic
				if self.str_eval_metric == 'AUC':
					metric_ = roc_auc_score(y_true=y_valid, y_score=y_hat)
				elif self.str_eval_metric == 'Logloss':
					metric_ = log_loss(y_true=y_valid, y_pred=y_hat)
				elif self.str_eval_metric == 'MAP':
					metric_ = average_precision_score(y_true=y_valid, y_score=y_hat)
			# create dictionary
			dict_ = {'feature_removed':col, self.str_eval_metric:metric_}
			# append dict_ to df_sensitivity
			df_sensitivity = df_sensitivity.append(dict_, ignore_index=True)
			# sort it
			if self.str_eval_metric in ['RMSE', 'Logloss']: # lower is better
				df_sensitivity.sort_values(by=self.str_eval_metric, ascending=False, inplace=True)
			elif self.str_eval_metric in ['AUC', 'Accuracy', 'Recall', 'Precision', 'F1', 'MAP']: # higher is better
				df_sensitivity.sort_values(by=self.str_eval_metric, ascending=True, inplace=True)
			# write to csv
			df_sensitivity.to_csv(str_filename_df, index=False)
		# if using logger
		if self.logger:
			self.logger.warning(f'Sensitivity analysis complete, output saved to {str_filename_df}')
		# save to object
		self.df_sensitivity = df_sensitivity
		# return
		return self
	# define function for generating plot
	def sensitivity_plot(self, str_filename='./output/plt_sensitivity.png'):
		# get min
		flt_min_eval_metric = np.min(self.df_sensitivity[self.str_eval_metric])
		# get max
		flt_max_eval_metric = np.max(self.df_sensitivity[self.str_eval_metric])
		# get median
		flt_mdn_eval_metric = np.median(self.df_sensitivity[self.str_eval_metric])
		# create axis
		fig, ax = plt.subplots(figsize=(self.df_sensitivity.shape[0], 10))
		# title
		if self.str_eval_metric in ['AUC', 'Accuracy']:
			ax.set_title(f'{self.str_eval_metric} (ascending) by Removed Feature')
		elif self.str_eval_metric in ['RMSE']:
			ax.set_title(f'{self.str_eval_metric} (descending) by Removed Feature')
		# xlabel
		ax.set_xlabel('Removed Feature')
		# ylabel
		ax.set_ylabel(self.str_eval_metric)
		# line plot of sensitivity analysis
		ax.plot(self.df_sensitivity['feature_removed'], self.df_sensitivity[self.str_eval_metric], color='red', label=self.str_eval_metric)
		# line of min
		ax.plot(self.df_sensitivity['feature_removed'], [flt_min_eval_metric for x in self.df_sensitivity[self.str_eval_metric]], linestyle=':', color='blue', label=f'Minimum {self.str_eval_metric} ({flt_min_eval_metric:0.4})')
		# line of max
		ax.plot(self.df_sensitivity['feature_removed'], [flt_max_eval_metric for x in self.df_sensitivity[self.str_eval_metric]], linestyle=':', color='red', label=f'Maximum {self.str_eval_metric} ({flt_max_eval_metric:0.4})')
		# line of median
		ax.plot(self.df_sensitivity['feature_removed'], [flt_mdn_eval_metric for x in self.df_sensitivity[self.str_eval_metric]], linestyle=':', color='green', label=f'Median {self.str_eval_metric} ({flt_mdn_eval_metric:0.4})')
		# rotate xticks 90 degrees
		plt.xticks(rotation=90)
		# legend
		plt.legend()
		# save figure
		plt.savefig(str_filename, bbox_inches='tight')
		# if using logger
		if self.logger:
			# log it
			self.logger.warning(f'Sensitivity analysis plot saved to {str_filename}')