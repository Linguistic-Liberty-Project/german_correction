import re
import pandas as pd

#open the xcel file (short version of one of our files here)
xls = pd.ExcelFile('/Users/lidiiamelnyk/Documents/Non_binary_small.xlsx')

#create a dictionary object with list names as keys and contents as pd dataframe as values
sheet_to_df_map = {}
i = 0
for sheet_name in xls.sheet_names:
    sheet_to_df_map[sheet_name] = xls.parse(sheet_name)

#transfer replies column to the matching (empty) cell in the comments column so that we can treat it all together
for key in sheet_to_df_map.keys():
    for i,row in sheet_to_df_map[key].iterrows():
      for m in str(row['Reply']).split('\n'):
        if m == 'nan':
            pass
        if m != 'nan':
            sheet_to_df_map[key].loc[i, 'Comment'] = m


for key in sheet_to_df_map.keys():
    for i,row in sheet_to_df_map[key].iterrows():
        for line in str(row['Comment']).split('/n'):
            URLless_string = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', line)
            URLless_string = URLless_string.replace('&quot;', '').replace('<br>', '')
            sheet_to_df_map[key].loc[i, 'Comment'] = URLless_string

import xlsxwriter
import os
filepath = '/Users/lidiiamelnyk/Documents/Non_binary_small_processed.xlsx'
def save_excel_sheet(df, filepath, sheetname, index=False):
    # Create file if it does not exist
    if not os.path.exists(filepath):
        df.to_excel(filepath, sheet_name=sheetname, index=index)

    # Otherwise, add a sheet. Overwrite if there exists one with the same name.
    else:
        with pd.ExcelWriter(filepath, engine='openpyxl', if_sheet_exists='replace', mode='a') as writer:
            df.to_excel(writer, sheet_name=sheetname, index=index)

for key in sheet_to_df_map.keys():
    save_excel_sheet(df = sheet_to_df_map[key], filepath = filepath, sheetname = key, index = False)