
from functions import *
import time

# define class
class ParsePayload:
    # init
    def __init__(self, list_cols_raw_app, list_cols_raw_ln, list_cols_raw_tu, list_cols_raw_all):
        self.list_cols_raw_app = list_cols_raw_app
        self.list_cols_raw_ln = list_cols_raw_ln
        self.list_cols_raw_tu = list_cols_raw_tu
        self.str_datecol = 'applicationdate'
        self.dict_output = {}
        self.list_cols_raw_all = list_cols_raw_all
    # get data
    def get_data(self, dict_json_request):
        # start time
        time_start = time.perf_counter()

        # use helper
        list_unique_id, dict_list_tables = get_data_helper(
            dict_json_request=dict_json_request,
        )

        # save to object now for uniformity later
        self.dict_output['list_unique_id'] = list_unique_id

        # flt_sec
        flt_sec = time.perf_counter() - time_start
        # print
        print(f'{self.dict_output["list_unique_id"]}: Get Data: {flt_sec:0.5f} sec.')

        # save to object
        self.dict_json_request = dict_json_request
        # save to dict_output
        self.dict_output['flt_sec_get_data'] = flt_sec
        self.dict_output['dict_list_tables'] = dict_list_tables
        # return object
        return self
    # parse data
    def parse_data(self):
        # start time
        time_start = time.perf_counter()

        # empty dict
        dict_list_x = {}
        # another empty dict
        dict_list_errors = {}
        # iterate through unique ids
        for unique_id in self.dict_output['list_unique_id']:
            # put empty list in dict errors
            dict_list_errors[unique_id] = []
            # empty list
            dict_list_x[unique_id] = []
            # get tables
            list_dict_tables = self.dict_output['dict_list_tables'][unique_id]
            # iterate through tables
            for dict_table in list_dict_tables:
                # get str_values
                str_values = dict_table['values']
                # Application table
                if dict_table['name'] == 'Application':
                    # get application table
                    X, dict_list_errors = get_application_table(
                        str_values=str_values, 
                        str_datecol=self.str_datecol, 
                        list_cols=self.list_cols_raw_app, 
                        unique_id=unique_id, 
                        dict_list_errors=dict_list_errors,
                    )
                    dict_list_x[unique_id].append(X)
                # Income table
                elif dict_table['name'] == 'Incomes':
                    # get income table
                    X, dict_list_errors = get_income_table(
                        str_values=str_values, 
                        unique_id=unique_id, 
                        dict_list_errors=dict_list_errors,
                    )
                    dict_list_x[unique_id].append(X)
                # LexisNexis
                elif dict_table['name'] == 'Lexis Nexis Risk View 5':
                    # get ln table
                    X, dict_list_errors = get_lexis_nexis_table(
                        str_values=str_values,
                        list_cols=self.list_cols_raw_ln,
                        unique_id=unique_id, 
                        dict_list_errors=dict_list_errors,
                    )
                    dict_list_x[unique_id].append(X)
                # TU
                elif dict_table['name'] == 'TUXML':
                    # get tu table
                    X, dict_list_errors = get_transunion_table(
                        str_values=str_values,
                        list_cols=self.list_cols_raw_tu,
                        unique_id=unique_id, 
                        dict_list_errors=dict_list_errors,
                    )
                    dict_list_x[unique_id].append(X)
                else:
                    pass

        # flt_sec
        flt_sec = time.perf_counter() - time_start
        # print
        print(f'{self.dict_output["list_unique_id"]}: Parse Data: {flt_sec:0.5f} sec.')

        # save to dict_output
        self.dict_output['flt_sec_parse_data'] = flt_sec
        self.dict_output['dict_list_x'] = dict_list_x
        self.dict_output['dict_list_errors'] = dict_list_errors
        # return object
        return self
    # create X
    def create_x(self):
        # start time
        time_start = time.perf_counter()

        # empty list
        list_x_cbind = []
        # concatenate cols of df in each list
        for list_x in self.dict_output['dict_list_x'].values():
            # concatenate
            x_cbind = pd.concat(list_x, axis=1)
            # append
            list_x_cbind.append(x_cbind)
        # concatenate rows
        X = pd.concat(list_x_cbind, axis=0)

        # ensure there is a field for every feature
        for col in self.list_cols_raw_all:
            if col not in list(X.columns):
                X[col] = np.nan

        # flt_sec
        flt_sec = time.perf_counter() - time_start
        # print()
        print(f'{self.dict_output["list_unique_id"]}: Create X: {flt_sec:0.5f} sec.')

        # save to dict_output
        self.dict_output['flt_sec_create_x'] = flt_sec
        self.dict_output['X_raw'] = X
        # return object
        return self
