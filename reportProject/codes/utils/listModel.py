import re

def checkType(els):
    """
    :param els: list
    :return: return either str or float
    """
    for el in els:
        if isinstance(el, str):
            return str
    return float

def changeCase(els, case='l'):
    """
    :param els: []
    :return: []
    """
    new_l = []
    for el in els:
        if case == 'l':
            mel = el.lower()
        else:
            mel = el.upper()
        new_l.append(mel)
    return new_l

def filterList(els, pattern):
    required_els = []
    for el in els:
        if re.search(pattern, el):
            required_els.append(el)
    return required_els

def shift_list(lst, s):
    s %= len(lst)
    s *= -1
    shifted_lst = lst[s:] + lst[:s]
    return shifted_lst