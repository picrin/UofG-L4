from transvis.utils import *
from transvis.io import *
from transvis.alterSplice import *

def serveGenes():
    cutoff = 0.05
    allOurGenes = set()
    counter = 0
    result = []
    for probeset, pvalue in redisConn["alterSplice"].zrange("probe$ASPvalue", 0, 10, withscores = True):
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
