"""
Module to read genomic data from redis.
"""

import redis
import fakeredis
import json
from transvis.utils import *


annotationDB = 1
probeDB = 2
alterSpliceDB = 3
genecodeDB = 4

redisConn = {}


def initDB(host="localhost", port=2050):
    """
    Initializes connection to a real redis instance running on a given
    interface and a given port. This function is not expected to raise any
    exceptions. If database is not accessible on the given interface/port,
    redisConn.exceptions.ConnectionError will be raised.

    To access probe data use redisConn["probe"]

    To access annotation data use redisConn["annot"]

    To access alternative splicing data use redisConn["alterSplice"]

    To access genecode data use redisConn["genecode"]

    For the purpose of testing use initFakeDB.

    @param host: interface to connect to. Example values include localhost,
    127.0.0.1 and 0.0.0.0 (not recommended).
    @param port: port to run on. 2050 is recommended, and used by transvis-db.
    """
    redisConn["genecode"] = redis.StrictRedis(host='localhost',
                                              db=genecodeDB,
                                              port=port)
    redisConn["annot"] = redis.StrictRedis(host='localhost',
                                           db=annotationDB,
                                           port=port)
    redisConn["probe"] = redis.StrictRedis(host='localhost',
                                           db=probeDB,
                                           port=port)
    redisConn["alterSplice"] = redis.StrictRedis(host='localhost',
                                                 db=alterSpliceDB,
                                                 port=port)


def initFakeDB(*args, **kwargs):
    """
    Initializes connection to a fake redisConn instance for the purpose of
    testing. Any (named) parameter may be passed, but will not change the
    behaviour of the function.
    """
    redisConn["genecode"] = fakeredis.FakeStrictRedis()
    redisConn["annot"] = fakeredis.FakeStrictRedis()
    redisConn["probe"] = fakeredis.FakeStrictRedis()
    redisConn["alterSplice"] = fakeredis.FakeStrictRedis()


def transToProbeset(trans):
    """
    Retrieves probeset associated with a given transcription cluster ID.

    @param trans: valid transcription cluster ID.
    @return: A set of probeset IDs.
    """
    return set(d(i) for i in redisConn["annot"].smembers('trans$probeset$' +
                                                         str(trans)))


def probesetToTrans(probeset):
    """
    Retrieves transcription clusters, to whom the given probeset belongs.

    Although we'd hope there's only one cluster, we still return a set, just in
    case.

    @param probeset: valid probeset ID.
    @return: a set (mostly 1-element) of transcription cluster IDs.
    """
    return set(d(i) for i in redisConn["annot"].smembers("search$probeset$" +
                                                         convertToStr(probeset)))

@cache
def metadataKeys():
    """
    Retrieves a list of headers, which can be used to understand the output of
    L{probesetAnnotationMetadata}.

    @return: list of metadata keys
    """
    try:
        return json.loads(d(redisConn["annot"].get("main$metadataKeys")))
    except AttributeError:
        return []


def probesetAnnotationMetadata(probeset):
    """
    Retrieve annotation metadata for a probeset. To understand the output use
    L{metadataKeys}.

    @param probeset: valid probeset ID.
    @return: list of metadata.
    """
    try:
        return json.loads(d(redisConn["annot"].hget('probeset$metadata',
                                                    str(probeset))))
    except AttributeError:
        return []


def geneToTrans(gene):
    """
    Retrive transcription cluster IDs given a HGNC gene name, such as MBNL1 or
    FOXP2.

    @param gene: A HGNC gene name, such as MBNL1 or FOXP2.
    @return: set of transcription cluster IDs.
    """
    return set(d(i) for i in redisConn["annot"].smembers('search$usual$' +
                                                         gene))


def extendedToTrans(gene):
    """
    Retrive transcription cluster IDs given a non-standard gene name, such as
    OTTHUMT00000058841.

    @param gene: a non-standard gene name, e.g. OTTHUMT00000058841
    @return: set of transcription clusters (usually just one)
    """
    return set(d(i) for i in redisConn["annot"].smembers('search$weird$' +
                                                         gene))


def transToGene(trans):
    """
    Retrieve the HUGO Gene Nomenclature Committee (HGNC) gene names associated
    with a given transcription clusterID.

    @param trans: transcription cluster ID.
    @return: set of transcription clusters (can be more than one, e.g. CFHR1,
    CFHR2 and CFHR3 are all part of a single transcription cluster).
    """
    return set(d(i) for i in redisConn["annot"].smembers(
            "search$trans$usual$" + str(trans)))


def transToExtended(trans):
    """
    Retrieve the extended gene names associated with a given transcription
    clusterID.

    @param trans: transcription cluster ID.
    @return: set of transcription clusters.
    """
    return set(d(i) for i in redisConn["annot"].smembers(
            "search$trans$weird$" + str(trans)))

@cache
def alleleData():
    """
    Return patient data in form of quadruples: [modalAllele, progenitalAllele,
    patient id, filename].

    @return: patient data.
    """
    try:
        return json.loads(d(redisConn["probe"].get("main$alleleData$")))
    except AttributeError:
        return []

@cache
def totalProbesets():
    return redisConn["alterSplice"].zcard("probe$ASPvalue")

def probesetChipMetadata(probeset):
    """
    Return the chip metadata for a probeset.

    @param probeset: valid probeset ID.
    @return: a list of up to 4 triples of the form
    [25-bases probe length, Y coord, X coord]. You have to take the complement
    of the probe sequence before using BLAST.
    """
    try:
        return json.loads(d(redisConn["probe"].
                            hget("probes$metadata", convertToStr(probeset))))
    except AttributeError:
        return []


def probesetPatientData(probeset):
    """
    Return all probe intensities for a given probeset. The results can be
    associated with patients by looking at output of L{alleleData}, and are
    produced in the same order.

    @param probeset: valid probeset ID.
    @return: return n tuples, where n is the number of patients. Each tuple has
    arity k, with k between 1 and 4, corresponding to the number of probes in
    the probeset.
    """
    address = "probes$probeset$" + str(probeset)
    patientData = redisConn["probe"].lrange(address, 0, -1)

    # remember to reverse the list
    return [json.loads(d(i)) for i in patientData[::-1]]

def convertToStr(bytesOrInt):
    try:
        return d(bytesOrInt)
    except AttributeError:
        return str(bytesOrInt)

# TODO make these to be tests.
# initDB()
# print(metadataKeys())
# print(transToProbeset(2315100))
# print(geneToTrans("MBNL1"))
# print(probesetAnnotationMetadata(2315104))
# print(type(convertToStr(b'10')))
#print(list(probesetToTrans(b'3307988')))
# print(extendedToTrans('NONHSAT051717'))
# print(transToGene(2315100))
# print(transToExtended(2315100))
# print(alleleData())
# print(probesetChipMetadata(3973794))
# print(probesetPatientData(2819466))
# print(dataForProbeset(2819466))
