from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

from os import listdir
from os.path import isfile, join, isdir

app = Flask(__name__)
es = Elasticsearch('localhost', port=9200)

#@app.route('/')
#def home():
#    return render_template('search.html')

@app.route('/search/results', methods=['GET', 'POST'])
def search_request():
    search_term = request.form["input"]
    res = es.search(
        index="is",
        size=1000,
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

@app.route('/search/survey', methods=['GET', 'POST'])
def search_survey():
    survey = request.form["survey"]
    res = es.search(
        index="is",
        size=1000,
        body={
            "query": {
                "bool": {
                  "must": [
                    {
                      "match": {
                        "survey": survey
                      }
                    }
                  ]
                }
              }
        }
    )
    return render_template('results.html', res=res)


@app.route('/')
def home():
    res = es.search(
        index="is",
        size=0,
        body={
            "aggs": {
                "surveys": {
                    "terms": {
                        "field": "survey",
                        "size": 10000
                    }
                }
              }
        }
    )
    surveys = sorted([s["key"] for s in res["aggregations"]["surveys"]["buckets"]])
    return render_template('surveys.html', res=surveys)


@app.route('/figures/')
def figure_request():
    # TODO: add more validation here
    index = int(request.args["index"])
    res = es.get(index="is", doc_type='_doc', id=index)
    q = res["_source"]
    path = join("figs", q["survey"], q["alias"])
    imgs = []
    no_figs = ""
    print(path)
    if isdir(join("static", path)):
        imgs = [[join(path, "png", f), join(path, "csv", f.split(".")[0] + ".csv")]
                for f in listdir(join("static", path, "png"))
                if isfile(join("static", path, "png", f)) and ".png" in f]
        print(join("static", path, "png"), listdir(join("static", path, "png")))
        imgs = sorted(imgs)
    else:
        no_figs = "No figures have been generated for this question. " + join("static", path)
    search_term = q["description"]
    res = es.search(
        index="is",
        size=5,
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
    print(imgs)
    return render_template('figures.html', question=q, imgs=imgs, no_figs=no_figs, related=res, zip=zip)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
