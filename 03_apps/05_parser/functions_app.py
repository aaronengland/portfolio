import pandas as pd
import numpy as np 
import json
import pickle
import plotly
import plotly.express as px
from plotly.subplots import make_subplots

# static table
def create_static_table(df):
	df = df.to_html(index=False, header='true', justify='left')
	return df

# sortable table
def create_sortable_table(df):
	df = df.to_html(classes='display', escape=False, index=False)
	return df

# read file
def read_file(str_local_path):
	try:
		dict_json_request = json.load(open(str_local_path))['request']
	except KeyError:
		dict_json_request = json.load(open(str_local_path))
	return dict_json_request

# load parser
def load_parser(str_local_path):
	cls_parse_payload = pickle.load(open(str_local_path, 'rb'))
	return cls_parse_payload

list_cols_start = [
	'applicationdate__app',
	'bigaccountid__app',
	'bitdebtor__app',
]

# list cols drop
list_cols_drop_raw = [
	'str_institution__tu_pmthx',
	'str_dtm_opened__tu_pmthx',
	'str_dtm_closed__tu_pmthx',
	'str_closed_indicator__tu_pmthx',
	'flt_current_balance__tu_pmthx',
	'flt_payment__tu_pmthx',
	'flt_past_due__tu_pmthx',
	'flt_30_dpd__tu_pmthx',
	'flt_60_dpd__tu_pmthx',
	'flt_90_dpd__tu_pmthx',
	'str_loan_type__tu_pmthx',
	'str_pmt_hx__tu_pmthx',
	'str_dtm_most_recent_pmt__tu_pmthx',
	'str_method__tu_pmthx',
	'auto__tu_pmthx',
	'pmt_hx',
	'list_institutions',
]

# list drop after pricing
list_cols_drop_pricing = [
	'tier',
	'current_apr',
	'roe_required',
	'raw_discount',
	'operating_expenses',
	'reserve',
	'equity',
	'profit',
	'discount',
	'late_fee',
	'funding_cost',
	'adjusted_ecnl',
	'expected_losses',
	'buy_rate',
	'raw_apr',
	'raw_discount_adjustment',
	'raw_apr_adjustment',
	'rate_cap_handicap',
	'additional_discount_needed',
]

# list of chime tags
list_str_inst = [
	# from ben: 2025-02-21
	'CURRENT',
	'SELF',
	# key words
	'CHIME-STRIDE',
	'CHIMEFINAL',
	# from dustin: 2025-02-24
	'SELF FIN',
	'SELF/LEAD',
	'SELFINC/LEAD',
	'SBNASELFLNDR',
	'SBNA SELF',
	'CHIME',
	'CLEO',
	'CLEO AI',
	'VARO',
	'ATLAS',
	'ATLCAPBKSELF',
	'POSSIBLE',
	'POSSIBLE FIN',
	'KIKOFF',
	'SUPER.COM',
	'STEP',
	'STEP MOBILE',
	'BRIGHT',
	'BRIGHT BLDR',
	'FIG TECH INC',
	'SELF/RENT',
	'SELFBILLSE',
	'PROGRESSRES',
	'FLEX',
	'FLEXFINANCE',
]

# feature contribution plot
def plot_feature_contribution(df, str_filename):
	# copy
	df_tmp = df.copy()
	# see if Codebtor in df
	if 'Codebtor' in list(df_tmp.columns):
		bool_codebtor = True 
	else:
		bool_codebtor = False
	# debtor
	df_tmp['Debtor'] = df_tmp['Debtor'].round(2)
	df_tmp['debtor_color'] = df_tmp['Debtor Contribution'].apply(
		lambda x: 'red' if x > 0 else 'green',
	)
	# codebtor
	if bool_codebtor:
		df_tmp['Codebtor'] = df_tmp['Codebtor'].round(2)
		df_tmp['codebtor_color'] = df_tmp['Codebtor Contribution'].apply(
			lambda x: 'red' if x > 0 else 'green',
		)
	else:
		pass
	# plot debtor
	df_tmp.sort_values(by='Debtor Contribution', ascending=True, inplace=True)
	fig1 = px.bar(
		df_tmp,
		x='Feature',
		y='Debtor Contribution',
		title=f'Debtor Contribution by Feature ({str_filename})',
		labels={
			'Debtor Contribution': 'Debtor Contribution',
			'Feature': 'Feature',
		},
		text=df_tmp['Debtor'],
		hover_data={'Feature': True, 'Debtor': True, 'Description': True}
	)
	fig1.update_layout(
		title_x=0.5,
		height=700,
	)
	fig1.update_traces(
		marker_color=list(df_tmp['debtor_color']),
		textangle=90,
	)

	# if there is a codebtor
	if bool_codebtor:
		df_tmp.sort_values(by='Codebtor Contribution', ascending=True, inplace=True)
		fig2 = px.bar(
			df_tmp,
			x='Feature',
			y='Codebtor Contribution',
			title=f'Codebtor Contribution by Feature ({str_filename})',
			labels={
				'Codebtor Contribution': 'Codebtor Contribution',
				'Feature': 'Feature',
			},
			text=df_tmp['Codebtor'],
			hover_data={'Feature': True, 'Codebtor': True, 'Description': True}
		)
		fig2.update_layout(
			title_x=0.5,
			height=700,
		)
		fig2.update_traces(
			marker_color=list(df_tmp['codebtor_color']),
			textangle=90,
		)

	# if there is a codebtor
	if bool_codebtor:
		fig = make_subplots(
			rows=2,
			cols=1,
			shared_xaxes=False,
			subplot_titles=[f'Debtor Contribution ({str_filename})', f'Codebtor Contribution ({str_filename})'],
			vertical_spacing=0.25,
		)
		# add traces for fig1
		for trace in fig1.data:
			fig.add_trace(trace, row=1, col=1)
		# add traces for fig2
		for trace in fig2.data:
			fig.add_trace(trace, row=2, col=1)
		# update layout
		fig.update_layout(
            height=1650,
            showlegend=False,
        )
		# make json
		graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
	else:
		# make json
		graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
	# return
	return graphJSON