import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

from codes.controllers.NodeJsServerController import NodeJsServerController


class MonthlyPlotController:
    def __init__(self, locator=None, formatter=None, adjustTimeResolution=False, figsize=(10, 6), dpi=150):
        self.locator = locator
        self.formatter = formatter
        self.adjustTimeResolution = adjustTimeResolution
        self.fig = plt.figure(figsize=figsize, dpi=dpi)
        self.serverController = NodeJsServerController()
        self._maximum = 0  # used in clean kWh value

    # get the dataframe timestep in seconds
    def getTimestep(self, df):
        totalDiff_second = df.index.to_series().diff().dt.seconds.fillna(0).sum() / (len(df) - 1)
        return totalDiff_second

    # get required time resolution to display based on the start and end date range
    def getRequiredTimeResolution(self, df, adjust=True):
        # if adjust is False, then then the original width and daily sample

        # calculate the time difference between start and end
        totalDiff_second = df.index.to_series().diff().dt.seconds.fillna(0).sum()
        totalDiff_day = totalDiff_second / 3600 / 24

        # check if larger than 10 day, if so, then resample as 'D'
        if (totalDiff_day > 10.0) or not adjust:
            width = 0.35
            resampleFactor = 'D'
            minsDiff = 1440
        else:
            width = 0.02
            resampleFactor = '1H'
            minsDiff = 60
        return width, resampleFactor, minsDiff

    # fuel consumption
    def getFuelConsumptionPlot(self, fl, fuelTank, topVolume, outPath, filename):

        # get required resolution
        width, _, _ = self.getRequiredTimeResolution(fl, adjust=self.adjustTimeResolution)

        # reset axis
        plt.delaxes()

        fl["fuel_use_l"] = (fl['fl_usage'] / 100.0 * fuelTank + fl['initcount'] * topVolume).fillna(0)

        ax = self.fig.add_subplot()
        ax.bar(fl.index, fl['fuel_use_l'], width=width, label="Consumption", color="darkorange", edgecolor="black")
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
        image_name = os.path.join(outPath, filename)
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)

        # total consumption
        totalConsumption = fl['fuel_use_l'].sum()
        return totalConsumption

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
        image_name = os.path.join(outPath, filename)
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)
        # plt.delaxes(ax=ax)

    # clean-up duplicated of data in kwh
    def _cleanDuplicated_kwh(self, row):
        if row > self._maximum:
            self._maximum = row
        else:
            row = self._maximum
        return row

    # get required kWh from main_df
    def _refactorkWhDf(self, raw_kwh, resampleFactor):
        """
        :param raw_kwh: kWh Series without factoring the timeindex
        :param resampleFactor: 'D', '5min', etc
        :return: pd.Series
        """
        # extract the kWh
        kwhDf = raw_kwh.dropna()

        # clean the duplicated data
        kwhCleanDuplicated = kwhDf.apply(self._cleanDuplicated_kwh)
        self._maximum = 0

        # take the difference values
        kwhDiff = kwhCleanDuplicated.diff()

        # resample and sum of them
        kwhResampleData = kwhDiff.resample(resampleFactor).sum()

        return kwhResampleData

    # Daily KWH
    def getkWhPlot(self, main_df, outPath, filename):

        # get required resolution
        width, resampleFactor, _ = self.getRequiredTimeResolution(main_df, adjust=self.adjustTimeResolution)

        # reset axis
        plt.delaxes()
        ax = self.fig.add_subplot()

        # get the kWh
        kwhResampleData = self._refactorkWhDf(main_df.kwh, resampleFactor)

        ax.bar(kwhResampleData.index, kwhResampleData, width=width, label="kWh", color="darkorange", edgecolor="black")
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        # ax.xaxis.set_major_formatter(self.formatter)
        ax.set_ylabel("kWh")
        try:
            ax.set_ylim((kwhResampleData.min() * 0.9, kwhResampleData.max() * 1.1))
        except ValueError:
            pass
        max_height = kwhResampleData.max() - kwhResampleData.min()
        for p in ax.patches:
            value = p.get_height()
            if value > 0:
                if value > max_height * 0.9 + kwhResampleData.min() * 0.9:
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
        image_name = os.path.join(outPath, filename)
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)
        kwh = {}
        if kwhResampleData.shape[0]:
            kwh['min'] = kwhResampleData.min()
            kwh['avg'] = kwhResampleData.mean()
            kwh['max'] = kwhResampleData.max()
            kwh['total'] = kwhResampleData.sum()
        else:
            kwh['min'] = 0
            kwh['avg'] = 0
            kwh['max'] = 0
            kwh['total'] = 0

        print(f"Electricity Consumption = {kwh['avg']:.1f}kWh, Max Consumption = {kwh['max']:.1f}kWh")
        return kwh

    # CO2 emissions (ton)
    def getCO2Plot(self, fl, outPath, filename):

        # get required width
        width, _, _ = self.getRequiredTimeResolution(fl, adjust=self.adjustTimeResolution)

        # reset axis
        plt.delaxes()

        fl["CO2"] = fl.fuel_use_l.apply(lambda x: x * 0.2641729 * 2778 * 3.66 * 0.99 * 0.000001)
        co2_df = fl["CO2"]

        ax = self.fig.add_subplot()
        ax.bar(co2_df.index, co2_df, width=width, label="CO2", color="darkgrey", edgecolor="black")
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
        image_name = os.path.join(outPath, filename)
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)
        return co2_df

    # kw power
    def getkWPowerPlot(self, main_df, outPath, filename):
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
        ax.plot(main_df_copy.index, main_df_copy['actual_power'])
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        # ax.xaxis.set_major_formatter(self.formatter)
        ax.set_ylabel("kW")
        self.fig.tight_layout()
        image_name = os.path.join(outPath, filename)
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)

        kw = {}
        if main_df_copy['actual_power'].shape[0]:
            kw['min'] = main_df_copy['actual_power'].min()
            kw['avg'] = main_df_copy['actual_power'].mean()
            kw['max'] = main_df_copy['actual_power'].max()
        else:
            kw['min'] = 0
            kw['avg'] = 0
            kw['max'] = 0

        print(f"Avg Power = {kw['avg']:.1f}kW, Max Power = {kw['max']:.1f}kW")
        return kw

    def getTotalRefillPlot(self, fls, fuelTanks, topVolumes, outPath, filename):
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
        ax.set_ylabel("Total Litres")
        self.fig.tight_layout()
        image_name = os.path.join(outPath, filename)
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)
        return totalRefill

    def getGroupFuelConsumption(self, fls, fuelTanks, topVolumes, outPath, filename):
        fuelConsumptionDf = pd.DataFrame()
        for plantno, fl in fls.items():
            topVolume = topVolumes[plantno]
            fuelTank = fuelTanks[plantno]
            fuelConsumptionDf[plantno] = (fl['fl_usage'] / 100 * fuelTank + fl['initcount'] * topVolume).fillna(0)
        totalConsumptionDf = fuelConsumptionDf.sum(axis=1)

        # reset axis
        plt.delaxes()
        ax = self.fig.add_subplot()

        # define the bar width
        width = 0.3
        # calculate the width assignment table
        widthTable = [w * width for w in np.arange(len(fuelConsumptionDf.columns))]  # [0, 0.2, 0.4, 0.6]
        widthTable = np.array(widthTable) - np.mean(widthTable)  # [-0.3, -0.1, 0.1, 0.3]
        x = np.arange(0, len(fuelConsumptionDf.index) * 2, 2)  # make it wider when step is 2
        for i, plantno in enumerate(fuelConsumptionDf):
            ax.bar(x + widthTable[i], fuelConsumptionDf[plantno], width=width, label=plantno)
        ax.plot(x, totalConsumptionDf, label='Total(L)')

        # reassign the x-ticks
        ax.set_xticks(x, fuelConsumptionDf.index.strftime('%Y-%m-%d'))
        plt.xticks(rotation=90)

        ax.xaxis.set_major_locator(self.locator)
        ax.set_ylabel("Litres")
        ax.legend(loc='upper right')
        # set layout
        self.fig.tight_layout()
        plt.autoscale(enable=True, axis='x', tight=True)
        image_name = os.path.join(outPath, filename)
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)

        # sum of fuel consumption
        return totalConsumptionDf.sum()

    # calculate the grouped of kWh
    def getGroupkWhPlot(self, kWhs, outPath, filename):

        dailyKWhDf = pd.DataFrame()
        for plantno, kWhDf in kWhs.items():
            _, resampleFactor, _ = self.getRequiredTimeResolution(kWhDf, adjust=self.adjustTimeResolution)  # default daily and width 0.3
            dailyKWhDf[plantno] = self._refactorkWhDf(kWhDf, resampleFactor)
        dailyTotalKWhDf = dailyKWhDf.sum(axis=1)

        # reset axis
        plt.delaxes()
        ax = self.fig.add_subplot()

        # define the bar width
        width = 0.3
        # calculate the width assignment table
        widthTable = [w * width for w in np.arange(len(dailyKWhDf.columns))]  # [0, 0.2, 0.4, 0.6]
        widthTable = np.array(widthTable) - np.mean(widthTable)  # [-0.3, -0.1, 0.1, 0.3]
        x = np.arange(0, len(dailyKWhDf.index) * 2, 2)  # make it wider when step is 2
        for i, plantno in enumerate(dailyKWhDf):
            ax.bar(x + widthTable[i], dailyKWhDf[plantno], width=width, label=plantno)
        ax.plot(x, dailyTotalKWhDf, label='Total')

        # reassign the x-ticks
        ax.set_xticks(x, dailyKWhDf.index.strftime('%Y-%m-%d'))
        plt.xticks(rotation=90)

        ax.xaxis.set_major_locator(self.locator)
        ax.set_ylabel("kWh")
        ax.legend(loc='upper left')
        # set layout
        self.fig.tight_layout()
        plt.autoscale(enable=True, axis='x', tight=True)
        image_name = os.path.join(outPath, filename)
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)

        kwh = {}
        if dailyTotalKWhDf.shape[0]:
            kwh['min'] = dailyTotalKWhDf.min()
            kwh['avg'] = dailyTotalKWhDf.mean()
            kwh['max'] = dailyTotalKWhDf.max()
        else:
            kwh['min'] = 0
            kwh['avg'] = 0
            kwh['max'] = 0

        return kwh

    # this is group fuel level measurement
    def getGroupFuelLevelMeasurement(self, df_fuel_level_avgs, outPath, filename):
        # reset axis
        plt.delaxes()

        ax = self.fig.add_subplot()
        for plantno, df_fuel_level_avg in df_fuel_level_avgs.items():
            ax.plot(df_fuel_level_avg.index, df_fuel_level_avg, label=plantno)
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        ax.set_ylabel("Fuel Level %")
        self.fig.tight_layout()
        image_name = os.path.join(outPath, filename)
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)

    def getGroupkWPowerPlot(self, main_dfs, outPath, filename):
        """
        :param main_dfs: {plantno: pd.DataFrame}
        :param outPath:
        :return:
        """
        # reset axis
        plt.delaxes()
        ax = self.fig.add_subplot()

        kWPowerDf = pd.DataFrame()
        for i, (plantno, df) in enumerate(main_dfs.items()):
            df = df.resample("1T").mean()
            df = df.interpolate(method="linear", limit_direction="both")
            df = df[df.rpm > 1450]
            # create temp dataframe
            if i == 0:
                kWPowerDf = pd.DataFrame(df['actual_power'].values, index=df.index, columns=[plantno])
            else:
                actualPower = pd.DataFrame(df['actual_power'].values, index=df.index, columns=[plantno])
                kWPowerDf = pd.concat([kWPowerDf, actualPower], axis=1, join='outer')
        # fill nan
        kWPowerDf.fillna(0.0, inplace=True)
        # calculate the sum
        kWPowerDf['Total'] = kWPowerDf.sum(axis=1)
        # plot graph
        for plantno in kWPowerDf:
            ax.plot(kWPowerDf.index, kWPowerDf[plantno], label=plantno)
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        ax.set_ylabel("kW")
        ax.legend(loc='upper left')
        self.fig.tight_layout()
        image_name = os.path.join(outPath, filename)
        self.fig.savefig(image_name, bbox_inches="tight", transparent=True)

        # total kWh
        kwh_total = {}
        if kWPowerDf['Total'].shape[0]:
            kwh_total['min'] = kWPowerDf['Total'].min()
            kwh_total['avg'] = kWPowerDf['Total'].mean()
            kwh_total['max'] = kWPowerDf['Total'].max()
        else:
            kwh_total['min'] = 0
            kwh_total['avg'] = 0
            kwh_total['max'] = 0
        return kwh_total
