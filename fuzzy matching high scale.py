import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer

import re

def ngrams(string, n = 3):
  string = string.encode('ascii', errors = 'ignore' ).decode()
  chars_to_remove = ['(', ')', '[', ']', '{', '}', '.', ';', ',']
  rx = '[' + re.escape(' '.join(chars_to_remove)) + ']'
  string = re.sub(rx, '', string)
  string = string.replace ('&', 'and')
  string = string.replace('-', ' ')
  string = string.replace(',', ' ')
  string = re.sub(' +',' ', string).strip() #remove extra white spaces
  string = ' ' + string + ' ' #pad names for ngrams
  ngrams = zip(*[string[i:] for i in range(n)])
  return [' '.join(ngram) for ngram in ngrams]

xls = pd.ExcelFile('/content/Non_binary_small.xlsx')

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

df = pd.DataFrame()

for key in sheet_to_df_map.keys():
  df = df.append(sheet_to_df_map[key])


values = [ ] #get raw text from string data in the comments
for i, row in df.iterrows():
  for line in str(row['Comment']).split('/n'):
    values.append(line)
print(values[:10])

vectorizer = TfidfVectorizer(min_df = 1, analyzer = ngrams)
tf_idf_matrix = vectorizer.fit_transform(values)

import numpy as np
from scipy.sparse import csr_matrix
import sparse_dot_topn.sparse_dot_topn as ct


def cossim_top(A, B, ntop, lower_bound=0):
    # transform A and B to csr matrix
    # in case they are already in format acceptable for csr, there will be no overhead
    A = A.tocsr()
    B = B.tocsr()
    M, _ = A.shape
    _, N = B.shape

    idx_dtype = np.int32
    nnz_max = M * ntop
    indptr = np.zeros(M + 1, dtype=idx_dtype)  # row indices
    indices = np.zeros(nnz_max, dtype=idx_dtype)  # column indices
    data = np.zeros(nnz_max, dtype=A.dtype)

    ct.sparse_dot_topn(M, N, np.asarray(A.indptr, dtype=idx_dtype),
                       np.asarray(A.indices, dtype=idx_dtype),
                       A.data,
                       np.asarray(B.indptr, dtype=idx_dtype),
                       np.asarray(B.indices, dtype=idx_dtype),
                       B.data,
                       ntop,
                       lower_bound,
                       indptr, indices, data)

    return csr_matrix((data, indices, indptr), shape=(M, N))

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import time

t1 = time.time()
print(process.extractOne('trans', values))
t = time.time()-t1
print("SELFTIMED:", t)
print("Estimated hours to complete for full dataset:", (t*len(org_names))/60/60)

t1 = time.time()
matches = cossim_top(tf_idf_matrix, tf_idf_matrix.transpose(), 10, 0.85)
t = time.time()-t1
print("SELFTIMED:", t)
