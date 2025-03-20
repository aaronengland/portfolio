
from sklearn.base import BaseEstimator, TransformerMixin
import time
import pandas as pd
import numpy as np
from tqdm import tqdm

# replace nana
class ReplaceNaNs(BaseEstimator, TransformerMixin):
    # init
    def __init__(self, bool_verbose=True, str_message='NaN replacer'):
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        return self
    # transform
    def transform(self, X):
        # replace NaNs
        time_start = time.perf_counter()

        X.replace(['None', None, 'NaN', 'nan', ''], np.nan, inplace=True)

        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return
        return X

# set strings
class SetStrings(BaseEstimator, TransformerMixin):
    # init
    def __init__(self, bool_verbose=True, str_message='Set strings'):
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        return self
    # transform
    def transform(self, X):
        # replace NaNs
        time_start = time.perf_counter()
        
        # list of columns
        list_cols = [
            'intopenbktype__app',
            'vehiclemake__app',
            'vehiclemodel__app',
        ]
        for col in tqdm(list_cols):
            try:
                X[col] = X[col].astype(str)
            except KeyError:
                print(f'Unable to convert {col} to string, not found in data')
        
        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return
        return X
    
# replace booleans
class ReplaceBooleans(BaseEstimator, TransformerMixin):
    # init
    def __init__(self, bool_verbose=True, str_message='Boolean replacer'):
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        return self
    # transform
    def transform(self, X):
        # replace NaNs
        time_start = time.perf_counter()
        
        # replacement dictionary
        dict_replace = {
            True: 1,
            False: 0,
            'True': 1,
            'False': 0,
            '0': 0,
            '1': 1,
        }
        X.replace(dict_replace, inplace=True)

        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return
        return X

# data type setter
class SetDataTypes(BaseEstimator, TransformerMixin):
    # initialize
    def __init__(self, bool_verbose=True, str_message='Data Type Setter'):
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        # get the data types into a dictionary
        dict_dtypes = dict(X.dtypes)
        # save to object
        self.dict_dtypes = dict_dtypes
        return self
    # transform
    def transform(self, X):
        # fillna
        time_start = time.perf_counter()

        # rm key val pairs not in X
        dict_dtypes = {key: val for key, val in self.dict_dtypes.items() if key in list(X.columns)}
    
        # change O to str
        dict_dtypes = {key: ('str' if val == 'O' else val) for key, val in dict_dtypes.items()}
        # iterate
        for key, val in tqdm (dict_dtypes.items()):
            X[key] = X[key].astype(val)

        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return
        return X

# class for cleaning text
class CleanText(BaseEstimator, TransformerMixin):
    # initialize class
    def __init__(self, list_cols, bool_verbose=True, str_message='Text Cleaner'):
        self.list_cols = list_cols
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        return self
    # transform
    def transform(self, X):
        # start timer
        time_start = time.perf_counter()

        # future proof
        list_cols = [col for col in self.list_cols if col in list(X.columns)]
        
        # iterate
        for col in tqdm (list_cols):
            # convert to string
            X[col] = X[col].astype(str)
            # lower, strip, replace
            X[col] = X[col].str.lower().str.strip().str.replace(' ', '')
        
        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # return
        return X

# class for inflation
class Inflator(BaseEstimator, TransformerMixin):
    # initialize class
    def __init__(self, list_cols, dict_inflation_rate, bool_verbose=True, str_message='Inflator'):
        self.list_cols = list_cols
        self.dict_inflation_rate = dict_inflation_rate
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        return self
    # transform
    def transform(self, X):
        # start timer
        time_start = time.perf_counter()

        # future proof
        list_cols = [col for col in self.list_cols if col in list(X.columns)]
        
        # make sure date is datetime
        X['applicationdate__app'] = pd.to_datetime(X['applicationdate__app'])
        # create year
        X['year'] = X['applicationdate__app'].dt.year
        # map factor to year
        X['factor'] = X['year'].map(self.dict_inflation_rate)

        # convert
        for col in tqdm (list_cols):
            # multiply by factor
            X[col] = X[col] * X['factor']

        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # return
        return X

