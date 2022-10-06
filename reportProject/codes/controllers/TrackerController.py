import pandas as pd
import os
import logging
from datetime import datetime

from codes import config


class Tracker:
    def __init__(self):
        self.logger = self.loggingSetup()  # logging in text
        self.plantRecord = {}
        # self.debugPlantRecord = {}
        # self.debugPlants = []

    def loggingSetup(self):
        # logging setup
        self.ct = datetime.strftime(datetime.now(), "%Y%m%dT%H%M%S")
        log_file = os.path.join(config.logsPath, f"{self.ct}.log")

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # or whatever
        handler = logging.FileHandler(log_file, 'w', 'utf-8')  # or whatever
        logger.addHandler(handler)
        # logging.basicConfig(filename=log_file, filemode="w", level=logging.INFO)
        return logger

    def initCsvDf(self):
        columnsNames = ['plantno', 'report', 'data', 'inout', 'register', 'installed', 'fuelTankCapacity',
                        'measurabletanksize', 'msg']
        df = pd.DataFrame(columns=columnsNames)
        df = df.set_index('plantno')
        return df

    def logging(self, msg='', logType='info'):
        """
        if plantno exist, append to
        """
        if logType == 'error':
            self.logger.error(msg)
        elif logType == 'warning':
            self.logger.warning(msg)
        elif logType == 'info':
            self.logger.info(msg)
        print(msg)

    def updateRecord(self, PlantData, msg='', reportOk=False):
        # init the plant record, if no plant record before
        if PlantData.plantno not in self.plantRecord.keys():
            self.plantRecord[PlantData.plantno] = {}
            self.plantRecord[PlantData.plantno]['msg'] = ''
        self.plantRecord[PlantData.plantno]['report'] = 'yes' if reportOk else 'no'
        self.plantRecord[PlantData.plantno]['data'] = 'yes' if not PlantData.rawData.empty else 'no'
        self.plantRecord[PlantData.plantno]['inout'] = 'yes' if PlantData.inout else 'no'
        self.plantRecord[PlantData.plantno]['register'] = 'yes' if PlantData.register else 'no'
        self.plantRecord[PlantData.plantno]['installed'] = 'yes' if PlantData.installed else 'no'
        self.plantRecord[PlantData.plantno]['fuelTankCapacity'] = 'yes' if PlantData.fuelTankCapacity else 'no'
        self.plantRecord[PlantData.plantno]['measurabletanksize'] = 'yes' if PlantData.measurabletanksize else 'no'
        if msg: self.plantRecord[PlantData.plantno][
            'msg'] = f"{self.plantRecord[PlantData.plantno]['msg']}\n{msg}".strip()  # concat msg
        # if debug: self.debugPlants.append(PlantData.plantno)

    def updateHealth(self, plantno, reportOk=True):
        self.plantRecord[plantno]['report'] = 'good' if reportOk else 'error'

    def writeCSV(self):
        recordCSV = self.initCsvDf()
        # recordCSV_debug = self.initCsvDf()
        for plantno, dicData in self.plantRecord.items():
            series = pd.Series(dicData, name=plantno)
            recordCSV = recordCSV.append(series)  # if not debug, append on recordCSV
            # recordCSV_debug = recordCSV_debug.append(series)                            # append all record
        recordCSV.to_csv(os.path.join(config.logsPath, f"{self.ct}.csv"))
        # recordCSV_debug.to_csv(os.path.join(config.logsPath, f"{self.ct}_debug.csv"))
        self.logging("Wrote CSV ok.", 'info')
