import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

from codes.controllers.ServerController import ServerController


class MonthlyPlotController:
    def __init__(self, locator=None, formatter=None, figsize=(10, 6), dpi=150):
        self.locator = locator
        self.formatter = formatter
        self.fig = plt.figure(figsize=figsize, dpi=dpi)
        self.serverController = ServerController()

    # fuel consumption
    def getFuelConsumptionPlot(self, fl, fuelTank, topVolume, outPath, filename):

        # reset axis
        plt.delaxes()

        fl["fuel_use_l"] = (fl['fl_usage'] / 100.0 * fuelTank + fl['initcount'] * topVolume).fillna(0)

        ax = self.fig.add_subplot()
        ax.bar(fl.index, fl['fuel_use_l'], label="Consumption", color="darkorange", edgecolor="black")
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        # ax.xaxis.set_major_formatter(self.formatter)
        ax.set_ylabel("Litres")
        max_height = fl['fuel_use_l'].max()
        fontsize = "medium"
        for i, p in enumerate(ax.patches):
            value = p.get_height()
            if value > 0.5:
                if value > max_height * 0.85:
                    va = "top"
                else:
                    va = "bottom"
                ax.text(
                    p.get_x() + (p.get_width() * 0.65),
                    value,
                    s=f"  {value:.1f}L ",
                    ha="center",
                    va=va,
                    rotation=90,
                    color="black",
                    fontsize=fontsize,
                )

        self.fig.tight_layout()
        image_name = os.path.join(outPath, "{}-fuel.png".format(filename))
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)
        # plt.delaxes(ax=ax)

    # fuel consumption
    def getReFuelPlot(self, fl, fuelTank, topVolume, outPath, filename):

        # reset axis
        plt.delaxes()

        fl["refill_l"] = (fl['refill'] / 100.0 * fuelTank + fl['fullcount'] * topVolume).fillna(0)

        ax = self.fig.add_subplot()
        ax.bar(fl.index, fl['refill_l'], label="Consumption", color="darkorange", edgecolor="black")
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        # ax.xaxis.set_major_formatter(self.formatter)
        ax.set_ylabel("Litres")
        max_height = fl['refill_l'].max()
        fontsize = "medium"
        for i, p in enumerate(ax.patches):
            value = p.get_height()
            if value > 0.5:
                if value > max_height * 0.85:
                    va = "top"
                else:
                    va = "bottom"
                ax.text(
                    p.get_x() + (p.get_width() * 0.65),
                    value,
                    s=f"  {value:.1f}L ",
                    ha="center",
                    va=va,
                    rotation=90,
                    color="black",
                    fontsize=fontsize,
                )

        self.fig.tight_layout()
        image_name = os.path.join(outPath, "{}-refuel.png".format(filename))
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)

    # fuel level
    def getFuelLevelPlot(self, df_fuel_level_avg, outPath, filename):
        # reset axis
        plt.delaxes()

        ax = self.fig.add_subplot()
        ax.plot(df_fuel_level_avg.index, df_fuel_level_avg, label="Fuel Level")
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        # ax.xaxis.set_major_formatter(self.formatter)
        ax.set_ylabel("%")

        self.fig.tight_layout()
        image_name = os.path.join(outPath, "{}-fuel_level.png".format(filename))
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)
        # plt.delaxes(ax=ax)

    # Daily KWH
    def getkWhPlot(self, main_df, outPath, plantno):

        # reset axis
        plt.delaxes()

        main_df_copy = main_df.copy()
        main_df_copy = main_df_copy.kwh.dropna().diff()
        main_df_copy = main_df_copy[(main_df_copy.abs() < 5000) & (main_df_copy >= 0)].resample("D").sum()

        ax = self.fig.add_subplot()
        width = 0.35
        ax.bar(main_df_copy.index, main_df_copy, width=width * 2, label="kWh", color="darkorange", edgecolor="black")
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        # ax.xaxis.set_major_formatter(self.formatter)
        ax.set_ylabel("kWh")
        try:
            ax.set_ylim((main_df_copy.min() * 0.9, main_df_copy.max() * 1.1))
        except ValueError:
            pass
        max_height = main_df_copy.max() - main_df_copy.min()
        for p in ax.patches:
            value = p.get_height()
            if value > 0:
                if value > max_height * 0.9 + main_df_copy.min() * 0.9:
                    va = "top"
                else:
                    va = "bottom"
                ax.text(
                    p.get_x() + (p.get_width() * 0.6),
                    value,
                    s=f"  {int(value)} ",
                    ha="center",
                    va=va,
                    rotation=90,
                    color="black",
                )

        self.fig.tight_layout()
        image_name = os.path.join(outPath, "{}-daily_kwh.png".format(plantno))
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)
        if main_df_copy.shape[0]:
            max_kwh = main_df_copy.sum()
        else:
            max_kwh = 0
        return max_kwh

    def getGroupkWhPlot(self):
        # reset axis
        plt.delaxes()

    # CO2 emissions
    def getCO2Plot(self, fl, outPath, plantno):
        # reset axis
        plt.delaxes()

        fl["CO2"] = fl.fuel_use_l.apply(lambda x: x * 0.2641729 * 2778 * 3.66 * 0.99 * 0.000001)
        co2_df = fl["CO2"]

        ax = self.fig.add_subplot()
        width = 0.35
        ax.bar(co2_df.index, co2_df, width=width * 2, label="CO2", color="darkgrey", edgecolor="black")
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        # ax.xaxis.set_major_formatter(self.formatter)
        ax.set_ylabel("Metric Ton")
        ax.set_facecolor("whitesmoke")
        max_height = co2_df.max()
        for p in ax.patches:
            value = p.get_height()
            if value > 0.05:
                if value > max_height * 0.9:
                    va = "top"
                    color = "white"
                else:
                    va = "bottom"
                    color = "black"
                ax.text(
                    p.get_x() + (p.get_width() * 0.6),
                    value,
                    s=f"  {value:.2f} ",
                    ha="center",
                    va=va,
                    rotation=90,
                    color=color,
                )
        self.fig.tight_layout()
        image_name = os.path.join(outPath, "{}-co2_emissions.png".format(plantno))
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)
        return co2_df

    # kw power
    def getkWPowerPlot(self, main_df, outPath, plantno):
        # reset axis
        plt.delaxes()

        main_df_copy = main_df.copy()
        main_df_copy = main_df_copy.resample("1T").mean()
        main_df_copy = main_df_copy.interpolate(method="linear", limit_direction="both")
        main_df_copy = main_df_copy[main_df_copy.rpm > 1450]

        """
        main_df_copy = main_df.copy()
        rpm = main_df_copy['rpm']
        actual_power = main_df_copy['actual_power'].resample("1T").mean().fillna(method='bfill')
        actual_power = actual_power.interpolate(method="linear", limit_direction="both")
        actual_power[rpm[rpm < 1450].index] = np.nan
        """

        ax = self.fig.add_subplot()
        # ax.plot(actual_power.index, actual_power)
        ax.plot(main_df_copy.index, main_df_copy)
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        # ax.xaxis.set_major_formatter(self.formatter)
        ax.set_ylabel("kW")
        self.fig.tight_layout()
        image_name = os.path.join(outPath, "{}-power_output_consumption.png".format(plantno))
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)

        if main_df_copy['actual_power'].shape[0]:
            avg_kw = main_df_copy['actual_power'].mean()
            max_kw = main_df_copy['actual_power'].max()
        else:
            avg_kw = 0
            max_kw = 0

        print(f"Avg Power = {avg_kw:.1f}kW, Max Power = {max_kw:.1f}kW")
        return avg_kw, max_kw

    def getTotalRefillPlot(self, fls, fuelTanks, topVolumes, outPath):
        # calculate the cumsum
        refuelByPlantnoDf = pd.DataFrame()
        for plantno, fl in fls.items():
            topVolume = topVolumes[plantno]
            fuelTank = fuelTanks[plantno]
            refuelByPlantnoDf[plantno] = (fl['refill'] / 100.0 * fuelTank + fl['fullcount'] * topVolume).fillna(0)
        refuelByPlantnoDf['sum'] = refuelByPlantnoDf.sum(axis=1)
        refuelByPlantnoDf['cumsum'] = refuelByPlantnoDf['sum'].cumsum()
        totalRefill = refuelByPlantnoDf['cumsum'][-1]

        # reset axis
        plt.delaxes()

        ax = self.fig.add_subplot()
        ax.plot(refuelByPlantnoDf.index, refuelByPlantnoDf['cumsum'])
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        ax.set_ylabel("Total Refilling")
        self.fig.tight_layout()
        image_name = os.path.join(outPath, "Total Fuel Level.png")
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)
        return totalRefill

    def getGroupFuelConsumption(self, fls, fuelTanks, topVolumes, outPath):
        fuelConsumptionDf = pd.DataFrame()
        for plantno, fl in fls.items():
            topVolume = topVolumes[plantno]
            fuelTank = fuelTanks[plantno]
            fuelConsumptionDf[plantno] = (fl['fl_usage'] / 100 * fuelTank + fl['initcount'] * topVolume).fillna(0)
        totalConsumptionDf = fuelConsumptionDf.sum(axis=1)

        # reset axis
        plt.delaxes()

        ax = self.fig.add_subplot()
        width = 0.3
        # calculate the width assignment table
        widthTable = [w * width for w in np.arange(len(fuelConsumptionDf.columns))]  # [0, 0.2, 0.4, 0.6]
        widthTable = np.array(widthTable) - np.mean(widthTable)  # [-0.3, -0.1, 0.1, 0.3]
        x = np.arange(0, len(fuelConsumptionDf.index) * 2, 2)
        for i, plantno in enumerate(fuelConsumptionDf):
            ax.bar(x + widthTable[i], fuelConsumptionDf[plantno], width=width, label=plantno)
        ax.plot(x, totalConsumptionDf, label='Total')
        # reassign the x-ticks
        ax.set_xticks(x, fuelConsumptionDf.index.strftime('%Y-%m-%d'))
        plt.xticks(rotation=90)

        ax.xaxis.set_major_locator(self.locator)
        ax.set_ylabel("Fuel Consumption (L)")
        ax.legend(loc='upper right')
        # set layout
        self.fig.tight_layout()
        plt.autoscale(enable=True, axis='x', tight=True)
        image_name = os.path.join(outPath, "Fuel Consumption L.png")
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)

    def getFuelLevelMeasurement(self, df_fuel_level_avgs, outPath):
        # reset axis
        plt.delaxes()

        ax = self.fig.add_subplot()
        for plantno, df_fuel_level_avg in df_fuel_level_avgs.items():
            ax.plot(df_fuel_level_avg.index, df_fuel_level_avg, label=plantno)
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        ax.set_ylabel("Fuel Level %")
        self.fig.tight_layout()
        image_name = os.path.join(outPath, "Fuel Level Measurement.png")
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)