# -*- coding: utf-8 -*-
"""
Created on Tue Apr 20 09:56:34 2021

@author: bobby
"""

import os 
import re
import datetime; import dateparser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopy.distance as distance
import PowerFunctions as power

start = datetime.datetime.now()

#os.chdir(os.path.dirname(sys.argv[0])) #set wd to source file location

data_path = os.getcwd()+"\\ride\\"
data_files = os.listdir(data_path)

# CREATE RIDE DATAFRAME 
ride, ride_name = power.load_ride_gpx(data_path + data_files[0])
ride_data = power.ride_to_dataframe(ride)
ride_data = power.speed_distance_climbing(ride_data)
ride_date = ride_data.time[0].date()
ride_path = power.make_ride_folder(ride_name, ride_data)
user_path = power.make_user_folder()
# add gradient to make linear model of gradient*cadence and CdA analysis 

# PLOT RIDE OVERVIEW
power.ride_summary_plot(ride_data, ride_name, ride_date, ride_path)

# POWER CURVE 
power_curve = power.get_power_curve(ride_data)
power.powerCurve_plot_seconds(power_curve, ride_name, ride_date, ride_path)
power.powerCurve_plot_minutes(power_curve, ride_name, ride_date, ride_path)
# include all time best power curve on here

# RIDE SUMMARY STATS 
ride_summary_stats = power.get_summary_stats(ride_data, power_curve)
# include median cadence, best 20min speed, max speed, training stress?

# SAVE DATA 
ride_data.to_csv(ride_path + ride_name.replace(" ","_") +"_data")
power_curve.to_csv(ride_path + ride_name.replace(" ", "_") + "_power_curve")
ride_summary_stats.to_csv(ride_path + ride_name.replace(" ", "_") + "_summary_data")
power.User_data_update(user_path, ride_data, ride_summary_stats)


end = datetime.datetime.now()
print("run time: ", end - start)




###### DEV #######

# cadence histogram
plt.hist(ride_data.cadence)
plt.xlabel("Cadence (rpm)")
plt.ylabel("Time at cadence (s)")
plt.title("Cadence {}: Max: {:.0f}, Median: {:.0f}, Mean: {:.0f}".format(str(ride_date),
                                                              ride_data.cadence.max(),
                                                              ride_data.cadence.median(),
                                                              ride_data.cadence.iloc[np.where(ride_data.cadence != 0)].mean()))
plt.savefig(ride_path+ride_name.replace(" ","_")+"_cadence_distribution")
plt.show()

# cadence plot 
plt.fill_between(ride_data.seconds, y1 = ride_data.power.rolling(window=5*60).mean().max(), y2 = ride_data.elevation, color = "blue", alpha = 0.3)
plt.fill_between(ride_data.seconds, y1 =ride_data.elevation, y2=0, color = "lightgreen", alpha = 0.8, label = "elevation")
plt.plot(ride_data.seconds, ride_data.cadence.rolling(window=5*60).mean(), label ="cadence")
plt.plot(ride_data.seconds, ride_data.power.rolling(window=5*60).mean(), label = "5 min power")
plt.legend()
plt.savefig(ride_path + ride_name.replace(" ","_") + "_cadence_power", dpi =300)
plt.title("cadence power elevation plot")
plt.show()


# speed duration plot

cols = ["max_speed", "max_5s_speed", "max_5min_speed", "max_20min_speed", "max_60min_speed"]
labs = ["max", "5s", "5min", "20min","60min"]
for i in range(len(cols)):
    plt.bar(labs[i], ride_summary_stats.loc[0, cols[i]])
    plt.annotate(str(round(ride_summary_stats.loc[0, cols[i]], 1))+" km/h", xy = ( labs[i], ride_summary_stats.loc[0, cols[i]]), ha="center")
plt.plot(np.arange(len(labs)), np.repeat(ride_summary_stats.average_speed.iloc[0], len(labs)),
         linestyle ="dashed", label ="Average speed: {:.1f} km/h".format(ride_summary_stats.average_speed.iloc[0]))
plt.title("Speed Duration curve")
plt.ylabel("Speed (km/h)") ; plt.xlabel("Time at speed")
plt.legend(fontsize = "small", markerscale = 1, frameon = False)
plt.savefig(ride_path + ride_name.replace(" ","_") + "_speed_duration")
plt.show()