# clip values
class ClipValues(BaseEstimator, TransformerMixin):
    # initialize
    def __init__(self, list_cols, bool_verbose=True, str_message='Value clipper', a_min=0, a_max=None):
        self.list_cols = list_cols
        self.bool_verbose = bool_verbose
        self.str_message = str_message
        self.a_min = a_min
        self.a_max = a_max
    # fit
    def fit(self, X, y=None):
        return self
    # transform
    def transform(self, X):
        # start time
        time_start = time.perf_counter()

        # future proof
        list_cols = [col for col in self.list_cols if col in list(X.columns)]

        # if iterating
        for col in tqdm (list_cols):
            X[col] = np.clip(a=X[col], a_min=self.a_min, a_max=self.a_max)
        
        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return X
        return X

# custom imputer
class CustomImputer(BaseEstimator, TransformerMixin):
    # initialize
    def __init__(self, dict_imputation, bool_verbose=True, str_message='Imputer'):
        self.dict_imputation = dict_imputation
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        # return object
        return self
    # transform
    def transform(self, X):
        # fillna
        time_start = time.perf_counter()
        
        # future proof
        list_cols = list(self.dict_imputation.keys())
        list_cols = [col for col in list_cols if col in list(X.columns)]
        
        # impute
        for col in tqdm (list_cols):
            X[col] = X[col].fillna(self.dict_imputation[col])
        
        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return
        return X
    
# imputer
class Imputer(BaseEstimator, TransformerMixin):
    # initialize
    def __init__(self, bool_verbose=True, str_message='Imputer'):
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        # return object
        return self
    # transform
    def transform(self, X):
        # fillna
        time_start = time.perf_counter()
        
        # impute
        X = X.fillna(0)

        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return
        return X

# define value replacer class
class FeatureValueReplacer(BaseEstimator, TransformerMixin):
    # initialize
    def __init__(self, dict_value_replace, bool_verbose=True, str_message='Value Replacer'):
        self.dict_value_replace = dict_value_replace
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        return self
    # transform
    def transform(self, X):
        # start time
        time_start = time.perf_counter()

        # future proof
        dict_value_replace = {key: val for key, val in self.dict_value_replace.items() if key in list(X.columns)}
        # replace
        for key, val in tqdm (dict_value_replace.items()):
            X[key] = X[key].replace(val)

        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return
        return X

# date features
class DateFeatures(BaseEstimator, TransformerMixin):
    # initialize
    def __init__(self, bool_verbose=True, str_message='Date features'):
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        return self
    # transform
    def transform(self, X):
        # fillna
        time_start = time.perf_counter()
        
        # make sure date is datetime
        X['applicationdate__app'] = pd.to_datetime(X['applicationdate__app'])
        # date features
        X['ENG-applicationdate__app_month'] = X['applicationdate__app'].dt.month
        X['ENG-applicationdate__app_quarter'] = X['applicationdate__app'].dt.quarter

        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return
        return X

# rounding binner
class RoundBinning(BaseEstimator, TransformerMixin):
    # initialize
    def __init__(self, dict_round, bool_verbose=True, str_message='Binner'):
        self.dict_round = dict_round
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X):
        return self
    # transform
    def transform(self, X):
        # start time
        time_start = time.perf_counter()

        # rm key val pairs not in X
        dict_round = {key: val for key, val in self.dict_round.items() if key in list(X.columns)}
        for key, val in tqdm (dict_round.items()):
            X[key] = val * round(pd.to_numeric(X[key]) / val)
        
        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return X
        return X

# feature engineering
class FeatureEngineering(BaseEstimator, TransformerMixin):
    # initialize
    def __init__(self, bool_verbose=True, str_message='Engineer PTI and LTV'):
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        return self
    # transform
    def transform(self, X):
        # fillna
        time_start = time.perf_counter()
        
        # payment to income
        try:
            X['ENG-payment_to_income'] = X['payment__app'] / X['fltgrossmonthly__income_sum']
        except KeyError as e:
            print(f'Unable to engineer PTI: {e} is not in the data frame')
        # loan to value
        try:
            X['ENG-loan_to_value'] = X['amtfinanced__app'] / X['bookvalue__app']
        except KeyError as e:
            print(f'Unable to engineer LTV: {e} is not found in the data frame')
        # vehicle age
        try:
            # make sure date is datetime
            X['applicationdate__app'] = pd.to_datetime(X['applicationdate__app'])
            X['ENG-vehicle_age'] = X['applicationdate__app'].dt.year - X['vehicleyear__app']
        except KeyError as e:
            print(f'Unable to engineer vehicle age: {e} is not found in the data frame')
        # dealership age
        try:
            # make sure dates are datetime
            X['applicationdate__app'] = pd.to_datetime(X['applicationdate__app'])
            X['dealerstampcreation__app'] = pd.to_datetime(X['dealerstampcreation__app'])
            X['ENG-dealership_age'] = (X['applicationdate__app'] - X['dealerstampcreation__app']).dt.days / 365
        except KeyError as e:
            print(f'Unable to engineer dealership age: {e} is not found in the data frame')  
        
        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return
        return X 

