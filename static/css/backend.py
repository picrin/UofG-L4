import redis
import random
import json
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
import scipy.stats as stats
import scipy.special
import math
import collections
import scipy.stats
import scipy.stats.distributions as distributions
import sys
from pylab import rcParams
import matplotlib.pyplot as plt


annotationDB = 1
probeDB = 2
alterSpliceDB = 3

redisAnnot = redis.StrictRedis(host='localhost', db=annotationDB)
redisProbe = redis.StrictRedis(host='localhost', db=probeDB)
redisAlterSplice = redis.StrictRedis(host='localhost', db=alterSpliceDB)

patientMetadata = json.loads(redisProbe.get("main$alleleData").decode("ascii", errors="ignore"))
modalAllele = [mal for mal, _, _, _ in patientMetadata]

LinregressResult = collections.namedtuple("LinregressResult", ["slope", "intercept", "leftpvalue", "rightpvalue", "stderr"])

def linregressTesting(X, Y):
    sampleSize = len(X)
    # Compute averages of X and Y
    avgX = sum(X)/sampleSize
    avgY = sum(Y)/sampleSize

    # Partial steps to compute estimators of linear regression parameters.
    XDiff = [X_i - avgX for X_i in X]
    XDiffSquared = [i*i for i in XDiff]
    YDiff = [Y_i - avgY for Y_i in Y]

    # B1 is the estimator of slope.
    # B0 is the estimator of intercept.
    # r is the estimator of Y given X.
    B1 = sum(x * y for x, y in zip(XDiff, YDiff)) / (sum(XDiffSquared))
    B0 = avgY - B1 * avgX
    r = lambda x: B0 + B1 * x

    # Partial steps to compute Wald Statistic.
    errs = [y - r(x) for x, y in zip(X, Y)]
    errStd = math.sqrt(sum([err**2 for err in errs]) / (sampleSize - 2))
    XStd = math.sqrt(sum([diff**2 for diff in XDiff]) / sampleSize)
    stdB1 = errStd / (XStd * math.sqrt(sampleSize))

    # Wald Statistic.
    W = (B1 - 0) / stdB1

    # one-tailed pvalues of Wald Test with B1 under T distribution with (sampleSize - 2) degrees of freedom.
    # testing B1 < 0 yields leftpvalue
    # testing B1 > 0 yields rightpvalue
    leftpvalue = distributions.t.cdf(W, sampleSize - 2)
    rightpvalue = 1 - leftpvalue

    resultT = LinregressResult(slope=B1, intercept=B0, leftpvalue=leftpvalue, rightpvalue=rightpvalue, stderr=stdB1)
    return resultT

# That's slightly more numerically stable.
def linregress(x, y):
    TINY = 1.0e-20
    if y is None:  # x is a (2, N) or (N, 2) shaped array_like
        x = np.asarray(x)
        if x.shape[0] == 2:
            x, y = x
        elif x.shape[1] == 2:
            x, y = x.T
        else:
            msg = ("If only `x` is given as input, it has to be of shape "
                   "(2, N) or (N, 2), provided shape was %s" % str(x.shape))
            raise ValueError(msg)
    else:
        x = np.asarray(x)
        y = np.asarray(y)

    if x.size == 0 or y.size == 0:
        raise ValueError("Inputs must not be empty.")

    n = len(x)
    xmean = np.mean(x, None)
    ymean = np.mean(y, None)

    # average sum of squares:
    ssxm, ssxym, ssyxm, ssym = np.cov(x, y, bias=1).flat
    r_num = ssxym
    r_den = np.sqrt(ssxm * ssym)
    if r_den == 0.0:
        r = 0.0
    else:
        r = r_num / r_den
        # test for numerical error propagation
        if r > 1.0:
            r = 1.0
        elif r < -1.0:
            r = -1.0

    df = n - 2
    t = r * np.sqrt(df / ((1.0 - r + TINY)*(1.0 + r + TINY)))
    leftpvalue = distributions.t.cdf(t, n - 2)
    rightpvalue = 1 - leftpvalue
    slope = r_num / ssxm
    intercept = ymean - slope*xmean
    sterrest = np.sqrt((1 - r**2) * ssym / ssxm / df)
    return LinregressResult(slope, intercept, leftpvalue, rightpvalue, sterrest)

def productPDF(x, n):
    return ((-1 * math.log(x)) ** (n - 1)) / math.factorial(n - 1)

def productCDF(x, n):
    if x < 0 or x > 1:
        raise ValueError("intermediate p-values must be in range [0, 1]")
    else:
        return scipy.special.gammaincc(n, -math.log(x))

