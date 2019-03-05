from storecontent import fetchclickssince
# from sklearn import preprocessing
# from sklearn import tree
# import pandas as pd

def rebuildmodel():
    allclicks = fetchclickssince(None)
    print allclicks
    # # df = pd.DataFrame(data=allclicks)
    # gender = allclicks['gender']
    # region = allclicks['region']
    # age = allclicks['age']
    # url = allclicks['region']
    # print(gender, region, age, url)
    #
    # # mapping from label code to url string
    # le = preprocessing.LabelEncoder()
    # movie_names = set(url)
    # le.fit(movie_names)
    # le.transform(url)
    #
    # X = [gender, region, age]
    # clf = tree.DecisionTreeClassifier()
    # clf = clf.fit(X, url)



    # result = clf.predict([])
