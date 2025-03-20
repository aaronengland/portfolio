#!/usr/bin/env python
# coding: utf-8

# # Set up

# ## Load libraries

# In[1]:


import numpy as np
import pandas as pd
import seaborn as sns; sns.set()
from matplotlib import pyplot as plt

# Check
## Get run date
import datetime
## Get URIs
import awswrangler as wr
## Clean text
import string


# ## Declare constants

# In[2]:


# Check
## Get data URIs
data_uri_prefix_sr = 's3://20231010-gen-xii/01_ad/01_data_prep/05_leaky_features/04_write_dfs'
## Get preprocessor URIs
preprocessor_uri_prefix_sr = 's3://20231010-gen-xii/01_ad/02_model/00_preprocessing/01_create_preprocessor'


# # Check

# ## Get run date

# In[3]:


str(datetime.datetime.now())


# ## Get data URIs

# In[4]:


data_uris_ss = pd.Series(data=wr.s3.list_objects(path=data_uri_prefix_sr))

print(*data_uris_ss, sep='\n')


# ## Get URI

# In[5]:


data_uri_sr = (
    data_uris_ss
    .loc[data_uris_ss.str.contains(pat='train') & data_uris_ss.str.contains(pat='raw')]
    .squeeze())

data_uri_sr


# ## Read in data

# In[6]:


X_train = pd.read_parquet(path=data_uri_sr)

X_train.info()
X_train


# ## Split into target vector and feature matrix

# In[7]:


print(f'Shape: {X_train.shape}')

target_sr = 'target'
y_train = X_train.pop(item=target_sr)

print(f'Shape: {X_train.shape}')


# ## Get preprocessor URIs

# In[8]:


preprocessor_uris_ss = pd.Series(data=wr.s3.list_objects(path=preprocessor_uri_prefix_sr))

print(*preprocessor_uris_ss, sep='\n')


# ## Copy

# In[9]:


for preprocessor_uri_sr in preprocessor_uris_ss:
    get_ipython().system('aws s3 cp $preprocessor_uri_sr .')


# ## Load module

# In[10]:


import preprocessing


# ## Get URI

# In[11]:


preprocessor_uri_sr = (
    preprocessor_uris_ss
    .loc[preprocessor_uris_ss.str.contains(pat='pkl')]
    .squeeze())

preprocessor_uri_sr


# ## Read in preprocessor

# In[12]:


pm = pd.read_pickle(filepath_or_buffer=preprocessor_uri_sr)

pm


# ## Get steps

# In[13]:


print(*map(lambda x: x.__class__.__name__, pm.list_transformers), sep='\n')


# ## Test replace NaNs

# ### Does it do anything?

# In[14]:


tmp = pm.list_transformers[0]
to_replace_lt = ['None', None, 'NaN', 'nan', '']

print(f'Before: {X_train.map(func=lambda x: x in to_replace_lt).sum().sum():,}')

X_train = tmp.transform(X=X_train)

print(f'After: {X_train.map(func=lambda x: x in to_replace_lt).sum().sum():,}')


# ### Would it do anything?

# In[15]:


size_te = (2**3, 2**2)
test_df = pd.DataFrame(data=np.random.choice(a=to_replace_lt, size=size_te))

print(f'Before: {test_df.map(func=lambda x: x in to_replace_lt).sum().sum():,}')
display(test_df)

test_df = tmp.transform(X=test_df)

print(f'After: {test_df.map(func=lambda x: x in to_replace_lt).sum().sum():,}')
display(test_df)


# ## Test replace booleans

# ### Does it do anything?

# In[16]:


tmp = pm.list_transformers[1]
to_replace_dt = {
    True: 1,
    False: 0,
    'True': 1,
    'False': 0,
    '0': 0,
    '1': 1}
to_replace_lt = list(to_replace_dt.keys())

print(f'Before: {X_train.map(func=lambda x: x in to_replace_lt).sum().sum():,}')

X_train = tmp.transform(X=X_train)

print(f'After: {X_train.map(func=lambda x: x in to_replace_lt).sum().sum():,}')


# ### Would it do anything?

# In[17]:


test_df = pd.DataFrame(data=np.random.choice(a=to_replace_lt, size=size_te))

print(f'Before: {test_df.map(func=lambda x: x in to_replace_lt).sum().sum():,}')
display(test_df)

test_df = tmp.transform(X=test_df)

print(f'After: {test_df.map(func=lambda x: x in to_replace_lt).sum().sum():,}')
display(test_df)


# ## Test set data types

# ### Fit

# In[18]:


tmp = pm.list_transformers[2]

tmp.fit(X=X_train)


# ### Does it do anything?

# In[19]:


print(f'Before:', X_train.dtypes.value_counts(), sep='\n')

X_train = tmp.transform(X=X_train)

