#functions
import pandas as pd
from pprint import pprint

#check columns about ID and date
def check_columns(list_cols):
    #check ID columns
    list_id_cols = [col for col in list_cols if 'id' in col.lower()]
    print(f'There are {len(list_id_cols)} columns containing the string "id"')
    # show
    for a, col in enumerate(list_id_cols):
        print(f'{a+1} - {col}')
    print('')

    # check for date columns
    list_date_cols = []
    for col in list_cols:
        # check for date
        if ('date' in col.lower()) or ('dtm' in col.lower()) or ('dte' in col.lower()):
            list_date_cols.append(col)
        else:
            pass
    print(f'There are {len(list_date_cols)} columns containing the strings "date", "dtm", or "dte"')
    # show
    for a, col in enumerate(list_date_cols):
        print(f'{a+1} - {col}')
    print('')

    #check for score columns
    list_score_cols = [col for col in list_cols if 'score' in col.lower()]
    print(f'There are {len(list_score_cols)} columns containing the string "score"')
    # show
    for a, col in enumerate(list_score_cols):
        print(f'{a+1} - {col}')
    print('')

    #check for fund columns
    list_fund_cols = [col for col in list_cols if 'fund' in col.lower()]
    print(f'There are {len(list_fund_cols)} columns containing the string "fund"')
    # show
    for a, col in enumerate(list_fund_cols):
        print(f'{a+1} - {col}')
    print('')

    # return lists
    return list_id_cols, list_date_cols, list_score_cols, list_fund_cols
