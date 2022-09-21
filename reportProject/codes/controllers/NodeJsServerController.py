from codes import config
from codes.models import excelModel
import requests
import json


class NodeJsServerController:
    def __init__(self):
        # main URL
        self.mainUrl = config.serverUrl
        # upload unit values
        self.uploadUnitValuesUrl = self.mainUrl + '/api/v1/ssme/unitValues/upload'
        # get unit values
        self.getUnitValuesUrl = self.mainUrl + '/api/v1/ssme/unitValues/get'
        # get distinct plant no
        self.getDistinctPlantnoUrl = self.mainUrl + '/api/v1/ssme/units/plantno'
        # renew the machine master excel from Sam
        self.renewMachineItemMasterUrl = self.mainUrl + '/api/v1/machine/itemmaster'
        # get the key project from Hugo
        self.renewHkKeyProjectUrl = self.mainUrl + '/api/v1/workflow/renew/hkkeyproject'
        # get machine details from mySQL
        self.getMachineDetailsUrl = self.mainUrl + '/api/v1/machine/getDetail'
        # trigger server to fetch the unit values and upload to mySQL
        self.triggerUnitUpdateUrl = self.mainUrl + '/api/v1/ssme/units/fetchAndUpload'
        # get table row total
        self.getRowTotalUrl = self.mainUrl + '/api/v1/ssme/rowtotal?table={}'
        # access internal variable
        self.accessVariableUrl = self.mainUrl + '/api/v1/ssme/variables'
        # image plot generate
        self.plotGenerateUrl = self.mainUrl + '/api/v1/report/ssme/plot?type={}'
        # get the customer info from production
        self.getCustInfoUrl = self.mainUrl + '/api/v1/workflow/customer?server=prod'
        # upload the monthly ssme data into database
        self.uploadMonthlySsmeDataUrl = self.mainUrl + '/api/v1/workflow/ssme/data?server=dev'

    # renew the machine master through server API to mySQL database
    def uploadMachineItemMaster(self):

        # read as dataframe
        df = excelModel.readMachineItemMaster()

        # update records to server
        records = df.fillna('').to_dict('records')  # records is a parameter from pd.DataFrame

        # send to server
        body = {'data': records}
        r = requests.post(self.renewMachineItemMasterUrl, json=body)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return True

    # mainly for credit facility workflow
    def uploadHkKeyProject(self):
        # read as dataframe
        df = excelModel.readKeyProject()

        # update records to server
        records = df.fillna('').to_dict('records')

        # send to server
        body = {'data': records}
        r = requests.post(self.renewHkKeyProjectUrl, json=body)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return True

    # getting all plant needed details
    def getMachineDetails(self):
        print('Getting plant data from server ... ')
        r = requests.get(self.getMachineDetailsUrl)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return res['data']

    # trigger server to get Unit update
    def triggerUnitUpdate(self):
        print('Trigger server to update unit ... ')
        r = requests.get(self.triggerUnitUpdateUrl)
        res = r.json()  # res has the data fetching from websupervisor
        if r.status_code != 200:
            print(r.text)
            return False
        return res

    # upload the unit values
    def uploadUnitValues(self, tableName, datas):
        body = {
            "tableName": tableName,
            "data": datas
        }
        r = requests.post(self.uploadUnitValuesUrl, json=body)
        if r.status_code != 200:
            print(r.text)
            return False
        return True

    # get unit values
    def getUnitValues(self, plantno, datetimefrom, datetimeto):
        """
        plantno: str
        datetimefrom: str: 2022-07-20 00:00:00
        datetimeto: str 022-08-20 23:59:59
        """
        body = {
            "plantno": plantno,
            "datefrom": datetimefrom,
            "dateto": datetimeto
        }
        r = requests.get(self.getUnitValuesUrl, json=body)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return res['results']  # return data

    # get distinct plantno
    def getDistinctPlantno(self, datetimefrom, datetimeto):
        """
        datetimefrom: str
        datetimeto: str
        """
        body = {
            "datefrom": datetimefrom,
            "dateto": datetimeto
        }
        r = requests.get(self.getDistinctPlantnoUrl, json=body)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return res['results']  # return data

    # get the ssme variables
    def getVariable(self, varName):
        body = {
            'varName': varName
        }
        r = requests.get(self.accessVariableUrl, json=body)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return res['result'][0]['varValue']

    # update the ssme variables
    def updateVariable(self, varName, varValue):
        body = {
            'varName': varName,
            'varValue': varValue
        }
        r = requests.post(self.accessVariableUrl, json=body)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return True

    # count the table rows
    def getTableRowTotal(self, tableName):
        r = requests.get(self.getRowTotalUrl.format(tableName))
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return res['result'][0]['count']

    def getPlotImage(self, legends, X, Ys, plotType='line', path='./', filename='image.png'):
        Ys_data = {}
        for i, legend in enumerate(legends):
            Ys_data[legend] = Ys[i]
        body = {
            'X': X,
            'Ys': Ys_data,
            'path': path,
            'filename': filename
        }
        r = requests.post(self.plotGenerateUrl.format(plotType), json=body)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return res

    # get customer info customer code - customer name
    def getCustInfo(self):
        r = requests.get(self.getCustInfoUrl)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        custCode2Name = {}
        for d in res['data']:
            custCode2Name[d['CUSTOMERCODE']] = d['CUSTOMERNAME']
        return custCode2Name

    # post the monthly data into database
    def postMonthlyData(self, dataDict):
        r = requests.post(self.uploadMonthlySsmeDataUrl, json=dataDict)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return res

# import pandas as pd
# serverController = NodeJsServerController()
# data = serverController.getUnitValues("PG1147", "2022-07-20 00:00:00", "2022-08-19 23:59:59")
# serverController.getCustInfo()
# print()
