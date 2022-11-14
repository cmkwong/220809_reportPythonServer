from codes import config
from codes.models import excelModel
import requests
from datetime import date
import json


class NodeJsServerController:
    def __init__(self):
        # main URL
        self.mainUrl = config.nodeJsServerUrl
        # get token
        self.getWebServerTokenUrl = self.mainUrl + '/api/v1/auth/getToken'
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
        self.getCustInfoUrl = self.mainUrl + '/api/v1/workflow/customer?wfserver=prod'
        # upload the monthly ssme data into database
        self.uploadMonthlySsmeDataUrl = self.mainUrl + '/api/v1/ssme/month/data?wfserver=dev'

        # ------------------ getting token to work ------------------
        self.token = self.getWebServerToken()

    # get the token from webserver (login)
    def getWebServerToken(self):
        today = date.today()
        timeStr = today.strftime("%Y-%m-%d %H:%M:%S")
        body = {
            "username": config.WEB_LOGINNAME,
            "password": config.WEB_PASSWORD,
            "payload": timeStr
        }
        r = requests.post(self.getWebServerTokenUrl, json=body)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            raise Exception("Cannot get the token from webserver. ")
        return res['token']

    # renew the machine master through server API to mySQL database
    def uploadMachineItemMaster(self):

        # read as dataframe
        df = excelModel.readMachineItemMaster()

        # update records to server
        records = df.fillna('').to_dict('records')  # records is a parameter from pd.DataFrame

        # build header
        headers = {"Authorization": f"Bearer {self.token}"}

        # send to server
        body = {'data': records}
        r = requests.post(self.renewMachineItemMasterUrl, json=body, headers=headers)
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

        # build header
        headers = {"Authorization": f"Bearer {self.token}"}

        # send to server
        body = {'data': records}
        r = requests.post(self.renewHkKeyProjectUrl, json=body, headers=headers)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return True

    # getting all plant needed details
    def getMachineDetails(self):
        print('Getting plant data from server ... ')
        # build header
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.get(self.getMachineDetailsUrl, headers=headers)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return res['data']

    # trigger server to get Unit update
    def triggerUnitUpdate(self):
        print('Trigger server to update unit ... ')
        # build header
        headers = {"Authorization": f"Bearer {self.token}"}
        r = requests.get(self.triggerUnitUpdateUrl, headers=headers)
        res = r.json()  # res has the data fetching from websupervisor
        if r.status_code != 200:
            print(r.text)
            return False
        return res

    # upload the unit values
    def uploadUnitValues(self, tableName, datas):
        # build header
        headers = {"Authorization": f"Bearer {self.token}"}
        # build body
        body = {
            "tableName": tableName,
            "data": datas
        }
        r = requests.post(self.uploadUnitValuesUrl, json=body, headers=headers)
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
        # build header
        headers = {"Authorization": f"Bearer {self.token}"}
        # build body
        body = {
            "plantno": plantno,
            "datefrom": datetimefrom,
            "dateto": datetimeto
        }
        r = requests.get(self.getUnitValuesUrl, json=body, headers=headers)
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
        # build header
        headers = {"Authorization": f"Bearer {self.token}"}
        # build body
        body = {
            "datefrom": datetimefrom,
            "dateto": datetimeto
        }
        r = requests.get(self.getDistinctPlantnoUrl, json=body, headers=headers)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return res['results']  # return data

    # get the ssme variables
    def getVariable_DISCARD(self, varName):
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
    def updateVariable_DISCARD(self, varName, varValue):
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
        # build header
        headers = {"Authorization": f"Bearer {self.token}"}
        # build body
        r = requests.get(self.getRowTotalUrl.format(tableName), headers=headers)
        res = r.json()
        if r.status_code != 200:
            print(r.text)
            return False
        return res['result'][0]['count']

    def getPlotImage_DISCARD(self, legends, X, Ys, plotType='line', path='./', filename='image.png'):
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
        # build header
        headers = {"Authorization": f"Bearer {self.token}"}
        # build request
        r = requests.get(self.getCustInfoUrl, headers=headers)
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
        # build header
        headers = {"Authorization": f"Bearer {self.token}"}
        # build request
        r = requests.post(self.uploadMonthlySsmeDataUrl, json=dataDict, headers=headers)
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
