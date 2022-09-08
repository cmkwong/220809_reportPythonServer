import os
import matplotlib.pyplot as plt
from codes.controllers.ServerController import ServerController

class MonthlyPlotController:
    def __init__(self, locator=None, formatter=None, figsize=(10, 6), dpi=150):
        self.locator = locator
        self.formatter = formatter
        self.fig = plt.figure(figsize=figsize, dpi=dpi)
        self.serverController = ServerController()

    # fuel consumption
    def getFuelConsumptionPlot(self, fl, fuelTank, topVolume, outPath, plantno):

        # reset axis
        plt.delaxes()

        fl["fuel_use_l"] = (fl['fl_usage'] / 100.0 * fuelTank + fl['initcount'] * topVolume).fillna(0)

        ax = self.fig.add_subplot()
        ax.bar(fl.index, fl.fuel_use_l, label="Consumption", color="darkorange", edgecolor="black")
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        # ax.xaxis.set_major_formatter(self.formatter)
        ax.set_ylabel("Litres")
        max_height = fl.fuel_use_l.max()
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
        image_name = os.path.join(outPath, "{}-fuel.png".format(plantno))
        self.fig.savefig(image_name, bbox_inches="tight")
        # plt.delaxes(ax=ax)

    # fuel level
    def getFuelLevelPlot(self, df_fuel_level_avg, outPath, plantno):
        # reset axis
        plt.delaxes()

        ax = self.fig.add_subplot()
        ax.plot(df_fuel_level_avg.index, df_fuel_level_avg, label="Fuel Level")
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        # ax.xaxis.set_major_formatter(self.formatter)
        ax.set_ylabel("%")

        self.fig.tight_layout()
        image_name = os.path.join(outPath, "{}-fuel_level.png".format(plantno))
        self.fig.savefig(image_name, bbox_inches="tight")
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
        self.fig.savefig(image_name, bbox_inches="tight")
        if main_df_copy.shape[0]:
            max_kwh = main_df_copy.sum()
        else:
            max_kwh = 0
        return max_kwh

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
        self.fig.savefig(image_name, bbox_inches="tight")
        return co2_df

    # kw power
    def getkWPowerPlot(self, main_df, outPath, plantno):
        # reset axis
        plt.delaxes()

        main_df_copy = main_df.copy()
        main_df_copy = main_df_copy.resample("1T").mean()
        main_df_copy = main_df_copy.interpolate(method="linear", limit_direction="both")
        main_df_copy = main_df_copy[main_df_copy.rpm > 1450]

        ax = self.fig.add_subplot()
        ax.plot(main_df_copy.index, main_df_copy.actual_power)
        plt.xticks(rotation=90)
        ax.xaxis.set_major_locator(self.locator)
        # ax.xaxis.set_major_formatter(self.formatter)
        ax.set_ylabel("kW")
        self.fig.tight_layout()
        image_name = os.path.join(outPath, "{}-power_output_consumption.png".format(plantno))
        self.fig.savefig(image_name, bbox_inches="tight")

        if main_df_copy.actual_power.shape[0]:
            avg_kw = main_df_copy.actual_power.mean()
            max_kw = main_df_copy.actual_power.max()
        else:
            avg_kw = 0
            max_kw = 0

        print(f"Avg Power = {avg_kw:.1f}kW, Max Power = {max_kw:.1f}kW")
        return avg_kw, max_kw
