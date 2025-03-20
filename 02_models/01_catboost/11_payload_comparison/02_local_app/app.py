# app
from flask import Flask, render_template, request, Response, jsonify
from functions_app import *
import datetime as dt
import os
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, dsa
from cryptography.hazmat.primitives import serialization

# instantiate app
application = Flask(__name__)

# dict_dataframes
dict_contents = {}

# tiers
dict_tiers = {
	'A1': 0.0760,
	'A': 0.1320,
	'B': 0.2650,
	'C': 0.3220,
	'D': 0.3500,
}

@application.route('/download_json/<str_idx>')
def download_json(str_idx):
	# convert to int
	int_idx = int(str_idx)
	# get the request from dictionary
	str_request = dict_contents['list_str_request'][int_idx]
	# get account id
	str_accountid = dict_contents['str_bigaccountid']
	# create filename
	int_row = int_idx + 1
	str_filename = f"request_{str_accountid}_{int_row}.json"
	# return response
	return Response(
		str_request,
		mimetype="text/json",
		headers={"Content-Disposition": f"attachment;filename={str_filename}"}
	)

@application.route('/download_csv/<str_file_key>')
def download_csv(str_file_key):
	# get data frame from dictionary
	df = dict_contents[str_file_key]
	# rm html
	str_file_key_new = str_file_key.replace('_html','')
	# drop the download link column
	try:
		df.drop('Download', axis=1, inplace=True)
	except:
		pass
	# convert to csv
	csv_output = StringIO()
	df.to_csv(csv_output, index=False)
	# move cursor to the beginning
	csv_output.seek(0)
	# get account id
	str_accountid = dict_contents['str_bigaccountid']

	# logic for filename
	if str_file_key_new == 'df_scores':
		# add account id
		str_filename = f'{str_file_key_new}_{str_accountid}.csv'
	elif str_file_key_new == 'df_differences':
		# get rows
		int_row_1 = dict_contents['int_row_1']
		int_row_2 = dict_contents['int_row_2']
		# add account id and rows
		str_filename = f'{str_file_key_new}_{str_accountid}_{int_row_1}_vs_{int_row_2}.csv'
	else:
		pass
	# return response
	return Response(
		csv_output,
		mimetype="text/csv",
		headers={"Content-Disposition": f"attachment;filename={str_filename}"}
	)

# show page for entering big account id
@application.route('/', methods = ['GET','POST'])
def enter_bigaccountid():
	# year for footer
	dtm_now_year = dt.datetime.now().year
	# load page
	return render_template(
		'index.html',
		dtm_now_year=dtm_now_year,
	)

