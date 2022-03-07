import numpy as np
import pandas as pd
from polyfuzz import PolyFuzz
from polyfuzz.models import BaseMatcher
from rapidfuzz import fuzz

xls = pd.ExcelFile('/Users/lidiiamelnyk/Documents/Non_binary_small.xlsx')

sheet_to_df_map = {}
i = 0
for sheet_name in xls.sheet_names:
    sheet_to_df_map[sheet_name] = xls.parse(sheet_name)

for key in sheet_to_df_map.keys():
    for i, row in sheet_to_df_map[key].iterrows():
        for m in str(row['Reply']).split('\n'):
            if m == 'nan':
                pass
            elif m != 'nan':
                sheet_to_df_map[key].loc[i, 'Comment'] = m

df = pd.DataFrame()
for key in sheet_to_df_map.keys():
    df = df.append(sheet_to_df_map[key])



def readGlobalVecData(glove_word_vec_file):
    file = open(glove_word_vec_file, encoding="utf8")
    rawData = file.readlines()
    glove_word_vec_dict = {}
    try:
        for line in rawData:
            line = line.strip().split()
            tag = line[0].encode()
            vec = line[1:]
            glove_word_vec_dict[tag] = np.array(vec, dtype=float)
    except ValueError:
        pass
    return glove_word_vec_dict

gloveFile = ('/Users/lidiiamelnyk/Downloads/vectors.txt')


print("\nLoading Glove data in progress...")
glove_word_vec_dict = readGlobalVecData(gloveFile)
print("\nLoading Glove data is done...")

values = df['Comment'].values

from_list = []
for value in str(values).split(' '):
    value = value.encode()
    value = value.lower()
    if value not in glove_word_vec_dict:
        from_list.append(value)


class MyModel(BaseMatcher):
    def match(self, from_list, glove_word_vec_dict):
        # Calculate distances
        matches = [[fuzz.ratio(from_string, to_string) / 100 for to_string in glove_word_vec_dict]
                   for from_string in from_list]

        # Get best matches
        try:
            mappings = [glove_word_vec_dict[index] for index in np.argmax(matches, axis=1)]
            scores = np.max(matches, axis=1)

        # Prepare dataframe
            matches = pd.DataFrame({'From': from_list, 'To': mappings, 'Similarity': scores})

        except KeyError:
            pass
        return matches


custom_model = MyModel()
model = PolyFuzz(custom_model)

from polyfuzz import PolyFuzz
from polyfuzz.models import Embeddings, TFIDF, RapidFuzz
from flair.embeddings import WordEmbeddings

fasttext_embeddings = WordEmbeddings('de')
fasttext = Embeddings(fasttext_embeddings, min_similarity=0, model_id="FastText")
tfidf = TFIDF(min_similarity=0, model_id="TF-IDF")
rapidfuzz = RapidFuzz(n_jobs=-1, score_cutoff=0, model_id="RapidFuzz")

matchers = [tfidf, fasttext, rapidfuzz]

model = PolyFuzz(matchers)
model.match(from_list, glove_word_vec_dict)
model.visualize_precision_recall(kde=True)