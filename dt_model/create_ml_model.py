import requests

body = {
    "name": "v1",
    "deploymentUri": "gs://servian_cpj_ml_model/",
    "runtimeVersion": "1.12",
    "framework": "SCIKIT_LEARN",
    "pythonVersion": "2.7"
  }

r = requests.post("https://ml.googleapis.com/v1/projects/servianhack-cpj-team/models/dt_model/versions")
print(r.content)



