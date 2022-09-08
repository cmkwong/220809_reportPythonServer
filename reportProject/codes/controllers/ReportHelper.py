from codes.controllers.MonthlyReportController import MonthlyReportController
from codes.models import commandModel

class ReportHelper:
    def __init__(self):
        self.reportController = MonthlyReportController()

    def enter(self):
        # setting placeholder
        placeholder = 'Input: '
        user_input = input(placeholder)  # waiting user input
        command = commandModel.control_command_check(self, user_input)
        return command