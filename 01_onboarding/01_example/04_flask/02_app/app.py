# app
from flask import Flask, render_template, Response, request, jsonify, send_file
import os
import json
from datetime import datetime as dt
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot
import plotly 
from functions import *

# instantiate app
application = Flask(__name__)

# function to create the dataframe with our 3 extra columns
def calculate_dataframe(opex_a1, opex_a, opex_b, opex_c, opex_d, roe, cnl_scalar_a1, cnl_scalar_a, cnl_scalar_b, cnl_scalar_c, cnl_scalar_d, equity_slope, securitization, late_fee, equity_intercept, average_life):
	# read in the sql pull dataframe
	str_filename = 'df_ecnl.csv'
	str_local_path = f'./static/tables/{str_filename}'
	df = pd.read_csv(str_local_path)

	#calculate each column - ready for tier IF statement
	theoretical_revenue_a1 = (equity_intercept + equity_slope * df['GEN12_ECNL'] * cnl_scalar_a1) * roe + (1 - (equity_intercept + equity_slope * df['GEN12_ECNL'] * cnl_scalar_a1)) * securitization + opex_a1 + (df['GEN12_ECNL'] * cnl_scalar_a1 / average_life) - ((df['GEN12_ECNL'] / cnl_scalar_a1) * late_fee)
	theoretical_revenue_a = (equity_intercept + equity_slope * df['GEN12_ECNL'] * cnl_scalar_a) * roe + (1 - (equity_intercept + equity_slope * df['GEN12_ECNL'] * cnl_scalar_a)) * securitization + opex_a + (df['GEN12_ECNL'] * cnl_scalar_a / average_life) - ((df['GEN12_ECNL'] / cnl_scalar_a) * late_fee)
	theoretical_revenue_b = (equity_intercept + equity_slope * df['GEN12_ECNL'] * cnl_scalar_b) * roe + (1 - (equity_intercept + equity_slope * df['GEN12_ECNL'] * cnl_scalar_b)) * securitization + opex_b + (df['GEN12_ECNL'] * cnl_scalar_b / average_life) - ((df['GEN12_ECNL'] / cnl_scalar_b) * late_fee)
	theoretical_revenue_c = (equity_intercept + equity_slope * df['GEN12_ECNL'] * cnl_scalar_c) * roe + (1 - (equity_intercept + equity_slope * df['GEN12_ECNL'] * cnl_scalar_c)) * securitization + opex_c + (df['GEN12_ECNL'] * cnl_scalar_c / average_life) - ((df['GEN12_ECNL'] / cnl_scalar_c) * late_fee)
	theoretical_revenue_d = (equity_intercept + equity_slope * df['GEN12_ECNL'] * cnl_scalar_d) * roe + (1 - (equity_intercept + equity_slope * df['GEN12_ECNL'] * cnl_scalar_d)) * securitization + opex_d + (df['GEN12_ECNL'] * cnl_scalar_d / average_life) - ((df['GEN12_ECNL'] / cnl_scalar_d) * late_fee)
	# implement the calculated columns
	df.insert(0, 'GEN12_Theo_Rev','')
	for i in df['Tier']:
		if i == 'A1':
			df['GEN12_Theo_Rev'] = theoretical_revenue_a1
		elif i == 'A':
			df['GEN12_Theo_Rev'] = theoretical_revenue_a
		elif i == 'B':
			df['GEN12_Theo_Rev'] = theoretical_revenue_b
		elif i == 'C':
			df['GEN12_Theo_Rev'] = theoretical_revenue_c
		elif i == 'D':
			df['GEN12_Theo_Rev'] = theoretical_revenue_d
		else:
			pass
	# add the actual rev and rev diff
	df['GEN12_Theo_Rev'] = df['GEN12_Theo_Rev']*100
	df.insert(1, 'Actual_Rev','')
	df['Actual_Rev'] = df['OriginalInterestRate'] + ((df['mnyDiscount'] - df['mnyReserve']) / df['AmtFinanced'])/2.3
	df['Actual_Rev'] = df['Actual_Rev']*100
	df.insert(2, 'Rev_Diff','')
	df['Rev_Diff'] = df['Actual_Rev'] - df['GEN12_Theo_Rev']
	df['Rev_Diff'] = df['Rev_Diff']
	df = df.sort_values(by=['GEN12_Theo_Rev'], ascending=True)

	df.to_csv('./static/tables/df_daily_originations.csv', index=False)
	
	return df 

