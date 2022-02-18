
import spacy
import de_core_news_sm
nlp_de = de_core_news_sm.load()

import pandas as pd

xls = pd.ExcelFile('/content/Non Binary.xlsx')

sheet_to_df_map = {}
i = 0
for sheet_name in xls.sheet_names:
    sheet_to_df_map[sheet_name] = xls.parse(sheet_name)


for key in sheet_to_df_map.keys():
  for i,row in sheet_to_df_map[key].iterrows():
    for m in str(row['Reply']).split('\n'):
      if m == 'nan':
        pass
      elif m != 'nan':
        sheet_to_df_map[key].loc[i, 'Comment'] = m


def lowercase_sentence_beginning(key):
    for i,row in sheet_to_df_map[key].iterrows():
      doc = nlp_de(row['Comment'])
      for sent in doc.sents:
        for word in sent:
          if word.pos_ != 'NOUN':
            word = str(word)
            sent = str(sent).replace(word, word.lower())
          elif word.pos_ == 'NOUN':
            word = str(word)
            sent = str(sent).replace(word, word.capitalize())

for key in sheet_to_df_map.keys():
  try:
    lowercased = lowercase_sentence_beginning(key)
    print(key)
  except KeyError:
    pass

filepath = '/Users/lidiiamelnyk/Documents/pos_tagged_non_binary.xlsx'
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