import os
import socket
from codes.utils import sysModel

# project_path
SER_PATH = sysModel.getTargetPath('220809_reportPythonServer')
PRJ_PATH = os.path.join(SER_PATH, 'reportProject')
paramPath = os.path.join(PRJ_PATH, 'codes')
# ------------------------------------------------------------------------------------------
hostname = socket.gethostname()
if (hostname == 'APDC-DATA02'):
    LOCATION = 'prod'  # dev / prod
else:
    LOCATION = 'dev'

# dev (Notebook environment)
if (LOCATION == 'dev'):
    monthlyReportDocsPath = os.path.join(PRJ_PATH, 'docs/monthlyReport')
    reportDataPath = os.path.join(monthlyReportDocsPath, "reportData")  # csv path
    sqliteOutPath = os.path.join(monthlyReportDocsPath, "sqliteData")  # sqlite path
    inoutRecordPath = os.path.join(monthlyReportDocsPath, "inOutRecord")
    logsPath = os.path.join(monthlyReportDocsPath, "logs")
    reportPath = os.path.join(monthlyReportDocsPath, "reports")
    pdfImagesPath = os.path.join(monthlyReportDocsPath, "pdfImages")
    tankSizePath = os.path.join(monthlyReportDocsPath, "tankSize")
    registeredPath = os.path.join(monthlyReportDocsPath, 'registerPlant')
    installedSSMEPath = os.path.join(monthlyReportDocsPath, 'installedSSME')
    tempPath = os.path.join(monthlyReportDocsPath, "pdfImages/temp")  # for storing the plot graph
    tempComparePlotsPath = os.path.join(
        "C:/Users/chris.cheung.APRENTALSHK/Desktop/Chris/projects/220219_APWebServer/dev-data/compareReport/plots")  # for storing the compare plot graph
    # terex report (move from generated dir to shared dir)
    terexReportFolder = os.path.join(monthlyReportDocsPath, "terexReport/reportFolder")
    terexReoirtSharedFolder = os.path.join(monthlyReportDocsPath, "terexReport/sharedFolder")
    nodeJsServerUrl = 'http://localhost:3001'
    # HK key project path
    keyProjectPath = 'C:/Users/chris.cheung.APRENTALSHK/Desktop/Chris/projects/211207_APrental/AP_creditFacility/docs/01. Request'

# prod (apdc-data02 environment)
elif (LOCATION == 'prod'):
    # prod (In server)
    monthlyReportDocsPath = os.path.join(PRJ_PATH, 'docs/monthlyReport')
    reportDataPath = "D:\\WebSupervisorData"  # csv path
    sqliteOutPath = os.path.join("D:\\SSME Reports\\v2", "sqliteData")  # sqlite path
    inoutRecordPath = "\\\\apdc-data01\\UserData\\BA"
    logsPath = os.path.join(monthlyReportDocsPath, "logs")
    reportPath = "\\\\apdc-data02\\SSME Reports\\v2"
    pdfImagesPath = os.path.join(monthlyReportDocsPath, "pdfImages")
    tankSizePath = "C:\\SSME_Python\\Data"
    registeredPath = '\\\\apdc-data01\\ComApAPIData\\Units'
    installedSSMEPath = '\\\\apdc-dc01\\ShareData\\Data\\Inventory\\Machine\\Plant Master'
    tempPath = os.path.join(monthlyReportDocsPath, "pdfImages/temp")  # for storing the plot graph
    tempComparePlotsPath = os.path.join(
        "C:/Users/itsupport/projects/220219_APWebServer/dev-data/compareReport/plots")  # for storing the compare plot graph
    # terex report (move from generated dir to shared dir)
    terexReportFolder = "C:\\Terex_Python\\Reports"
    terexReoirtSharedFolder = "\\\\apdc-dc01\\ShareData\\Data\\WS-TA\\07.Tunneling\\Operator\\Terex   TA400\\ISM Reports"
    nodeJsServerUrl = 'http://localhost:3001'
    # HK key project path
    keyProjectPath = '\\\\apdc-data01\\UserData\\MP'

