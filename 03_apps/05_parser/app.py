# app
from flask import Flask, render_template, Response, request, jsonify
from functions_app import *
from functions_pricing import dict_tiers, get_tier, Pricing
from functions_counters import CounterOffers
import os
import json
import pickle
import time
import numpy as np
import datetime as dt
from tqdm import tqdm


# instantiate app
application = Flask(__name__)

# upload folder
str_upload_dir = './uploads'

# get counters threshold
flt_threshold_counters = (dict_tiers['D'] + dict_tiers['C']) / 2

# make sure upload folder exists
try:
	os.mkdir(str_upload_dir)
except FileExistsError:
	pass

# home page
@application.route('/', methods=['GET','POST'])
def show_home_page():

	# get current year
	int_year_today = dt.datetime.today().year

	# render index.html
	return render_template(
		'index.html',
		int_year_today=int_year_today,
	)

@application.route('/parse_payload', methods=['POST'])
def parse_payload():
	# get the file
	file = request.files['str_request']

	# save file
	str_filename = file.filename
	print(f'Reading file: {str_filename}')
	str_local_path = f'{str_upload_dir}/{str_filename}'
	file.save(str_local_path)

	# read file
	dict_json_request = read_file(str_local_path)

	# rm file
	os.remove(str_local_path)

	# load parser
	str_local_path = './cls_parser.pkl'
	cls_parse_payload = load_parser(str_local_path)

	###################################################
	################# PARSE PAYLOAD ##################
	###################################################
	
	# get data
	cls_parse_payload.get_data(dict_json_request)
	# engineer pmt hx
	cls_parse_payload.engineer_pmt_hx()

	# get raw data
	df_raw = cls_parse_payload.df_raw.copy()

	# create list of institutions
	df_raw['list_institutions'] = df_raw['str_institution__tu_pmthx'].apply(
		lambda x: x if isinstance(x, list) else [],
	)
	# create tags for institutions
	list_str_col_new = []
	for str_inst in tqdm(list_str_inst):
		str_col_new = f'{str_inst}_tag'
		df_raw[str_col_new] = df_raw['list_institutions'].apply(
			lambda x: 1 if str_inst in x else 0,
		)
		list_str_col_new.append(str_col_new)
	# get the sum
	df_raw['sum'] = df_raw[list_str_col_new].sum(axis=1)
	# tag
	df_raw['has_inst_tag'] = df_raw['sum'].apply(
		lambda x: 1 if x > 0 else 0,
	)
	# get number of debtors with chime tag
	int_sum_chime = df_raw['has_inst_tag'].sum()
	# logic
	if int_sum_chime >= 1:
		str_bool_chime = 'True'
	else:
		str_bool_chime = 'False'
	print(f'Chime: {str_bool_chime}')

	# reorder cols
	list_cols_end = [col for col in df_raw.columns if col not in list_cols_start]
	list_cols = list_cols_start + list_cols_end
	df_raw = df_raw[list_cols].copy()
	# drop
	df_raw.drop(list_cols_drop_raw, axis=1, inplace=True)
	print(df_raw)
	# make table
	df_html_raw = create_static_table(df_raw)

	# preprocess
	cls_parse_payload.preprocessing()

	# get predictions
	cls_parse_payload.get_predictions()

	# get clean data
	df_clean = cls_parse_payload.df_clean.copy()
	list_cols_end = [col for col in df_clean.columns if col not in list_cols_start]
	list_cols = list_cols_start + list_cols_end
	df_clean = df_clean[list_cols].copy()
	print(df_clean)
	# make table
	df_html_clean = create_static_table(df_clean)

	# adverse action
	cls_parse_payload.adverse_action()
	# generate response
	cls_parse_payload.generate_response()

	# get response
	dict_response = cls_parse_payload.dict_response
	# format response
	dict_response = json.dumps(dict_response, indent=4)
	
	# get columns in the model
	list_cols_model = list(cls_parse_payload.cls_model_inference.feature_names_in_)
	# get the original
	list_cols = [col.split('_binned')[0] for col in list_cols_model]

	# get the non-binned values of the features in the model
	df_original = df_clean[list_cols].copy()
	# get the values of the features in the model (i.e., the binned values)
	df_cols_model = df_clean[list_cols_model].copy()
	print(df_cols_model)

	# transpose df_original
	int_nrows = df_original.shape[0]
	if int_nrows == 1:
		list_index = ['Debtor']
	else:
		list_index = ['Debtor','Codebtor']
	df_original.index = list_index
	df_original = df_original.T.reset_index()
	dict_rename = {
		'index': 'Feature',
	}
	df_original.rename(columns=dict_rename, inplace=True)

	# transpose df_cols_model
	int_nrows = df_cols_model.shape[0]
	if int_nrows == 1:
		list_index = ['Debtor Binned']
	else:
		list_index = ['Debtor Binned','Codebtor Binned']
	df_cols_model.index = list_index
	df_cols_model = df_cols_model.T.reset_index()
	dict_rename = {
		'index': 'Feature',
	}
	df_cols_model.rename(columns=dict_rename, inplace=True)
	df_cols_model['Feature'] = df_cols_model['Feature'].apply(
		lambda x: x.split('_binned')[0],
	)

	# join
	df = pd.merge(
		left=df_original,
		right=df_cols_model,
		on='Feature',
		how='left',
	)

	# get the coefficients
	list_cols = [col.split('_binned')[0] for col in list_cols_model]
	list_flt_coef = list(cls_parse_payload.cls_model_inference.coef_[0])
	dict_map = dict(zip(list_cols, list_flt_coef))
	df['Coefficient'] = df['Feature'].map(dict_map)

	# get contributions
	df['Debtor Contribution'] = df['Debtor Binned'] * df['Coefficient']
	try:
		df['Codebtor Contribution'] = df['Codebtor Binned'] * df['Coefficient']
	except:
		pass

	print(df)

	# get the reason and description
	str_filename_tmp = 'df_aa.csv'
	str_local_path = f'./input/{str_filename_tmp}'
	df_aa = pd.read_csv(str_local_path)
	
	# reason
	dict_map = dict(zip(df_aa['feature'], df_aa['reason']))
	df['Reason'] = df['Feature'].map(dict_map)

	# description
	dict_map = dict(zip(df_aa['feature'], df_aa['description']))
	df['Description'] = df['Feature'].map(dict_map)

	# create plot
	graphJSON_features = plot_feature_contribution(
		df=df,
		str_filename=str_filename,
	)

	# sortable table
	df_html_features = create_sortable_table(df)

	###################################################
	################# COUNTER OFFERS ##################
	###################################################

	# counter offers
	flt_ltv = df_clean['ENG-loan_to_value'].iloc[0]
	int_n_offers = 100
	flt_threshold_counters = (dict_tiers['C'] + dict_tiers['D']) / 2
	print(f'Counters threshold: {flt_threshold_counters}')
	cls_counters = CounterOffers(
		flt_ltv_original=flt_ltv,
		int_n_offers=int_n_offers,
		df_clean=df_clean,
		cls_parser=cls_parse_payload,
		flt_threshold_counters=flt_threshold_counters,
		dict_tiers=dict_tiers,
	)
	# run methods
	cls_counters.get_vals_ltv()
	cls_counters.expand_clean_data()
	df = cls_counters.bin_and_predict()

	# add chime penalty
	if str_bool_chime == 'True':
		df['ecnl'] = df['ecnl'] * 1.203
	else:
		df['ecnl'] = df['ecnl'] * 0.936
	
	# add bad pmt hx decision
	if (cls_parse_payload.bool_apply_pmt_hx_decline) and (cls_parse_payload.bool_bad_pmt_hx):
		df['ecnl'] = 1
	else:
		pass

	# get tier
	df['Tier'] = df['ecnl'].apply(
		lambda x: get_tier(
			flt_ecnl=x,
			dict_tiers=dict_tiers,
		)
	)

	print(df)

	# bk
	int_bk = df_clean['ENG-bk'].iloc[0]
	if int_bk == 1:
		bool_bk = True 
	else:
		bool_bk = False
	# vehicle class
	try:
		str_vehicle_class = df_raw['vehicleclass__app'].iloc[0]
	except:
		str_vehicle_class = 'Class 2'
	# dealer type
	str_dealer_type = df_raw['strdealershiptrackertype__app'].iloc[0]
	# dealer state
	str_dealer_state = df_raw['dealerstate__app'].iloc[0]
	# pricing
	cls_pricing = Pricing(
		df=df,
		bool_bk=bool_bk,
		dict_tiers=dict_tiers,
		flt_cnl_scaler=0.8039,
		flt_avg_life=2.3,
		flt_equity_intercept=0.04,
		flt_equity_slope=0.80,
		flt_securitization=0.0595,
		flt_late_fee_income=0.0042,
		flt_state_rate_cap=1.0,
		int_dollars_round_fees=1,
		str_vehicle_class=str_vehicle_class,
		str_dealer_type=str_dealer_type,
		str_dealer_state=str_dealer_state,
	)
	# run methods
	cls_pricing.pricing_test_logic()
	cls_pricing.map_to_tier()
	cls_pricing.get_equity()
	cls_pricing.get_profit()
	cls_pricing.get_discount()
	cls_pricing.get_late_fee()
	cls_pricing.get_funding_cost()
	cls_pricing.get_adjusted_ecnl()
	cls_pricing.get_expected_losses()
	cls_pricing.get_buy_rate()
	cls_pricing.get_raw_apr()
	cls_pricing.get_raw_discount_adjustment()
	cls_pricing.get_raw_apr_adjustment()
	cls_pricing.get_rate_cap_handicap()
	cls_pricing.get_additional_discount_needed()
	cls_pricing.get_apr()
	cls_pricing.get_net_discount()
	# get the output
	df = cls_pricing.df.copy()
	# drop
	df.drop(list_cols_drop_pricing, axis=1, inplace=True)

	# get amt financed reduction
	flt_amtfinanced_original = df_clean['amtfinanced__app'].iloc[0]
	df['amtfinanced_diff'] = flt_amtfinanced_original - df['amtfinanced__app']
	# convert to prop
	df['amtfinanced_diff_prop'] = df['amtfinanced_diff'] / flt_amtfinanced_original

	# get fee reduction
	flt_fee_original = df['net_discount'].iloc[0]
	df['fee_diff'] = flt_fee_original - df['net_discount']
	# convert to prop
	df['fee_diff_prop'] = df['fee_diff'] / flt_fee_original

	# get difference in reductions
	df['Profit'] = df['fee_diff'] - df['amtfinanced_diff']

	# subset
	list_cols = [
		'ENG-loan_to_value',
		'amtfinanced__app',
		'amtfinanced_diff',
		'amtfinanced_diff_prop',
		'PD',
		'LGD',
		'ecnl_24',
		'ecnl',
		'Tier',
		'apr',
		'net_discount',
		'fee_diff',
		'fee_diff_prop',
		'Profit',
	]
	df = df[list_cols].copy()
	
	# rename
	dict_rename = {
		'amtfinanced__app': 'Amt. Fin.',
		'ENG-loan_to_value': 'LTV',
		'ecnl_24': 'ECNL 24 Mo.',
		'ecnl': 'ECNL 72 Mo.',
		'apr': 'Rate',
		'net_discount': 'Fee',
		'fee_diff': 'Fee Red.',
		'fee_diff_prop': 'Fee Red. Prop.',
		'amtfinanced_diff': 'Amt. Fin. Red.',
		'amtfinanced_diff_prop': 'Amt. Fin. Red. Prop.',
	}
	df.rename(columns=dict_rename, inplace=True)
	
	# round
	dict_round = {
		'LTV': 2,
		'Amt. Fin.': 2,
		'Amt. Fin. Red.': 2,
		'Amt. Fin. Red. Prop.': 2,
		'PD': 3,
		'LGD': 3,
		'ECNL 24 Mo.': 3,
		'ECNL 72 Mo.': 3,
		'Rate': 3,
		'Fee': 2,
		'Fee Red.': 2,
		'Fee Red. Prop.': 2,
		'Profit': 2,
	}
	for key, val in dict_round.items():
		df[key] = df[key].round(val)

	# make sortable table
	df_html_counters = create_static_table(df)

	# get decision
	flt_ecnl = df['ECNL 72 Mo.'].iloc[0]
	str_tier = df['Tier'].iloc[0]
	if flt_ecnl <= dict_tiers['D']:
		str_decision = f'APPROVED (ECNL = {flt_ecnl:0.4f}; Tier = {str_tier}; Chime = {str_bool_chime})'
		str_color = 'green'
	else:
		str_decision = f'DECLINED (ECNL = {flt_ecnl:0.4f}; Chime = {str_bool_chime})'
		str_color = 'red'

	# dict_output
	dict_output = {
		'str_filename': str_filename,
		'str_decision': str_decision,
		'str_color': str_color,
		'df_html_raw': df_html_raw,
		'df_html_clean': df_html_clean,
		'graphJSON_features': graphJSON_features,
		'df_html_features': df_html_features,
		'dict_response': dict_response,
		'df_html_counters': df_html_counters,
	}
	return jsonify(dict_output)

# run app		
if __name__ == '__main__':
	application.run(host='0.0.0.0', debug=False)