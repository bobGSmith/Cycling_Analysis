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
os.mkdir(os.getcwd()+"\\ride")
data_path = os.getcwd()+"\\ride\\"
data_files = os.listdir(data_path)

# CREATE RIDE DATAFRAME 
ride, ride_name = power.load_ride_gpx(data_path + data_files[0])
ride_data = power.ride_to_dataframe(ride)
ride_data = power.speed_distance_climbing(ride_data)
ride_date = ride_data.time[0].date()
ride_path = power.make_ride_folder(ride_name, ride_data)
user_path = power.make_user_folder()

# PLOT RIDE OVERVIEW
power.ride_summary_plot(ride_data, ride_name, ride_date, ride_path)

# POWER CURVE 
power_curve = power.get_power_curve(ride_data)
power.powerCurve_plot_seconds(power_curve, ride_name, ride_date, ride_path)
power.powerCurve_plot_minutes(power_curve, ride_name, ride_date, ride_path)

# RIDE SUMMARY STATS 
ride_summary_stats = power.get_summary_stats(ride_data, power_curve)

# SAVE DATA 
ride_data.to_csv(ride_path + ride_name.replace(" ","_") +"_data")
power_curve.to_csv(ride_path + ride_name.replace(" ", "_") + "_power_curve")
ride_summary_stats.to_csv(ride_path + ride_name.replace(" ", "_") + "_summary_data")
power.User_data_update(user_path, ride_data, ride_summary_stats)


end = datetime.datetime.now()
print("run time: ", end - start)
