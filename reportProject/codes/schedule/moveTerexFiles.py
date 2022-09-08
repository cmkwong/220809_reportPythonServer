import shutil
import os

from utils import fileModel
from codes import config
from codes.controllers.ReportHelper import ReportHelper
from codes.models import emailModel

def will_moveTerexFiles():
    # define the apHelper
    reporthelper = ReportHelper()

    # getting the start and end date string
    report_start_date, report_start_str, report_end_date, report_end_str = reporthelper.reportController.getReportDuration(monthDelta=1)

    # check if file exist
    targetTerexFileName = '{}-{}'.format(report_start_date.year, str(report_start_date.month).zfill(2))
    reportFileList = fileModel.getFileList(config.terexReportFolder)
    sharedFileList = fileModel.getFileList(config.terexReoirtSharedFolder)
    # not last month report generated yet
    if targetTerexFileName not in reportFileList:
        return
    # shared dir already has the target month report
    elif targetTerexFileName in sharedFileList:
        return
    else:
        source = os.path.join(config.terexReportFolder, targetTerexFileName)
        destination = os.path.join(config.terexReoirtSharedFolder, targetTerexFileName)
        shutil.copytree(source, destination)
        print(f"The file is copied from {source} to {destination}")
    # sending email
    emailModel.sendEmail(contentHtml=config.TEREX_REPORT_MOVEMENT_NOTICE_HTML.format(config.terexReportFolder),
                         emailFrom='chris.cheung@aprentalshk.com',
                         emailTo='chris.cheung@aprentalshk.com',
                         fileName='',
                         reportStartDateStr=report_start_str, reportEndDateStr=report_end_str)
    print('Email sent.')