colNameTable = {
    "Date": "Datetime",
    "Fuel Level": "fuel_level",
    "Fuel level": "fuel_level",  # that is noisy fuel level, need to filter out the zero fuel-level
    "Nomin power": "nominal_power",
    "Nominal Power": "nominal_power",
    "actual_power": "actual_power",
    "Act power": "actual_power",
    "Load kW": "actual_power",
    "Load P": "actual_power",
    "Generator kW": "actual_power",
    "Genset kWh": "kwh",
    "kWh (Import)": "kwh",
    "RPM": "rpm",
    "Genset kVArh": "kvarh",
    "kVArhours": "kvarh",
    "Running Hours": "run_hours",
    "Run hours": "run_hours",
    "Total Fuel Consumption": "fuel_cons",
    # 'BatteryVoltage' : 'battery_v',
    # 'CoolantTemp' : 'coolant_temp',
    # 'Oil Press' : 'oil_pressure',
    # 'Fuel Rate' : 'fuel_rate',
    # 'Engine Speed (RPM)' : 'engine_rpm',
    # 'Nominal RPM' : 'nominal_rpm',
    # 'Water temp' : 'water_temp',
    # 'Coolant Temp' : 'water_temp',
}

# for replace the item master column into database col name
itemMasterColName = {
    "Company Code": "companycode",
    "Plant No": "plantno",
    "Old Plant No": "oldPlantno",
    "Status": "status",
    "Product Class": "productClass",
    "Product Category": "productCategory",
    "Product Standard": "productStandard",
    "Products Capabity": "productsCapabity",
    "UOM": "uom",
    "Products Description": "productsDescription",
    "Brand": "brand",
    "Model": "model",
    "Serial No": "serialNo",
    "Measurement (LxWxH) m": "measurement",
    "Gross Weight (KG)": "grossWeight",
    "Fuel Tank Capacity (L)": "fuelTankCapacity",
    "Coolant Volumn": "coolantVolumn",
    "Hydraulic Oil Volumn": "hydraulicOilVolumn",
    "Base Unit": "baseUnit",
    "Purchase Order No.": "purchaseOrderNo",
    "Supplier Code": "supplierCode",
    "Maker": "maker",
    "Origin": "origin",
    "Manufacturer Year (YYYY)": "manufacturerYear",
    "Manufacturer Month (MM)": "manufacturerMonth",
    "Currency": "currency",
    "Unit Price (corr to currency)": "unitPriceCC",
    "Unit Price": "unitPrice",
    "Payment Terms": "paymentTerms",
    "Delivery Terms": "deliveryTerms",
    "Physical Condition (Purchase in)": "physicalCondition",
    "Engine Family Model": "engineFamilyModel",
    "Engine Model": "engineModel",
    "Engine Serial No": "engineSerialNo",
    "Engine Family No": "engineFamilyNo",
    "Engine Manufacturer Year": "engineManufacturerYear",
    "Engine Emission Standard \n(T2, T3, T4)": "engineEmissionStandard",
    "Emission Standard (MLIT / CE)": "emissionStandard",
    "Power Source": "powerSource",
    "Rated Output": "ratedOutput",
    "Rated Output (50Hz)": "ratedOutput50hz",
    "Engine Oil Volumn": "engineOilVolumn",
    "Options": "options",
    "SSME Bundle no.": "ssmeBundle",
}

keyProjectColName = {
    "Key Project": "keyProject",
    " Project Code": "projectCode",
    "Contract No.": "contractNo",
    "Contract Title": "contractTitle",
    "Main Contractor": "mainContractor",
    "Responsible Salesman": "responsibleSalesman",
    "Contract Award Date": "contractAwardDate",
    "Estimated End Date": "estimatedEndDate",
    "Contract Amount (MHKD)": "contractAmount",
    "Update on": "updateOn",
    "link for reference": "link"
}

# outlook
OUTLOOK_SERVER = '192.168.10.223:587'
OUTLOOK_LOGIN = "chris.cheung@aprentalshk.local"
OUTLOOK_PW = "#AP.20211206..."