def product(lista):
    result = 1
    for elem in lista:
        result *= elem
    return result

def pValueForProbeset(modalAllele, probeData):
    left_pvalues = []
    right_pvalues = []
    for seq, data in probeData.items():
        assert(len(modalAllele) == len(data))
        regressR = linregress(modalAllele, data)
        left_pvalues.append(regressR.leftpvalue)
        right_pvalues.append(regressR.rightpvalue)
    leftresult = productCDF(product(left_pvalues), len(left_pvalues))
    rightresult = productCDF(product(right_pvalues), len(right_pvalues))    
    return min(leftresult, rightresult) * 2

def pValueForProbesetWithoutAS(modalAllele, probeData):
    result = [0] * len(modalAllele)
    for seq, data in probeData.items():
        assert(len(modalAllele) == len(data))
        for j, v in enumerate(data):
            result[j] += v
    linregress = stats.linregress(modalAllele, result)
    return linregress.pvalue

metadataKeys = json.loads(redisAnnot.get(b'main$metadataKeys').decode("ascii", errors="ignore"))
metadataToIndex = {key:i for i, key in enumerate(metadataKeys)}

def checkProbesetLevel(probeset):
    metadata = json.loads(redisAnnot.hget(b'probeset$metadata', probeset).decode("ascii", errors="ignore"))
    result = metadata[metadataToIndex["level"]]
    return result

def dataForProbeset(probeset):
    key = b"probes$probeset$" + probeset
    metadatakey = b"probes$metadata"
    probemetadata = json.loads(redisProbe.hget(metadatakey, probeset).decode("ascii", errors="ignore"))
    indexToSeq = {}
    data = {}
    for i, seq in enumerate(probemetadata):
        indexToSeq[i] = seq[0]
        data[seq[0]] = []
    length = redisProbe.llen(key)
    for i in range(length):
        for j, intensity in enumerate(json.loads(redisProbe.lindex(key, i).decode("ascii", errors="ignore"))):
            data[indexToSeq[j]].append(intensity)
    data = {seq:data[::-1] for seq, data in data.items()}
    return data, probemetadata

def plotForProbeset(probeset):
    intensities, probemetadata = dataForProbeset(probeset)
    print("probeset", probeset)
    print("p-value for probeset", pValueForProbeset(modalAllele, intensities))
    print("p-value without AS", pValueForProbesetWithoutAS(modalAllele, intensities))
    
    for seq, intensity in intensities.items():
        plt.figure()
        plt.scatter(modalAllele, intensity)
        plt.plot(np.unique(modalAllele), np.poly1d(np.polyfit(modalAllele, intensity, 1))(np.unique(modalAllele)))
        plt.title(seq[::-1])
        print("seqInv:", seq[::-1])

def getClusters(gene):
    clusters = redisAnnot.smembers(b"search$usual$" + gene)
    return clusters

def getClusters2(gene):
    clusters = redisAnnot.smembers(b"search$weird$" + gene)
    return clusters

def getProbesets(cluster):
    address = b"trans$probeset$" + cluster
    probesets = redisAnnot.smembers(address)
    return probesets

def geneLevelASPValues(cluster, customMA = None, probesets = None):
    if not customMA:
        customMA = modalAllele
    allProbeData = []
    if probesets is None:
        probesets = getProbesets(cluster)
    if probesets == []:
        raise ValueError("probesets can't be empty")
    probesets2 = getProbesets(cluster)
    #print(probesets)
    #print("passed", probesets.difference(probesets2))
    #print("would have received", probesets2.difference(probesets))
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

def writePValues(probeset, pvalue):
    redisAlterSplice.zadd("probe$ASPvalue", pvalue, probeset)

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
  cutoff = 0.05
  allOurGenes = set()
  counter = 0

  for probeset, pvalue in redisAlterSplice.zrange("probe$ASPvalue", 0, -1, withscores = True):
      bonferroniCorrected = pvalue * totalProbesets
      if bonferroniCorrected > cutoff:
          break
      transCluster = redisAnnot.smembers(b"search$probeset$" + probeset)
      transCluster = list(transCluster)
      assert(len(transCluster) == 1)
      transCluster = transCluster[0]
      usualName = redisAnnot.smembers(b"search$trans$usual$" + transCluster)
      if usualName:
          print(usualName, bonferroniCorrected)
      else:
          print(transCluster, bonferroniCorrected)
      allOurGenes.update(usualName)
      counter += 1
  return json.dumps(allOurGenes)
if __name__ == "__main__":
    app.run()
