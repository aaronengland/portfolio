# app
from flask import Flask, render_template
import datetime as dt

# instantiate app
application = Flask(__name__)

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

# run app		
if __name__ == '__main__':
	application.run(host='0.0.0.0', debug=False)