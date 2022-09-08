from codes import config
from utils import paramModel
from codes.models import emailModel

def control_command_check(helper, ans):
    command_checked = True
    command_not_checked = False
    quit_program = "quit"

    if ans == '':
        print("cannot input empty string")
        return command_checked

    if ans[0] == '-':
        if ans == '-quit' or ans == '-q':
            return quit_program

        # reading all SSME raw data needed
        elif ans == "-data":
            helper.reportController.base_setUp()
            print("report setup OK")
            return command_checked

        # sending email attached with csv SSME report
        elif ans == '-email':
            params = paramModel.ask_params(emailModel.sendEmail, config.paramPath, 'param.txt')
            contentHtml = emailModel.buildingHtmlSummaryTable(helper.reportController)
            emailModel.sendEmail(contentHtml=contentHtml, **params)
            return command_checked

        # reading csv and making sqlite
        elif ans == '-sql':
            params = paramModel.ask_params(helper.reportController.processMonthToSqlite, config.paramPath, 'param.txt')
            helper.reportController.processMonthToSqlite(**params)
            return command_checked

        # reading sqlite and generating tex files
        elif ans == "-tex":
            # ask param
            params = paramModel.ask_params(helper.reportController.loopForEachPlant, config.paramPath, 'param.txt')
            # assign param
            helper.reportController.loopForEachPlant(**params)
            helper.reportController.tracker.writeCSV()      # write the record csv
            # helper.reportController.conn.close() # close the connection to sqlite
            print("Loop plant report tex finished.")
            return command_checked

        elif ans == '-write':
            # ask param
            params = paramModel.ask_params(helper.reportController.writePdf, config.paramPath, 'param.txt')
            # write the pdf
            helper.reportController.writePdf(**params)
            return command_checked

        # making tex and writing PDF
        elif ans == '-fw':
            # ask param
            params = paramModel.ask_params(helper.reportController.loopForEachPlant, config.paramPath, 'param.txt')
            # assign param
            helper.reportController.loopForEachPlant(**params)
            print("Loop plant report tex finished.")
            # ask param
            params = paramModel.ask_params(helper.reportController.writePdf, config.paramPath, 'param.txt')
            # write the pdf
            helper.reportController.writePdf(**params)
            return command_checked

        elif ans == '-remove':
            params = paramModel.ask_params(helper.reportController.removeRelated, config.paramPath, 'param.txt')
            helper.reportController.removeRelated(**params)
            return command_checked
    else:
        return command_not_checked