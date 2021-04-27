# -*- coding: utf-8 -*-
"""
                |=========================|
                | RIDE AND POWER ANALYSIS |
                |=========================|

Created on Tue Apr 20 09:56:34 2021

@author: Bobby (Github: ovrhuman)
"""

import os 
import re
import sys 
import datetime; import dateparser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopy.distance as distance
sys.path.insert(1, os.getcwd()+"/source/")
import CyclingAnalysisFunctions as power

start = datetime.datetime.now()

#os.chdir(os.path.dirname(sys.argv[0])) #set wd to source file location
working_dir = os.getcwd() + "/"
data_path = "Current_Ride/"  #os.getcwd()+
data_files = os.listdir(data_path)

# CREATE RIDE DATAFRAME 
ride, ride_name = power.load_ride_gpx(data_path + data_files[0])
ride_data = power.ride_to_dataframe(ride)
ride_data = power.speed_distance_climbing(ride_data)
ride_date = ride_data.time[0].date()
ride_path = power.make_ride_folder(ride_name, ride_data, working_dir)
user_path = power.make_user_folder(working_dir)

# add gradient to make linear model of gradient*cadence and CdA analysis 

# PLOT RIDE OVERVIEW
power.ride_summary_plot(ride_data, ride_name, ride_date, ride_path)

# POWER CURVE 
ride_length = len(ride_data)
power_curve = power.get_power_curve(ride_data)
power.powerCurve_plot_seconds(power_curve, ride_name, ride_date, ride_path, ride_length)
power.powerCurve_plot_minutes(power_curve, ride_name, ride_date, ride_path, ride_length)
# include all time best power curve on here

# RIDE SUMMARY STATS 
ride_summary_stats = power.get_summary_stats(ride_data, power_curve)
# include median cadence, best 20min speed, max speed, training stress?

# SAVE DATA 
ride_data.to_csv(ride_path + ride_name.replace(" ","_") +"_data.csv")
power_curve.to_csv(ride_path + ride_name.replace(" ", "_") + "_power_curve.csv")
ride_summary_stats.to_csv(ride_path + ride_name.replace(" ", "_") + "_summary_data.csv")
power.User_data_update(user_path, ride_data, ride_summary_stats)

"""
# move current ride to ride_history/current ride folder
try:
    os.rename(working_dir + data_path + data_files[0],ride_path+data_files[0])
except:
    print("Original gpx file not found, possibly already moved to ride_history")

end = datetime.datetime.now()
print("run time: ", end - start)
"""


