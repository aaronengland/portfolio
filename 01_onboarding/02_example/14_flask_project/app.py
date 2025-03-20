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

#Home page
@application.route('/', methods=['GET','POST'])																#HOME PAGE
def show_home_page():
	dtm_now = dt.datetime.now()
	int_year_today = dtm_now.year

	return render_template(
		'index.html',
		dtm_now=dtm_now
		)


@application.route('/python-sql_page')
def pythonsql_page():


	return render_template(
		'python-sql_page.html')

@application.route('/aws_page')
def aws_page():

	return render_template(
		'aws_page.html')	


# run app		
if __name__ == '__main__':
	application.run(host="0.0.0.0", debug=True)