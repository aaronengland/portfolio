# custom metrics
import numpy as np
from scipy.special import expit
from sklearn.metrics import confusion_matrix, average_precision_score, mean_squared_error

# define custom metric for converting to logit
class LogitContinuous:
	# returns whether greater values of metric error are better
	def is_max_optimal(self):
		return False
	# compute metric
	def evaluate(self, approxes, target, weight):
		# make sure theres only 1 item in approxes
		assert len(approxes) == 1
		# make sure there are as many actual (target) as there are predictions (approxes[0])
		assert len(target) == len(approxes[0])
		# set target to float and save as y_true
		y_true = np.array(target).astype(float)
		# get predictions, fit to logistic sigmoid function, and set as float
		y_pred = expit(approxes[0]).astype(float)
		# get rmse
		error = np.sqrt(mean_squared_error(y_true, y_pred))
		# return
		return error, 1
	# get final error
	def get_final_error(self, error, weight):
		# Returns final value of metric
		return error

# define class for dollars gained (catboost -- just a prototype)
class DollarsGainedPD:	
	# Returns whether great values of metric error are better
	def is_max_optimal(self):
		return True
	# Compute metric
	def evaluate(self, approxes, target, weight):
		# make sure theres only 1 item in approxes
		assert len(approxes) == 1
		# make sure there are as many actual (target) as there are predictions (approxes[0])
		assert len(target) == len(approxes[0])
		# set target to integer and save as y_true
		y_true = np.array(target).astype(int)
		# get predictions, fit to logistic sigmoid function, and set as float
		y_pred = expit(approxes[0]).astype(float)
		# round y_pred to make binary
		y_pred = np.where(np.array(y_pred) < 0.5, 0, 1)
		# get true negative, false positives, etc
		tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
		# multiply by weights
		sum_tp = tp * 0
		sum_fp = fp * -5000
		sum_tn = tn * 5000
		sum_fn = fn * -5000
		# calculate sum
		error = np.sum([sum_tp, sum_fp, sum_tn, sum_fn])
		# return
		return error, 1
	# get final error   
	def get_final_error(self, error, weight):
		# Returns final value of metric
		return error

# define class for precision-recall AUC (catboost)
class PrecisionRecallAUC:	
	# Returns whether great values of metric error are better
	def is_max_optimal(self):
		return True
	# Compute metric
	def evaluate(self, approxes, target, weight):
		# make sure theres only 1 item in approxes
		assert len(approxes) == 1
		# make sure there are as many actual (target) as there are predictions (approxes[0])
		assert len(target) == len(approxes[0])
		# set target to integer and save as y_true
		y_true = np.array(target).astype(int)
		# get predictions, fit to logistic sigmoid function, and set as float
		y_pred = expit(approxes[0]).astype(float)
		# generate pr-auc
		error = average_precision_score(y_true=y_true, y_score=y_pred)
		# return
		return error, 1
	# get final error   
	def get_final_error(self, error, weight):
		# Returns final value of metric
		return error