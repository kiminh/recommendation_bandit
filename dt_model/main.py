import cython
from google.cloud import datastore
from google.cloud import storage
import schedule
import time
import numpy as np
from sklearn import preprocessing
from sklearn.pipeline import Pipeline
from sklearn import tree
from sklearn.externals import joblib
import subprocess as sp


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


def job():
    client = datastore.Client('servianhack-cpj-team')
    query = client.query(kind='Click')
    data = list(query.fetch())
    age = []
    gender = []
    region = []
    url = []

    for item in data:
        age.append(item['age'])
        gender.append(item['gender'])
        region.append(item['region'])
        url.append(item['url'])

    # mapping from label code to url string
    le = preprocessing.LabelEncoder()
    movie_names = list(set(url))
    # raise ValueError(movie_names)
    le.fit(movie_names)
    url = le.transform(url)

    state_value = list(set(region))
    le.fit(state_value)
    region = le.transform(region)

    gender_value = list(set(gender))
    le.fit(gender_value)
    gender = le.transform(gender)

    age_value = list(set(age))
    le.fit(age_value)
    age = le.transform(age)

    X = np.stack([gender, region, age],axis=1)
    Y = np.array(url)
    # clf = tree.DecisionTreeClassifier()
    # clf = clf.fit(X, Y)

    pipeline = Pipeline([
        ('classification', (tree.DecisionTreeClassifier()))
    ])

    pipeline.fit(X, Y)

    # Export the classifier to a file
    joblib.dump(pipeline, '/tmp/modeldd.joblib')
    upload_blob('servian_cpj_ml_model', '/tmp/modeldd.joblib', 'modeldd.joblib')
    sp.check_call('gcloud ml-engine versions create 1.1 --model better-classifier --origin gs://servian_cpj_ml_model/ --runtime-version=1.12 --framework SCIKIT_LEARN --python-version=2.7')
    raise ValueError("Done")


schedule.every(5).seconds.do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)