@application.route('/')
def index():
	# Default values
	opex_a1 = 0.0564
	opex_a = 0.0603
	opex_b = 0.0639
	opex_c = 0.0639
	opex_d = 0.0639
	roe = 0.275
	cnl_scalar_a1 = 0.8039
	cnl_scalar_a = 0.8039
	cnl_scalar_b = 0.8039
	cnl_scalar_c = 0.8039
	cnl_scalar_d = 0.8039
	equity_slope = 0.59
	securitization = 0.07
	late_fee = 0.0042
	equity_intercept = 0.0807
	average_life = 2.3

	# Calculate dataframe with default values
	df = calculate_dataframe(opex_a1, opex_a, opex_b, opex_c, opex_d, roe, cnl_scalar_a1, cnl_scalar_a, cnl_scalar_b, cnl_scalar_c, cnl_scalar_d, equity_slope, securitization, late_fee, equity_intercept, average_life)
	df_html = create_sortable_table(df=df)

	return render_template('index.html', df_theo_rev=df_html, dtm_now=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'))

@application.route('/update_values', methods=['POST'])
def update_values():
	# Get values from input field
	opex_a1 = float(request.form['opex_a1'])
	opex_a = float(request.form['opex_a'])
	opex_b = float(request.form['opex_b'])
	opex_c = float(request.form['opex_c'])
	opex_d = float(request.form['opex_d'])
	roe = float(request.form['roe'])
	cnl_scalar_a1 = float(request.form['cnl_scalar_a1'])
	cnl_scalar_a = float(request.form['cnl_scalar_a'])
	cnl_scalar_b = float(request.form['cnl_scalar_b'])
	cnl_scalar_c = float(request.form['cnl_scalar_c'])
	cnl_scalar_d = float(request.form['cnl_scalar_d'])
	equity_slope = float(request.form['equity_slope'])
	securitization = float(request.form['securitization'])
	late_fee = float(request.form['late_fee'])
	equity_intercept = float(request.form['equity_intercept'])
	average_life = float(request.form['average_life'])

	# Calculate dataframe with new values
	df = calculate_dataframe(opex_a1, opex_a, opex_b, opex_c, opex_d, roe, cnl_scalar_a1, cnl_scalar_a, cnl_scalar_b, cnl_scalar_c, cnl_scalar_d, equity_slope, securitization, late_fee, equity_intercept, average_life)
	df_html = create_sortable_table(df=df)

	# #logging due to ajax issues
	# print('Generated table html:', df_html)

	dict_output = {
		'df_theo_rev': df_html
	}

	return jsonify(dict_output)

# download csvs
@application.route('/download_excel')
def download_excel():
	# specify the xlsx filename to be downloaded
	excel_file = './static/tables/df_daily_originations.csv'
	# send the file as a download attachment
	return send_file(excel_file, as_attachment=True)

# home page
@application.route('/', methods=['GET','POST'])
def show_home_page():
	# get current dt
	dtm_now = dt.now()

	# # read theoretical revenue table
	# str_filename = 'df_theo_rev.csv'
	# str_local_path = f'./static/tables/{str_filename}'
	# df = pd.read_csv(str_local_path)

	# # convert theo rev df to html
	# df_theo_rev = create_static_table(df=df)

	# # read table
	# str_filename = 'df_apps_per_day.gzip'
	# str_local_path = f'./static/tables/{str_filename}'
	# df = read_my_gzip_file(str_local_path) # df = ...

	# # convert to html (static)
	# df_html = create_static_table(df=df)

	# # pie charts plotly
	# fig = make_subplots(rows=1, cols=2, specs=[[{'type':'pie'}, {'type':'pie'}]])
	# fig.add_trace(go.Pie(
	# 	values=[32.50, 37.31, 8.58, 21.60],
	# 	labels=['Auto Decline', 'Gen 11 Model Decline','Policy Decline', 'Gen 11 Approval'],
	# 	domain=dict(x=[0, 0.5]),
	# 	name='Gen 11'),
	# 	row=1, col=1)
	# fig.add_trace(go.Pie(
	# 	values=[32.50, 45.18, 8.58, 13.74],
	# 	labels=['Auto Decline', 'Gen 12 Model Decline','Policy Decline', 'Gen 12 Approval'],
	# 	domain=dict(x=[0.5, 1.0]),
	# 	name='Gen 12'),
	# 	row=1, col=2)
	# fig.update_layout(title='Decline Reason and Approval Rate by Model')
	# graphJSON_pie_charts = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	# # initialize class for plotting app's
	# cls_plot_applications = PlotApplications(df=df)
	# # create plot
	# str_filename = 'df_plot.png'
	# str_local_path = f'./static/plots/{str_filename}'
	# cls_plot_applications.plot_applications(
	# 	str_local_path=str_local_path,
	# 	flt_ylim_buffer=1.1,
	# )
	# cls_plot_applications = PlotApplications(df=df)
	# str_filename = 'mean_ecnl.png'
	# str_local_path = f'./static/plots/{str_filename}'
	# cls_plot_applications.plot_ecnl(
	# 	str_local_path=str_local_path
	# )

	# # plotly example============================
	# str_filename = 'df_plotly.gzip'
	# str_local_path = f'./static/tables/{str_filename}'
	# df = read_my_gzip_file(str_local_path)

	# fig = go.Figure()
	# fig.add_trace(go.Bar(x=df['Date'], y=df['Gen 11 ECNL'], name='Gen 11 ECNL'))
	# fig.add_trace(go.Bar(x=df['Date'], y=df['Gen 12 ECNL'], name='Gen 12 ECNL'))
	# fig.update_layout(barmode='group')

	# fig.update_layout(
	# 	title='ECNL per day'
	# 	)

	# fig.update_xaxes(type='category')

	# # make json
	# graphJSON_ecnl_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	##################################################

	# # Tier Thresholds
	# str_filename = 'df_thresholds.csv'
	# str_local_path = f'./static/tables/{str_filename}'
	# df = pd.read_csv(str_local_path)
	# df_thresholds = df.to_html(index=False, header='true', justify='left')


	# # Tier Proportions
	# str_filename = 'df_tiers.csv'
	# str_local_path = f'./static/tables/{str_filename}'
	# df = pd.read_csv(str_local_path)
	# df_tiers = df.to_html(index=False, header='true', justify='left')


	# render index.html
	return render_template(
		'index.html',
		# df_theo_rev=df_theo_rev,
		dtm_now=dtm_now,
		# df_html=df_html,
		# graphJSON_pie_charts=graphJSON_pie_charts,
		# graphJSON_ecnl_plot=graphJSON_ecnl_plot,
		# df_thresholds=df_thresholds,
		# df_tiers=df_tiers,
	)

	


# run app		
if __name__ == '__main__':
	application.run(host="0.0.0.0", debug=True)