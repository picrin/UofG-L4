from transvis.utils import *
from transvis.io import *
from transvis.alterSplice import *

initDB()
def clusterID(probesetID):
    toReturn = dataForProbeset(probesetID)
    print(toReturn)
    toReturn.update({"names": list(transToGene(toReturn["annotation"]["transcript_cluster_id"]))})
    return json.dumps(toReturn)
