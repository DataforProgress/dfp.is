from elasticsearch import Elasticsearch

es = Elasticsearch('http://localhost:9200')

import pandas as pd
import os

# TODO: create config for data/figs paths, secret for app.py
data_path = "data"

eid = 0

import numpy as np


# iter over all surveys, over all questions, running gen_figs when possible (there is a type match)
def load_es(survey_path, survey_name=""):
    global eid
    print(survey_name, eid)
    contents = [c for c in os.listdir(survey_path)]
    for c in contents:
        if os.path.isdir(os.path.join(survey_path, c)):
            load_es(os.path.join(survey_path, c), survey_name=survey_name + c)
    codebook_paths = [os.path.join(survey_path, c) for c in contents if "codebook" in c and "csv" in c]
    if len(codebook_paths) == 0:
        return
    cb = pd.read_csv(codebook_paths[0])
    survey = survey_name.replace(" ", "")
    for alias in cb["Variable"].unique():
        q = cb[cb["Variable"] == alias]
        qnp = q.to_numpy()
        qd = {
            "alias": qnp[0, 2],
            "description": qnp[0, 3] if isinstance(qnp[0, 3], str) else "",
            "name": qnp[0, 4],
            "type": qnp[0, 5],
            "aliases": [i if isinstance(i, str) else "" for i in qnp[:, 7]],
            "rows": [i if isinstance(i, str) else "" for i in qnp[:, 8]],
            "categories": [i if isinstance(i, str) else "" for i in qnp[:, 0]],
            "values": [i if isinstance(i, float) and not np.isnan(i) else -1 for i in qnp[:, 1]],
            "survey": survey,
            "survey_name": survey_name
        }
        if qd["type"] == "numeric":
            qd["aliases"] = [""]
            qd["rows"] = [""]
            qd["categories"] = [""]
            qd["values"] = [-1]
        es.index(index='is', doc_type='_doc', id=eid, body=qd)
        eid += 1

load_es("data")