from django.db import models
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from rest_framework.decorators import api_view

# from codes.controllers.CompareReportController import CompareReportController
from codes.controllers.MonthlyReportController import MonthlyReportController
from codes import config


# Create your models here.
@api_view(['POST'])
def generateComparePlotImages_req(req):
    # getting req body
    body_unicode = req.body.decode('utf-8')
    body = json.loads(body_unicode)
    plantnos, datefrom, dateto = body['plantnos'], body['datefrom'], body['dateto']
    outputData = generateComparePlotImages(plantnos, datefrom, dateto)
    res = JsonResponse(outputData)
    res.status_code = 200
    return res


def generateComparePlotImages(plantnos, datefrom, dateto):
    # define the controller
    reportController = MonthlyReportController()
    reportController.base_setUp()
    reportController.loop_setup(datefrom, dateto)

    # looping each plant no
    fls, df_fuel_level_avgs, topVolumes, fuelTanks, kWhs, kWs = {}, {}, {}, {}, {}, {}
    outputData = {}
    outputData['fuelConsumptions_L'] = {}  # plantno: value
    outputData['totalFuelConsumptions_L'] = 0.0  # value
    outputData['totalRefill_L'] = 0.0  # value
    outputData['actualPowers_kW'] = {}  # plantno: min max average
    outputData['electricityConsumption_kWh'] = {}  # plantno: min max average
    outputData['totalActualPower'] = {}  # plantno: min max average
    outputData['totalElectricityConsumption_kWh'] = {}  # plantno: min max average
    for plantno in plantnos:
        PlantData = reportController.getPlantData(plantno)
        fl, df_fuel_level_avg = reportController.getFuelLevelUsage(PlantData.rawData)
        # plot the fuel consumption image
        outputData['fuelConsumptions_L'][plantno] = reportController.graphPlotter.getFuelConsumptionPlot(fl, PlantData.fuelTankCapacity, PlantData.topVolume, config.tempComparePlotsPath, plantno)
        # store the fuel tank
        fuelTanks[plantno] = reportController.fuelTanks[plantno]['fuelTankCapacity']
        # store the top volume
        topVolumes[plantno] = PlantData.topVolume
        # store the fls
        fls[plantno] = fl
        # store the kWhs
        kWhs[plantno] = PlantData.rawData['kwh']
        # store the kW
        kWs[plantno] = PlantData.rawData
        # get the fuel level df
        df_fuel_level_avgs[plantno] = df_fuel_level_avg
        # plot the kWh image (bar)
        outputData['electricityConsumption_kWh'][plantno] = reportController.graphPlotter.getkWhPlot(PlantData.rawData, config.tempComparePlotsPath, plantno)
        # plot the kW image (line)
        outputData['actualPowers_kW'][plantno] = reportController.graphPlotter.getkWPowerPlot(PlantData.rawData, config.tempComparePlotsPath, plantno)
    outputData['totalElectricityConsumption_kWh'] = reportController.graphPlotter.getGroupkWhPlot(kWhs, config.tempComparePlotsPath)
    reportController.graphPlotter.getGroupFuelLevelMeasurement(df_fuel_level_avgs, config.tempComparePlotsPath)
    outputData['totalRefill_L'] = reportController.graphPlotter.getTotalRefillPlot(fls, fuelTanks, topVolumes, config.tempComparePlotsPath)
    outputData['totalFuelConsumptions_L'] = reportController.graphPlotter.getGroupFuelConsumption(fls, fuelTanks, topVolumes, config.tempComparePlotsPath)
    outputData['totalActualPower'] = reportController.graphPlotter.getGroupkWPowerPlot(kWs, config.tempComparePlotsPath)
    return outputData

# generateComparePlotImages(plantnos=["YG634", "YG716"], datefrom="2022-07-20 00:00:00", dateto="2022-08-19 23:59:59")
# print()
