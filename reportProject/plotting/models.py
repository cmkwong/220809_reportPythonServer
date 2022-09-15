from django.db import models
from django.shortcuts import render
from django.http import HttpResponse
import json

# from codes.controllers.CompareReportController import CompareReportController
from codes.controllers.MonthlyReportController import MonthlyReportController
from codes import config

# Create your models here.

def generateComparePlotImages(req):
    # getting req body
    body_unicode = req.body.decode('utf-8')
    body = json.loads(body_unicode)
    plantnos, datefrom, dateto = body['plantno'], body['datefrom'], body['dateto']

    # define the controller
    reportController = MonthlyReportController()
    reportController.base_setUp()
    reportController.loop_setup(datefrom, dateto)

    # looping each plant no
    fls, df_fuel_level_avgs, topVolumes, fuelTanks = {}, {}, {}, {}
    for plantno in plantnos:
        PlantData = reportController.getPlantData(plantno)
        fl, df_fuel_level_avg = reportController.getFuelLevelUsage(PlantData.rawData)
        # plot the fuel consumption image
        reportController.graphPlotter.getFuelConsumptionPlot(fl, PlantData.fuelTankCapacity, PlantData.topVolume, config.tempComparePath, plantno)
        # store the fuel tank
        fuelTanks[plantno] = reportController.fuelTanks[plantno]['fuelTankCapacity']
        # store the top volume
        topVolumes[plantno] = PlantData.topVolume
        # store the fls
        fls[plantno] = fl
        # get the fuel level df
        df_fuel_level_avgs[plantno] = df_fuel_level_avg
        # plot the kWh image (bar)
        reportController.graphPlotter.getkWhPlot(PlantData.rawData, config.tempComparePath, plantno)
        # plot the kW image (line)
        reportController.graphPlotter.getkWPowerPlot(PlantData.rawData, config.tempComparePath, plantno)
    reportController.graphPlotter.getFuelLevelMeasurement(df_fuel_level_avgs, config.tempComparePath)
    reportController.graphPlotter.getTotalRefillPlot(fls, fuelTanks, topVolumes, config.tempComparePath)
    reportController.graphPlotter.getGroupFuelConsumption(fls, fuelTanks, topVolumes, config.tempComparePath)
    return HttpResponse('Hello World')