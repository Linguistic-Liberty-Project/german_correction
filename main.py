import spacy
nlp = spacy.load('de_core_news_sm')
nlp.max_length = 107702912
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
  try:
    for i,row in sheet_to_df_map[key].iterrows():
      for m in str(row['Reply']).split('\n'):
        if m == 'nan':
          pass
        elif m != 'nan':
          sheet_to_df_map[key].at[i, 'Comment'] = m
  except KeyError:
    pass

#since we are going to be looking for the hits of the words in corpus, we have to standardise our words through bringing them the common lemmas
words_lemma = []
def lemmatizer(key):
      for i,row in sheet_to_df_map[key].iterrows():
        doc = nlp(row['Comment'])
        #for word in doc:
        for x in doc:
          result = ' '.join([x.lemma_ for x in doc])
          print(result)
          words_lemma.append(result)
          return words_lemma

#use lemmatisation function for each sheet of our excel file
lemmatized_words = []
for key in sheet_to_df_map.keys():
  try:
    lemmatized_words.append(lemmatizer(key))
    print(key)
  except KeyError:
    pass

#now we are creating corpus through adding together word embedding corpus from fasttext and denglish corpus from wikipedia
corpus_file = open('/Users/lidiiamelnyk/Downloads/cc.de.300.txt', encoding = "ISO-8859-1")
file_contents = corpus_file.readlines()
denglish_file = open('/Users/lidiiamelnyk/Downloads/denglish.txt', encoding =  "ISO-8859-1").read()
file_contents =[w.strip('\n') for w in file_contents]
words = [w.strip("'") for w in denglish_file.split(' ')]
for word in str(words).split(','):
  file_contents.append(word)


#create a spacy readable vocabulary doc from the two merged corpus files
vocab_doc = nlp.make_doc(str(file_contents))
vocab_lemmatized = []
for word in vocab_doc:
    result = ' '.join([x.lemma_ for x in vocab_doc])
    vocab_lemmatized.append(result)


#create a function to generate only unique lemmas for both corpora
# i assume they are going to be unique since we are applying hash value

def unique_words_in_list(doc):
  unique_lemmas = []
  word_hashes =[]
  for token in doc:
    hash_value=nlp.vocab.strings[token.text]
    unique_lemmas.append(token)
    word_hashes.append(hash_value)
  return unique_lemmas


non_standard_words = []

unique_lemmas_non_binary_corpus = set(lemmatized_words)
unique_lemmas_corpus = set(vocab_lemmatized)
#check if the words in our non binary corpus are present in our gs corpus
for x in unique_lemmas_non_binary_corpus:
  if x not in unique_lemmas_corpus:
    non_standard_words.append(x)

print(non_standard_words)

#Part 2 Fuzzy word match
#fuzzy word match is going to be carried out with fuzzy wuzzy lib as well as python Levenshtein

import fuzzywuzzy
import Levenshtein
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


#create a nested dictionary for each non-standard word with the word it matches and the matching ratio
word_match_dict = {}
def fuzzy_word_match(list, corpus):
  for word in list:
    for other_word in corpus:
      if fuzz.token_set_ratio(word, other_word) > 0.6:
        if word_match_dict[word] is None:
            word_match_dict[word] = {}
        word_match_dict[word][other_word] = fuzz.token_set_ratio(word, other_word)