# app
from flask import Flask, render_template, Response, request, jsonify
try:
	from passwords import *
	bool_deployed = False
	bool_debug = True
except:
	bool_deployed = True
	bool_debug = False
from functions_app import *
import boto3
import os
import json
import pickle
import time
import datetime as dt

# instantiate app
application = Flask(__name__)

# if deployed
if bool_deployed:
	AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
	print(AWS_ACCESS_KEY_ID)
	AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
	print(AWS_SECRET_ACCESS_KEY)
else:
	pass

# declare global variables
dict_dataframes_index = {}
dict_dataframes = {}
dict_dict_response = {}

# init client
cls_client = boto3.client(
	's3',
	aws_access_key_id=AWS_ACCESS_KEY_ID,
	aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
# bucket
str_bucket = '20231010-gen-xii'
# variant
str_variant = 'noPTImodel10'
# upload folder
str_upload_dir = './uploads'

# make sure upload folder exists
try:
	os.mkdir(str_upload_dir)
except FileExistsError:
	pass

@application.route('/download_index/<file_key>')
def download_index_csv(file_key):
	# get data frame from dictionary
    df = dict_dataframes_index[file_key]
    # convert to csv
    csv_output = StringIO()
    # logic to get index for shap
    if file_key == 'df_html_shap_vals':
    	bool_index = True
    else:
    	bool_index = False
    df.to_csv(csv_output, index=bool_index)
    # move cursor to the beginning
    csv_output.seek(0)
    str_filename = f"{file_key.replace('_html','')}.csv"
    # return response
    return Response(
        csv_output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={str_filename}"}
    )

@application.route('/download/<file_key>')
def download_csv(file_key):
	# get data frame from dictionary
    df = dict_dataframes[file_key]
    # convert to csv
    csv_output = StringIO()
    df.to_csv(csv_output, index=False)
    # move cursor to the beginning
    csv_output.seek(0)
    str_filename = f"{file_key.replace('_html','')}.csv"
    # return response
    return Response(
        csv_output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={str_filename}"}
    )

@application.route('/download_json/<file_key>')
def download_json(file_key):
	# get data frame from dictionary
    dict_response = dict_dict_response[file_key]
    str_filename = f"{file_key}.json"
    # return response
    return Response(
        dict_response,
        mimetype="text/json",
        headers={"Content-Disposition": f"attachment;filename={str_filename}"}
    )

# home page
@application.route('/', methods=['GET','POST'])
def show_home_page():
	# model
	str_model = 'home'

	# get dt
	int_year_today = dt.datetime.now().year
	
	################################################################################
	# all features
	################################################################################
	# FEATURES IN ALL MODELS
	str_filename = 'df_list_cols_all_models.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes_index['df_html_list_cols_all_models'] = df
	int_n_feats_all = df.shape[0]
	df_html_list_cols_all_models = create_sortable_table(df)

	################################################################################
	# backtesting
	################################################################################
	# TIER DISTRIBUTIONS
	str_filename = 'df_tier_dist.csv'
	str_local_path = f'./static/{str_model}/{str_filename}'
	df = pd.read_csv(str_local_path)
	dict_dataframes_index['df_html_tier_dist'] = df
	df_html_tier_dist = create_sortable_table(df)

	################################################################################
	# parser
	################################################################################
	# PARSER ANALYSIS
	str_filename = 'df_all.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	# plotly plot
	graphJSON_parser_analysis = parser_plot(df)
	# render index.html
	return render_template(
		'index.html',
		graphJSON_parser_analysis=graphJSON_parser_analysis,
		int_n_feats_all=int_n_feats_all,
		df_html_list_cols_all_models=df_html_list_cols_all_models,
		df_html_tier_dist=df_html_tier_dist,
		int_year_today=int_year_today,
	)

@application.route('/get_response', methods=['GET','POST'])
def get_response():
	# get dt
	int_year_today = dt.datetime.now().year

	# get the file
	file = request.files['str_request']
	# save file
	str_filename = file.filename
	str_local_path = f'{str_upload_dir}/{str_filename}'
	file.save(str_local_path)
	# read file
	try:
		dict_json_request = json.load(open(str_local_path, 'r'))['request']
	except KeyError:
		dict_json_request = json.load(open(str_local_path, 'r'))
	# rm file
	os.remove(str_local_path)

	# start timer to load parser
	time_start = time.perf_counter()
	# load parser
	cls_parse_payload = pickle.load(open('cls_parser.pkl', 'rb'))
	# end time
	time_end = time.perf_counter()
	# flt_sec
	flt_sec_load = time_end - time_start

	# parse payload
	cls_parse_payload.get_data(dict_json_request)
	cls_parse_payload.engineer_pmt_hx()
	cls_parse_payload.shared_preprocessing()
	cls_parse_payload.generate_predictions()
	cls_parse_payload.apply_policies()
	cls_parse_payload.apply_chime()
	cls_parse_payload.adverse_action()
	try:
		cls_parse_payload.counter_offers()
	except Exception as e:
		print(e)
		return render_template(
			'error.html',
			int_year_today=int_year_today,
	)

	# get the counter offers
	df = cls_parse_payload.dict_output['df_counter_offers']

	# assign
	dict_dataframes['df_html_counter_offers'] = df
	# make table sortable
	df_html_counter_offers = create_sortable_table(df)
	
	# get the response
	cls_parse_payload.generate_output()

	# get raw data
	df = cls_parse_payload.dict_output['X_raw'].copy()
	dict_dataframes['df_html_raw'] = df.copy()
	df_html_raw = create_static_table(df)
	
	# get the clean data frame
	df = cls_parse_payload.dict_output['X_clean'].copy()
	dict_dataframes['df_html_clean'] = df.copy()
	df_html_clean = create_static_table(df)
	
	# get the SHAP df
	df = cls_parse_payload.dict_output['df_shap_vals']
	list_cols = list(df.columns)
	df = df.T
	df['Feature'] = list_cols
	# map reason
	df['Reason'] = df['Feature'].map(cls_parse_payload.dict_aa)
	dict_dataframes['df_html_shap_vals'] = df
	df_html_shap_vals = create_sortable_table(df)
	
	# get the response
	dict_response = cls_parse_payload.dict_output['output_final']
	# format response
	dict_response = json.dumps(dict_response, indent=4)
	dict_dict_response['dict_response'] = dict_response

	# create plot
	graphJSON_response, df = response_plot(
		dict_output=cls_parse_payload.dict_output,
		flt_sec_load=flt_sec_load,
	)
	dict_dataframes['df_html_response'] = df
	# sortable table
	df_html_response = create_sortable_table(df)

	# # get the dict_output
	# dict_output = cls_parse_payload.dict_output
	# # serialize it
	# dict_output = serialize_dict_output(
	# 	dict_output=dict_output,
	# )
	# # assign
	# dict_dict_response['dict_output'] = dict_output

	# render index.html
	return render_template(
		'response.html',
		df_html_raw=df_html_raw,
		df_html_clean=df_html_clean,
		df_html_shap_vals=df_html_shap_vals,
		df_html_counter_offers=df_html_counter_offers,
		dict_response=dict_response,
		str_filename=str_filename,
		df_html_response=df_html_response,
		graphJSON_response=graphJSON_response,
		int_year_today=int_year_today,
	)

# AD model
@application.route('/ad')
def show_ad_page():
	# model
	str_model = '01_ad'

	# get dt
	int_year_today = dt.datetime.now().year

	################################################################################
	# data prep
	################################################################################
	# EDA PT 1
	str_filename = 'df_eda_1.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_eda_1'] = df
	# static table
	df_html_eda_1 = create_static_table(df)
	# target
	str_filename = 'df_target_1.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	# plotly plot
	graphJSON_target_1 = target_plot_1(df, str_model)

	# EDA PT 2
	str_filename = 'df_eda_2.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_eda_2'] = df
	# sortable table
	df_html_eda_2 = create_sortable_table(df)
	# target
	str_filename = 'df_target_2.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	# plotly plot
	graphJSON_target_2 = target_plot_2(df, str_model)

	# LEAKY FEATURES
	str_filename = 'df_leaky.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_leaky'] = df
	# sortable table
	df_html_leaky = create_sortable_table(df)

	# EDA PT 3
	str_filename = 'df_eda_3.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_eda_3'] = df
	# sortable table
	df_html_eda_3 = create_sortable_table(df)

	################################################################################
	# preprocessing
	################################################################################
	# PREPROCESSING STEPS
	str_filename = 'df_preprocessing.csv'
	str_local_path = f'./static/shared/{str_filename}'
	df = pd.read_csv(str_local_path)
	dict_dataframes['df_html_preprocessing'] = df
	df_html_preprocessing = create_static_table(df)

	# LIST COLS FINAL
	str_filename = 'df_cols_final.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_cols_final'] = df
	# sortable table
	df_html_cols_final = create_sortable_table(df)

	################################################################################
	# feature selection
	################################################################################
	# FINAL LIST
	str_filename = 'df_list_starting_feats.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_list_features'] = df
	# sortable table
	df_html_list_features = create_sortable_table(df)

	# TUNING
	str_filename = 'df_tuning.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_tuning_1'] = df
	# sortable table
	df_html_tuning_1 = create_sortable_table(df)
	# plotly plot
	graphJSON_tuning_1 = tuning_plot(df)
	
	# RECURSIVE FEATURE ELMINATION
	str_filename = 'df_iterative_feat_select.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_rfe'] = df
	# sortable table
	df_html_rfe = create_sortable_table(df)
	# plotly plot
	graphJSON_rfe = rfe_plot(df)

	################################################################################
	# model
	################################################################################
	# TUNING - 2
	str_filename = 'df_tuning_2.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_tuning_2'] = df
	# sortable table
	df_html_tuning_2 = create_sortable_table(df)
	# plotly plot
	graphJSON_tuning_2 = tuning_plot(df)

	# SENSITIVITY ANALYSIS
	str_filename = 'df_sensitivity.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_sensitivity'] = df
	# sortable table
	df_html_sensitivity = create_sortable_table(df)
	# plotly plot
	graphJSON_sensitivity = sensitivity_plot(df)

	################################################################################
	# compliance
	################################################################################
	# DISPARATE IMPACT ANALYSIS
	str_filename = 'df_disparate.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_disparate'] = df
	# sortable table
	df_html_disparate = create_sortable_table(df)
	# plotly plot
	graphJSON_disparate = sensitivity_plot(df)

	# # ADVERSE ACTION
	# str_filename = 'df_aa_prod.csv'
	# str_key = f'10_writeup/{str_model}/{str_filename}'
	# df = get_object_from_s3(cls_client, str_bucket, str_key)
	# dict_dataframes['df_html_adverse_action'] = df
	# # sortable table
	# df_html_adverse_action = create_sortable_table(df)

	################################################################################
	# model eval
	################################################################################
	str_filename = 'df_metrics.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_model_eval'] = df
	# sortable table
	df_html_model_eval = create_sortable_table(df)

	# render page
	return render_template(
		'ad.html',
		# data prep
		df_html_eda_1=df_html_eda_1,
		graphJSON_target_1=graphJSON_target_1,
		df_html_eda_2=df_html_eda_2,
		graphJSON_target_2=graphJSON_target_2,
		df_html_leaky=df_html_leaky,
		df_html_eda_3=df_html_eda_3,
		# preprocessing
		df_html_preprocessing=df_html_preprocessing,
		df_html_cols_final=df_html_cols_final,
		# feat select
		df_html_list_features=df_html_list_features,
		df_html_tuning_1=df_html_tuning_1,
		graphJSON_tuning_1=graphJSON_tuning_1,
		df_html_rfe=df_html_rfe,
		graphJSON_rfe=graphJSON_rfe,
		# model
		df_html_tuning_2=df_html_tuning_2,
		graphJSON_tuning_2=graphJSON_tuning_2,
		df_html_sensitivity=df_html_sensitivity,
		graphJSON_sensitivity=graphJSON_sensitivity,
		# compliance
		df_html_disparate=df_html_disparate,
		graphJSON_disparate=graphJSON_disparate,
		#df_html_adverse_action=df_html_adverse_action,
		# model eval
		df_html_model_eval=df_html_model_eval,
		int_year_today=int_year_today,
	)

