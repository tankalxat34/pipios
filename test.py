import sys
import re
import string

pyver1 = "2.7"
pyver2 = "source"
pyver3 = ">=3.6,<4.0"
pyver4 = ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*"
pyver5 = ">=3.10.5"

def getCompareablePyVersion(s, myPythonVersion = list(map(int, list(sys.version_info)[:3]))):
    # print(s)
    result = {"sign": [], "version": []}
    if s != "source":
        separated = s.split(",")
        for value in separated:
            try:
                result["version"].append(list(map(int, re.findall(r"\d.+", value)[0].split(".")[:3])))
            except ValueError:
                result["version"].append(list(map(int, re.findall(r"\d.+", value[:-1] + "0")[0].split(".")[:3])))
            if len(result["version"][-1]) != 3:
                result["version"][-1].append(0)

            result["sign"].append("".join(re.findall(r"[^\d.+*]", value)))
    else:
        return {"sign": [''], "version": [myPythonVersion]}
    return result

def pythonVersionIsCorrect(dct, myPythonVersion = list(map(int, list(sys.version_info)[:3]))):
    result = []
    for i in range(len(dct["sign"])):
        sign = dct["sign"][i]
        ver  = dct["version"][i]
        local_result = False
        
        if sign == "":
            local_result = myPythonVersion == ver
        elif sign == ">=":
            local_result = myPythonVersion >= ver
        elif sign == "<=":
            local_result = myPythonVersion <= ver
        elif sign == ">":
            local_result = myPythonVersion > ver
        elif sign == "<":
            local_result = myPythonVersion < ver
        elif sign == "!=":
            local_result = myPythonVersion != ver
            
        result.append(local_result)
    
    return result[0] if len(set(result)) == 1 else None


class Multiclass:
    """Class with ability to set and get attributes. Could be use as parent class"""
    def __init__(self) -> None:
        pass
    
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)



    
        

    

# (getCompareablePyVersion(pyver1))
# (getCompareablePyVersion(pyver2))
# (getCompareablePyVersion(pyver3))
# (getCompareablePyVersion(pyver4))
print(getCompareablePyVersion(pyver3))
print(pythonVersionIsCorrect(getCompareablePyVersion(pyver5)))
# print(list(map(str, list(sys.version_info)[:3])))