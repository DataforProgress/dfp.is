from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

from os import listdir
from os.path import isfile, join, isdir

app = Flask(__name__)
es = Elasticsearch('localhost', port=9200)

@app.route('/')
def home():
    return render_template('search.html')

@app.route('/search/results', methods=['GET', 'POST'])
def search_request():
    search_term = request.form["input"]
    res = es.search(
        index="is",
        size=20,
        body={
            "query": {
                "multi_match": {
                    "query": search_term,
                    "fields": [
                        "name",
                        "description",
                        "alias",
                        "categories",
                        "type",
                        "survey_name",
                    ]
                }
            }
        }
    )
    return render_template('results.html', res=res)


@app.route('/figures/')
def figure_request():
    # TODO: add more validation here
    index = int(request.args["index"])
    res = es.get(index="is", doc_type='is', id=index)
    q = res["_source"]
    path = join("figs", q["survey"] + "_" + q["alias"])
    imgs = []
    no_figs = ""
    if isdir(path):
        imgs = [join(path, f) for f in listdir(path) if isfile(join(path, f)) and ".png" in f]
    else:
        no_figs = "No figures have been generated for this question."
    imgs = reversed(imgs)
    return render_template('figures.html', question=q, imgs=imgs, no_figs=no_figs)



if __name__ == '__main__':
    app.secret_key = ''
    app.run(host='0.0.0.0', port=None)
