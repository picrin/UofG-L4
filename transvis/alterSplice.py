from transvis.io import *
from transvis.utils import *
import numpy as np
import scipy
import math

@cache
def cachedAlleleData():
    return alleleData()

@cache
def modalAllele():
    metadata = alleleData()
    return [mal for mal, _, _, _ in metadata]


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

def pValueForProbeset(probeData):
    left_pvalues = []
    right_pvalues = []
    ma = modalAllele()
    for seq, data in probeData.items():
        assert(len(ma) == len(data))
        regressR = linregress(ma, data)
        left_pvalues.append(regressR.leftpvalue)
        right_pvalues.append(regressR.rightpvalue)
    leftresult = productCDF(product(left_pvalues), len(left_pvalues))
    rightresult = productCDF(product(right_pvalues), len(right_pvalues))
    return min(leftresult, rightresult) * 2

def dataForProbeset(probeset):
    chipMeta = probesetChipMetadata(probeset)
    annotMeta = probesetAnnotationMetadata(probeset)
    annotMetaKeys = metadataKeys()
    perProbeData = {seq[0]: t for t, seq in zip(probesetData(probeset), chipMeta)}
    annotation = {k: m for m, k in zip(annotMeta, annotMetaKeys)}
    alleleLength = modalAllele()
    return {"probeData": perProbeData, "annotation": annotation, "chipMeta": chipMeta, "modalAllele": alleleLength}

def pValueForProbesetWithoutAS(modalAllele, probeData):
    result = [0] * len(modalAllele)
    for seq, data in probeData.items():
        assert(len(modalAllele) == len(data))
        for j, v in enumerate(data):
            result[j] += v
    linregress = stats.linregress(modalAllele, result)
    return linregress.pvalue