# PD model
@application.route('/pd')
def show_pd_page():
	# model
	str_model = '02_pricing_pd'

	# get dt
	int_year_today = dt.datetime.now().year

	################################################################################
	# data prep
	################################################################################
	# EDA PT 1
	str_filename = 'df_eda_1.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_eda_1'] = df
	# static table
	df_html_eda_1 = create_static_table(df)
	# target
	str_filename = 'df_target_1.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	# plotly plot
	graphJSON_target_1 = target_plot_1(df, str_model)

	# EDA PT 2
	str_filename = 'df_eda_2.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_eda_2'] = df
	# sortable table
	df_html_eda_2 = create_sortable_table(df)
	# target
	str_filename = 'df_target_2.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	# plotly plot
	graphJSON_target_2 = target_plot_2(df, str_model)

	# LEAKY FEATURES
	str_filename = 'df_leaky.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_leaky'] = df
	# sortable table
	df_html_leaky = create_sortable_table(df)

	# EDA PT 3
	str_filename = 'df_eda_3.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_eda_3'] = df
	# sortable table
	df_html_eda_3 = create_sortable_table(df)

	################################################################################
	# preprocessing
	################################################################################
	# PREPROCESSING STEPS
	str_filename = 'df_preprocessing.csv'
	str_local_path = f'./static/shared/{str_filename}'
	df = pd.read_csv(str_local_path)
	dict_dataframes['df_html_preprocessing'] = df
	df_html_preprocessing = create_static_table(df)

	# LIST COLS FINAL
	str_filename = 'df_cols_final.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_cols_final'] = df
	# sortable table
	df_html_cols_final = create_sortable_table(df)

	################################################################################
	# feature selection
	################################################################################
	# FINAL LIST
	str_filename = 'df_list_starting_feats.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_list_features'] = df
	# sortable table
	df_html_list_features = create_sortable_table(df)

	# TUNING
	str_filename = 'df_tuning.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_tuning_1'] = df
	# sortable table
	df_html_tuning_1 = create_sortable_table(df)
	# plotly plot
	graphJSON_tuning_1 = tuning_plot(df)
	
	# RECURSIVE FEATURE ELMINATION
	str_filename = 'df_iterative_feat_select.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_rfe'] = df
	# sortable table
	df_html_rfe = create_sortable_table(df)
	# plotly plot
	graphJSON_rfe = rfe_plot(df)

	################################################################################
	# model
	################################################################################
	# TUNING - 2
	str_filename = 'df_tuning_2.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_tuning_2'] = df
	# sortable table
	df_html_tuning_2 = create_sortable_table(df)
	# plotly plot
	graphJSON_tuning_2 = tuning_plot(df)

	# SENSITIVITY ANALYSIS
	str_filename = 'df_sensitivity.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_sensitivity'] = df
	# sortable table
	df_html_sensitivity = create_sortable_table(df)
	# plotly plot
	graphJSON_sensitivity = sensitivity_plot(df)

	################################################################################
	# compliance
	################################################################################
	# DISPARATE IMPACT ANALYSIS
	str_filename = 'df_disparate.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_disparate'] = df
	# sortable table
	df_html_disparate = create_sortable_table(df)
	# plotly plot
	graphJSON_disparate = sensitivity_plot(df)

	# # ADVERSE ACTION
	# str_filename = 'df_aa_prod.csv'
	# str_key = f'10_writeup/{str_model}/{str_filename}'
	# df = get_object_from_s3(cls_client, str_bucket, str_key)
	# dict_dataframes['df_html_adverse_action'] = df
	# # sortable table
	# df_html_adverse_action = create_sortable_table(df)

	################################################################################
	# model eval
	################################################################################
	str_filename = 'df_metrics.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_model_eval'] = df
	# sortable table
	df_html_model_eval = create_sortable_table(df)

	# render page
	return render_template(
		'pd.html',
		# data prep
		df_html_eda_1=df_html_eda_1,
		graphJSON_target_1=graphJSON_target_1,
		df_html_eda_2=df_html_eda_2,
		graphJSON_target_2=graphJSON_target_2,
		df_html_leaky=df_html_leaky,
		df_html_eda_3=df_html_eda_3,
		# preprocessing
		df_html_preprocessing=df_html_preprocessing,
		df_html_cols_final=df_html_cols_final,
		# feat select
		df_html_list_features=df_html_list_features,
		df_html_tuning_1=df_html_tuning_1,
		graphJSON_tuning_1=graphJSON_tuning_1,
		df_html_rfe=df_html_rfe,
		graphJSON_rfe=graphJSON_rfe,
		# model
		df_html_tuning_2=df_html_tuning_2,
		graphJSON_tuning_2=graphJSON_tuning_2,
		df_html_sensitivity=df_html_sensitivity,
		graphJSON_sensitivity=graphJSON_sensitivity,
		# compliance
		df_html_disparate=df_html_disparate,
		graphJSON_disparate=graphJSON_disparate,
		#df_html_adverse_action=df_html_adverse_action,
		# model eval
		df_html_model_eval=df_html_model_eval,
		int_year_today=int_year_today,
	)

