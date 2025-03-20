# app
from flask import Flask, render_template, Response, request, jsonify
import os
import json
import datetime as dt
import pandas as pd
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot
import plotly.io as pio
import plotly.express as px

# instantiate app
application = Flask(__name__)

# home page
@application.route('/', methods=['GET','POST'])																#HOME PAGE
def show_home_page():
	# prefix
	str_prefix = 'home'

	# current datetime
	dtm_now = dt.datetime.now()
	# get current year
	int_year_today = dtm_now.year

	# get the table
	str_filename = 'df_scores.gzip'
	str_local_path = f'./static/{str_prefix}/{str_filename}'
	df = pd.read_parquet(str_local_path)

	# get sample to improve performance
	df = df.sample(frac=0.01, random_state=42)

	# convert to html
	df_html_scores = df.to_html(classes='display', escape=False, index=False)

	#DEALER APPLICATION PIE CHART

	str_file_app = 'dealerapps.gzip'
	str_local_path_application = f'./notebooks/output/{str_file_app}'

	dfapp = pd.read_parquet(str_local_path_application)

	appgrp = px.pie(dfapp, names='strName', values='YTDApplicationcount', title='Dealer Applications',
		color_discrete_sequence=px.colors.sequential.RdBu)

	appgrp.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=15,
								marker=dict(line=dict(color='#000000', width=2)))

	appgroup_html = pio.to_html(appgrp, full_html=False)


	#DEALER APPROVED PIE CHART

	str_file_approved = 'dealerapproved.gzip'
	str_local_path_approved = f'./notebooks/output/{str_file_approved}'

	dfapproved = pd.read_parquet(str_local_path_approved)

	approvegrp = px.pie(dfapproved, names='strName', values='YTDApprovedCount', title='Dealer Approved',
		color_discrete_sequence=px.colors.sequential.RdBu)

	approvegrp.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=15,
								marker=dict(line=dict(color='#000000', width=2)))

	approvegroup_html = pio.to_html(approvegrp, full_html=False)


	#DEALER FUNDED PIE CHART

	str_file_fund = 'dealerfunded.gzip'
	str_local_path_funded = f'./notebooks/output/{str_file_fund}'

	dffunded = pd.read_parquet(str_local_path_funded)

	fundedgrp = px.pie(dffunded, names='strName', values='YTDFundedCount', title='Dealer Funded',
		color_discrete_sequence=px.colors.sequential.RdBu)

	fundedgrp.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=15,
								marker=dict(line=dict(color='#000000', width=2)))

	fundedgroup_html = pio.to_html(fundedgrp, full_html=False)
	

	# render index.html
	return render_template(
		'index.html',
		dtm_now=dtm_now,
		df_html_scores=df_html_scores,
		int_year_today=int_year_today,
		
	)
