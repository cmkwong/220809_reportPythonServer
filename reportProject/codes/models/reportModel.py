import datetime

import pandas as pd
import numpy as np
import os
import re
import math
# from openpyxl import load_workbook
from difflib import SequenceMatcher

from codes import config
from codes.utils import excelModel, dfModel, fileModel, listModel


def convert_to_float(value):
    try:
        return float(value)
    except ValueError:
        return np.nan


def getInOutPivot():
    sheet_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    listFiles = listModel.filterList(fileModel.getFileList(config.inoutRecordPath), "^Daily Machinery In - Out Record_\d\d\d\d.xlsx")
    dfs = {}
    for filename in listFiles:
        # set the path
        inOutPath = os.path.join(config.inoutRecordPath, filename)
        # read required sheet and concat the sheets
        dfs[filename] = excelModel.readExcel(inOutPath, sheet_names, concat=True)
        # add year col
        year = re.findall("Record_(\d+)", filename)[0]
        dfs[filename]['年'] = year
    # concat the dataframe
    main_df = dfModel.concatDfs(dfs)
    # format the year, month, day into integer
    main_df = dfModel.transferColsType(main_df, cols=['年', '月', '日'], type=int)
    # combine the cols into 'YYYY-MM-DD'
    main_df = dfModel.combineCols(main_df, cols=['年', '月', '日'], separator='-', newColName='date')
    # transfer to datetime
    main_df['date'] = pd.to_datetime(main_df['date'], format="%Y-%m-%d", errors='coerce')
    # discard the empty row
    main_df = dfModel.discardEmptyRows(main_df, mustFields=['工作/機械編號', 'date'])
    # keep the row that did signed
    # main_df = dfModel.keepRows(main_df, fields={'Signed DN/CR': 'Y'})
    # concat the column into customer name || account code
    # main_df['accodeName'] = main_df.fillna('nan')[['客戶名稱 ', 'AC CODE']].agg('||11000'.join, axis=1)
    # create pivot table
    pivotTable = pd.pivot_table(main_df, index=['工作/機械編號', 'date'], values='AC CODE', columns=['出-1 /入 1'], aggfunc=lambda x: x)[[-1, 1]]
    return pivotTable


def _adjustPantInOutRecord(plantInOutRecord, requiredFromDate):
    """
    :param plantInOutRecord: dict
    :param requiredFromDate: datetime
    :return:
    """
    adjustedMachineInOutRecord = plantInOutRecord.copy()
    for i, record in plantInOutRecord.items():
        # adjust the OUT record
        if (record['out'] < requiredFromDate):
            adjustedMachineInOutRecord[i]['out'] = requiredFromDate
        # adjust the IN record: date time HH:MM:ss = 00:00:00 -> 23:59:59

    return adjustedMachineInOutRecord


def _sameDateInoutIssue(plantInOut):
    plantInOut_copy = plantInOut.copy()
    i = 0
    for index, row in plantInOut.iterrows():
        # same company, then should be either OUT or IN that depend on last record
        if row[-1] == row[1] and isinstance(row[-1], str) and isinstance(row[1], str):
            # first row default OUT
            if i == 0:
                plantInOut.loc[index, 1] = float('nan')  # assume only OUT to be valid, but IN is cancelled
            else:
                lastOut = isinstance(plantInOut.iloc[i - 1][-1], str)  # true = out
                lastIn = isinstance(plantInOut.iloc[i - 1][1], str)  # true = in
                if lastOut and not lastIn:
                    plantInOut_copy.loc[index, -1] = float('nan')
                    row = pd.Series(data={-1: row[-1], 1: float('nan')}, name=index + pd.Timedelta(minutes=30))
                    plantInOut_copy = plantInOut_copy.append(row, ignore_index=False)
                elif not lastOut and lastIn:
                    plantInOut_copy.loc[index, 1] = float('nan')
                    row = pd.Series(data={-1: float('nan'), 1: row[-1]}, name=index + pd.Timedelta(minutes=30))
                    plantInOut_copy = plantInOut_copy.append(row, ignore_index=False)
        i += 1
    # sort by index
    plantInOut_copy.sort_index(inplace=True)
    return plantInOut_copy