# show score table
@application.route('/score_table', methods = ['GET','POST'])
def get_score_table():
	# year for footer
	dtm_now_year = dt.datetime.now().year

	# get text from text1 and make sure its a string (5708014)
	print('Getting text input...')
	str_bigaccountid_raw = request.form['text']
	str_bigaccountid = str(str_bigaccountid_raw.strip())
	# assign
	dict_contents['str_bigaccountid'] = str_bigaccountid
	print(f'Big Account ID: {str_bigaccountid}')

	# connect to DB
	print('Connecting to snowflake...')
	# load 
	str_filename = 'datascience_rsa_key.p8'
	str_local_path = f'./{str_filename}'
	with open(str_local_path, "rb") as key:
		p_key = serialization.load_pem_private_key(
			key.read(),
			password=None,
			backend=default_backend(),
		)
	# convert to bytes
	private_key = p_key.private_bytes(
		encoding=serialization.Encoding.DER,
		format=serialization.PrivateFormat.PKCS8,
		encryption_algorithm=serialization.NoEncryption(),
	)
	# connect to snowflake
	conn = snowflake.connector.connect(
		user='datascience', 
		private_key=private_key,
		account='pfs', 
		warehouse='datascience',
		database='raw',
		schema='source_s3_scorehistory',
	)

	# pull data
	print('Pulling data...')
	# query
	str_query = f"""
	SELECT
		ACCOUNTID,
		REQUEST_DATETIME,
		REQUEST_JSON,
		RESPONSE_JSON,
		RESPONSE_MODEL_NAME,
		RESPONSE_MODEL_VERSION
	FROM 
		RAW.SOURCE_S3_SCOREHISTORY.PAYLOAD_PARSED
	WHERE ACCOUNTID = {str_bigaccountid}
	AND RESPONSE_MODEL_NAME = 'PRESTIGE-GEN-XII'
	ORDER BY REQUEST_DATETIME ASC
	"""
	print(str_query)
	# pull payloads
	df = pd.read_sql(
		sql=str_query,
		con=conn,
	)
	conn.close()
	print(df)

	# get number of rows
	int_nrows = df.shape[0]
	print(f'Number of requests by account {str_bigaccountid}: {int_nrows}')

	# logic
	if int_nrows == 0:
		return render_template(
			'error.html',
			dtm_now_year=dtm_now_year,
			str_bigaccountid_raw=str_bigaccountid_raw,
		)
	else:
		pass

	# create a row col
	print('Creating Row column...')
	df['ROW'] = list(range(1, int_nrows+1))

	# convert response to dict and get ecnl
	print('Getting ECNL from response...')
	df['ECNL'] = df['RESPONSE_JSON'].apply(
		lambda x: float(json.loads(x)['Response'][0]['Results'][0]['Score_ecnl_mod']),
	)
	df.drop('RESPONSE_JSON', axis=1, inplace=True)
	print(df)

	# map tier
	print('Mapping tier...')
	df['TIER'] = df['ECNL'].apply(
		lambda x: get_tier(
			flt_score=x,
			dict_tiers=dict_tiers,
		),
	)
	print(df)

	# reorder
	print('Reorder columns...')
	list_cols = [
		'ROW',
		'ACCOUNTID',
		'REQUEST_DATETIME',
		'REQUEST_JSON',
		'RESPONSE_MODEL_NAME',
		'RESPONSE_MODEL_VERSION',
		'ECNL',
		'TIER',
	]
	df = df[list_cols].copy()

	# list of requests
	print('Saving the requests to a list...')
	list_str_request = list(df['REQUEST_JSON'])
	# assign
	dict_contents['list_str_request'] = list_str_request

	# create df_show
	print('Creating df_show...')
	list_cols = [
		'ROW',
		'ACCOUNTID',
		'REQUEST_DATETIME',
		'RESPONSE_MODEL_NAME',
		'RESPONSE_MODEL_VERSION',
		'ECNL',
		'TIER',
	]
	df_show = df[list_cols].copy()
	print(df_show)

	# create hyperlinks
	print('Creating hyperlinks...')
	df_show = create_hyperlinks(
		df_show=df_show,
	)

	# rename
	print('Renaming columns...')
	dict_rename = {
		'ROW': 'Row',
		'ACCOUNTID': 'Account ID',
		'REQUEST_DATETIME': 'Date',
		'RESPONSE_MODEL_NAME': 'Model Name',
		'RESPONSE_MODEL_VERSION': 'Model Version',
		'TIER': 'Tier',
	}
	df.rename(columns=dict_rename, inplace=True)
	df_show.rename(columns=dict_rename, inplace=True)

	# assign
	print('Assigning to dictionary so they can be downloaded...')
	# assign so we can use in the next function
	dict_contents['df_html_scores_use'] = df
	# assign so we can download it as csv
	dict_contents['df_html_scores'] = df_show

	# convert to HTML
	print('Converting table to html...')
	df_html_scores = create_sortable_table(
		df=df_show,
	)
	# show table
	return render_template(
		'score_table.html',
		df_html_scores=df_html_scores,
		dtm_now_year=dtm_now_year,
	)

# show differences
@application.route('/get_differences', methods=['GET','POST'])
def get_differences():
	# get text from text1 and make sure its integer
	int_row_1 = int(request.form['payload1'].strip())
	# assign
	dict_contents['int_row_1'] = int_row_1
	# get text from text2 and make sure its integer
	int_row_2 = int(request.form['payload2'].strip())
	# assign
	dict_contents['int_row_2'] = int_row_2
	print(f'User has selected rows {int_row_1} and {int_row_2}')

	# get selected requests
	json_str_request_1, json_str_request_2 = get_selected_requests(
		df=dict_contents['df_html_scores_use'], 
		int_row_1=int_row_1, 
		int_row_2=int_row_2,
	)
	# import parser
	cls_parse_payload = import_parser(
		str_local_path='./cls_parser.pkl',
	)
	# parse both requests
	X_file1, X_file2 = parse_both_requests(
		cls_parse_payload=cls_parse_payload, 
		json_str_request_1=json_str_request_1, 
		json_str_request_2=json_str_request_2,
	)
	# find differences
	df = find_differences(
		X_first=X_file1,
		X_last=X_file2,
		int_row_1=int_row_1,
		int_row_2=int_row_2,
	)
	# get descriptions
	try:
		df = get_descriptions(
			df=df, 
			str_local_path='./df_descriptions.csv',
		)		
		# assign
		dict_contents['df_html_differences'] = df
		# convert to HTML
		df_html_output = create_sortable_table(
			df=df,
		)
	except KeyError:
		# assign empty df
		dict_contents['df_html_differences'] = df
		# create a df
		str_message = f'There are no differences to report between payloads selected from rows {int_row_1} and {int_row_2}'
		df = pd.DataFrame({
			'No Differences': [str_message],
		})
		# convert to HTML
		df_html_output = create_sortable_table(
			df=df,
		)
	# dictionary of output
	dict_output = {
		'df_html_output': df_html_output
	}
	# return json
	return jsonify(dict_output)

# run app
if __name__ == '__main__':
	application.run(host='0.0.0.0', debug=False)