from datetime import datetime
import numpy as np

class ReportLogic:
    def __init__(self, tracker):
        self.tracker = tracker
        self.summaryTable = self.init_summaryTable()

    def init_summaryTable(self):
        """
        return dic: {[registered, installed, data, IN/OUT] = 0}
        """
        summaryTable = {}
        mesh = np.array(np.meshgrid([0, 1], [0, 1], [0, 1], [0, 1]))
        combinations = mesh.T.reshape(-1, 4)
        for combination in combinations:
            key = tuple(combination.tolist())
            summaryTable[key] = 0
        return summaryTable

    def updateSummaryTable(self, PlantData):
        registered = int(bool(PlantData.register))
        installed = int(bool(PlantData.installed))
        data = int(not PlantData.rawData.empty)
        inout = int(bool(PlantData.inout))
        self.summaryTable[(registered, installed, data, inout)] += 1

    def getCompanyDatas(self, PlantData, custCode2Name, report_start_str, report_end_str):
        """
        checking logic by PlantData
        return: { companyName: {data: dataframe (within record-out and record-in),
                                out: datetime,
                                in: datetime}
                }
        """
        companyDatas = {}
        if not PlantData.fuelTankCapacity:
            # print(f"Unable to find PlantNo {PlantData.plantno} tank size")
            # self.logger.warning(f"{PlantData.plantno}:fuel tank: not listed in 'Denyo plants.xlsx / LightTowers.xlsx'")
            msg = f"{PlantData.plantno}:fuel tank: not listed in Denyo plants.xlsx / LightTowers.xlsx"
            self.tracker.logging(msg, 'warning')
            raise Exception(msg)

        # just warning
        if not PlantData.measurabletanksize:
            msg = f"{PlantData.plantno}: Unable to find Measureable Volumn, Model No: {PlantData.model}"
            self.tracker.logging(msg, 'warning')
            self.tracker.updateRecord(PlantData, msg)

        # update summary table (sum up the table that going to show in email)
        self.updateSummaryTable(PlantData)

        if PlantData.register and PlantData.installed:
            if not PlantData.rawData.empty and PlantData.inout:
                for record in PlantData.inout.values(): # PlantData.inout is dictionary: {0: {companyName, outDate, inDate}}
                    accountCode = '11000' + record['custCode']
                    companyName = custCode2Name[accountCode]
                    record_out = record['out']
                    record_in = record['in']
                    companyDatas[accountCode] = {}
                    companyDatas[accountCode]['companyName'] = companyName
                    companyDatas[accountCode]['data'] = PlantData.rawData[(PlantData.rawData.index >= record_out) & (PlantData.rawData.index <= record_in)]
                    companyDatas[accountCode]['out'] = record_out
                    companyDatas[accountCode]['in'] = record_in
                return companyDatas

            elif not PlantData.rawData.empty and not PlantData.inout:
                msg = f"{PlantData.plantno}: No IN/OUT record but having data between {report_start_str} and {report_end_str} (Registered and installed SSME)"
                self.tracker.logging(msg, 'info')
                self.tracker.updateRecord(PlantData, msg)
                # outputing the data but without customer code
                accountCode = 'NA'
                record_out = datetime.strptime(report_start_str, "%Y-%m-%d %H:%M:%S")
                record_in = datetime.strptime(report_end_str, "%Y-%m-%d %H:%M:%S")
                companyDatas[accountCode] = {}
                companyDatas[accountCode]['companyName'] = 'NA'
                companyDatas[accountCode]['data'] = PlantData.rawData[(PlantData.rawData.index >= record_out) & (PlantData.rawData.index <= record_in)]
                companyDatas[accountCode]['out'] = record_out
                companyDatas[accountCode]['in'] = record_in
                return companyDatas

            elif PlantData.rawData.empty and PlantData.inout:
                msg = f"{PlantData.plantno}: Having IN/OUT record but no data available between {report_start_str} and {report_end_str} (Registered and installed SSME)"
                self.tracker.logging(msg, 'warning')
                raise Exception(msg)

            elif PlantData.rawData.empty and not PlantData.inout:
                msg = f"{PlantData.plantno}: No IN/OUT record and no data available between {report_start_str} and {report_end_str} (Registered and installed SSME)"
                self.tracker.logging(msg, 'info')
                self.tracker.updateRecord(PlantData, msg, True) # update the heath as good, because it is normal
                return companyDatas

        elif PlantData.register and not PlantData.installed:
            if not PlantData.rawData.empty and PlantData.inout:
                msg = f"{PlantData.plantno}: Have data and IN/OUT (Registered but not installed SSME)"
                self.tracker.logging(msg, 'error')
                raise Exception(msg)

            elif not PlantData.rawData.empty and not PlantData.inout:
                msg = f"{PlantData.plantno}: Have data but no IN/OUT (Registered but not Installed SSME)"
                self.tracker.logging(msg, 'error')
                raise Exception(msg)

            elif PlantData.rawData.empty and PlantData.inout:
                msg = f"{PlantData.plantno}: Have IN/OUT record but no data (Registered but not Installed SSME)"
                self.tracker.logging(msg, 'warning')
                raise Exception(msg)

            elif PlantData.rawData.empty and not PlantData.inout:
                msg = f"{PlantData.plantno}: Have no IN/OUT record and no data (Registered but not Installed SSME)"
                self.tracker.logging(msg, 'warning')
                raise Exception(msg)

        elif not PlantData.register and PlantData.installed:
            if not PlantData.rawData.empty and PlantData.inout:
                msg = f"{PlantData.plantno}: Have data and IN/OUT (Installed but not registered SSME)"
                self.tracker.logging(msg, 'error')
                raise Exception(msg)

            elif not PlantData.rawData.empty and not PlantData.inout:
                msg = f"{PlantData.plantno}: Have data but no IN/OUT (Installed but not registered SSME)"
                self.tracker.logging(msg, 'error')
                raise Exception(msg)

            elif PlantData.rawData.empty and PlantData.inout:
                msg = f"{PlantData.plantno}: Have IN/OUT record but no data (Installed but not registered SSME)"
                self.tracker.logging(msg, 'warning')
                raise Exception(msg)

            elif PlantData.rawData.empty and not PlantData.inout:
                msg = f"{PlantData.plantno}: Have no IN/OUT record and no data (Installed but not registered SSME)"
                self.tracker.logging(msg, 'warning')
                raise Exception(msg)

        elif not PlantData.register and not PlantData.installed:
            if not PlantData.rawData.empty and PlantData.inout:
                msg = f"{PlantData.plantno}: Have data and IN/OUT (Not Installed and not registered SSME)"
                self.tracker.logging(msg, 'error')
                raise Exception(msg)

            elif not PlantData.rawData.empty and not PlantData.inout:
                msg = f"{PlantData.plantno}: Have data but no IN/OUT (Not Installed and not registered SSME)"
                self.tracker.logging(msg, 'error')
                raise Exception(msg)

            elif PlantData.rawData.empty and PlantData.inout:
                msg = f"{PlantData.plantno}: Have IN/OUT record but no data (Not Installed and not registered SSME)"
                self.tracker.logging(msg, 'info')
                raise Exception(msg)

            elif PlantData.rawData.empty and not PlantData.inout:
                msg = f"{PlantData.plantno}: Have no IN/OUT record and no data (Not Installed and not registered SSME)"
                self.tracker.logging(msg, 'info')
                raise Exception(msg)