# app
from flask import Flask, request, render_template, Response, jsonify
import os
from parse_payload import *
from functions_app import *
from tqdm import tqdm
import datetime as dt

# instantiate app
app = Flask(__name__)

# upload folder
str_upload_dir = './uploads'

# make sure upload folder exists
try:
	os.mkdir(str_upload_dir)
except FileExistsError:
	pass

# declare a global dict for downloads
dict_downloads = {}

# take us to index.html
@app.route('/', methods=['GET','POST'])
def index():
	# get datetime
	int_year_now = dt.datetime.now().year

	# show index
	return render_template(
		'index.html',
		int_year_now=int_year_now,
	)

# submit requests
@app.route('/submit_requests', methods=['GET','POST'])
def submit_requests():
	# get the first file
	file = request.files['str_request_1']
	# save file
	str_filename_1 = file.filename
	str_local_path = f'{str_upload_dir}/{str_filename_1}'
	file.save(str_local_path)
	# read file
	try:
		dict_json_request_1 = json.load(open(str_local_path, 'r'))['request']
	except KeyError:
		dict_json_request_1 = json.load(open(str_local_path, 'r'))
	print(type(dict_json_request_1))

	# get the first file
	file = request.files['str_request_2']
	# save file
	str_filename_2 = file.filename
	str_local_path = f'{str_upload_dir}/{str_filename_2}'
	file.save(str_local_path)
	# read file
	try:
		dict_json_request_2 = json.load(open(str_local_path, 'r'))['request']
	except KeyError:
		dict_json_request_2 = json.load(open(str_local_path, 'r'))

	# parse first file
	cls_parser = PayloadToDataFrame()
	# get data
	df_1 = cls_parser.get_data(dict_request=dict_json_request_1)

	# parse first file
	cls_parser = PayloadToDataFrame()
	# get data
	df_2 = cls_parser.get_data(dict_request=dict_json_request_2)

	# get the columns in both dfs
	list_cols = list(df_1.columns) + list(df_2.columns)
	list_cols = list(dict.fromkeys(list_cols))
	int_n_cols = len(list_cols)
	print(f'There are {int_n_cols} unique features')

	list_cols_mismatch = []
	for col in tqdm(list_cols):
		if not df_1[col].equals(df_2[col]):
			list_cols_mismatch.append(col)
		else:
			pass
	# get n cols
	int_n_cols = len(list_cols_mismatch)
	print(f'There are {int_n_cols} mismatching columns')

	# subset
	df_1_mismatch = df_1[list_cols_mismatch].copy()
	df_2_mismatch = df_2[list_cols_mismatch].copy()

	# convert to html
	df_html_1 = create_static_table(df=df_1_mismatch)
	df_html_2 = create_static_table(df=df_2_mismatch)

	# dict_output
	dict_output = {
		'str_filename_1': str_filename_1,
		'df_html_1': df_html_1,
		'str_filename_2': str_filename_2,
		'df_html_2': df_html_2,
	}
	# return
	return jsonify(dict_output)

# run app		
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=False)
