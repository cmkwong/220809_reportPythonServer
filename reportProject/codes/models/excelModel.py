from codes import config

import os
import pandas as pd


def readMachineItemMaster():
    print('Reading machine item master ... ')
    df = pd.read_excel(os.path.join(config.installedSSMEPath, 'Machine Item Master.xlsx'), sheet_name='Item Master', header=0)

    # rename the columns
    df.rename(columns=config.itemMasterColName, inplace=True)

    # extract the columns (existed in config.itemMasterColName.keys())
    requiredDf = df.loc[:, config.itemMasterColName.values()]

    # replace nan value into empty ''
    nonNaDf = requiredDf.fillna('')

    # filter out that without plantno
    filteredDf = nonNaDf[nonNaDf['plantno'].str.len() > 0]

    # strip all the values where is model col
    # df_obj = requiredDf.select_dtypes(['object'])
    # requiredDf.loc[:, df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
    filteredDf.loc[:, 'model'] = filteredDf.loc[:, 'model'].str.strip()

    return filteredDf

def readKeyProject():
    print('Reading HK key Project ... ')
    df = pd.read_excel(os.path.join(config.keyProjectPath, 'HK Key Projects 202203.xls'), sheet_name='HK-Project-List', header=2)

    # rename the columns
    df.rename(columns=config.keyProjectColName, inplace=True)

    # extract the columns (existed in config.keyProjectColName.keys())
    requiredDf = df.loc[:, config.keyProjectColName.values()]

    # replace nan value into empty ''
    nonNaDf = requiredDf.fillna('')

    # convert date column into string
    for colName in nonNaDf:
        nonNaDf[colName] = nonNaDf[colName].astype('string')

    # filter out that without plantno
    filteredDf = nonNaDf[nonNaDf['projectCode'].str.len() > 0]

    return filteredDf