# PD model
@application.route('/lgd')
def show_lgd_page():
	# model
	str_model = '03_pricing_lgd'

	# get dt
	int_year_today = dt.datetime.now().year

	################################################################################
	# data prep
	################################################################################
	# EDA PT 1
	str_filename = 'df_eda_1.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_eda_1'] = df
	# static table
	df_html_eda_1 = create_static_table(df)
	# # target
	# str_filename = 'df_target_1.csv'
	# str_key = f'10_writeup/{str_model}/{str_filename}'
	# df = get_object_from_s3(cls_client, str_bucket, str_key)
	# # plotly plot
	# graphJSON_target_1 = target_plot_1(df, str_model)

	# EDA PT 2
	str_filename = 'df_eda_2.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_eda_2'] = df
	# sortable table
	df_html_eda_2 = create_sortable_table(df)
	# # target
	# str_filename = 'df_target_2.csv'
	# str_key = f'10_writeup/{str_model}/{str_filename}'
	# df = get_object_from_s3(cls_client, str_bucket, str_key)
	# # plotly plot
	# graphJSON_target_2 = target_plot_2(df, str_model)

	# LEAKY FEATURES
	str_filename = 'df_leaky.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_leaky'] = df
	# sortable table
	df_html_leaky = create_sortable_table(df)

	# EDA PT 3
	str_filename = 'df_eda_3.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_eda_3'] = df
	# sortable table
	df_html_eda_3 = create_sortable_table(df)

	################################################################################
	# preprocessing
	################################################################################
	# PREPROCESSING STEPS
	str_filename = 'df_preprocessing.csv'
	str_local_path = f'./static/shared/{str_filename}'
	df = pd.read_csv(str_local_path)
	dict_dataframes['df_html_preprocessing'] = df
	df_html_preprocessing = create_static_table(df)

	# LIST COLS FINAL
	str_filename = 'df_cols_final.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_cols_final'] = df
	# sortable table
	df_html_cols_final = create_sortable_table(df)

	################################################################################
	# feature selection
	################################################################################
	# FINAL LIST
	str_filename = 'df_list_starting_feats.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_list_features'] = df
	# sortable table
	df_html_list_features = create_sortable_table(df)

	# TUNING
	str_filename = 'df_tuning.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_tuning_1'] = df
	# sortable table
	df_html_tuning_1 = create_sortable_table(df)
	# plotly plot
	graphJSON_tuning_1 = tuning_plot(df)
	
	# RECURSIVE FEATURE ELMINATION
	str_filename = 'df_iterative_feat_select.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_rfe'] = df
	# sortable table
	df_html_rfe = create_sortable_table(df)
	# plotly plot
	graphJSON_rfe = rfe_plot(df)

	################################################################################
	# model
	################################################################################
	# TUNING - 2
	str_filename = 'df_tuning_2.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_tuning_2'] = df
	# sortable table
	df_html_tuning_2 = create_sortable_table(df)
	# plotly plot
	graphJSON_tuning_2 = tuning_plot(df)

	# SENSITIVITY ANALYSIS
	str_filename = 'df_sensitivity.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_sensitivity'] = df
	# sortable table
	df_html_sensitivity = create_sortable_table(df)
	# plotly plot
	graphJSON_sensitivity = sensitivity_plot(df)

	################################################################################
	# compliance
	################################################################################
	# DISPARATE IMPACT ANALYSIS
	str_filename = 'df_disparate.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_disparate'] = df
	# sortable table
	df_html_disparate = create_sortable_table(df)
	# plotly plot
	graphJSON_disparate = sensitivity_plot(df)

	# # ADVERSE ACTION
	# str_filename = 'df_aa_prod.csv'
	# str_key = f'10_writeup/{str_model}/{str_filename}'
	# df = get_object_from_s3(cls_client, str_bucket, str_key)
	# dict_dataframes['df_html_adverse_action'] = df
	# # sortable table
	# df_html_adverse_action = create_sortable_table(df)

	################################################################################
	# model eval
	################################################################################
	str_filename = 'df_metrics.csv'
	str_key = f'10_writeup/{str_variant}/{str_model}/{str_filename}'
	df = get_object_from_s3(cls_client, str_bucket, str_key)
	dict_dataframes['df_html_model_eval'] = df
	# sortable table
	df_html_model_eval = create_sortable_table(df)

	# render page
	return render_template(
		'lgd.html',
		# data prep
		df_html_eda_1=df_html_eda_1,
		#graphJSON_target_1=graphJSON_target_1,
		df_html_eda_2=df_html_eda_2,
		#graphJSON_target_2=graphJSON_target_2,
		df_html_leaky=df_html_leaky,
		df_html_eda_3=df_html_eda_3,
		# preprocessing
		df_html_preprocessing=df_html_preprocessing,
		df_html_cols_final=df_html_cols_final,
		# feat select
		df_html_list_features=df_html_list_features,
		df_html_tuning_1=df_html_tuning_1,
		graphJSON_tuning_1=graphJSON_tuning_1,
		df_html_rfe=df_html_rfe,
		graphJSON_rfe=graphJSON_rfe,
		# model
		df_html_tuning_2=df_html_tuning_2,
		graphJSON_tuning_2=graphJSON_tuning_2,
		df_html_sensitivity=df_html_sensitivity,
		graphJSON_sensitivity=graphJSON_sensitivity,
		# compliance
		df_html_disparate=df_html_disparate,
		graphJSON_disparate=graphJSON_disparate,
		#df_html_adverse_action=df_html_adverse_action,
		# model eval
		df_html_model_eval=df_html_model_eval,
		int_year_today=int_year_today,
	)

# run app		
if __name__ == '__main__':
	application.run(host="0.0.0.0", debug=bool_debug)