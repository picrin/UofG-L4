#!/usr/bin/env python3
import redis
import random
import json
import numpy as np
import scipy.integrate as integrate
import scipy.stats as stats
import scipy.special
import math
import collections
import scipy.stats
import scipy.stats.distributions as distributions
import sys
from transvis.utils import *
from transvis.io import *
from transvis.alterSplice import *

initDB()

def checkProbesetLevel(probeset):
    metadata = probesetAnnotationMetadata(probeset)
    result = metadata[metadataToIndex()["level"]]
    return result

def getProbesets(cluster):
    address = b"trans$probeset$" + cluster
    probesets = redisAnnot.smembers(address)
    return probesets

def geneLevelASPValues(cluster, customMA = None, probesets = None):
    if not customMA:
        customMA = modalAllele()
    allProbeData = []
    if probesets is None:
        probesets = getProbesets(cluster)
    if probesets == []:
        raise ValueError("probesets can't be empty")
    probesets2 = getProbesets(cluster)
    corrections = []
    for i, probeset in enumerate(probesets):
        data, probemetadata = dataForProbeset(probeset)
        for seq, intensities in data.items():
            allProbeData.append(intensities)
    allProbeData = np.array(allProbeData)
    for j in range(allProbeData.shape[1]):
        corrections.append(sum(allProbeData[:, j])/allProbeData.shape[0])
    result = []
    for i, probeset in enumerate(probesets):
        data, probemetadata = dataForProbeset(probeset)
        newData = {}
        for seq, intensities in data.items():
            newIntensities = [datum - correction for datum, correction in zip(intensities, corrections)]
            newData[seq] = newIntensities
        result.append((pValueForProbeset(customMA, newData), probeset))
    result.sort()
    return result

def transIter():
    transIter = redisAnnot.scan_iter(match="trans\$probeset\$*")
    for elem in transIter:
        yield bytes(elem.decode("ascii", errors="ignore").split("$")[-1], encoding="ascii", errors="ignore")

def probesetIter(level = None):
    for trans in transIter():
        probesets = []
        for probeset in getProbesets(trans):
            if level is not None and checkProbesetLevel(probeset) == level:
                probesets.append(probeset)
            elif level is None:
                probesets.append(probeset)
        if probesets:
            yield (trans, probesets)

from flask import Flask, request, send_from_directory, current_app
app = Flask(__name__)

app.debug=True

@app.route("/api/geneList")
def serveGenes():
    cutoff = 0.05
    allOurGenes = set()
    counter = 0
    result = []
    for probeset, pvalue in redisConn["alterSplice"].zrange("probe$ASPvalue", 0, -1, withscores = True):
        bonferroniCorrected = pvalue * totalProbesets()
        if bonferroniCorrected > cutoff:
            break
        transCluster = list(probesetToTrans(probeset))
        assert(len(transCluster) == 1)
        transCluster = transCluster[0]
        usualName = transToGene(transCluster)
        result.append([list(usualName), transCluster, bonferroniCorrected])
        allOurGenes.update(usualName)
        counter += 1
    return json.dumps(result)

# set the project root directory as the static folder, you can set others.
@app.route('/<path:path>')
def serveStatics(path):
    return current_app.send_static_file(path)

@app.route('/')
def serveIndex():
    return current_app.send_static_file("index.html")

@app.route('/api/genecode/<path:path>')
def genes(path):
    path = path.split(":")
    c = path[0]
    left = int(path[1])
    right = int(path[2])
    return json.dumps(funcGenes(c, left, right))

import re
def validateInput(i):
    e = ValueError("invalid or insecure input.")
    if len(i) > 24 or not re.findall("^[\w]+$", i):
        raise e

def funcGenes(c, left, right):
    validateInput(c)
    response = []
    for elem in redisConn["genecode"].zrangebyscore("genecode$" + c, left, right):
        parsedElem = json.loads(d(elem))
        response.append(parsedElem)
    return(response)

import redis, json

@app.errorhandler(redis.exceptions.ConnectionError)
def dberror(e):
    return json.dumps({"error": "db"}), 500

annotDB = 1
@app.route('/api/clusterID/<path:path>')
def clusterID(path):
    chromosome = None
    leftMost = 2**64
    rightMost = -2**64
    result = []
    for probeset in transToProbeset(path):
        elems = probesetAnnotationMetadata(probeset)
        if elems[3] < leftMost:
            leftMost = elems[3]
        if elems[4] > rightMost:
            rightMost = elems[4]
        if elems[-1] == "core":
            probesetData = dataForProbeset(str(elems[0]))
            checkPValue = pValueForProbeset(probesetData)
            extendedElems = elems + [checkPValue * totalProbesets(), modalAllele(), probesetData]
            result.append(extendedElems)

        chromosome = elems[1]
    return json.dumps([[chromosome, leftMost, rightMost], funcGenes(chromosome, leftMost, rightMost), result])

if __name__ == '__main__':  # pragma: no cover
    app.run(threaded=True, port=80, host="0.0.0.0")
