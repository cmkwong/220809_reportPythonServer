import pandas as pd
import os
from codes.utils import dicModel, listModel, dfModel, fileModel

def readExcel(path, required_sheets, concat=True):
    dfs = pd.read_excel(path, sheet_name=None, header=1)
    required_dfs = {}
    dfs = dicModel.changeCase(dfs, case='l')    # change sheet name of read excel case to lower
    required_sheets = listModel.changeCase(required_sheets, case='l')   # change required name case to lower
    for sheet_name in required_sheets:
        if sheet_name.lower() in dfs.keys():   # check if required sheet in excel file
            required_dfs[sheet_name] = dfs[sheet_name]
    if concat:
        return dfModel.concatDfs(required_dfs)
    return required_dfs

def xlsx2csv(main_path):
    """
    note 84d
    :param main_path: str, the xlsx files directory
    :return:
    """
    files = fileModel.getFileList(main_path, reverse=False)
    for file in files:
        # read excel file
        excel_full_path = os.path.join(main_path, file)
        print("Reading the {}".format(file))
        df = pd.read_excel(excel_full_path, header=None)

        # csv file name
        csv_file = file.split('.')[0] + '.csv'
        csv_full_path = os.path.join(main_path, csv_file)
        print("Writing the {}".format(csv_file))
        df.to_csv(csv_full_path, encoding='utf-8', index=False, header=False)
    return True

def transfer_all_xlsx_to_csv(main_path):
    """
    note 84d
    :param main_path: str, the xlsx files directory
    :return:
    """
    files = fileModel.getFileList(main_path, reverse=False)
    for file in files:
        # read excel file
        excel_full_path = os.path.join(main_path, file)
        print("Reading the {}".format(file))
        df = pd.read_excel(excel_full_path, header=None)

        # csv file name
        csv_file = file.split('.')[0] + '.csv'
        csv_full_path = os.path.join(main_path, csv_file)
        print("Writing the {}".format(csv_file))
        df.to_csv(csv_full_path, encoding='utf-8', index=False, header=False)
    return True