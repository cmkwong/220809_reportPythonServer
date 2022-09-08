from datetime import date
from codes.controllers.ReportHelper import ReportHelper
from codes.controllers.ServerController import ServerController
from codes.models import emailModel


def will_dailySummary():
    # trigger server to update the unit value
    serverController = ServerController()
    res = serverController.triggerUnitUpdate()
    print(res)

    # define the apHelper
    reporthelper = ReportHelper()
    reporthelper.reportController.base_setUp()  # getting data setup

    # getting the start and end date string
    report_start_date, report_start_str, report_end_date, report_end_str = reporthelper.reportController.getReportDuration(
        endUntil=True)
    # loop for plants
    reporthelper.reportController.loopForEachPlant(reportPdfNeeded=False, report_start_str=report_start_str,
                                                   report_end_str=report_end_str, request_plantno=[])
    # write the csv report
    reporthelper.reportController.tracker.writeCSV()  # write the record csv
    print('SSME summary completed')
    # building html table
    contentHtml = emailModel.buildingHtmlSummaryTable(reporthelper.reportController)
    # send email
    emailModel.sendEmail(contentHtml=contentHtml,
                         emailFrom='chris.cheung@aprentalshk.com',
                         emailTo='chris.cheung@aprentalshk.com, albert.wong@aprentalshk.com',
                         fileName=reporthelper.reportController.tracker.ct + '.csv',
                         reportStartDateStr=report_start_str, reportEndDateStr=report_end_str)
    print('Email sent.')


# get running hour of plant from sqlite manually
def getRunningHour(year, month, plantno, fromDate, toDate=None):
    # define the apHelper
    reporthelper = ReportHelper()

    # mainPath = "C:/Users/chris.cheung.APRENTALSHK/Desktop/Chris/projects/220206_APReport/docs/monthlyReport/sqliteData"
    mainPath = "D:/WebSupervisorData"
    fileName = f"{year}-{str(month).zfill(2)}.sqlite"

    command = f"""
    SELECT * FROM SSME{year}{str(month).zfill(2)} WHERE SSMEName='Running Hours' 
                                and PlantNo='{plantno}'
                                and SSMETimeFrom>='{fromDate}'
    """
    if toDate:
        command += f" and SSMETimeTo<='{toDate}'"

    results = reporthelper.reportController.readSqlite(mainPath, fileName, command)
    if len(results) != 0:
        print(results[0])
        print(results[-1])
    else:
        print('No Data')

# getRunningHour(year=2021,
#                month=7,
#                plantno='YTL105',
#                fromDate='2021-07-01',
#                toDate='2021-07-30')
# will_dailySummary()
# print()
