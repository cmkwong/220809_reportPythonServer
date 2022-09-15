import pandas as pd
import numpy as np
from codes.utils import listModel

def discardEmptyRows(df, mustFields):
    if len(mustFields) != 0:
        for mustField in mustFields:
            df = df.loc[df[mustField].notnull()]
    return df

def keepRows(df, fields:dict):
    if len(fields) != 0:
        for field, value in fields.items():
            df = df.loc[df[field] == value]
    return df

def dropLastRows(df, n):
    df.drop(df.tail(n).index, inplace=True)

def dropHeadRows(df, n):
    df.drop(df.head(n).index,inplace=True)

def combineCols(df, cols, separator=',', newColName=''):
    colsListType = listModel.checkType(cols)
    if len(newColName) == 0:
        newColName = '-'.join(cols)
    if colsListType == str:
        sub_df = df[cols]
    else:
        sub_df = df[df.iloc[cols]]
    df[newColName] = sub_df.apply(lambda x: separator.join(x.dropna().astype(str)), axis=1)
    return df

def transferColsType(df, cols, type):
    """
    :param df: dataframe
    :param cols: col name, not accept index
    :param type: data type, float, int, etc
    :return:
    """
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df = discardEmptyRows(df, mustFields=[col])
        df[col] = df[col].astype(type)
    return df

def concatDfs(df_dict):
    """
    :param df_dict: dict
    :return: concated DataFrame
    """
    main_df = pd.DataFrame()
    for key, df in df_dict.items():
        main_df = pd.concat([main_df, df], axis=0, sort=True)
    return main_df

def getLastRow(df, pop=False):
    """
    :param df: machineInOut
    :param colName: -1/1
    :return: int, company name, year, month, day
    """
    last_row = df.tail(1)
    values = last_row.values
    last_index = last_row.index.item()  # get OUT[-1] and its date
    # if pop True
    if pop:
        df.drop(df.tail(1).index, inplace=True)
    if values.size == 1:
        values = values[0]
    return last_index, values

def getPreviousIndex(currentIndex, df, limitReplace=None):
    idx = np.searchsorted(df.index, currentIndex)
    if limitReplace and idx == 0:
        return limitReplace
    return df.index[max(0, idx - 1)]

def getNextIndex(currentIndex, df, limitReplace=None):
    idx = np.searchsorted(df.index, currentIndex)
    if limitReplace and idx == len(df)-1:
        return limitReplace
    return df.index[min(idx+1, len(df)-1)]

