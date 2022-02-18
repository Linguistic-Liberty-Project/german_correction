
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
  try:
    for i,row in sheet_to_df_map[key].iterrows():
      for m in str(row['Reply']).split('\n'):
        if m == 'nan':
          pass
        elif m != 'nan':
          sheet_to_df_map[key].at[i, 'Comment'] = m
  except KeyError:
    pass

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

def saver(dictionary):
    for key, val in dictionary.items():
        val.to_csv("data_{}.csv".format(str(key)))

to_file = saver(sheet_to_df_map)