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
def get_deals():
	# user input
	int_income = float(request.form['int_income'])
	print(f'Income: {int_income}')
	flt_amtfinanced = float(request.form['flt_amtfinanced'])
	print(f'Amount Financed: {flt_amtfinanced}')
	flt_bookvalue = float(request.form['flt_bookvalue'])
	print(f'Book Value: {flt_bookvalue}')
	int_mileage = float(request.form['int_mileage'])
	print(f'Mileage: {int_mileage}')
	int_bk = int(request.form['int_bk'])
	print(f'BK: {int_bk}')
	int_franchise = int(request.form['int_franchise'])
	print(f'Franchise: {int_franchise}')
	int_class = int(request.form['int_class'])
	print(f'Class: {int_class}')
	str_state = str(request.form['str_state'])
	print(f'State: {str_state}')

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

	# subset to debtor only
	df = cls_parse_payload.df_raw.copy()
	df = df[df['bitdebtor__app'] == 1].copy()
	cls_parse_payload.df_raw = df.copy()

	# engineer pmt hx
	cls_parse_payload.engineer_pmt_hx()

	# get raw data
	df = cls_parse_payload.df_raw.copy()

	# replace with user input
	df['fltgrossmonthly__income_sum'] = int_income
	df['amtfinanced__app'] = flt_amtfinanced
	df['bookvalue__app'] = flt_bookvalue
	df['miles_odometer__app'] = int_mileage
	# bk
	if int_bk == 0:
		int_bk = np.nan
	else:
		pass
	df['intopenbktype__app'] = int_bk
	
	# franchise
	if int_franchise == 1:
		int_franchise = 'Franchise'
	else:
		int_franchise = 'Independent'
	df['strdealershiptrackertype__app'] = int_franchise
	
	# reassign df 
	cls_parse_payload.df_raw = df.copy()
	
	# preprocess
	cls_parse_payload.preprocessing()
	# get predictions
	cls_parse_payload.get_predictions()
	
	# get the data
	df = cls_parse_payload.df_clean.copy()

	# get the new LTV
	flt_ltv = df['ENG-loan_to_value'].iloc[0]

	# get columns in the model
	list_cols_model = list(cls_parse_payload.cls_model_inference.feature_names_in_)

	# get the pd score
	flt_pd = cls_parse_payload.flt_mean_pd
	print(f'Model PD: {flt_pd}')
	# get the lgd score
	flt_lgd = cls_parse_payload.flt_mean_lgd
	print(f'Model LGD: {flt_lgd}')
	# get loss at 24 months
	flt_loss_at_24 = cls_parse_payload.flt_mean_score
	print(f'Loss at 24 Months: {flt_loss_at_24}')
	# get loss at 72 months (i.e., ecnl)
	flt_loss_at_72 = cls_parse_payload.flt_mean_score_mapped
	print(f'Loss at 72 Months: {flt_loss_at_72}')

	# get the non-binned values of the features in the model
	list_cols = [col.split('_binned')[0] for col in list_cols_model]
	df_original = df[list_cols].copy()

	# get the values of the features in the model (i.e., the binned values)
	df_cols_model = df[list_cols_model].copy()

	# change to vertical df on df_original
	df_fin = df_original.T.reset_index()
	df_fin.columns = ['Feature', 'Raw Value']  

	# add binned value
	df_fin['Binned Value'] = df_fin['Feature'].apply(lambda x: df_cols_model[f'{x}_binned'].values[0])
	# add coefficient
	df_fin['Coefficient'] = cls_parse_payload.cls_model_inference.coef_[0]
	# add Contribution
	df_fin['Contribution'] = df_fin['Binned Value'] * df_fin['Coefficient']

	# get intercept
	flt_intercept = cls_parse_payload.cls_model_inference.intercept_[0]
	print(f'Intercept: {flt_intercept}')
	# get sum of contribution
	flt_sum_of_contribution = df_fin['Contribution'].sum()
	print(f'Sum of contribution: {flt_sum_of_contribution}')
	# get log odds
	flt_logit = flt_intercept + flt_sum_of_contribution
	print(f'Log odds: {flt_logit}')
	# get pd
	flt_pd_tmp = np.exp(flt_logit) / (1 + np.exp(flt_logit))
	print(f'PD: {flt_pd_tmp}')

	# add AA Reason
	df_aa = pd.read_csv('./input/df_aa.csv')
	# merge with df_fin/ get AA reason and description
	df_fin = df_fin.merge(df_aa[['feature', 'reason', 'description']], left_on='Feature', right_on='feature', how='left')
	df_fin = df_fin.drop(columns=['feature'])
	df_fin = df_fin.rename(columns={'reason': 'Reason', 'description': 'Description'})

	# sortable table
	df_html_fin = create_sortable_table(df_fin)

	#score df
	df_score = pd.DataFrame()
	# PD score
	df_score['PD'] = [flt_pd]
	# LTV
	df_score['LTV'] = flt_ltv
	# LGD score
	df_score['LGD'] = flt_lgd
	# ECNL at 24 months (PD * LGD)
	df_score['ECNL 24 Mo.'] = flt_loss_at_24
	# ECNL at 72 months (PD * LGD * 2.36)
	df_score['ECNL 72 Mo.'] = flt_loss_at_72
	# add Tier
	df_score['Tier'] = df_score['ECNL 72 Mo.'].apply(
		lambda x: get_tier(
			flt_ecnl=x,
			dict_tiers=dict_tiers,
		),
	)

	# args
	df = pd.DataFrame({
		'ecnl': [flt_loss_at_72],
		'amtfinanced__app': flt_amtfinanced,
	})
	# bk
	if int_bk == 1:
		bool_bk = True 
	else:
		bool_bk = False
	# tiers
	flt_cnl_scaler = 0.8039
	flt_avg_life = 2.3
	flt_equity_intercept = 0.04
	flt_equity_slope = 0.80
	flt_securitization = 0.0595
	flt_late_fee_income = 0.0042
	flt_state_rate_cap = 1.0
	int_dollars_round_fees = 1
	str_vehicle_class = f'Class {int_class}'
	# dealer type
	if int_franchise == 1:
		str_dealer_type = 'Franchise'
	else:
		str_dealer_type = 'Independent'
	str_dealer_state = str_state.title()

	# pricing
	cls_pricing = Pricing(
		df=df,
		bool_bk=bool_bk,
		dict_tiers=dict_tiers,
		flt_cnl_scaler=flt_cnl_scaler,
		flt_avg_life=flt_avg_life,
		flt_equity_intercept=flt_equity_intercept,
		flt_equity_slope=flt_equity_slope,
		flt_securitization=flt_securitization,
		flt_late_fee_income=flt_late_fee_income,
		flt_state_rate_cap=flt_state_rate_cap,
		int_dollars_round_fees=int_dollars_round_fees,
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
	# get the rate
	flt_rate = df['apr'].iloc[0]
	# get the fee
	flt_fee = df['net_discount'].iloc[0]

	# assign to df_score
	df_score['Rate'] = flt_rate
	df_score['Fee'] = flt_fee

	# reorder
	list_cols = [
		'LTV',
		'PD',
		'LGD',
		'ECNL 24 Mo.',
		'ECNL 72 Mo.',
		'Tier',
		'Rate',
		'Fee',
	]
	df_score = df_score[list_cols].copy()

	# sortable table
	df_html_score = create_static_table(df_score)

	# get some of the stuff we need for amt financed reduction vs fee reduction
	flt_amtfinanced_original = flt_amtfinanced
	flt_fee_original = flt_fee

	###################################################
	################# COUNTER OFFERS ##################
	###################################################

	# counter offers
	df_clean = cls_parse_payload.df_clean.copy()
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

	# get rate and fee
	cls_pricing = Pricing(
		df=df,
		bool_bk=bool_bk,
		dict_tiers=dict_tiers,
		flt_cnl_scaler=flt_cnl_scaler,
		flt_avg_life=flt_avg_life,
		flt_equity_intercept=flt_equity_intercept,
		flt_equity_slope=flt_equity_slope,
		flt_securitization=flt_securitization,
		flt_late_fee_income=flt_late_fee_income,
		flt_state_rate_cap=flt_state_rate_cap,
		int_dollars_round_fees=int_dollars_round_fees,
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

	# get amt financed reduction
	df['amtfinanced_diff'] = flt_amtfinanced_original - df['amtfinanced__app']
	# convert to prop
	df['amtfinanced_diff_prop'] = df['amtfinanced_diff'] / flt_amtfinanced_original

	# get fee reduction
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
	# sort
	df.sort_values(by='ENG-loan_to_value', ascending=False, inplace=True)

	# # rm any where rate increased
	# df = df[df['apr'] < flt_rate].copy()
	# # rm any where fee increased
	# df = df[df['net_discount'] < flt_fee].copy()
	# rm any negative fees
	df = df[df['net_discount'] >= 0].copy()

	# get max ltv by ecnl change
	df = df.loc[df.groupby('ecnl')['ENG-loan_to_value'].idxmax()].copy()
	# sort
	df.sort_values(by='ENG-loan_to_value', ascending=False, inplace=True)

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
	# get list of cols
	list_cols = list(df.columns)
	# create offer col
	df['Offer'] = list(range(1, df.shape[0]+1))
	# reorder
	list_cols = ['Offer'] + list_cols
	df = df[list_cols].copy()

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

	# dict_output
	dict_output = {
		'str_filename': str_filename,
		'df_html_fin': df_html_fin,
		'df_html_score':df_html_score,
		'df_html_counters': df_html_counters,
	}
	return jsonify(dict_output)

# run app		
if __name__ == '__main__':
	application.run(host='0.0.0.0', debug=False)