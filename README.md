# Manual Planner For Gates

Calculates x,y,z and yaw commands from a list of gate dimensions.

# Dependencies
* python3
* matplotlib (optional)

# Usage

```
usage: path_planner.py [--gatesin /path/to/gates.csv] [--pathout /path/to/path_out.csv] 
                       [--pathin /path/to/spline.csv]

optional arguments:
  --gatesin gates.csv    Gate definitions input file
  --pathout path.csv     Path output file
  --pathin spline.csv    Spline input file
``` 

If --pathout is specified, a set of waypoints will be computed based on the gates input file. If matplotlib is available, a figure will be shown illustrating the resulting gate and path waypoint data.

If --pathin is specified, a spline representation can be overlayed on top of the gates data to visualize the smoothed path waypoints. Note: a separate path waypoints to spline generation algorithm must be used.

# Gates Definition
The gates file should be a csv with the following header, and appropriately followed rows of data.

```
column params:
  - num                 Gate number
  - x                   X coordinate of the center of the gate (m)
  - y                   Y coordinate of the center of the gate (m)
  - z                   Z coordinate of the center of the gate (m)
  - rotation            Rotation of the entry direction of the gate (degrees)
  - offset_x            Offset in X of the entry from the center of the gate (m)
  - offset_y            Offset in Y of the entry from the center of the gate (m)
  - offset_z            Offset in Z of the entry from the center of the gate (m)
  - waypoint_before     Distance to insert a waypoint before a gate (m) [0 = no waypoint]
  - waypoint_after      Distance to insert a waypoint after a gate (m) [0 = no waypoint]
```


# IROS 2017
This script was originally designed as part of the autonomous drone racing competition for IROS 2017 in Vancouver, BC.

![IROS 2017](https://github.com/First-Commit/manual_planner/blob/master/iros2007_path.png)
