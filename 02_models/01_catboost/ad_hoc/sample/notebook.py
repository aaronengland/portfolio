#!/usr/bin/env python
# coding: utf-8

# # Set up

# ## Load libraries

# In[1]:


import numpy as np
import pandas as pd
import seaborn as sns; sns.set()
from matplotlib import pyplot as plt

# Sample
## Get URIs
import awswrangler as wr
## Run
import pathlib
import sagemaker
from sagemaker import sklearn as srsn


# ## Declare constants

# In[2]:


# Sample
## Get files
data_uri_prefix_sr = 's3://20231010-gen-xii/01_ad/01_data_prep/05_leaky_features/04_write_dfs'
## Run
frac_ft = 1e-2


# # Sample

# ## Get URIs

# In[3]:


data_uris_ss = pd.Series(data=wr.s3.list_objects(path=data_uri_prefix_sr))

print(*data_uris_ss, sep='\n')


# ## Write script

# In[4]:


get_ipython().run_cell_magic('file', 'script.py', "\nimport numpy as np\nimport pandas as pd\n# import seaborn as sns; sns.set()\n# from matplotlib import pyplot as plt\n\nimport pathlib\n\nimport argparse\nimport logging\n\nif __name__ == '__main__':\n    # Configure logger\n    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.INFO)\n    logging.info(msg='Configure logger')\n    \n    # Parse arguments\n    ap = argparse.ArgumentParser()\n    # Read in data\n    ap.add_argument('--file_ph', type=str)\n    # Sample\n    ap.add_argument('--frac_ft', type=float)\n    args_ns, _ = ap.parse_known_args()\n    logging.info(msg='Parse arguments')\n    \n    # Assign\n    # Read in data\n    file_ph = pathlib.Path(args_ns.file_ph)\n    # Sample\n    frac_ft = args_ns.frac_ft\n    logging.info(msg='Assign')\n    \n    # Read in data\n    base_directory_sr = '/opt/ml/processing'\n    input_directory_sr = f'{base_directory_sr}/input'\n    split_sr = file_ph.stem.split('_')[1]\n    df = pd.read_parquet(path=f'{input_directory_sr}/{split_sr}/{file_ph}')\n    logging.info(msg='Read in data')\n    \n    # Sample\n    print(f'Shape: {df.shape}')\n    df = df.sample(frac=frac_ft, random_state=0)\n    print(f'Shape: {df.shape}')\n    logging.info(msg='Sample')\n    \n    # Write\n    output_directory_sr = f'{base_directory_sr}/output'\n    file_sr = f'{file_ph.stem}_raw_{str(int(frac_ft * 1e2))}{file_ph.suffix}'\n    df.to_parquet(path=f'{output_directory_sr}/{split_sr}/{file_sr}', compression='gzip')\n    logging.info(msg='Write')\n")


# ## Run

# In[5]:


sklp = srsn.SKLearnProcessor(
    framework_version='1.2-1', 
    role=sagemaker.get_execution_role(), 
    instance_count=1, 
    instance_type='ml.m5.4xlarge')
base_directory_sr = '/opt/ml/processing'
input_directory_sr = f'{base_directory_sr}/input'
output_directory_sr = f'{base_directory_sr}/output'

for index_it, data_uri_sr in enumerate(iterable=data_uris_ss):
    file_sr = pathlib.Path(data_uri_sr).name
    split_sr = file_sr.split('_')[1]
    sklp.run(
        code='script.py', 
        inputs=[sagemaker.processing.ProcessingInput(
            source=data_uri_sr, destination=f'{input_directory_sr}/{split_sr}')],
        outputs=[sagemaker.processing.ProcessingOutput(
            source=f'{output_directory_sr}/{split_sr}', destination=data_uri_prefix_sr)], 
        arguments=[
            # Read in data
            '--file_ph', file_sr,
            # Sample
            '--frac_ft', str(frac_ft)])


# ## Get URIs

# In[6]:


data_uris_ss = pd.Series(data=wr.s3.list_objects(path=data_uri_prefix_sr))

print(*data_uris_ss, sep='\n')

