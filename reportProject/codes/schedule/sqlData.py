from datetime import date
from codes.controllers.ReportHelper import ReportHelper

def will_sqliteData():
    # define the apHelper
    reporthelper = ReportHelper()

    # getting the start and end date string (only this month)
    report_start_date, report_start_str, report_end_date, report_end_str = reporthelper.reportController.getReportDuration()
    # process last month data
    reporthelper.reportController.processMonthToSqlite(year=str(report_start_date.year), month=str(report_start_date.month))
    # completed notice
    print('SQLite file prepare finished.')

# upload the unit value to mySQL from CSV
def will_sqlData():
    pass