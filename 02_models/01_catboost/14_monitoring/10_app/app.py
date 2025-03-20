# app
from flask import Flask, request, render_template, Response, jsonify
import pandas as pd
import numpy as np
import os
import datetime as dt

try:
	from passwords import *
	bool_debug = True
except:
	bool_debug = False
	AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
	AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# instantiate app
app = Flask(__name__)

# take us to index.html
@app.route('/', methods=["GET","POST"])
def index():
	# get datetime
	int_year_now = dt.datetime.now().year

	# show index
	return render_template(
		'index.html',
		int_year_now=int_year_now,
	)

# run app		
if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=bool_debug)
