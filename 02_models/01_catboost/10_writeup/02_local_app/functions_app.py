import pandas as pd
from io import StringIO
import json
import plotly
import plotly.express as px
import plotly.figure_factory as ff
import json

# get object from s3
def get_object_from_s3(cls_client, str_bucket, str_key):
	s3_object = cls_client.get_object(Bucket=str_bucket, Key=str_key)
	bytes_object = s3_object['Body'].read().decode('utf-8')
	df = pd.read_csv(StringIO(bytes_object))
	return df

# static table
def create_static_table(df):
	df = df.to_html(index=False, header='true', justify='left')
	return df

# sortable table
def create_sortable_table(df):
	df = df.to_html(classes='display', escape=False, index=False)
	return df

# parser plot
def parser_plot(df):
	# plotly plot
	fig = px.bar(
		df, 
		x='Step', 
		y='Seconds', 
		color='Type', 
		barmode='group',
	)
	str_title = 'Seconds by Parser Step by Type (Single or Codebtor)'
	fig.update_layout(
		title={'text': str_title, 'x': 0.5, 'xanchor': 'center'},
		autosize=True,
	)
	graphJSON_parser_analysis = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return graphJSON_parser_analysis

# response plot
def response_plot(dict_output, flt_sec_load):
	dict_df = {
		'Load Parser': flt_sec_load,
		'Get Data': dict_output['flt_sec_get_data'],
		'Preprocessing': dict_output['flt_sec_preprocessing'],
		'Predictions': dict_output['flt_sec_predictions'],
		'Adverse Action': dict_output['flt_sec_adverse_action'],
		'Counter Offers': dict_output['flt_sec_counters'],
		'Generate Output': dict_output['flt_sec_generate_output'],
	}
	# create plot
	df = pd.DataFrame({
		'Step': list(dict_df.keys()),
		'Seconds': list(dict_df.values()),
	})
	df['Sequence'] = list(range(1, df.shape[0]+1))
	# reorder
	list_cols = [
		'Sequence',
		'Step',
		'Seconds',
	]
	df = df[list_cols]
	# plot
	fig = px.bar(df, x='Step', y='Seconds')
	flt_sec = df['Seconds'].sum()
	str_title = f'Seconds by Parser Step (Total = {flt_sec:0.4f} seconds)'
	fig.update_layout(
		title={'text': str_title, 'x': 0.5, 'xanchor': 'center'},
		autosize=True,
	)
	graphJSON_response = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return graphJSON_response, df

# serialize dict_output
def serialize_dict_output(dict_output):
	# convert each df to dict
	dict_list_x = dict_output['dict_list_x']
	dict_list_x_tmp = {}
	for key, list_x in dict_list_x.items():
		list_x_tmp = []
		for x in list_x:
			# convert to str
			try:
				x['applicationdate'] = x['applicationdate'].astype(str)
			except:
				pass
			try:
				x['dealerstampcreation'] = x['dealerstampcreation'].astype(str)
			except:
				pass
			# convert to dict
			dict_x = x.to_dict(orient='records')
			# append
			list_x_tmp.append(dict_x)
		# assign
		dict_list_x_tmp[key] = list_x_tmp
	# reassign
	dict_output['dict_list_x'] = dict_list_x_tmp

	# X_raw
	X_raw = dict_output['X_raw']
	# convert to str
	X_raw['applicationdate__app'] = X_raw['applicationdate__app'].astype(str)
	X_raw['dealerstampcreation__app'] = X_raw['dealerstampcreation__app'].astype(str)
	# convert to dict
	X_raw = X_raw.to_dict(orient='records')
	# assign
	dict_output['X_raw'] = X_raw

	# X_clean
	X_clean = dict_output['X_clean']
	# convert to str
	X_clean['applicationdate__app'] = X_clean['applicationdate__app'].astype(str)
	X_clean['dealerstampcreation__app'] = X_clean['dealerstampcreation__app'].astype(str)
	# convert to dict
	X_clean = X_clean.to_dict(orient='records')
	# assign
	dict_output['X_clean'] = X_clean

	# df_shap_vals
	df_shap_vals = dict_output['df_shap_vals']
	# convert to dict
	df_shap_vals = df_shap_vals.to_dict(orient='records')
	# assign
	dict_output['df_shap_vals'] = df_shap_vals

	# serialize
	y_hat_ad = dict_output['y_hat_ad']
	# convert to json
	y_hat_ad = y_hat_ad.to_json()
	# assign
	dict_output['y_hat_ad'] = y_hat_ad

	# serialize
	y_hat_pd = dict_output['y_hat_pd']
	# convert to json
	y_hat_pd = y_hat_pd.to_json()
	# assign
	dict_output['y_hat_pd'] = y_hat_pd

	# serialize
	y_hat_lgd = dict_output['y_hat_lgd']
	# convert to json
	y_hat_lgd = y_hat_lgd.to_json()
	# assign
	dict_output['y_hat_lgd'] = y_hat_lgd

	# serialize
	ser_list_reasons = dict_output['ser_list_reasons']
	# convert to json
	ser_list_reasons = ser_list_reasons.to_json()
	# assign
	dict_output['ser_list_reasons'] = ser_list_reasons

	# serialize
	# df_counter_offers
	df_counter_offers = dict_output['df_counter_offers']
	# convert to dict
	df_counter_offers = df_counter_offers.to_dict(orient='records')
	# assign
	dict_output['df_counter_offers'] = df_counter_offers

	# format
	dict_output = json.dumps(dict_output, indent=4)

	# return dict_output
	return dict_output

