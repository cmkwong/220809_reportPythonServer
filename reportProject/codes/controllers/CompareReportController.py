import pandas as pd
from datetime import timedelta

from codes.controllers.MonthlyReportController import MonthlyReportController
from codes.models import reportModel
from codes import config


class CompareReportController(MonthlyReportController):
    def __init__(self, plantnos, datefrom, dateto):
        super(CompareReportController, self).__init__()
        self.plantnos = plantnos
        self.datefrom = datefrom
        self.dateto = dateto
        self.base_setUp()
        self.loop_setup(datefrom, dateto)

    def getCompareReportImage(self):
        fls, df_fuel_level_avgs, topVolumes, fuelTanks = {}, {}, {}, {}
        for plantno in self.plantnos:
            PlantData = self.getPlantData(plantno)
            fl, df_fuel_level_avg = self.getFuelLevelUsage(PlantData.rawData)
            # plot the fuel consumption image
            self.graphPlotter.getFuelConsumptionPlot(fl, PlantData.fuelTankCapacity, PlantData.topVolume, config.tempPath, plantno)
            # store the fuel tank
            fuelTanks[plantno] = self.fuelTanks[plantno]['fuelTankCapacity']
            # store the top volume
            topVolumes[plantno] = PlantData.topVolume
            # store the fls
            fls[plantno] = fl
            # get the fuel level df
            df_fuel_level_avgs[plantno] = df_fuel_level_avg
            # plot the kWh image (bar)
            self.graphPlotter.getkWhPlot(PlantData.rawData, config.tempPath, plantno)
            # plot the kW image (line)
            self.graphPlotter.getkWPowerPlot(PlantData.rawData, config.tempPath, plantno)
        self.graphPlotter.getFuelLevelMeasurement(df_fuel_level_avgs, config.tempPath)
        self.graphPlotter.getTotalRefillPlot(fls, fuelTanks, topVolumes, config.tempPath)
        self.graphPlotter.getGroupFuelConsumption(fls, fuelTanks, topVolumes, config.tempPath)

    def getCompareReportImage__DISCARD(self):
        refuelByPlantnoDf = pd.DataFrame()  # re-fuel df
        fuelLevelMeasureDf = pd.DataFrame()  # fuel level comparing df
        fuelConsumptionDf = pd.DataFrame()  # fuel consumption
        powerDf = pd.DataFrame()  # Power usage
        for plantno in self.plantnos:
            PlantData = self.getPlantData(plantno)
            # get the re-fuel df
            fl, df_fuel_level_avg = self.getFuelLevelUsage(PlantData.rawData)
            fuelTank = self.fuelTanks[plantno]['fuelTankCapacity']
            refuelByPlantnoDf[plantno] = (fl['refill'] / 100.0 * fuelTank + fl['fullcount'] * PlantData.topVolume).fillna(0)
            # get the fuel level df
            fuelLevelMeasureDf[plantno] = df_fuel_level_avg
            # get fuel consumption df
            fuelConsumptionDf[plantno] = (fl['fl_usage'] / 100 * fuelTank + fl['initcount'] * PlantData.topVolume).fillna(0)
            # get actual power kW
            _df = PlantData.rawData.copy()
            _df = _df['kwh'].dropna().diff()
            powerDf[plantno] = _df[(_df.abs() < 5000) & (_df >= 0)].resample("D").sum()
        # re-fuel process
        refuelByPlantnoDf['sum'] = refuelByPlantnoDf.sum(axis=1)
        refuelByPlantnoDf['cumsum'] = refuelByPlantnoDf['sum'].cumsum()
        # fuel consumption process
        fuelConsumptionDf['sum'] = fuelConsumptionDf.sum(axis=1)
        # trigger to re-fuel image
        self.serverController.getPlotImage(['Cumsum'],
                                           X=list(refuelByPlantnoDf.index.strftime('%Y-%m-%d')),
                                           Ys=[list(refuelByPlantnoDf['cumsum'].values)],
                                           plotType='line',
                                           path='./dev-data',
                                           filename='refuel.jpg')
        # trigger to fuel level measurement (group)
        Ys = []
        fuelLevelMeasureDf = fuelLevelMeasureDf.fillna(0.0)  # reset to zero
        for plantno in fuelLevelMeasureDf:
            Ys.append(list(fuelLevelMeasureDf[plantno].values))
        self.serverController.getPlotImage(['YG634', 'YG635', 'YG700', 'YG701', 'YG709', 'YG716'],
                                           X=list(fuelLevelMeasureDf.index.strftime('%Y-%m-%d')),
                                           Ys=Ys,
                                           plotType='line',
                                           path='./dev-data',
                                           filename='fuelLevelMeasurement.jpg')
        return refuelByPlantnoDf


# YG1063 YG1064 is very frustrated fuel level example
# compareController = CompareReportController(['YG1063', 'YG1064'], "2022-07-20 00:00:00", "2022-08-19 23:59:59")
# compareController = CompareReportController(['YG634', 'YG635', 'YG700', 'YG701', 'YG709', 'YG716'], "2022-07-20 00:00:00", "2022-08-19 23:59:59")
# compareController = CompareReportController(['YG409', 'YG716'], "2022-07-20 00:00:00", "2022-08-19 23:59:59")
# compareController = CompareReportController(['YG716'], "2022-07-20 00:00:00", "2022-08-19 23:59:59")
# compareController = CompareReportController(['YG409'], "2022-07-01 00:00:00", "2022-07-31 23:59:59") # very frustrated
# compareController.getCompareReportImage()
