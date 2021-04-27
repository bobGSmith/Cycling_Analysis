# -*- coding: utf-8 -*-

# CYCLING ANALYSIS FUNCTIONS #

import os 
import re
import datetime; import dateparser
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopy.distance as distance

def load_ride_gpx(path):
    with open(path, "r") as infile:
        ride = (infile.read()).replace("\n", " ")
        ride_name = re.search("<name>(.*)</name>", ride).group(1)
        ride = ride.split("<trkpt ")
        metadata = ride.pop(0)
    return ride, ride_name

def ride_to_dataframe(ride):
    ride_data = {"time":[], "seconds":[],"latitude":[], "longitude":[], "elevation":[], "temperature":[], "cadence":[], "power":[]}
    first = True
    start_unixtime = None
    for trackpoint in ride:
        ride_data = clean_trackpoint(trackpoint, ride_data)
        if first:
            ride_data["seconds"].append(0)
            start_unixtime = ride_data["time"][0].timestamp()
            first = False
        else:
            ride_data["seconds"].append(ride_data["time"][-1].timestamp() - start_unixtime)
    return pd.DataFrame(ride_data)


def powerCurve_plot_minutes(power_curve, ride_name, ride_date, plot_path,ride_length):
    power_curve = power_curve[20:]; power_curve = power_curve.set_index(power_curve.minutes)
    minutes_of_interest = [5,8,10,15,20,30,45,60]
    benchmark_minutes = np.array([x for x in minutes_of_interest if x < (ride_length//60)+1])
    print(benchmark_minutes)
    plt.grid(color = "silver", linestyle = "-", linewidth = 0.5)
    plt.plot(power_curve.minutes, power_curve.power)
    plt.ylabel("Watts")
    plt.xlabel("Minutes")
    plt.scatter(benchmark_minutes, y = power_curve.power[benchmark_minutes]) 
    for bs in benchmark_minutes:
        if bs in power_curve.minutes:
            if bs > 30:
                plt.annotate("{} min\n{:.0f} W".format(bs, power_curve.power[bs]), (bs-2,power_curve.power[bs]+3),size = 7)
            else:
                plt.annotate("{} min\n{:.0f} W".format(bs, power_curve.power[bs]), (bs+1,power_curve.power[bs]+1),size = 7)
    plt.title("Power Curve (4 - 60 minutes) - {}".format(ride_date))
    plt.savefig(plot_path+ride_name.replace(" ","_") + "_powercurve_minutes", dpi=300)
    plt.show()



def powerCurve_plot_seconds(power_curve, ride_name, ride_date, plot_path, ride_length):
    power_curve = power_curve.set_index(power_curve.seconds)
    seconds_of_interest = [5,10,30,60,90,120,180,240]
    benchmark_seconds = np.array([x for x in seconds_of_interest if x < (ride_length)+30])
    plt.grid(color = "silver", linestyle = "-", linewidth = 0.5)
    plt.plot(power_curve.seconds[0:21], power_curve.power[0:21])
    plt.ylabel("Watts")
    plt.xlabel("Seconds")
    plt.scatter(benchmark_seconds, y = power_curve.power[benchmark_seconds]) 
    for bs in benchmark_seconds:
        if bs in power_curve.seconds:
            if bs > 120:
                plt.annotate("{} sec\n{:.0f} W".format(bs, power_curve.power[bs]), (bs-10,power_curve.power[bs]+25),size = 7)
            else:
                plt.annotate("{} sec\n{:.0f} W".format(bs, power_curve.power[bs]), (bs+1,power_curve.power[bs]+25),size = 7)
    plt.title("Power Curve (0 - 240 sec) - {}".format(ride_date))
    plt.savefig(plot_path + ride_name.replace(" ","_") + "_powercurve_seconds", dpi=300)
    plt.show()



def power_ma(ride_data, window = 60*5):
    first = np.mean(ride_data.power[0:window])
    movingpower = [first] * window
    for i in range(60*5, len(ride_data)):
        movingpower.append(np.mean(ride_data.power[i-window:i]))
    return movingpower


def ride_summary_plot(ride_data,ride_name,ride_date, plot_path):
    ride_data["fiveminpower"]= power_ma(ride_data)
    max_speed = max(ride_data.speed)
    max_fiveminpower = max(ride_data.fiveminpower)
    peak_altitude = max(ride_data.elevation)
    plt.fill_between(ride_data.seconds,y1=(ride_data.elevation/peak_altitude * max_speed)+(max_speed/2), y2=0,alpha = 0.3,label = "Elevation", color = "gray")
    #plt.plot(ride_data.seconds, (ride_data.fiveminpower/max_fiveminpower * max_speed) - (min(ride_data.fiveminpower/max_fiveminpower)*(max_speed/2)),
    #         label = "5 min power (w)", color = "blue", alpha = 0.5)
    #plt.plot(ride_data.seconds, ride_data.speed.rolling(window = 30).mean(), label = "speed (km/h)",color = "black", alpha = 0.8)
    plt.scatter(ride_data.seconds,np.zeros(len(ride_data)),s=200, c = ride_data.power.rolling(window=5*60).mean(),cmap="hot", alpha = 0.5,marker ="s")
    plt.plot(ride_data.seconds, ride_data.speed.rolling(window = 30).mean(), label = "Speed (km/h)",color = "black", alpha = 0.8)
    #plt.annotate("Power Heatmap\nLighter = More Power!", (50, -5), color = "black", size= 10, alpha = 0.7)
    plt.scatter(x = [100], y = [0], label = "Power Heatmap\n(lighter = more power)", color = "red", marker = "s", s=200)
    plt.legend(fontsize = "small", markerscale = 0.5, frameon = False)
    plt.ylabel("Speed (km/h)")
    plt.xlabel("Time elapsed (s)")
    plt.title(ride_name +" "+str(ride_date) + "\nClimbing: {:.1f} m, Av.Speed: {:.1f} kph, Av.Power: {:.1f} W".format(ride_data.climbing.iloc[-1],
                                                                                                  np.mean(ride_data.speed),
                                                                                                  np.mean(ride_data.power)))
    plt.savefig(plot_path+ride_name.replace(" ","_") + "_overview.png", dpi = 300)
    plt.show()


def make_ride_folder(ride_name, ride_data, working_dir):
    try:
        os.mkdir(working_dir+"ride_history\\")
    except:
        None
    plot_path = working_dir+"ride_history\\" + ride_name.replace(" ","_") + "_" + (str(ride_data.time[0]).split("+")[0]).replace(" ","_").replace("-","").replace(":","")
    try:
        os.mkdir(plot_path)
    except:
        print("directory already exists") 
    return plot_path + "/"

def make_user_folder(working_dir):
    plot_path = working_dir+"ride_history/User_Overview" 
    try:
        os.mkdir(plot_path)
    except:
        print("updataing user overview")
    return plot_path + "/"

def get_summary_stats(ride_data,power_curve):
    ride_summary_stats = {"date":ride_data.time[0].timestamp(),
                          "duration_sec":(ride_data.time.iloc[-1] - ride_data.time[0]).total_seconds(),
                          "climbing_meters":ride_data.climbing.iloc[-1],
                          "average_speed":ride_data.speed.mean(),
                          "average_power":ride_data.power.mean(),
                          "max_speed":ride_data.speed.max(),
                          }
    if len(ride_data) > 60*2:
        ride_summary_stats["max_5s_speed"] = ride_data.speed.rolling(window=5).mean().max(),
        ride_summary_stats["power_3s"] = float(power_curve.power.iloc[np.where(power_curve.seconds == 3)]),
        ride_summary_stats["power_5s"] = float(power_curve.power.iloc[np.where(power_curve.seconds == 5)]),
        ride_summary_stats["power_10s"] = float(power_curve.power.iloc[np.where(power_curve.seconds == 10)]),
        ride_summary_stats["power_30s"] = float(power_curve.power.iloc[np.where(power_curve.seconds == 30)]),
        ride_summary_stats["power_1m"] = float(power_curve.power.iloc[np.where(power_curve.minutes == 1)]),
        ride_summary_stats["power_2m"] = float(power_curve.power.iloc[np.where(power_curve.minutes == 2)])
        
    if len(ride_data) > 60*5:
        ride_summary_stats["max_5min_speed"]= ride_data.speed.rolling(window= 60*5).mean().max()
        ride_summary_stats["power_5m"]= float(power_curve.power.iloc[np.where(power_curve.minutes == 5)])
    if len(ride_data) > 60*20:
        ride_summary_stats["power_10m"]= float(power_curve.power.iloc[np.where(power_curve.minutes == 10)])
        ride_summary_stats["max_20min_speed"]= ride_data.speed.rolling(window= 60*20).mean().max()
        ride_summary_stats["power_20m"]= float(power_curve.power.iloc[np.where(power_curve.minutes == 20)])
    if len(ride_data) > 60 * 60:
        ride_summary_stats["max_60min_speed"]= ride_data.speed.rolling(window= 60*60).mean().max()
        ride_summary_stats["power_1h"]= float(power_curve.power.iloc[np.where(power_curve.minutes == 60)])
    ride_summary_stats = pd.DataFrame(ride_summary_stats, index=[0])
    return ride_summary_stats


def User_data_update(user_path, ride_data, ride_summary_stats):
    if "User_data.csv" in os.listdir(user_path):
        User_data = pd.read_csv(user_path + "User_data.csv")
        User_data = User_data.set_index(User_data.date)
        if ride_data.time[0].timestamp() not in User_data.date:
            ride_summary_stats.set_index(ride_summary_stats.date)
            User_data = User_data.append(ride_summary_stats)
    else: 
        ride_summary_stats.to_csv(user_path+"User_data.csv")


def get_power_curve(ride_data):
    power_zones = np.array([1,2,3])
    power_zones = np.append(power_zones,np.arange(5,60,5)) 
    power_zones = np.append(power_zones,np.arange(60,5*60, 30))
    power_zones = np.append(power_zones,np.arange(5*60, 20*60, 60))
    power_zones = np.append(power_zones,np.arange(20*60, 65*60, 5*60))
    
    power_curve = {"seconds":[], "minutes":[],"power":[]}
    for z in power_zones:
        if len(ride_data) + 30 > z:
            cur = power_ma(ride_data, window = z)
            power_curve["seconds"].append(z)
            power_curve["minutes"].append(round(z/60, 2))
            power_curve["power"].append(max(cur))
    power_curve = pd.DataFrame(power_curve)
    return power_curve 




def speed_distance_climbing(ride_data):
    distances = [0]
    speed = [0]
    climbing = [0]
    for i in range(1, len(ride_data)):
        cur_dist = distance_between(ride_data, i-1, i)
        cur_time = (ride_data.seconds[i]- ride_data.seconds[i-1])/ (60*60)
        cur_elev = abs((ride_data.elevation[i] - ride_data.elevation[i-1])/1000)
        cur_dist_traveled = (cur_dist**2+cur_elev**2)**0.5
        
        distances.append(distances[-1] + cur_dist_traveled)
        climbing.append(climbing[-1]+relu(ride_data.elevation[i] - ride_data.elevation[i-1]))
        speed.append(cur_dist_traveled/ cur_time)
    ride_data["distance"] = distances
    ride_data["speed"] = speed
    ride_data["climbing"] = climbing
    return ride_data



def clean_trackpoint(trackpoint, tp):
    """where tp is a dictionary"""
    tp["time"].append(dateparser.parse(re.search("<time>(.*)</time>", trackpoint).group(1)))
    tp["latitude"].append(float(re.search('"(.*)"',trackpoint.split(' ')[0]).group(1)))
    tp["longitude"].append(float(re.search('"(.*)"',trackpoint.split(' ')[1]).group(1)))
    tp["elevation"].append(float(re.search("<ele>(.*)</ele>", trackpoint).group(1)))
    tp["temperature"].append(int(re.search("<gpxtpx:atemp>(.*)</gpxtpx:atemp>", trackpoint).group(1)))
    tp["cadence"].append(int(re.search("<gpxtpx:cad>(.*)</gpxtpx:cad>", trackpoint).group(1)))
    tp["power"].append(int(re.search("<power>(.*)</power>", trackpoint).group(1)))
    return tp



def relu(x):
    '''rectified linear activation function ReLU'''
    if x >= 0:
        return x
    else:
        return 0
    
    
def distance_between(ride_data, a, b):
    """where a and b are the index of the two points, and ride_data is a 
    dataframe containing columns .latitude and .longitude"""
    return distance.distance((ride_data.latitude[a], ride_data.longitude[a]),(ride_data.latitude[b], ride_data.longitude[b])).km
