from elasticsearch import Elasticsearch

es = Elasticsearch('http://localhost:9200')

import pandas as pd


# TODO: create config for data/figs paths, secret for app.py
data_path = "data"
fig_path = "figs"
qs = pd.read_csv("data/qs_full.csv")


# iter over all surveys, over all questions, running gen_figs when possible (there is a type match)
for _, q in qs.iterrows():
    tmp = q.to_dict()
    for k in tmp.keys():
        if not isinstance(tmp[k], str):
            tmp[k] = ""
    es.index(index='is', doc_type='is', id=q["Unnamed: 0"], body=tmp)
