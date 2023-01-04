import sys
sys.path.append("../../../AtomLib") # import the AtomLib path
sys.path.append("../../") # import project main path

import schedule
import time
from codes.schedule.reportAll import will_reportAll
from codes.schedule.sqlData import will_sqliteData
from codes.schedule.moveTerexFiles import will_moveTerexFiles
from codes.schedule.dailySummary import will_dailySummary
from codes.schedule.dailyRoutineJob import will_uploadRoutineJob

import threading

def run_threaded(job_func, *args):
    job_thread = threading.Thread(target=job_func, args=args)
    job_thread.start()

# upload item master table every day
schedule.every().day.at('19:00').do(will_uploadRoutineJob)

# get sqlite data every day
# schedule.every().day.at('20:00').do(run_threaded, will_sqliteData)   # do it every day

# send daily email notice
schedule.every().day.at('03:00').do(will_dailySummary)

# get monthly report
schedule.every().day.at('03:00').do(will_reportAll, 3)    # 3rd of month

# check terex report exist and move to required path
schedule.every().day.at('03:00').do(run_threaded, will_moveTerexFiles)

print('Schedule is running ... ')
while True:
    # Checks whether a scheduled task
    # is pending to run or not
    schedule.run_pending()
    time.sleep(1)