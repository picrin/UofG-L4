from __future__ import print_function
import sys
try:
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor
except ImportError:
    print("Warning: couldn't import nbformat", file=sys.stderr)

def executeNotebook(notebookName, wd):
    with open(notebookName) as file:
        nb = nbformat.read(file, as_version=4)
        ep = ExecutePreprocessor(timeout=600, kernel_name='ir')
        ep.preprocess(nb, {'metadata': {'path': wd}})

def assertEqual(valA, valB):
    if valA != valB:
        raise AssertionError(str(valA) + " != " + str(valB))