def getInOutDateRecord(plantno, inOutPivot, requiredFromDate, requiredToDate):
    plantInOutRecord = {}
    # find the plantno is in the inOutPivot, if not exist return {}
    if plantno not in list(inOutPivot.index.get_level_values(inOutPivot.index.names[0])):  # https://stackoverflow.com/questions/24495695/pandas-get-unique-multiindex-level-values-by-label
        return {}
    plantInOut = inOutPivot.loc[plantno][inOutPivot.loc[plantno].index <= requiredToDate]  # get data before the report end date
    plantInOut.sort_index(inplace=True)
    plantInOut = _sameDateInoutIssue(plantInOut)  # settle the same date IN/OUT issue
    inRecord = plantInOut[1].dropna()  # drop none row
    outRecord = plantInOut[-1].dropna()  # drop none row
    for i, outDate in enumerate(reversed(outRecord.index)):
        if (outDate > requiredToDate): continue
        # get OUT date and its cust code
        outCustCode = outRecord.loc[outDate]
        plantInOutRecord[i] = {}
        plantInOutRecord[i]['custCode'] = outCustCode
        plantInOutRecord[i]['out'] = outDate
        # find the possible IN date
        plantInOutRecord[i]['in'] = requiredToDate
        # if no IN record, just break
        if len(inRecord) == 0:
            break

        # get last row (last in-date)
        inDate, inCompanyCode = dfModel.getLastRow(inRecord, pop=False)
        # because of BA have only yyyy-mm-dd but have no HH:MM:ss. So, I assumed the time is the end of date, eg: 23:59:59
        inDate = inDate + datetime.timedelta(hours=23, minutes=59, seconds=59)

        # find the last similar customer code
        # similarity = SequenceMatcher(None, outCompanyName, inCompanyName).ratio()
        # if IN date out of range and has same customer code (means that IN/OUT record is not needed)
        if (inCompanyCode == outCustCode and inDate > outDate and inDate < requiredFromDate):
            del plantInOutRecord[i]
            break
        # user sometimes hide the data in the excel, if customer code is [], means the IN/OUT record is invalid
        if str(outCustCode) == '[]':
            del plantInOutRecord[i]
            break
        # find the possible true IN date (might ended before this month)
        if (inCompanyCode == outCustCode and outDate < inDate):
            # need inDate before required maximum date, or re-assign max date
            if inDate > requiredToDate:
                plantInOutRecord[i]['in'] = requiredToDate
            else:
                plantInOutRecord[i]['in'] = inDate
            dfModel.dropLastRows(inRecord, 1)
        # if OUT date is out of requiredFromDate, means the record is already full and do not need to find previous IN/OUT record
        if outDate <= requiredFromDate:
            break
    adjustedPlantInOutRecord = _adjustPantInOutRecord(plantInOutRecord, requiredFromDate)  # return False if no IN/OUT
    return adjustedPlantInOutRecord


def getDumpInOutRecord(start, end):
    dumpInOutRecord = {}
    dumpInOutRecord[0] = {}
    dumpInOutRecord[0]['custCode'] = "--"
    dumpInOutRecord[0]['out'] = start
    dumpInOutRecord[0]['in'] = end
    return dumpInOutRecord


# def getMeasureableFuelTanks__DISCARD():
#     """
#     return dict = {model: tanksize} measuredFuelTanks with measured tank size
#     """
#     # Actual Tank Size
#     measuredFuelTanks = {}
#     # wb = load_workbook(os.path.join(config.tankSizePath, "Measureable_Volume.xlsx"))
#     df = pd.read_excel(os.path.join(config.tankSizePath, 'Measureable_Volume.xlsx'), sheet_name='Sheet1')
#     for i, row in df.iterrows():
#         measuredFuelTanks[row['Model']] = row['Volume']
#         # if model.strip() == required_modelno.strip():
#         #     return measured_tank_size
#     return measuredFuelTanks
#
#
# def getFuelTanks__DISCARD():
#     """
#     return {plantno: {brand, model, tanksize}}
#     """
#     tanks = {}
#     denyoDf = pd.read_excel(os.path.join(config.tankSizePath, 'Denyo plants.xlsx'), sheet_name='工作表1')
#     for i, row in denyoDf.iterrows():
#         tank = {}
#         tank['brand'], tank['model'], tank['fuelTankCapacity'] = row[1], row[2], row[3]
#         tanks[row[0]] = tank
#
#     lightToweroDf = pd.read_excel(os.path.join(config.tankSizePath, 'LightTowers.xlsx'), sheet_name='工作表1')
#     for i, row in lightToweroDf.iterrows():
#         tank = {}
#         tank['brand'], tank['model'], tank['fuelTankCapacity'] = row[1], row[2], row[3]
#         tanks[row[0]] = tank
#     return tanks