# replace inf and -inf with NaN
class ReplaceInf(BaseEstimator, TransformerMixin):
    # initialize
    def __init__(self, bool_verbose=True, str_message='Inf Replacer'):
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        # get list columns
        list_cols = list(X.columns)
        # save
        self.list_cols = list_cols
        # return object
        return self
    # transform
    def transform(self, X):
        # start time
        time_start = time.perf_counter()

        # future proof
        list_cols = [col for col in self.list_cols if col in list(X.columns)]

        # if find and replace
        for col in tqdm (list_cols):
            X[col] = X[col].replace([np.inf, -np.inf], np.nan)
        
        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return X
        return X

# define function for mapping term
def custom_mapping_term(int_term):
    if int_term == 0:
        return 72
    elif int_term <= 12:
        return 12
    elif int_term <= 24:
        return 24
    elif int_term <= 36:
        return 36
    elif int_term <= 48:
        return 48
    elif int_term <= 60:
        return 60
    else:
        return 72

# map term
class MapTerm(BaseEstimator, TransformerMixin):
    # init
    def __init__(self, bool_verbose=True, str_message='Map term'):
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        return self
    # transform
    def transform(self, X):
        # map
        time_start = time.perf_counter()
        
        # map
        try:
            X['intterm__app'] = X['intterm__app'].apply(custom_mapping_term)
        except KeyError:
            pass
        
        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return
        return X

# define function for mapping PTI
def custom_mapping_pti(flt_pti):
    if flt_pti <= 0:
        return 0.15
    elif flt_pti <= 0.03:
        return 0
    elif flt_pti <= 0.06:
        return 0.03
    elif flt_pti <= 0.09:
        return 0.06
    elif flt_pti <= 0.12:
        return 0.09
    elif flt_pti <= 0.15:
        return 0.12
    else:
        return 0.15

# map PTI
class MapPTI(BaseEstimator, TransformerMixin):
    # init
    def __init__(self, bool_verbose=True, str_message='Map PTI'):
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X, y=None):
        return self
    # transform
    def transform(self, X):
        # map
        time_start = time.perf_counter()
        
        # map ENG-payment_to_income
        try:
            X['ENG-payment_to_income'] = X['ENG-payment_to_income'].apply(custom_mapping_pti)
        except KeyError:
            pass
        
        # map pti__app
        try:
            X['pti__app'] = X['pti__app'].apply(custom_mapping_pti)
        except KeyError:
            pass
        
        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return
        return X
    
# rounding binner
class RoundBinning(BaseEstimator, TransformerMixin):
    # initialize
    def __init__(self, dict_round, bool_verbose=True, str_message='Binner'):
        self.dict_round = dict_round
        self.bool_verbose = bool_verbose
        self.str_message = str_message
    # fit
    def fit(self, X):
        return self
    # transform
    def transform(self, X):
        # start time
        time_start = time.perf_counter()

        # rm key val pairs not in X
        dict_round = {key: val for key, val in self.dict_round.items() if key in list(X.columns)}
        for key, val in tqdm (dict_round.items()):
            X[key] = val * round(pd.to_numeric(X[key]) / val)
        
        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        if self.bool_verbose:
            print(f'{self.str_message}: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return X
        return X

# define preprocessing model class
class PreprocessingModel(BaseEstimator, TransformerMixin):
    # initialize
    def __init__(self, list_transformers):
        self.list_transformers = list_transformers
    # fit
    def fit(self, X, y=None):
        return self
    # transform
    def transform(self, X):
        # start time
        time_start = time.perf_counter()

        # iterate through transformers
        for transformer in self.list_transformers:
            X = transformer.transform(X)
        
        # end time
        time_end = time.perf_counter()
        # flt_sec
        flt_sec = time_end - time_start
        # print
        print(f'Preprocessing Model: {flt_sec:0.5} sec.')
        # save to object
        self.flt_sec = flt_sec
        # return
        return X
