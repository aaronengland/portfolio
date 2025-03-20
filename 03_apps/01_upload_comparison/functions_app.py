import pandas as pd
import numpy as np
import json

# download from s3
def download_from_s3(cls_client, str_local_path, str_bucket_path, str_project):
	# download file
	cls_client.download_file(
		str_project, 
		str_bucket_path, 
		str_local_path,
	)

# static table
def create_static_table(df):
	df = df.to_html(index=False, header='true', justify='left')
	return df

# df to sortable table
def create_sortable_table(df, index_bl=False):
	df_html = df.to_html(
		classes='display',
		escape=False,
		index=index_bl,
		justify='left',
		float_format='{:.3f}'.format
	)
	return df_html