# ------------------------------- html -----------------------------------
DEFAULT_HTML = """
<h2>Testing</h2>
"""

DAILY_SUMMARY_HTML = """
                    <style>
                      * {
                        box-sizing: border-box;
                      }
                      table,
                      td {
                        border: 1px solid black;
                        text-align: center;
                      }
                      .header-row {
                        height: 30px;
                      }
                      /* table {
                        width: 1000px;
                      } */
                      .table-container {
                        margin: 30px;
                      }
                      .header {
                        font-weight: 700;
                        font-size: 18px;
                      }
                      .black {
                        background-color: black;
                      }
                      .red {
                        background-color: rgb(255, 94, 0);
                        color: white;
                      }
                      .yellow {
                        background-color: rgb(255, 230, 0);
                      }
                      .green {
                        background-color: rgb(0, 255, 34);
                        color: white;
                      }
                      .grey {
                        background-color: rgb(102, 102, 102);
                        color: white;
                      }
                      .small-width {
                        width: 100px;
                      }
                      .meddle-width {
                        width: 200px;
                      }
                      .wide-width {
                        width: 400px;
                      }
                    </style>
                    <body>
                      <h2>SSME Daily Report</h2>
                      <div class="table-container">
                        <table>
                          <tr class="header-row">
                            <td class="small-width"></td>
                            <td class="small-width header">Data</td>
                            <td class="wide-width" colspan="2">Yes</td>
                            <td class="wide-width" colspan="2">No</td>
                          </tr>
                          <tr class="header-row">
                            <td></td>
                            <td class="header">IN/OUT</td>
                            <td class="middle-width">Yes</td>
                            <td class="middle-width">No</td>
                            <td class="middle-width">Yes</td>
                            <td class="middle-width">No</td>
                          </tr>
                          <tr>
                            <td class="header">Registered</td>
                            <td class="header">Installed</td>
                            <td class="black"></td>
                            <td class="black"></td>
                            <td class="black"></td>
                            <td class="black"></td>
                          </tr>
                          <tr>
                            <td rowspan="2">Yes</td>
                            <td>Yes</td>
                            <td class="green">(1,1,1,1)</td>
                            <td>(1,1,1,0)</td>
                            <td class="red">(1,1,0,1)</td>
                            <td>(1,1,0,0)</td>
                          </tr>
                          <tr>
                            <td>No</td>
                            <td class="yellow">(1,0,1,1)</td>
                            <td class="yellow">(1,0,1,0)</td>
                            <td class="yellow">(1,0,0,1)</td>
                            <td class="yellow">(1,0,0,0)</td>
                          </tr>
                          <tr>
                            <td rowspan="2">No</td>
                            <td>Yes</td>
                            <td class="yellow">(0,1,1,1)</td>
                            <td class="yellow">(0,1,1,0)</td>
                            <td class="yellow">(0,1,0,1)</td>
                            <td class="yellow">(0,1,0,0)</td>
                          </tr>
                          <tr>
                            <td>No</td>
                            <td class="red">(0,0,1,1)</td>
                            <td class="red">(0,0,1,0)</td>
                            <td>(0,0,0,1)</td>
                            <td>(0,0,0,0)</td>
                          </tr>
                        </table>
                      </div>
                    </body>
"""

MONTHLY_REPORT_NOTICE_HTML = """
<div>
  <p>Dear Sir/Madam,</p>
  <p style="padding-left: 20px">The report is out.</p>
  <p style="padding-left: 20px">
    Please check
    <a href="{}">HERE</a>
  </p>
</div>
"""

TEREX_REPORT_MOVEMENT_NOTICE_HTML = """
<div>
  <p>Dear Sir/Madam,</p>
  <p style="padding-left: 20px">The Terex files is moved on this path:</p>
  <p style="padding-left: 40px">{}</p>
</div>
"""

FOOTER_HTML = """
    <footer>
        <p style="color: #b3b3cc;">This is system message from SSME.</p>
        <p style="color: #b3b3cc;">Do not reply to this email.</p>
        <p style="color: #b3b3cc;">Thank you.</p>
    </footer>
"""