print(f'Before:', X_train.dtypes.value_counts(), sep='\n')


# ### Would it do anything?

# In[20]:


test_df = X_train.copy().astype(dtype=str)

print(f'Before:', test_df.dtypes.value_counts(), sep='\n')

test_df = tmp.transform(X=test_df)

print(f'Before:', test_df.dtypes.value_counts(), sep='\n')


# ## Test clean text

# ### Does it do anything?

# In[21]:


tmp = pm.list_transformers[3]
to_replace_lt = list(string.ascii_uppercase + ' ')

print(f'Before: {X_train.map(func=lambda x: x in to_replace_lt).sum().sum():,}')

X_train = tmp.transform(X=X_train)

print(f'After: {X_train.map(func=lambda x: x in to_replace_lt).sum().sum():,}')


# ### Would it do anything?

# In[22]:


test_df = pd.DataFrame(
    data=np.random.choice(a=list('ABC') + [' A ', 'A B'], size=size_te),
    columns=tmp.list_cols[:size_te[1]])

print(f'Before: {test_df.map(func=lambda x: x in to_replace_lt).sum().sum():,}')
display(pd.concat(objs=[test_df, test_df.map(func=len)], axis=1))

test_df = tmp.transform(X=test_df)

print(f'After: {test_df.map(func=lambda x: x in to_replace_lt).sum().sum():,}')
display(pd.concat(objs=[test_df, test_df.map(func=len)], axis=1))


# ## Test inflator

# ### Does it do anything?

# In[23]:


tmp = pm.list_transformers[4]
columns_lt = X_train.columns.intersection(other=tmp.list_cols)

print('Before:')
display(X_train.groupby(by=X_train[tmp.str_datecol].dt.year)[columns_lt].max().T)

X_train = tmp.transform(X=X_train)

print(pd.Series(data=tmp.dict_inflation_rate))
print('After:')
display(X_train.groupby(by=X_train[tmp.str_datecol].dt.year)[columns_lt].max().T)


# ## Test inflator

# ### Does it do anything?

# In[24]:


tmp = pm.list_transformers[5]
columns_lt = X_train.columns.intersection(other=tmp.list_cols)

print('Before:')
display(X_train.groupby(by=X_train[tmp.str_datecol].dt.year)[columns_lt].max().T)

X_train = tmp.transform(X=X_train)

print(pd.Series(data=tmp.dict_inflation_rate))
print('After:')
display(X_train.groupby(by=X_train[tmp.str_datecol].dt.year)[columns_lt].max().T)


# ## Test clip values

# ### Does it do anything?

# In[25]:


tmp = pm.list_transformers[6]
columns_lt = X_train.columns.intersection(other=tmp.list_cols)

print('Before:', X_train[columns_lt].agg(func=['min', 'max']).T.sort_values(by=['min', 'max']), sep='\n')

X_train = tmp.transform(X=X_train)

print('After:', X_train[columns_lt].agg(func=['min', 'max']).T.sort_values(by=['min', 'max']), sep='\n')


# ## Test clip values

# ### Does it do anything?

# In[26]:


tmp = pm.list_transformers[7]
columns_lt = X_train.columns.intersection(other=tmp.list_cols)

print('After:', X_train[columns_lt].agg(func=['min', 'max']).T.sort_values(by=['min', 'max']), sep='\n')

X_train = tmp.transform(X=X_train)

print('After:', X_train[columns_lt].agg(func=['min', 'max']).T.sort_values(by=['min', 'max']), sep='\n')


# ## Test custom imputer

# ### Does it do anything?

# In[27]:


tmp = pm.list_transformers[8]
imputation_dt = {
    column_sr: value_ft 
    for column_sr, value_ft in tmp.dict_imputation.items() 
    if column_sr in X_train.columns}

print('Before:')
for column_sr, value_ft in imputation_dt.items():
    print(X_train[column_sr].value_counts().head(), end='\n' + '-' * int(8e1))

X_train = tmp.transform(X=X_train)

print('=' * int(8e1), 'After:', sep='\n')
for column_sr, value_ft in imputation_dt.items():
    print(X_train[column_sr].value_counts().head(), end='\n' + '-' * int(8e1))


# ### Would it do anything?

# In[28]:


imputation_dt = tmp.dict_imputation
test_df = pd.DataFrame(data={key_sr: np.nan for key_sr in imputation_dt.keys()}, index=[0])

print('Before:')
for column_sr, value_ft in imputation_dt.items():
    print(test_df[column_sr].value_counts().head(), end='\n' + '-' * int(8e1))

test_df = tmp.transform(X=test_df)

print('=' * int(8e1), 'After:', sep='\n')
for column_sr, value_ft in imputation_dt.items():
    print(test_df[column_sr].value_counts().head(), end='\n' + '-' * int(8e1))


