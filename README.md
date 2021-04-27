# Cycling_Analysis
## Table of Contents
1. [About](#1)
2. [Instructions:](#2)
3. [Future plans](#3)


## About<a name = 1></a>
Takes .gpx data from a gps cycling computer or downloaded from strava. It analyses power (W), cadence, speed, meters of climbing etc. It will plot power duration and speed duration curves etc. 

## Instructions:<a name = 2></a>

  1. download gpx file from cycling computer or strava
  2. put gpx file in the "Current_Ride" folder
  3. run the RideAnalysis.py script (ensuring working directory is set to the script location).

In the ride_history directory, a directory will be created with specific info about current ride, plots and a backup of the gpx file. There will also be a folder called User_Overview which will update with each ride to track long term performance. 

## Future plans<a name = 3></a>
### Calculate Efficency of Rider
I may implement something like a CdA estimator, which will calculate your efficency by working out how much power is lost to Drag and rolling resistance. 

It may be worth tracking this over time generally, as well as using it in specific rides to test efficeny of different bodypositions or equipment (Possibly using the lap button to Id the different test)

### Power to heart rate
I want to track something like the users average power output for a given heart rate as a way to esimate their fitness. 
