#!/usr/bin/env python3
import redis
from transvis.utils import *
from transvis.io import *
from transvis.alterSplice import *
import transvis.geneList
import transvis.geneCanvas
from flask import Flask, request, send_from_directory, current_app
import os


app = Flask(__name__)

with open("isDebug") as f:
    if f.read().rstrip() == "1":
        app.debug=True
    else:
        app.debug=False

initDB()


@app.route('/')
def serveIndex():
    print("hi")
    return current_app.send_static_file("index.html")

@app.route("/api/geneList")
def serveGenes(*args, **kwargs):
    return transvis.geneList.serveGenes(*args, **kwargs)

@app.route('/<path:path>')
def serveStatics(path):
    return current_app.send_static_file(path)


@app.errorhandler(redis.exceptions.ConnectionError)
def dberror(e):
    return json.dumps({"error": "db"}), 500

@app.route('/api/clusterID/<path:path>')
def clusterID(*args, **kwargs):
    return transvis.geneCanvas.clusterID(*args, **kwargs)

if __name__ == '__main__' and app.debug:
    app.run(threaded=True, port=80, host="0.0.0.0")
