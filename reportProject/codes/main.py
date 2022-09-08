import sys
sys.path.append("../../AtomLib") # import the AtomLib path
from codes.controllers.ReportHelper import ReportHelper

command = False
# define the apHelper
reporthelper = ReportHelper()

while (not (command == 'quit')):

    command = reporthelper.enter()

    if not command:
        print("Not is command")