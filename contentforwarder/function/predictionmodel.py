import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn import tree
from sklearn.feature_selection import SelectKBest, f_classif

df = pd.read_csv("train.csv")
print(df.dtypes)

# age = df['age'].values
# state = df['state'].values
# gender = df['gender'].values
# url = df['url'].values
#
# # mapping from label code to url string
# le = preprocessing.LabelEncoder()
# movie_names = set(url)
# le.fit(movie_names)
# le.transform(url)
#
# state_value = set(state)
# le.fit(state_value)
# le.transform(state)
#
# gender_value = set(gender)
# le.fit(gender)
# le.transform(gender)
#
# X = pd.concat(gender, state, age)
#
# clf = tree.DecisionTreeClassifier()
# clf = clf.fit(X, url)


def cosine_similarity(ratings):
    '''
    Calculate the cosine similarity matrix
    :param ratings: the ratings matrix with user_id as rows and item_id (moives) as columns
    :return: cosine similarity matrix
             where the value of row i, column j is the cosine similarity between vector i and vector j
    '''
    similarity = None
    # Calculate the dot products as numerators
    similarity = ratings.T.dot(ratings) + 1e-9 # In case the result is 0
    # Norms of vectors as denominators
    norms = np.array([np.sqrt(np.diagonal(similarity))])
    return similarity / (norms.T.dot(norms))
