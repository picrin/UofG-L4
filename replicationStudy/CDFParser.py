import sys
import re

contextDict = {}

with open(sys.argv[1]) as f:
    lines = f.readlines()
    context = None
    for line in lines:
        line = line.rstrip()
        if line:
            c1 = line[0] == "["
            c2 = "Unit" in line
            c3 = "_Block1]" in line
            checkConds = [c1, c2, c3]
            if all(checkConds):
                context = line[len("Unit") + 1: -1 * len("_Block1") - 1]
                if context in contextDict:
                    print(line)
                    raise ValueError
                else:
                    contextDict[context] = {}
            elif context is not None:
                eqPos = line.find("=")
                key = line[:eqPos]
                matchedList = re.findall("Cell[1-9]+", key)
                if matchedList:
                    value = line[eqPos + 1:].split("\t")
                    contextDict[context][key] = value[:3]
        else:
            context = None


def extractCoords():
    for _, cellDict in contextDict.items():
        for _, elems in cellDict.items():
            yield elems[0], elems[1]

allCoords = list(extractCoords())
