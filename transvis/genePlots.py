from transvis.utils import *
from transvis.io import *
from transvis.alterSplice import *

initDB()
def clusterID(probesetID):
    return json.dumps(dataForProbeset(probesetID))
