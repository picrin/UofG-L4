import collections
import re
def d(bytes):
    """
    A dumb decoder from bytes to ascii. Should only be used where unicode is
    not expected by design, e.g. gene names on transcription cluster IDs.

    Should not be used where unicode is expected.

    @return: a string representation of bytes.

    @param bytes: a bytes-like object.
    """
    return bytes.decode("ascii", errors="ignore")


def e(str):
    """
    A dumb encoder from python string to bytes. Should only be used where
    unicode is not expected by design, e.g. gene names on transcription cluster
    IDs.

    Should not be used where unicode is expected.

    @return: a string representation of bytes.

    @param str: a string-like object.
    """
    return bytes(str, encoding="ascii", errors="ignore")

def validateInput(i):
    """
    Basic input validator. Makes sure that passed string is made up of only
    ascii characters and not too long.

    Should be good enough to prevent HTML injection and some other forms of
    attack.
    """
    e = ValueError("invalid or insecure input.")
    if len(i) > 24 or not re.findall("^[\w]+$", i):
        raise e



cache_db = {}


def cache(func):
    """
    If the function was already executed in this python session, it returns
    result of the previous execution. Otherwise it executes the function and
    stores the result.

    Example usage:

    @cache
    def functToCache():
        toReturn = makeDBCall()
        return toReturn

    Warning -- doesn't work well with functions which take more than 0
    parameters.
    """
    def wrapper(x=None):
        if func.__name__ in cache_db:
            return cache_db[func.__name__]
        funcResult = func()
        cache_db[func.__name__] = funcResult
        return funcResult
    return wrapper

LinregressResult = collections.namedtuple("LinregressResult", ["slope", "intercept", "leftpvalue", "rightpvalue", "stderr"])

def linregressTesting(X, Y):
    """
    Easily understandable linear regression.
    """
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
    import numpy as np
    from scipy.stats import distributions
    """
    Linear regression taken from scipy. It appears to be numerically stable.
    """
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
