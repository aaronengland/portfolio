# functions

# id all NaN
def find_all_nan_columns(df):
	# sample
	df_tmp = df.sample(
		frac=0.01, 
		random_state=42,
	)
	ser_isnull = df_tmp.isnull().mean()
	ser_isnull = ser_isnull[ser_isnull==1.0]
	list_cols = list(ser_isnull.index)
	# full
	ser_isnull = df[list_cols].isnull().mean()
	ser_isnull = ser_isnull[ser_isnull==1.0]
	list_cols = list(ser_isnull.index)
	return list_cols

# id no var cols
def find_no_variance_columns(df):
	# sample
	df_tmp = df.sample(
		frac=0.01, 
		random_state=42,
	)
	ser_nunique = df_tmp.nunique()
	ser_nunique = ser_nunique[ser_nunique==1]
	list_cols = list(ser_nunique.index)
	# full
	ser_nunique = df[list_cols].nunique()
	ser_nunique = ser_nunique[ser_nunique==1]
	list_cols = list(ser_nunique.index)
	return list_cols

# get redundant features
def find_redundant_columns(df):
	# sample
	df_tmp = df.sample(
		frac=0.01, 
		random_state=42,
	)
	# transpose the dataframe and check for duplicate rows
	ser_duplicates = df_tmp.T.duplicated() * 1
	ser_duplicates = ser_duplicates[ser_duplicates==1]
	list_cols_a = list(ser_duplicates.index)

	list_cols = []
	a = 0
	for a, col_a in enumerate(list_cols_a):
		# add 1 to a
		a += 1
		if col_a not in list_cols:
			# create new list
			list_cols_b = list_cols_a[a:]
			for col_b in list_cols_b:
				if df[col_a].equals(df[col_b]):
					list_cols.append(col_b)   
		else:
		    pass
	# return
	return list_cols