def getPlantInfoFromMachineDetails(machineDetails, plantTypes):
    """
    return tanks: {plantno: {brand, model, fuelTankCapacity}}
    return measureableTanks: {plantno: size}
    return installedPlantList
    """
    tanks = {}
    measureableTanks, topvolumes, bottomvolumes = {}, {}, {}
    installedPlantList = []
    for machineDetail in machineDetails:
        plantno = machineDetail['plantno']
        # which has tanks size and its brand and model
        if machineDetail['fuelTankCapacity']:
            tanks[plantno] = {'brand': machineDetail['brand'], 'model': machineDetail['model'], 'fuelTankCapacity': float(machineDetail['fuelTankCapacity'])}
        # which has measurable tanks size
        if machineDetail['measurabletanksize']:
            measureableTanks[machineDetail['model']] = float(machineDetail['measurabletanksize'])
        if machineDetail['topvolume']:
            topvolumes[machineDetail['model']] = float(machineDetail['topvolume'])
        if machineDetail['bottomvolume']:
            bottomvolumes[machineDetail['model']] = float(machineDetail['bottomvolume'])
        # which install SSME module
        if machineDetail['ssmeBundle']:
            if plantno.startswith(tuple(plantTypes)):
                installedPlantList.append(plantno)
    return tanks, measureableTanks, topvolumes, bottomvolumes, installedPlantList


def getRegistedPlant():
    """
    The plant registered in SSME
    """
    print('Units.CSV reading ... ')
    registeredPlants = set()
    df = pd.read_csv(os.path.join(config.registeredPath, 'Units.CSV'))
    for i, row in df.iterrows():
        registeredPlants.add(row['Unit_PlantNo'])
    return list(registeredPlants)


# def getInstalledPlant__DISCARD(plantTypes):
#     """
#     The plant installed SSME module
#     plantTypes: ['YG', 'PG', 'YLT']
#     """
#     installedPlants = set()
#     print('Reading machine item master ... ')
#     df = pd.read_excel(os.path.join(config.installedSSMEPath, 'Machine Item Master.xlsx'), sheet_name='Item Master', header=0)
#     noNullplantDf = df[df['Plant No'].notnull()]
#     typePlantsDf = noNullplantDf[noNullplantDf['Plant No'].str.startswith(tuple(plantTypes))]
#     noSoldPlantDf = typePlantsDf[typePlantsDf['Status'] != 'SOLD']
#     installedPlantsDf = noSoldPlantDf[noSoldPlantDf['SSME Bundle no.'].notnull()]
#     for i, row in installedPlantsDf.iterrows():
#         installedPlants.add(row['Plant No'])
#     return installedPlants


def append_chart_page(title, image_name, summary=""):
    return (
            r"""
    \newpage
    \backgroundsetup{
    contents={\includegraphics[width=\paperwidth,height=\paperheight]{background.jpg} }
    }
    \BgThispage
    \Huge
    \sffamily
    \textbf{"""
            + f"{title}"
            + r"""}
    \newline
    \includegraphics{"""
            + f"{image_name}"
            + r""".png}
    \begin{center}
    """
            + f"{summary}"
            + r"""
    \end{center}"""
    )


def append_title_page(title):
    return (
            r"""
    \newpage
    \backgroundsetup{
    contents={\includegraphics[width=\paperwidth,height=\paperheight]{"""
            + f"{title}"
            + r"""} }
    }
    \BgThispage
    \begin{center}
    \end{center}
    """
    )
