import pandas as pd
import numpy as np
from numpy.linalg import inv
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import catboost as cb

# define function for pooling data
def POOL_DATA(X, y, list_non_numeric, logger=None):
	# pool
	pool = cb.Pool(X, y, cat_features=list_non_numeric)
	# if logging
	if logger:
		logger.warning('Pooled data for catboost model')
	# return
	return pool

# define function for fitting catboost model
def FIT_CATBOOST_MODEL(int_iterations, str_eval_metric, int_early_stopping_rounds, list_non_numeric=None, 
					   X_train=None, y_train=None, X_valid=None, y_valid=None, str_task_type='GPU', 
					   bool_classifier=True, list_class_weights=None, dict_monotone_constraints=None, 
					   int_random_state=None, bool_pool=True, train_pool=None, valid_pool=None, l2_leaf_reg=None,
					   str_auto_class_weights=None, flt_learning_rate=None, flt_rsm=None):
	# logic for pooling
	if bool_pool:
		# pool train
		train_pool = cb.Pool(X_train, 
		                     y_train,
		                     cat_features=list_non_numeric)
		# pool valid
		valid_pool = cb.Pool(X_valid,
		                     y_valid,
		                     cat_features=list_non_numeric)
	# if fitting classifier
	if bool_classifier:
		# instantiate CatBoostClassifier model
		model = cb.CatBoostClassifier(iterations=int_iterations,
		                              eval_metric=str_eval_metric,
		                              task_type=str_task_type,
		                              class_weights=list_class_weights,
		                              monotone_constraints=dict_monotone_constraints,
		                              random_state=int_random_state,
		                              l2_leaf_reg=l2_leaf_reg,
		                              auto_class_weights=str_auto_class_weights,
		                              learning_rate=flt_learning_rate,
		                              rsm=flt_rsm)
	else:
		# instantiate CatBoostRegressor model
		model = cb.CatBoostRegressor(iterations=int_iterations,
		                             eval_metric=str_eval_metric,
		                             task_type=str_task_type,
		                             monotone_constraints=dict_monotone_constraints,
		                             random_state=int_random_state,
		                             l2_leaf_reg=l2_leaf_reg,
		                             learning_rate=flt_learning_rate)
	# fit to training
	model.fit(train_pool,
	          eval_set=[valid_pool], # can only handle one eval set when using gpu
	          use_best_model=True,
	          early_stopping_rounds=int_early_stopping_rounds)
	# return model
	return model


