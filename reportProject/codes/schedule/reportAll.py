from datetime import date
from codes.controllers.ReportHelper import ReportHelper
from codes.models import emailModel
from codes import config

def will_reportAll(doDay):
    if date.today().day != doDay:
        return
    # define the apHelper
    reporthelper = ReportHelper()
    reporthelper.reportController.base_setUp() # getting data setup

    # getting the start and end date string (last month)
    report_start_date, report_start_str, report_end_date, report_end_str = reporthelper.reportController.getReportDuration(monthDelta=1)
    # loop for plants
    reporthelper.reportController.loopForEachPlant(report_start_str=report_start_str, report_end_str=report_end_str, request_plantno=[])
    print('Tex file completed.')
    reporthelper.reportController.tracker.writeCSV()  # write the record csv
    print('SSME summary completed')
    reporthelper.reportController.writePdf(year=str(report_start_date.year), month=str(report_start_date.month))
    print('PDF convert completed.')
    # sending email
    emailModel.sendEmail(contentHtml=config.MONTHLY_REPORT_NOTICE_HTML.format(reporthelper.reportController.report_dir),
                         emailFrom='chris.cheung@aprentalshk.com',
                         emailTo='chris.cheung@aprentalshk.com',
                         fileName='',
                         reportStartDateStr=report_start_str, reportEndDateStr=report_end_str)
    print('Email sent.')
