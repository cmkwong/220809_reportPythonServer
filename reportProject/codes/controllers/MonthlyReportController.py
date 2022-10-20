# report
import calendar
import subprocess
import os
import sqlite3
import csv
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import collections
import pandas as pd
import linecache
import sys

# self
from codes import config
from codes.utils import fileModel
from codes.controllers.ReportLogic import ReportLogic
from codes.controllers.TrackerController import Tracker
from codes.controllers.MonthlyPlotController import MonthlyPlotController
from codes.controllers.NodeJsServerController import NodeJsServerController
from codes.models import reportModel


class MonthlyReportController:
    def __init__(self):
        self.serverController = NodeJsServerController()  # will get token from nodeJS webserver
        self.customeReport = False
        self.tracker = Tracker()
        self.reportLogic = ReportLogic(self.tracker)  # for logic checking
        self.graphPlotter = self.setGraphPlotter()  # setting the graph plotter

    def rename_alias(self, header_name):
        for k, v in config.colNameTable.items():
            if header_name == k:
                return v
        return False

    def getReportDuration(self, report_start_str='', report_end_str='', monthDelta=0, endUntil=False):
        """
        endUntil: this month first date to current date
        """
        if len(report_start_str) == 0 or len(report_end_str) == 0:
            now = datetime.now()
            y, m, d, h, M, s = now.year, now.month - monthDelta, now.day, now.hour, now.minute, now.second
            last_date = calendar.monthrange(y, m)[1]
            if endUntil:
                last_date = d
            report_start_date = datetime(y, m, 1, 0, 0, 0)
            report_start_str = datetime.strftime(report_start_date, "%Y-%m-%d %H:%M:%S")
            report_end_date = datetime(y, m, last_date, 23, 59, 59)  # + timedelta(days=1)
            report_end_str = datetime.strftime(report_end_date, "%Y-%m-%d %H:%M:%S")
        else:
            report_start_date = datetime.strptime(report_start_str, "%Y-%m-%d %H:%M:%S")
            report_end_date = datetime.strptime(report_end_str, "%Y-%m-%d %H:%M:%S")  # + timedelta(days=1)
        return report_start_date, report_start_str, report_end_date, report_end_str

    def setGraphPlotter(self):
        # ---------------------------------------------------------------------------------------#
        # matplotlib format setup
        locator = mdates.AutoDateLocator()
        locator.intervald[mdates.DAILY] = [1]
        locator.intervald[mdates.HOURLY] = [1, 2, 3, 6]
        formatter = mdates.ConciseDateFormatter(locator, show_offset=False)  # formatter is disabled
        formatter.formats = [
            "%y",
            "%d %b %y",
            "%d",
            "%H:%M",
            "%H:%M",
            "%S.%f",
        ]
        formatter.zero_formats = [""] + formatter.formats[:-1]
        formatter.offset_formats = [
            "",
            "%Y",
            "%b %Y",
            "%d %b %Y",
            "%d %b %Y",
            "%d %b %Y %H:%M",
        ]
        # set fig configuration
        graphPlotter = MonthlyPlotController(locator, formatter, figsize=(10, 6), dpi=150)
        return graphPlotter

    def base_setUp(self):
        # get IN / OUT Pivot Table
        print('Reading IN/OUT Pivot table...')
        self.inOutPivot = reportModel.getInOutPivot()

        # getting plant data from server (API: status not SOLD)
        machineDetails = self.serverController.getMachineDetails()

        # read fuel tank size, measurable tank size and installed SSME module (just included 'YG', 'PG', 'YLT')
        print('Reading plant info from machine details ...')
        self.fuelTanks, self.measurableFuelTanks, self.topvolumes, self.bottomvolumes, self.installedPlantList = reportModel.getPlantInfoFromMachineDetails(machineDetails,
                                                                                                                                                            plantTypes=['YG', 'PG', 'YLT'])

        # read registered SSME plantno
        print('Reading registered SSME plantno ...')
        self.registeredPlantList = reportModel.getRegistedPlant()

        # read customer info
        print('Reading Customer Info ...')
        self.custCode2Name = self.serverController.getCustInfo()

    def reportDirSetup(self, year_str, month_str):
        """
        :param: year: str
        :param: month: stt
        """
        # report folder create
        self.report_dir = os.path.join(config.reportPath, "{}-{}".format(year_str, month_str))
        if not os.path.exists(self.report_dir):
            os.mkdir(self.report_dir)

    # def date_setup_DISCARD(self, report_start_str='', report_end_str=''):
    #     """
    #     if empty, will get the current date
    #     """
    #     self.report_start_date, self.report_start_str, self.report_end_date, self.report_end_str = self.getReportDuration(report_start_str, report_end_str)

    def loop_setup(self, report_start_str, report_end_str):
        """
        setting the duration
        """
        self.report_start_date, self.report_start_str, self.report_end_date, self.report_end_str = self.getReportDuration(report_start_str, report_end_str)  # if empty, will get the current date
        requiredYear, requiredMonth = self.report_start_date.year, self.report_start_date.month
        self.table_name = "SSME{}".format(requiredYear + requiredMonth)
        self.reportYearMonth = "{}-{}".format(requiredYear, str(requiredMonth).zfill(2))

        # sqlite connection
        # sqlite_file = self.getSqliteFile()
        # self.conn = sqlite3.connect(sqlite_file)

    def removeRelated(self, *, year: str, month: str, request_plantno: list):
        try:
            report_dir = os.path.join(config.reportPath, "{}-{}".format(year, month.zfill(2)))
            # if not specific, remove all files
            if len(request_plantno) == 0:
                fileModel.clearFiles(config.tempPath, None)
                fileModel.clearFiles(report_dir, None)
            # if specific plantno remove
            else:
                for plantno in request_plantno:
                    fileModel.clearFiles(config.tempPath, plantno)
                    fileModel.clearFiles(report_dir, plantno)
        except:
            msg = "Remove error. "
            print(msg)

    def writePdf(self, *, year: str, month: str):
        # set up write pdf dir
        self.reportDirSetup(year, month.zfill(2))
        # get the temp files
        files = fileModel.getFileList(config.tempPath)
        # find the required tex files
        texes = []
        for file in files:
            head, tail = file.rsplit('.', 1)
            if tail == 'tex':
                texes.append(head)

        for jobName in texes:
            # skipping the existing pdf
            if os.path.exists(os.path.join(self.report_dir, f"{jobName}.pdf")) and not self.customeReport:
                print(f"{jobName}.....skipping")
                continue

            quit = False
            while quit is False:
                texPath = os.path.join(config.tempPath, "{}.tex".format(jobName))
                subprocess.run(["latex", "-quiet", "-output-format=pdf", "-job-name", jobName, "-output-directory", self.report_dir, texPath])

                # if there is warning, re-create the pdf again
                try:
                    rerun_flag = False
                    logDir = os.path.join(self.report_dir, "{}.log".format(jobName))
                    with open(logDir, "r") as f:
                        for line in f:
                            error_txt = "LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right."
                            if line.startswith(error_txt):
                                rerun_flag = True
                                break
                    if rerun_flag is False:
                        quit = True
                except FileNotFoundError:
                    quit = True
            print("{} PDF file created".format(jobName))

    def getSqliteFile(self):
        # ---------------------------------------------------------------------------------------#
        sqlite_file = os.path.join(config.sqliteOutPath, "{}.sqlite".format(self.reportYearMonth))
        # sqlite_file = f"\\\\apdc-data02\\WebSupervisorData\\{self.report_date}.sqlite"
        print(sqlite_file)
        if os.path.exists(sqlite_file):
            print("Sqlite file present")
        else:
            msg = f"{sqlite_file} does not exists"
            self.tracker.logging(msg, 'error')
            exit(1)
        return sqlite_file

    def getPlantNo(self):
        # ---------------------------------------------------------------------------------------#
        # list of PlantNo
        print("Getting List of PlantNo")
        # request_plantno = [no[0] for no in self.conn.execute(f"SELECT DISTINCT PlantNo FROM {self.table_name}").fetchall()]
        request_plantno = self.serverController.getDistinctPlantno(self.report_start_str, self.report_end_str)
        return request_plantno

    def getPlantRawData(self, plantno, record_out, record_in):
        # read raw data from sqlite
        # sql_cmd = f"SELECT SSMEName, SSMEValue, SSMETimeFrom, SSMETimeTo FROM {table_name} WHERE PlantNo == '{plantno}'"
        # sql_cmd = f"SELECT * FROM {self.table_name} WHERE PlantNo == '{plantno}'"
        # raw_df = pd.read_sql(sql_cmd, con=self.conn, parse_dates=["SSMETimeFrom", "SSMETimeTo"])
        raw_df = pd.DataFrame(self.serverController.getUnitValues(plantno, str(record_out), str(record_in)))
        if raw_df.empty:
            return pd.DataFrame()

        # drop the 'Fuel Level' with empty unit (That is useless value)
        dropIndex = raw_df[
            (raw_df['ssmename'] == 'Fuel Level') &
            ((raw_df['ssmeunit'] == '') | (raw_df['ssmevalue'] < '0'))].index
        raw_df.drop(index=dropIndex, inplace=True)

        # drop the 'Fuel level' with zero value (That is noisy value)
        dropIndex = raw_df[(raw_df['ssmename'] == 'Fuel level') & (raw_df['ssmevalue'] <= '0')].index
        raw_df.drop(index=dropIndex, inplace=True)

        df = raw_df.copy()
        print(f"{datetime.now()} - combine dataframes")

        df["value"] = df.ssmevalue.apply(reportModel.convert_to_float)
        df.drop("ssmevalue", axis=1, inplace=True)  # delete the column SSMEValue column

        df.rename(
            columns={"ssmename": "parameter", "ssmetimefrom": "start_dt", "ssmetimeto": "end_dt"}, inplace=True
        )

        # remove the time zone information while keeping the local time
        df.start_dt = pd.DatetimeIndex(df.start_dt) + pd.Timedelta(hours=8)
        df.start_dt = df.start_dt.dt.tz_localize(None)
        df.end_dt = pd.DatetimeIndex(df.end_dt) + pd.Timedelta(hours=8)
        df.end_dt = df.end_dt.dt.tz_localize(None)

        # PIVOT data
        # create row using START datetime
        startPivot = df.pivot_table(index="start_dt", columns="parameter", values="value")
        startPivot.index.rename("Datetime", inplace=True)
        startPivot.reset_index(inplace=True)

        # create row using END datetime
        endPivot = df.pivot_table(index="end_dt", columns="parameter", values="value")
        endPivot.index.rename("Datetime", inplace=True)
        endPivot.reset_index(inplace=True)

        # combine the two datetimes: https://towardsdatascience.com/why-and-how-to-use-merge-with-pandas-in-python-548600f7e738
        mergeDF = startPivot.merge(endPivot, how="outer")
        mergeDF.set_index("Datetime", inplace=True)

        # get required duration data based on the rental period
        mergeDF = mergeDF[(mergeDF.index >= record_out) & (mergeDF.index <= record_in)]

        mergeDF.sort_index(inplace=True)

        # create dict of the new names
        # new_column_names = dict()
        # for col_name in list(mergeDF.columns.values):
        #     new_name = self.rename_alias(col_name)
        #     if new_name is False:
        #         # msg = f"{plantno}: {col_name} missing column alias"
        #         continue
        #     else:
        #         new_column_names[col_name] = new_name

        # check if two fuel level parameters present in list
        # fuel_level has priority
        # if "fuel_level" not in new_column_names.values():
        #     if "fuel_level2" in new_column_names.values():
        #         new_column_names["Fuel Level"] = "fuel_level"

        # rename the columns name
        mergeDF.rename(columns=config.colNameTable, inplace=True)

        # process the noisy fuel level

        # if empty dataframe, return empty Dataframe
        if mergeDF.empty:
            return pd.DataFrame()

        return mergeDF

    def getFuelLevelUsage(self, main_df):
        # df = main_df.copy()
        # df = df.interpolate(method="linear", limit_direction="both")

        # df = df[(df.fuel_level >= 0) & (df.rpm == 0.0)]
        # df = df[df.fuel_level >= 0]
        rawFuelLevel = main_df['fuel_level'].dropna()

        # taking moving average
        rawFuelLevel.sort_index(inplace=True)
        df_fuel_level_avg = rawFuelLevel.resample("10T").mean()
        df_fuel_level_avg = df_fuel_level_avg.interpolate(method="linear", limit_direction="both").rolling(5, win_type='exponential').mean(tau=10).fillna(method='bfill')

        # merge the start and end of day
        s = df_fuel_level_avg.resample("D").first()
        e = df_fuel_level_avg.resample("D").last()
        fl = pd.merge(s, e, left_index=True, right_index=True)
        fl.columns = ["fl_start", "fl_end"]

        # calculate the fuel usage amount
        fl["fl_usage"] = fl.fl_start - fl.fl_end
        fl = self.calculateFuelUsage(fl, df_fuel_level_avg)

        # calculate the re-fuel amount
        fl["refill"] = 0
        fl = self.calculateRefuel(fl, df_fuel_level_avg)

        # calculating how many times being deep V
        fl['fullcount'] = 0  # from using -> 100%
        fl['initcount'] = 0  # from 100% -> using
        fl = self.getFullTankCount_initUsageCount(fl, df_fuel_level_avg)
        return fl, df_fuel_level_avg

    # for calculating how many times being full refuel in a day
    def getFullTankCount_initUsageCount(self, fl, df_fuel_level_avg):
        for d, _ in fl.iterrows():
            dayFuelDf = df_fuel_level_avg[
                (df_fuel_level_avg.index >= d) & (df_fuel_level_avg.index < d + timedelta(hours=24))
                ]
            fullTankCount = 0
            initUsageCount = 0
            for i, daytime in enumerate(dayFuelDf.index):
                if i != 0:
                    # it means refill fully
                    if dayFuelDf.iloc[i] == 100.0 and dayFuelDf.iloc[i] - dayFuelDf.iloc[i - 1] > 0:
                        fullTankCount = fullTankCount + 1
                if i != len(dayFuelDf) - 1:
                    if dayFuelDf.iloc[i] == 100.0 and dayFuelDf.iloc[i] - dayFuelDf.iloc[i + 1] > 0:
                        initUsageCount = initUsageCount + 1
            fl.loc[d, "fullcount"] = fullTankCount
            fl.loc[d, "initcount"] = initUsageCount
        return fl

    def getFuelSlop_NOTUSED(self, dayFuelDf):
        dayFuelDfCopy = dayFuelDf.copy()
        lastDayTime = None
        for i, (dayTime, row) in enumerate(dayFuelDfCopy.iterrows()):
            if i == 0:
                lastDayTime = dayTime
                continue
            timeDiff = dayTime - lastDayTime
            minutes = (timeDiff.days * 86400 + timeDiff.seconds) / 60  # minutes
            dayFuelDf.loc[dayTime, 'slope'] = dayFuelDfCopy.loc[dayTime] / minutes
            lastDayTime = dayTime
        return dayFuelDf

    def calculateRefuel(self, fl, df_fuel_level_avg):
        for d, _ in fl.iterrows():
            dayFuelDf = df_fuel_level_avg[
                (df_fuel_level_avg.index >= d) & (df_fuel_level_avg.index < d + timedelta(hours=24))
                ]
            # calculate the total refill percentage
            refillPercentage = dayFuelDf.diff()[dayFuelDf.diff() > 0].sum()
            fl.loc[d, "refill"] = refillPercentage
        return fl

    def calculateFuelUsage(self, fl, df_fuel_level_avg):
        for d, _ in fl.iterrows():
            dayFuelDf = df_fuel_level_avg[
                (df_fuel_level_avg.index >= d) & (df_fuel_level_avg.index < d + timedelta(hours=24))
                ]
            # calculate the total refill percentage
            refillPercentage = dayFuelDf.diff()[dayFuelDf.diff() < 0].sum() * -1
            fl.loc[d, "fl_usage"] = refillPercentage
        return fl

    # from philip (original that include refill date)
    def calculateFuelUsage_DISCARD(self, fl, df_fuel_level_avg):
        # re-calculate for fl_usage in re-fuel days
        for d, _ in fl.iterrows():
            temp_df = df_fuel_level_avg[
                (df_fuel_level_avg.index >= d) & (df_fuel_level_avg.index < d + timedelta(hours=24))
                ]
            s1 = temp_df.iloc[0]
            print("start", s1)
            e1 = s1
            s2 = None
            e2 = temp_df.iloc[-1]
            i = -1
            # find the last 3 of smallest value of fuel level and assign to e2
            for _ in range(3):
                try:
                    elast = temp_df.iloc[i]
                except IndexError:
                    break
                # print("elast:", elast)
                if elast > e2:
                    break
                else:
                    e2 = elast
                i -= 1

            max_s1 = 0
            print("end", e2)
            for index, value in temp_df.iteritems():
                # find the largest value of fuel level
                if value > max_s1:
                    max_s1 = value
                # find the smallest value of fuel level
                if value < s1 or value < max_s1:
                    if e1 > e2:
                        e1 = value
                if value > e1 + 30:
                    if s2 is None or value > s2:
                        s2 = value

            if s2 is None:
                print(d)
                print(f"({max_s1}, {e2})")
                fuel_used = max_s1 - e2
            else:
                print(d)
                print(f"({s1}, {e1})")
                print(f"({s2}, {e2})")
                if e1 > s1:
                    s1 = e1
                if e2 > s2:
                    s2 = e2
                print(f"({s1}, {e1})")
                print(f"({s2}, {e2})")
                fuel_used = (s1 - e1) + (s2 - e2)
            print("fuel_used: ", fuel_used)
            fl.loc[d, "fl_usage2"] = fuel_used
        return fl

    def calculateRefillDf_DISCARD(self, fl):
        fl_refill = fl.copy()
        for i, row in fl.iterrows():
            # refill dates
            if row['fl_start'] <= row['fl_end']:
                fl_refill.loc[i, 'refill'] = row['fl_end'] - row['fl_start'] - row['fl_usage']
            else:
                fl_refill.loc[i, 'refill'] = 0.0
        return fl_refill

    def getPlantData(self, plantno):
        """
        rawData: dataframe / False
        inout: dataframe / False
        register True / False
        installed: True / False
        tanksize: int / False
        measurabletanksize: True / False
        brand: str / False
        model: str / False
        """
        # tank['ws_plantno'], tank['brand'], tank['model'], tank['fuelTankCapacity']
        fields = ['plantno', 'rawData', 'inout', 'register', 'installed', 'fuelTankCapacity', 'topVolume', 'bottomVolume', 'measurabletanksize', 'brand', 'model']
        PlantData_nt = collections.namedtuple('PlantData_nt', fields)

        # get the Plant Raw Data (return empty dataframe is not existed)
        rawData = self.getPlantRawData(plantno, self.report_start_date, self.report_end_date)  # main_df
        # plantData._replace(rawData=rawData)

        # read plant IN/OUT record (return empty {} is not existed)
        inout = reportModel.getInOutDateRecord(plantno, self.inOutPivot, self.report_start_date, self.report_end_date)
        # plantData._replace(inout=inout)

        # check if plant registered SSME
        register = False
        if plantno in self.registeredPlantList or True:  # TODO: if datas includes required plantno, then assign to register always True
            register = True

        # check if plant installed SSME
        installed = False
        if plantno in self.installedPlantList:
            installed = True

        # check if tank size existed
        fuelTankCapacity, brand, model = False, False, False
        if plantno in self.fuelTanks:
            fuelTankCapacity = self.fuelTanks[plantno]['fuelTankCapacity']
            brand = self.fuelTanks[plantno]['brand']
            model = self.fuelTanks[plantno]['model']

        # check if measurable tank size existed
        measurabletanksize = False
        if model and model in self.measurableFuelTanks:
            measurabletanksize = True
            fuelTankCapacity = self.measurableFuelTanks[model]  # reassign the measured tank size

        # get the top volume
        topvolume = 0.0
        if model and model in self.topvolumes:
            topvolume = self.topvolumes[model]

        # get the bottom volume
        bottomvolume = 0.0
        if model and model in self.bottomvolumes:
            bottomvolume = self.bottomvolumes[model]

        PlantData = PlantData_nt(plantno=plantno,
                                 rawData=rawData,
                                 inout=inout,
                                 register=register,
                                 installed=installed,
                                 fuelTankCapacity=fuelTankCapacity,
                                 topVolume=topvolume,
                                 bottomVolume=bottomvolume,
                                 measurabletanksize=measurabletanksize,
                                 brand=brand,
                                 model=model,
                                 )
        return PlantData

    def loopForEachPlant(self, reportPdfNeeded=True, *, report_start_str: str, report_end_str: str, request_plantno: list, upload: bool):
        self.loop_setup(report_start_str, report_end_str)

        # get plant no, if empty request
        if len(request_plantno) == 0:
            # if request_plant equal to 0, means they are not custom report
            self.customeReport = False
            request_plantno = self.getPlantNo()
        else:
            # if request_plant not equal to 0, means they are custom report
            self.customeReport = True

        for loop_count, plantno in enumerate(request_plantno):
            print(f"Processing {plantno} - {loop_count + 1} of {len(request_plantno)}")
            PlantData = self.getPlantData(plantno)
            try:
                companyDatas = self.reportLogic.getCompanyDatas(PlantData, self.custCode2Name, self.report_start_str, self.report_end_str)

                # if pdf not needed then continue to get the logic table
                if not reportPdfNeeded:
                    continue

                # looping for each plant, as a plant might be trade IN/OUT more than one time
                for custCode, record in companyDatas.items():
                    companyName = record['companyName']
                    record_out = record['out']
                    record_in = record['in']
                    self.tracker.logging(f'company name: {companyName}', 'info')
                    fileName = "{}_{}".format(plantno, companyName)

                    # means the files are duplicated, do not run this again
                    if os.path.exists(os.path.join(config.tempPath, f"{fileName}.tex")) and not self.customeReport:
                        print(f"{fileName}.....skipping")
                        continue

                    main_df = record['data']
                    # print(f"{datetime.now()} - excel")

                    # ==================================================================================#
                    # Calculate Fuel df
                    fl, df_fuel_level_avg = self.getFuelLevelUsage(main_df)

                    # ==================================================================================#
                    # fuel consumption plot
                    self.graphPlotter.getFuelConsumptionPlot(fl, PlantData.fuelTankCapacity, PlantData.topVolume, config.tempPath, fileName)

                    # ==================================================================================#
                    # fuel level plot
                    self.graphPlotter.getFuelLevelPlot(df_fuel_level_avg, config.tempPath, fileName)

                    # ==================================================================================#
                    # kW Power Output plot
                    kw = self.graphPlotter.getkWPowerPlot(main_df, config.tempPath, fileName)

                    # ==================================================================================#
                    # daily kwh plot
                    kwh = self.graphPlotter.getkWhPlot(main_df, config.tempPath, fileName)

                    # ==================================================================================#
                    # CO2 emissions plot
                    co2_df = self.graphPlotter.getCO2Plot(fl, config.tempPath, fileName)

                    # ==================================================================================#

                    site_name = ""
                    project_name = ""
                    customer_name = ""

                    # plant required start date and end date
                    start_str = datetime.strftime(record_out, "%d %B %Y")
                    end_str = datetime.strftime(record_in, "%d %B %Y")

                    # ==================================================================================#
                    # create report tex
                    ################################################################

                    report_tex = r"""
                        \documentclass{ctexart}
                        \usepackage[a4paper, landscape, margin=1cm]{geometry}
                        \usepackage[pages=some]{background}
                        \usepackage{tikzpagenodes}
                        \pdfcompresslevel=9
                        \pdfminorversion=5
                        \pdfobjcompresslevel=2
                        \usepackage[en-GB]{datetime2}
                        \usepackage{hyperref}
        
                        \hypersetup{
                            pageanchor=false,
                            colorlinks=true,
                            linkcolor=blue,
                            filecolor=magenta,
                            urlcolor=cyan,
                        }
        
                        \graphicspath{
                                    {%s}
                                    {%s}
                                    {%s}
                                    {%s}
                                    {%s}
                        }
        
                        \backgroundsetup{
                        scale=1,
                        color=black,
                        opacity=1,
                        angle=0,
                        contents={\includegraphics[width=\paperwidth,height=\paperheight]{background.jpg} }
                        }
        
                        \sffamily
        
                        \begin{document}
        
                        \begin{titlepage}
                            \BgThispage
                            \pagenumbering{gobble}
        
                            \begin{tikzpicture}[remember picture, overlay]
                            \node [shift={(0cm, -5cm)}] at (current page.north) { \includegraphics[scale=1.8]{APR SSME logo.png} };
                    """ % (config.tempPath.replace('\\', '/'),
                           config.pdfImagesPath.replace('\\', '/'),
                           os.path.join(config.pdfImagesPath, "Companies").replace('\\', '/'),
                           os.path.join(config.pdfImagesPath, "Projects").replace('\\', '/'),
                           os.path.join(config.pdfImagesPath, "Title Pages").replace('\\', '/')
                           )

                    if len(customer_name):
                        report_tex = (
                                report_tex
                                + r"""
                            \node [shift={(0cm, 8.5cm)}] at (current page.south) { \includegraphics[height=4cm]{"""
                        )
                        report_tex = report_tex + f"{customer_name}" + r""".png} }; """

                    report_tex = (
                            report_tex
                            + r"""
                            \end{tikzpicture}
                            \vfill
                            \begin{center}
                            \Huge
                        """
                    )
                    report_tex = (
                            report_tex
                            + f"\\textbf{{{companyName}}}\n\\par\n"
                            + f"\\textbf{{{plantno.upper()} ({PlantData.brand.upper()} {PlantData.model.upper()})}}\n\\par\n\\textbf{{{start_str} - {end_str}}}"
                            + r"""
                            
                            \end{center}
        
                            \begin{flushright}
                            \Huge
                            Performance Review
                            \par
                            \Large
                            \today
                            \end{flushright}
                        \end{titlepage}
                        """
                    )

                    if len(site_name) and len(project_name):
                        report_tex = (
                                report_tex
                                + reportModel.append_title_page("project_page.jpg")
                                + f"\\vspace{{13.5cm}} \\Huge \\noindent\\hspace{{4cm}}{site_name}"
                                + r"""
                        \begin{tikzpicture}[remember picture, overlay]
                        \node [shift={(0cm, -7.5cm)}] at (current page.north) { \includegraphics[height=10cm]{"""
                                + f"{project_name}.jpg"
                                + r"""} };
                            \end{tikzpicture}
                        """
                        )

                    disclaimer = r"""
                        \begin{center}
                        \normalsize
                        * The sensors only allow approximation of fuel consumption
                        \end{center}
                        """
                    report_tex = report_tex + reportModel.append_title_page("title_fuel_consumption.jpg")
                    report_tex = report_tex + reportModel.append_chart_page(
                        "Fuel Consumption", "{}-fuel".format(fileName), f"Total Fuel Consumption = {fl.fuel_use_l.sum():.1f}L" + disclaimer
                    )
                    report_tex = report_tex + reportModel.append_chart_page("Fuel Level", "{}-fuel_level".format(fileName))

                    report_tex = report_tex + reportModel.append_title_page("title_actual_power_consumption.jpg")
                    report_tex = report_tex + reportModel.append_chart_page(
                        "Actual Power Consumption",
                        "{}-power_output_consumption".format(fileName),
                        f"Average kW = {kw['avg']:.1f}kW \\par Maximum kW = {kw['max']:.1f}kW",
                    )

                    report_tex = report_tex + reportModel.append_title_page("title_energy_consumption.jpg")
                    report_tex = report_tex + reportModel.append_chart_page(
                        "Daily kWh", "{}-daily_kwh".format(fileName), f"Total Energy Consumption = {kwh['max']:.0f} kWh"
                    )

                    report_tex = report_tex + reportModel.append_title_page("title_co2_emissions.jpg")

                    notes = r"""
                        \begin{center}
                        \normalsize
                        Calculation reference see \href{https://www.hunker.com/12284423/how-to-calculate-carbon-dioxide-emissions-from-a-diesel-generator} {How to Calculate Carbon Dioxide Emissions from a Diesel Generator}
                        \end{center}
                        """
                    report_tex = report_tex + reportModel.append_chart_page(
                        "CO2 Emissions (Metric Ton)",
                        "{}-co2_emissions".format(fileName),
                        f"Total CO2 Emissions = {co2_df.sum():.1f} Metric Ton" + notes,
                    )

                    report_tex = report_tex + reportModel.append_title_page("report ending A4 ratio.jpg")

                    report_tex = report_tex + r"\end{document}"

                    with open(os.path.join(config.tempPath, "{}.tex".format(fileName)), "w", encoding="utf8") as f:
                        f.write(report_tex)

                    ##########################################################################
                    # update database
                    if upload:
                        self.serverController.postMonthlyData({
                            "plantno": plantno,
                            "customerCode": custCode,
                            "dateFrom": record_out.strftime('%Y-%m-%d %H:%M:%S'),
                            "dateTo": record_in.strftime('%Y-%m-%d %H:%M:%S'),
                            "fuelReFill_L": fl.fuel_use_l.sum(),
                            "fuelConsumption_L": fl.fuel_use_l.sum(),
                            "co2Em_Kg": co2_df.sum(),
                            "totalPower_kWh": kw['avg']
                        })

                    ##########################################################################
                    print(f"{datetime.now()} - completed")
                    self.tracker.updateRecord(PlantData, reportOk=True)
                    print("_________________________________________________________________")

            except OSError:  # no disk space
                self.tracker.logging("OSError:No disk space", 'error')
                exit(1)

            except Exception as e:
                exc_type, exc_obj, tb = sys.exc_info()
                f = tb.tb_frame
                lineno = tb.tb_lineno
                filename = f.f_code.co_filename
                linecache.checkcache(filename)
                line = linecache.getline(filename, lineno, f.f_globals)
                msg = f"{plantno}:{e.__class__.__name__}:{lineno}:{exc_obj}"
                self.tracker.logging(msg, 'warning')
                self.tracker.updateRecord(PlantData, msg, reportOk=False)
                continue

    def processMonthToSqlite(self, *, year: str, month: str):
        # define table name
        table_name = f"SSME{year}{month.zfill(2)}"

        try:
            csvFilename = os.path.join(config.reportDataPath, table_name + ".csv")

            input_files = [csvFilename]
            print(input_files)

            db_name = os.path.join(config.sqliteOutPath, f"{year}-{month.zfill(2)}.sqlite")
            print(db_name)

            CHUNKSIZE = 500000
            if not os.path.exists(db_name):
                conn = sqlite3.connect(db_name)
                c = conn.cursor()
                c.execute(
                    f"""
                        CREATE TABLE [{table_name}] (
                        [PlantNo] text,
                        [SSMEName] text,
                        [SSMEUnit] text,
                        [SSMEDecimalPlaces] integer,
                        [SSMEValue] text,
                        [SSMETimeFrom] text,
                        [SSMETimeTo] text
                        )
                    """
                )

                # c.execute(f"CREATE INDEX pnsn ON {table_name} (Plantno, SSMEName);")
                c.execute(f"CREATE INDEX pn ON {table_name} (Plantno);")
                c.execute(f"CREATE INDEX sn ON {table_name} (SSMEName);")
                conn.commit()
                conn.close()
                last_line = 0
            else:
                with sqlite3.connect(db_name) as conn:
                    c = conn.cursor()
                    c.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                    last_line = c.fetchone()[0]
                    print(last_line)

            with sqlite3.connect(db_name) as conn:
                with open(input_files[0], newline="\n", encoding="utf-8-sig") as f:
                    try:
                        buf = []
                        chunk = 0
                        reader = csv.reader(f)
                        for i, row in enumerate(reader):
                            if i > last_line:
                                buf.append(row)
                                chunk += 1
                                if chunk % CHUNKSIZE == 0:
                                    print(f"SQLite line read: {chunk}")
                                    conn.executemany(f"INSERT INTO [{table_name}] VALUES ({','.join(['?'] * 7)})", buf)
                                    conn.commit()
                                    buf = []

                        # tailed set
                        if len(buf) > 0:
                            print(f"SQLite line read: {chunk}")
                            conn.executemany(f"INSERT INTO [{table_name}] VALUES ({','.join(['?'] * 7)})", buf)
                            conn.commit()

                    except Exception as e:
                        msg = f"{datetime.now()}:{e.__class__.__name__}:{e}"
                        self.tracker.logging(msg, 'warning')
                        print(row)
                        print(msg)

        except Exception as e:
            msg = f"{datetime.now()}:{e.__class__.__name__}:{e}"
            self.tracker.logging(msg, 'warning')
            print(msg)

    # upload to server, reading CSV and pushing to server (Not Completed 220815)
    def processMonth2Server(self, *, year: str, month: str):
        CHUNKSIZE = 500000
        table_name = f"ssme{year}{month.zfill(2)}"

        # define table name
        csvFileName = f"SSME{year}{month.zfill(2)}"

        csvFilename = os.path.join(config.reportDataPath, csvFileName + ".csv")

        # get the last line count
        # last_line = int(self.serverController.getVariable('monthLineCount'))
        last_line = self.serverController.getTableRowTotal(table_name)

        with open(csvFilename, newline="\n", encoding="utf-8-sig") as f:
            buf = []
            chunk = 0
            fileObject = csv.reader(f)
            # csvRowTotal = sum(1 for _ in fileObject)
            for i, row in enumerate(fileObject):
                if i > last_line:
                    buf.append({
                        "plantno": row[0],
                        "ssmename": row[1],
                        "ssmeunit": row[2],
                        "ssmedecimalplaces": row[3],
                        "ssmevalue": row[4],
                        "ssmetimefrom": row[5],
                        "ssmetimeto": row[6],
                        # "ssmetimefrom": str(datetime.strptime(row[5][0:19], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=8)),
                        # "ssmetimeto": str(datetime.strptime(row[6][0:19], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=8)),
                    })
                    chunk += 1
                    if chunk % CHUNKSIZE == 0:
                        uploadOk = self.serverController.uploadUnitValues(table_name, buf)
                        if uploadOk:
                            print(f"Expected Table Size: {(chunk + last_line)}")
                            buf = []
            # tailed set
            if len(buf) > 0:
                uploadOk = self.serverController.uploadUnitValues(table_name, buf)
                print(f"Expected line pushed: {chunk}")
                print(f"Real line pushed: {self.serverController.getTableRowTotal(table_name) + len(buf) - last_line}")
                print(f"All completed - {table_name}")

    def readSqlite(self, mainPath, fileName, command):
        conn = sqlite3.connect(os.path.join(mainPath, fileName))
        cur = conn.cursor()
        cur.execute(command)
        rows = cur.fetchall()
        return rows

# reportController = ReportController()
# reportController.processMonth2Server(year='2022', month='5')