# target plot - 1
def target_plot_1(df, str_model):
	# logic
	if 'lgd' not in str_model:
		ser_val_counts = df['Target'].value_counts()
		fig = px.bar(
			x=ser_val_counts.index, 
			y=ser_val_counts.values, 
			labels={'x': 'Values', 'y': 'Frequency'}, 
		)
		fig.update_xaxes(tickvals=[0, 1], ticktext=['0', '1'])
		str_title = 'Frequency of Target Values in Full Data Set'
	else:
		list_data = [list(df['Target'])]
		list_labels = ['All']
		fig = ff.create_distplot(list_data, list_labels, bin_size=.2, show_hist=False)
		str_title = 'Target Distribution in Full Data Set'
		fig.update_layout(title={'text': str_title, 'x': 0.5, 'xanchor': 'center'})
	# convert to json
	graphJSON_target_1 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return graphJSON_target_1

# target plot - 2
def target_plot_2(df, str_model):
	# logic
	if 'lgd' not in str_model:
		fig = px.bar(
			df, 
			x='Value', 
			y='Proportion', 
			color='Data Set', 
			barmode='group',
			labels={'Value': 'Value', 'Proportion': 'Proportion', 'Data Set': 'Data Set'},
		)
		fig.update_xaxes(categoryorder='category ascending')
		str_title = 'Target Value Proportions in Train, Valid, and Test Data'
	else:
		list_data = list(df['Target'])
		list_labels = list(df['Data Set'])
		fig = ff.create_distplot(list_data, list_labels, bin_size=.2, show_hist=False)
		str_title = 'Target Distributions in Train, Valid, and Test Data'
	# title
	fig.update_layout(title={'text': str_title, 'x': 0.5, 'xanchor': 'center'})
	# convert to json
	graphJSON_target_2 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return graphJSON_target_2

# tuning plot
def tuning_plot(df):
	fig = px.scatter(
		df, 
		x='Learning Rate', 
		y=['Train Score','Valid Score'], 
		color_discrete_sequence=['teal','violet'],
	)
	str_title = 'Training and Validation Score by Learning Rate'
	fig.update_layout(
		title={'text': str_title, 'x': 0.5, 'xanchor': 'center'},
		xaxis_title='Learning Rate',
		yaxis_title='Score',
	)
	graphJSON_tuning_1 = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return graphJSON_tuning_1

# rfe plot
def rfe_plot(df):
	fig = px.line(
		df, 
		x='Iteration', 
		y=['Train Score', 'Valid Score'], 
		line_shape='linear', 
		color_discrete_sequence=['teal','violet'],
	)
	str_title = 'Training and Validation Score by Iteration'
	fig.update_layout(
		title={'text': str_title, 'x': 0.5, 'xanchor': 'center'},
		xaxis_title='Iteration',
		yaxis_title='Score',
	)
	graphJSON_rfe = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return graphJSON_rfe

# sensitivity plot
def sensitivity_plot(df):
	fig = px.line(
		df, 
		x='Feature', 
		y='Performance Loss', 
		line_shape='linear', 
		color_discrete_sequence=['violet'],
	)
	str_title = 'Performance Loss by Feature Removed'
	fig.update_layout(
		title={'text': str_title, 'x': 0.5, 'xanchor': 'center'},
		xaxis_title='Feature',
		yaxis_title='Performance Loss',
	)
	graphJSON_sensitivity = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	return graphJSON_sensitivity