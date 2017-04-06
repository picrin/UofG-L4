from transvis.utils import *
from transvis.io import *
from transvis.alterSplice import *

def searchGene(name):
    searchResult = geneToTrans(name)
    if not searchResult:
        searchResult = extendedToTrans(name)
    return json.dumps(list(searchResult))

def funcGenes(c, left, right):
    validateInput(c)
    response = []
    for elem in redisConn["genecode"].zrangebyscore("genecode$" + c, left, right):
        parsedElem = json.loads(d(elem))
        response.append(parsedElem)
    return(response)

def clusterID(clusID):
    chromosome = None
    leftMost = 2**64
    rightMost = -2**64
    result = []
    for probeset in transToProbeset(clusID):
        elems = probesetAnnotationMetadata(probeset)
        if elems[3] < leftMost:
            leftMost = elems[3]
        if elems[4] > rightMost:
            rightMost = elems[4]
        if elems[-1] == "core":
            probesetData = dataForProbeset(str(elems[0]))["probeData"]
            checkPValue = pValueForProbeset(probesetData)
            extendedElems = elems + [checkPValue * totalProbesets(), modalAllele(), probesetData]
            result.append(extendedElems)

        chromosome = elems[1]
    return json.dumps([[chromosome, leftMost, rightMost], funcGenes(chromosome, leftMost, rightMost), result])