# ## Test imputer

# ### Does it do anything?

# In[29]:


tmp = pm.list_transformers[9]

print(f'Before: Zeros: {(X_train == 0).sum().sum():,} | Missing values: {X_train.isna().sum().sum():,}')

X_train = tmp.transform(X=X_train)

print(f'After: Zeros: {(X_train == 0).sum().sum():,} | Missing values: {X_train.isna().sum().sum():,}')


# ## Test feature value replacer

# ### Does it do anything?

# In[30]:


tmp = pm.list_transformers[10]
to_replace_dt = {
    key_sr: list(value_dt.keys()) + list(value_dt.values())
    for key_sr, value_dt in tmp.dict_value_replace.items() 
    if key_sr in X_train.columns}

print('Before:')
for column_sr, values_lt in to_replace_dt.items():
    value_counts_ss = X_train[column_sr].value_counts()
    print(value_counts_ss[value_counts_ss.index.isin(values=values_lt)], end='\n' + '-' * int(8e1))

X_train = tmp.transform(X=X_train)

print('=' * int(8e1), 'After:', sep='\n')
for column_sr, values_lt in to_replace_dt.items():
    value_counts_ss = X_train[column_sr].value_counts()
    print(value_counts_ss[value_counts_ss.index.isin(values=values_lt)], end='\n' + '-' * int(8e1))


# ## Test date features

# ### Does it do anything?

# In[31]:


tmp = pm.list_transformers[11]

print('Before:')
display(X_train.filter(like='applicationdate__app').head())

X_train = tmp.transform(X=X_train)

print('After:')
display(X_train.filter(like='applicationdate__app').head())


# ## Test round binning

# ### Does it do anything?

# In[32]:


tmp = pm.list_transformers[12]
columns_lt = list(tmp.dict_round.keys())

print('Before:')
display(X_train[columns_lt].head())

X_train = tmp.transform(X=X_train)

print('After:')
display(X_train[columns_lt].head())


# ## Test feature engineering

# ### Does it do anything?

# In[33]:


tmp = pm.list_transformers[13]

print('Before:')
display(X_train.filter(like='ENG'))

X_train = tmp.transform(X=X_train)

print('After:')
display(X_train.filter(like='ENG'))


# ## Test replace inf

# ### Does it do anything?

# In[34]:


tmp = pm.list_transformers[14]

print(f'Before: {X_train.map(func=lambda x: x in [np.inf, -np.inf]).sum().sum():,}')

X_train = tmp.transform(X=X_train)

print(f'After: {X_train.map(func=lambda x: x in [np.inf, -np.inf]).sum().sum():,}')


# ## Test imputer

# ### Does it do anything?

# In[35]:


tmp = pm.list_transformers[15]

print(f'Before: Zeros: {(X_train == 0).sum().sum():,} | Missing values: {X_train.isna().sum().sum():,}')

X_train = tmp.transform(X=X_train)

print(f'After: Zeros: {(X_train == 0).sum().sum():,} | Missing values: {X_train.isna().sum().sum():,}')


# ## Test term mapper

# ### Does it do anything?

# In[36]:


tmp = pm.list_transformers[16]
term_sr = 'intterm__app'

print(f'Before: {X_train[term_sr].value_counts()}')

X_train = tmp.transform(X=X_train)

print(f'After: {X_train[term_sr].value_counts()}')


# ## Would it do anything?

# In[37]:


test_df = pd.DataFrame(data={term_sr: [None, -1, 0] + list(range(6, 80, 6))})

test_df.assign(new_term = lambda x: x[term_sr].apply(func=preprocessing.custom_mapping_term))


# ## Test PTI mapper

# ### Does it do anything?

# In[38]:


tmp = pm.list_transformers[17]
pti_sr = 'ENG-payment_to_income'

print('Before:')
with pd.option_context('display.max_rows', None):
    display(X_train[pti_sr].round(decimals=2).value_counts().sort_index())

X_train = tmp.transform(X=X_train)

print('After:')
with pd.option_context('display.max_rows', None):
    display(X_train[pti_sr].round(decimals=2).value_counts().sort_index())


# ## Would it do anything?

# In[39]:


test_df = pd.DataFrame(data={pti_sr: [None] + np.arange(start=-1e-2, stop=2e-1, step=1e-2).tolist()})

test_df.assign(new_term = lambda x: x[pti_sr].apply(func=preprocessing.custom_mapping_pti))


# ## Test round binning

# ### Does it do anything?

# In[40]:


tmp = pm.list_transformers[18]
columns_lt = X_train.columns.intersection(other=list(tmp.dict_round.keys())).tolist()

print('Before:')
display(X_train[columns_lt].head())

X_train = tmp.transform(X=X_train)

print('After:')
display(X_train[columns_lt].head())

