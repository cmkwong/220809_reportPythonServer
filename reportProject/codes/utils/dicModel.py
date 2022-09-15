from codes.utils import listModel

def changeCase(dic, case='l'):
    """
    Change the key case
    """
    old_keys = list(dic.keys())
    new_keys = listModel.changeCase(old_keys, case)
    for i, o_key in enumerate(old_keys):
        dic[new_keys[i]] = dic.pop(o_key)
    return dic

def mergeDict(originDict, newDict):
    """
    Put the new dictionary merged into new dictionary
    """
    for key, value in newDict.items():
        originDict[key] = value
    return originDict

def keepDic(originDict, keepList):
    """
    Keep the dictionary list on the keepList
    """
    newDict = {}
    for key, value in originDict.items():
        if key in keepList:
            newDict[key] = value
    return newDict

# duplicated function with append_dictValues_into_text()
def dic2Txt(dicts):
    """
    concat the dict value (text) into one text format
    """
    txt = ''
    for key, value in dicts.items():
        txt += value + '\n'
    return txt

def append_dictValues_into_text(dic, txt=''):
    values = list(dic.values())
    txt += ','.join([str(value) for value in values]) + '\n'
    return txt