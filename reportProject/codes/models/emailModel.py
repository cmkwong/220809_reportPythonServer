import os
import re
from datetime import datetime
from codes import config

import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

def strPatternReplace(targetCode, replaceDict, subCodePattern=''):
    """
    :param targetCode: str, that being replaced
    :param replaceDict: {} replace the subCodePattern into empty or not
    :param subCodePattern: eg: include '_panel.php';
    :return: PMCodes
    """
    # insert the _file.php first

    subCodeNames = re.findall(subCodePattern, targetCode)  # getting all names of include lib
    for subCodeName in subCodeNames:
        # convert into tuple
        key = tuple(int(i) for i in subCodeName.replace('(', '').replace(')', '').split(','))
        targetCode = re.sub(subCodePattern, str(replaceDict[key]), targetCode, count=1) # replace 1-by-1 sequentially
    return targetCode

def buildingHtmlSummaryTable(reportController=None):
    if not reportController:
        return
    replaceDict = reportController.reportLogic.summaryTable
    htmlTable = strPatternReplace(config.DAILY_SUMMARY_HTML, replaceDict, '\(\d,\d,\d,\d\)')
    return htmlTable

def getAttachment(path, fileName, attachFileName):
    fileToSend = os.path.join(path, fileName)
    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend)
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "image":
        fp = open(fileToSend, "rb")
        attachment = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "audio":
        fp = open(fileToSend, "rb")
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
    # attachment
    attachmentFileName = f"{attachFileName}.csv"
    attachment.add_header("Content-Disposition", "attachment", filename=attachmentFileName)
    return attachment

def sendEmail(contentHtml=config.DEFAULT_HTML, *,
              emailFrom:str, emailTo:str, fileName:str, reportStartDateStr:str, reportEndDateStr:str):
    abbreviatedStartDateStr = datetime.strptime(reportStartDateStr, '%Y-%m-%d').strftime('%d %B %Y')
    abbreviatedEndDateStr = datetime.strptime(reportEndDateStr, '%Y-%m-%d').strftime('%d %B %Y')

    msg = MIMEMultipart()
    msg["From"] = emailFrom
    msg["To"] = emailTo
    msg["Subject"] = f"SSME Report Summary - {abbreviatedStartDateStr} - {abbreviatedEndDateStr}"
    msg.preamble = f"SSME Report Summary - {abbreviatedStartDateStr} - {abbreviatedEndDateStr}"

    # get attachment
    if fileName and (os.path.exists(os.path.join(config.logsPath, fileName))):
        attachment = getAttachment(config.logsPath, fileName, "SSME Daily Report")
        msg.attach(attachment)

    # html content
    msg.attach(MIMEText(contentHtml + config.FOOTER_HTML, 'html'))

    # connect SMTP server
    server = smtplib.SMTP(config.OUTLOOK_SERVER)
    server.starttls()
    server.login(config.OUTLOOK_LOGIN, config.OUTLOOK_PW)

    # send email
    server.sendmail(emailFrom, [email.strip() for email in emailTo.split(',')], msg.as_string())
    server.quit()