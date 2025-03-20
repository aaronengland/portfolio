
import numpy as np
import pandas as pd
# import seaborn as sns; sns.set()
# from matplotlib import pyplot as plt

import pathlib

import argparse
import logging

if __name__ == '__main__':
    # Configure logger
    logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.INFO)
    logging.info(msg='Configure logger')
    
    # Parse arguments
    ap = argparse.ArgumentParser()
    # Read in data
    ap.add_argument('--file_ph', type=str)
    # Sample
    ap.add_argument('--frac_ft', type=float)
    args_ns, _ = ap.parse_known_args()
    logging.info(msg='Parse arguments')
    
    # Assign
    # Read in data
    file_ph = pathlib.Path(args_ns.file_ph)
    # Sample
    frac_ft = args_ns.frac_ft
    logging.info(msg='Assign')
    
    # Read in data
    base_directory_sr = '/opt/ml/processing'
    input_directory_sr = f'{base_directory_sr}/input'
    split_sr = file_ph.stem.split('_')[1]
    df = pd.read_parquet(path=f'{input_directory_sr}/{split_sr}/{file_ph}')
    logging.info(msg='Read in data')
    
    # Sample
    print(f'Shape: {df.shape}')
    df = df.sample(frac=frac_ft, random_state=0)
    print(f'Shape: {df.shape}')
    logging.info(msg='Sample')
    
    # Write
    output_directory_sr = f'{base_directory_sr}/output'
    file_sr = f'{file_ph.stem}_raw_{str(int(frac_ft * 1e2))}{file_ph.suffix}'
    df.to_parquet(path=f'{output_directory_sr}/{split_sr}/{file_sr}', compression='gzip')
    logging.info(msg='Write')