@application.route('/tiers_page')                                                          #TIERS PAGE 
def tiers_page():

	# TIER PIE CHART 2024
	
	str_prefix='home'

	color_map = {
		'A1': '#50C234',
		'A': '#6EE383',
		'B': '#6EE3C6',
		'C': '#6ED1E3',
		'D': '#6E96E3'
	}

	str_filename_tier1 = 'dftier2024.gzip'
	str_local_path_tier1 = f'./notebooks/output/{str_filename_tier1}'

	dftier = pd.read_parquet(str_local_path_tier1)
 
	figtiers2024 = px.pie(dftier, names='Tiers', values='Amount', color='Tiers',
		color_discrete_map=color_map)
	
	figtiers2024.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=15,
								marker=dict(line=dict(color='#000000', width=2)))
	
	figpie_html = pio.to_html(figtiers2024, full_html=False)

	# TIER PIE CHART 2023

	str_filename_tier2 = 'dftier2023.gzip'
	str_local_path_tier2 = f'./notebooks/output/{str_filename_tier2}'

	dftier2 = pd.read_parquet(str_local_path_tier2)

	figtiers2023 = px.pie(dftier2, names='Tiers', values='Amount', color='Tiers',
		color_discrete_map=color_map)

	figtiers2023.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=15,
								marker=dict(line=dict(color='#000000', width=2)))

	figpie2_html = pio.to_html(figtiers2023, full_html=False)

	# TIER PIE CHART 2022

	str_filename_tier3 = 'dftier2022.gzip'
	str_local_path_tier3 = f'./notebooks/output/{str_filename_tier3}'

	dftier3 = pd.read_parquet(str_local_path_tier3)

	figtiers2022 = px.pie(dftier3, names='Tiers', values='Amount', color='Tiers',
		color_discrete_map=color_map)

	figtiers2022.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=15,
								marker=dict(line=dict(color='#000000', width=2)))

	figpie3_html = pio.to_html(figtiers2022, full_html=False)

	# TIER PIR CHART 2021

	str_filename_tier4 = 'dftier2021.gzip'
	str_local_path_tier4 = f'./notebooks/output/{str_filename_tier4}'

	dftier4 = pd.read_parquet(str_local_path_tier4)

	figtiers2021 = px.pie(dftier4, names='Tiers', values='Amount', color='Tiers',
		color_discrete_map=color_map)

	figtiers2021.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=15,
								marker=dict(line=dict(color='#000000', width=2)))

	figpie4_html = pio.to_html(figtiers2021, full_html=False)

	# TIER PIE CHART 2020

	str_filename_tier5 = 'dftier2020.gzip'
	str_local_path_tier5 = f'./notebooks/output/{str_filename_tier5}'

	dftier5 = pd.read_parquet(str_local_path_tier5)

	figtiers2020 = px.pie(dftier5, names='Tiers', values='Amount', color='Tiers',
		color_discrete_map=color_map)

	figtiers2020.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=15,
								marker=dict(line=dict(color='#000000', width=2)))

	figpie5_html = pio.to_html(figtiers2020, full_html=False)

	# TIER PIE CHART 2020 - current

	str_filename_tier6 = 'dftier2020-current.gzip'
	str_local_path_tier6 = f'./notebooks/output/{str_filename_tier6}'

	dftier6 = pd.read_parquet(str_local_path_tier6)

	figtiers2020_current = px.pie(dftier6, names='Tiers', values='Amount', color='Tiers',
		color_discrete_map=color_map)

	figtiers2020_current.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=15,
								marker=dict(line=dict(color='#000000', width=2)))

	figpie6_html = pio.to_html(figtiers2020_current, full_html=False)

	# TIER BAR CHART

	dftierbar = pd.read_parquet(str_local_path_tier1)

	tierbar = px.bar(dftierbar, x='Tiers', y='Amount', title='',
		text_auto='.2s',
		color="Tiers",
		pattern_shape="Tiers", pattern_shape_sequence=['/','\\','x','+','.','.'],
		hover_data={'Tiers': True, 'Amount': True})

	tierbar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
	tierbar.update_layout(xaxis={'categoryorder':'total descending'})

	#Shapes for pattern fill ['', '/', '\\', 'x', '-', '|', '+', '.']
	
	interact_tierbar_html = pio.to_html(tierbar, full_html=False)

	# MAP OF FUNDED LOANS

	str_filename3 = 'dfstate.gzip'
	str_local_path3 = f'./static/{str_prefix}/{str_filename3}'

	dfstate = pd.read_parquet(str_local_path3)

	figmap = go.Figure(data=go.Choropleth(
		locations=dfstate['State'],
		z = dfstate['Amount'].astype(float),
		locationmode = 'USA-states',
		colorscale ='Reds',
		colorbar_title="Amount Per State",
		))

	figmap.update_layout(
		title_text='',
		geo=dict(
			scope='usa',
			projection=go.layout.geo.Projection(type = 'albers usa'),
			showlakes=True
			))

	figmap_html= pio.to_html(figmap, full_html=False)

	#TIERS OF LOANS BY STATE STACK BAR CHART

	str_filename4 = 'dfstackedbar.gzip'
	str_local_path4 = f'./static/{str_prefix}/{str_filename4}'

	dfstackedbar = pd.read_parquet(str_local_path4)

	dfstackedbar = dfstackedbar.sort_values(by='NumberOfTiers', ascending=False)

	stackedbar = px.bar(dfstackedbar, x='State', y='NumberOfTiers',
		color='Tier', color_discrete_map=color_map)

	stackedbar_html = pio.to_html(stackedbar, full_html=False)

	return render_template(
		'tiers_page.html',
		figpie_html=figpie_html,
		figpie2_html=figpie2_html,
		figpie3_html=figpie3_html,
		figpie4_html=figpie4_html,
		figpie5_html=figpie5_html,
		figpie6_html=figpie6_html,
		interact_tierbar_html=interact_tierbar_html,
		figmap_html=figmap_html,
		stackedbar_html=stackedbar_html
		)

@application.route('/dealer_page')																#DEALER PAGE
def dealer_page():

	#DEALER APPLICATION PIE CHART

	str_file_app = 'dealerapps.gzip'
	str_local_path_application = f'./notebooks/output/{str_file_app}'

	dfapp = pd.read_parquet(str_local_path_application)

	appgrp = px.pie(dfapp, names='strName', values='YTDApplicationcount', title='Dealer Applications',
		color_discrete_sequence=px.colors.sequential.RdBu)

	appgrp.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=15,
								marker=dict(line=dict(color='#000000', width=2)))

	appgroup_html = pio.to_html(appgrp, full_html=False)


	#DEALER APPROVED PIE CHART

	str_file_approved = 'dealerapproved.gzip'
	str_local_path_approved = f'./notebooks/output/{str_file_approved}'

	dfapproved = pd.read_parquet(str_local_path_approved)

	approvegrp = px.pie(dfapproved, names='strName', values='YTDApprovedCount', title='Dealer Approved',
		color_discrete_sequence=px.colors.sequential.RdBu)

	approvegrp.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=15,
								marker=dict(line=dict(color='#000000', width=2)))

	approvegroup_html = pio.to_html(approvegrp, full_html=False)


	#DEALER FUNDED PIE CHART

	str_file_fund = 'dealerfunded.gzip'
	str_local_path_funded = f'./notebooks/output/{str_file_fund}'

	dffunded = pd.read_parquet(str_local_path_funded)

	fundedgrp = px.pie(dffunded, names='strName', values='YTDFundedCount', title='Dealer Funded',
		color_discrete_sequence=px.colors.sequential.RdBu)

	fundedgrp.update_traces(hoverinfo='label+percent', textinfo='percent', textfont_size=15,
								marker=dict(line=dict(color='#000000', width=2)))

	fundedgroup_html = pio.to_html(fundedgrp, full_html=False)
	
	return render_template(
		'dealer_page.html',
		appgroup_html=appgroup_html,
		approvegroup_html=approvegroup_html,
		fundedgroup_html=fundedgroup_html)

@application.route('/gen_scores')																									# GEN SCORES PAGE
def gen_scores():

	# prefix
	str_prefix = 'home'


	# get the table
	str_filename = 'genscores2024.gzip'
	str_local_path = f'./notebooks/output/{str_filename}'
	df = pd.read_parquet(str_local_path)

	# get sample to improve performance
	df = df.sample(frac=0.01, random_state=42)

	# convert to html
	genscores_html = df.to_html(classes='display', escape=False, index=False)


	return render_template(
		'gen_scores.html',
		genscores_html=genscores_html) 

# run app		
if __name__ == '__main__':
	application.run(host="0.0.0.0", debug=True)