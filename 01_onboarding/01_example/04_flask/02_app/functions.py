# static table
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

def create_static_table(df):
	df = df.to_html(index=False, header='true', justify='left')
	return df

def read_my_gzip_file(str_local_path):
	df = pd.read_parquet(str_local_path)
	return df

# sortable table
def create_sortable_table(df):
	df = df.to_html(classes='display', escape=False, index=False)
	return df

class PlotApplications:
	def __init__(self, df):
		self.df = df
	
	def plot_applications(self, str_local_path, flt_ylim_buffer=1.1):
		# create blank plot
		fig, ax = plt.subplots(figsize=(12,5))
		# title the graph
		ax.set_title('Number of Applications per Day and Gen11/Gen12 Approval Rate by Date. \n Gen 11 = 21.50%; Gen 12 = 13.5%; N Days = 13, N Apps = 28072, AVG = 2159.38 apps/day')
		# x axis
		ax.set_xlabel('Date')
		# y axis
		ax.set_ylabel('Number of Applications')
		# set y-axis step
		ax.yaxis.set_major_locator(plt.MultipleLocator(500))
		# rotate xticks
		ax.set_xticklabels(self.df['Date'], rotation=90)
		# expand y range
		flt_min = 0.0
		flt_max = self.df['Applications'].max() * flt_ylim_buffer
		ax.set_ylim([flt_min, flt_max])
		# plot
		bars = ax.bar(self.df['Date'], self.df['Applications'])
		for bar in bars:
			height = bar.get_height()
			ax.annotate(f'{height:0.2f}',
			xy = (bar.get_x() + bar.get_width() / 2, height),
				xytext = (0,3), # 3 points of vertical label offset
				textcoords = "offset points",
				ha = 'center',
				va = 'bottom',
			)
		ax2 = plt.twinx()
		a = ax2.plot(self.df['Date'], self.df['Gen 11'], color='r')
		b = ax2.plot(self.df['Date'], self.df['Gen 12'], color='c')
		ax2.set_ylabel('Approval Rate')
		ax2.set_ylim(0.12, 0.24)
		ax2.yaxis.set_major_locator(plt.MultipleLocator(0.02))
		ax2.legend([a, b], ['Gen 11', 'Gen 12'], loc='upper left', fancybox=True, framealpha=1, shadow=True, borderpad=1)

		# save plot to self
		self.fig = fig 
		# save
		plt.savefig(
			str_local_path,
			bbox_inches='tight',
		)
	
	def plot_ecnl(self, str_local_path):
		# create plot
		fig, ax = plt.subplots(figsize=(13,4))
		#title graph
		ax.set_title('Mean ECNL / Day - Gen 11 and Gen 12')
		# x axis
		ax.set_xlabel('Date')
		# y axis
		ax.set_ylabel('Mean ECNL')
		#set y range
		ax.set_ylim(0, 0.475)
		#set y step
		#ax.yaxis.set_major_locator(plt.MajorLocator(0.1))
		# rotate x ticks
		ax.set_xticklabels(self.df['Date'],
			rotation=90,
		)
		#plot
		bar_width = 0.40
		#Gen11 = ax.bar(self.df['Date'], self.df['Gen 11 ECNL'], -0.20, color='b', label='Gen 11')
		#Gen12 = ax.bar(self.df['Date'], self.df['Gen 12 ECNL'], 0.20, color='r', label='Gen 12')
		df_temp = self.df[['Date', 'Gen 11 ECNL', 'Gen 12 ECNL']]
		df_temp.to_parquet(path='./static/tables/df_plotly.gzip', compression='gzip')
		self.df_temp = df_temp
		bars = self.df_temp.plot.bar(x='Date',
			y=['Gen 11 ECNL', 'Gen 12 ECNL'],
			figsize=(13,4),
			title='Mean ECNL / Day - Gen 11 and Gen 12 \n Overall Means: Gen 11 = 0.24; Gen 12 = 0.44',
		)
		#legend
		ax.legend()

		self.fig = fig 

		# save plot
		plt.savefig(
			str_local_path,
			bbox_inches='tight',
		)
		
