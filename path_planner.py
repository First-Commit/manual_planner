#!/usr/bin/env python3

import csv
import math
# check for visualization capabilities
plotter = True
try:
  import matplotlib.pyplot as plt
  import matplotlib.patches as patches
except:
  plotter = False
import argparse

kGateWidth = 1.3 # meters
kGateThickness = 0.2 # meters
# assuming origin of gate data is at center of first gate, this param shifts the 
# vehicle origin to a different location (eg, take off 3 meters in x from the first gate)
kOriginShift = (7.1,0)

def main(gates_input_filename, path_input_filename="", path_output_filename=""):
  """Loads gates file, and selectively computes path waypoints or loads a spline from disk
  Args:
      gates_input_filename: Input csv file with gate information
      path_input_filename: Input csv file with spline information
      path_output_filename: Output csv file for path waypoints computed from gate data
  """
  if plotter:
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111, aspect='equal')
  
  gates_data = loadGates(gates_input_filename)
  if plotter:
    drawGates(ax1, gates_data)
    if path_input_filename:
      path_data_in = loadPath(path_input_filename)
      drawPath(ax1, path_data_in)
  if path_output_filename:
    path_data = calcPath(gates_data)
    printPath(path_data)
    if plotter:
      drawPath(ax1, path_data)
    savePath(path_data, path_output_filename)
  
  if plotter:
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    plt.axis('equal')
    plt.axis('off')

    plt.show()

def printPath(path_data):
  for i, wp in enumerate(path_data):
    print("{:02d} | x: {:2.3f} y: {:2.3f} z: {:2.3f} yaw: {:2.3f}".format(i, wp['x'], wp['y'], wp['z'], wp['yaw']))

def savePath(path_data, filename):
  """Saves an instance of the path_data struct to disk
  Args:
      path_data (list of dicts): The list of x,y,z,yaw waypoints
      filename (string): The system path and filename where to save the path csv
  """
  with open(filename, "w") as f:
    writer = csv.DictWriter(f, fieldnames=['x','y','z','yaw'])
    writer.writeheader()
    for row in path_data:
      writer.writerow(row)
    writer.writerow({'x': 0.0, 'y': 0.0, 'z': 0.0, 'yaw': 0.0})
  print("Wrote path to csv: {}".format(filename))

def drawOrientation(ax1, center, angle):
  """Helper function that draws an arrow from a x,y point at a specified angle
  Args:
      ax1: The subplot figure handle
      center: The x,y origin of the root of the arrow (meters)
      angle: The angle of the arrow from the x-axis of the root (radians)
  """
  delta_x = math.cos(angle)*0.5
  delta_y = math.sin(angle)*0.5
  ax1.add_patch(
    patches.Arrow(
      center[0],
      center[1],
      delta_x,
      delta_y,
      facecolor="#ff6600",
      width=0.5
    )
  )

def calcPath(gates_data):
  """Calculate a set of path waypoints based on provided gate data
  Args:
      gates_data: List of dicts containing gate origin data and specifiers to assist
                  with how to choose path waypoints in and around the gates
  """
  waypoints_out = []
  for i,row in enumerate(gates_data):
    origin = {'x': float(row['x'])+kOriginShift[0], 'y': float(row['y'])+kOriginShift[1]}
    shift = float(row['offset_y'])
    angle = float(row['rotation'])
    angle_rad = angle*math.pi/180.0
    altitude = float(row['z'])
    gate_center = {'x': origin['x'], 'y': origin['y']+shift, 'z': altitude, 'yaw': angle_rad}
    waypoint_before = float(row['waypoint_before'])
    waypoint_after = float(row['waypoint_after'])
    sign_flip = 1
    y_135_fix = 0
    if angle == -90 or angle == -270:
      sign_flip = -1
    if angle == -135:
      y_135_fix = kGateWidth
    if not waypoint_before == 0:
      before_wp = {'x': -math.cos(angle_rad)*waypoint_before + gate_center['x'], 'y': sign_flip*math.sin(angle_rad)*waypoint_before + gate_center['y'] + y_135_fix, 'z': altitude, 'yaw': angle_rad}
      waypoints_out.append(before_wp)
    waypoints_out.append(gate_center)
    if not waypoint_after == 0:
      after_wp = {'x': math.cos(angle_rad)*waypoint_after + gate_center['x'], 'y': -sign_flip*math.sin(angle_rad)*waypoint_after + gate_center['y'] + y_135_fix, 'z': altitude, 'yaw': angle_rad}
      waypoints_out.append(after_wp)
  return waypoints_out

def drawPath(ax1, path_data):
  """Draws the path waypoints and connects them using arrows
  Args:
      ax1: The subplot figure handle
      path_data: The list of x,y,z,yaw waypoints
  """
  for i,wp in enumerate(path_data):
    # ax1.add_patch(
    #   patches.Circle(
    #     (float(wp['x']), float(wp['y'])),           # (x,y)
    #     0.2,          # radius
    #     facecolor="#ff6600"
    #   )
    # )
    if i < len(path_data)-1:
      delta = {'x': float(path_data[i+1]['x'])-float(path_data[i]['x']), 'y': float(path_data[i+1]['y'])-float(path_data[i]['y'])}
      ax1.add_patch(
        patches.Arrow(
          float(wp['x']),
          float(wp['y']),
          delta['x'],
          delta['y']
        )
      )
    drawOrientation(ax1, (float(wp['x']),float(wp['y'])), float(wp['yaw']))

def loadPath(path_file):
  """Loads a list of x,y,z,yaw path waypoints from disk (can be a discretized spline)
  Args:
      path_file: System filepath of the csv file
  """
  print("Opening path file: {}".format(path_file))
  reader = csv.DictReader(open(path_file), delimiter=',', skipinitialspace=True)
  return list(reader)

def loadGates(gates_file):
  """Loads a list of x,y,z,yaw waypoints from disk
  Args:
      gates_file: System filepath of the csv file
  """
  print("Opening gates file: {}".format(gates_file))
  reader = csv.DictReader(open(gates_file), delimiter=',', skipinitialspace=True)
  return list(reader)

def drawGates(ax1, gates_data):
  """Draws representations of the gate locations
  Args:
      ax1: The subplot figure handle
      gates_data: List of dicts containing gate origin data and specifiers to assist
                  with how to choose path waypoints in and around the gates
  """
  for i,row in enumerate(gates_data):
    origin = {'x': float(row['x'])+kOriginShift[0], 'y': float(row['y'])+kOriginShift[1]}
    angle = float(row['rotation'])
    shift = float(row['offset_y'])
    # angle = 0  
    bottomLeftOfRect = (origin['x']-kGateThickness/2.0, origin['y']-kGateWidth/2.0+shift)
    if angle == -90:
      bottomLeftOfRect = (origin['x']-kGateWidth/2.0, origin['y']+kGateThickness/2.0)
    if angle == -270:
      bottomLeftOfRect = (origin['x']+kGateWidth/2.0, origin['y']-kGateThickness/2.0)
    if angle == -135:
      # Hardcoded because geometry is hard
      bottomLeftOfRect = (origin['x']-kGateWidth*0.30, origin['y']+kGateWidth*0.40)
    if angle == -178:
      bottomLeftOfRect = (origin['x']+kGateThickness/2.0, origin['y']+kGateWidth/2.0+shift)
    ax1.add_patch(
      patches.Rectangle(
        bottomLeftOfRect,         # (x,y)
        0.2,                      # width
        kGateWidth,               # length
        angle=angle
      )
    )
    ax1.add_patch(
      patches.Circle(
        (origin['x'], origin['y']),   # (x,y)
        0.2,          # radius
        facecolor="#ff0000"
      )
    )
    text_origin = {'x': origin['x'], 'y': origin['y']-2.0}
    ax1.text(text_origin['x'], text_origin['y'], str(i+1))

  # add coordinate system
  ax1.add_patch(
    patches.Arrow(
      0.0,            # x
      0.0,            # y
      1.0,            # dx
      0.0,            # dy
      width=1.0,
      facecolor="#00ff00"
    )
  )
  ax1.text(1.1, -0.2, 'x')

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--gatesin", default="gates.csv", help="Gates input file")
  parser.add_argument("--pathin", default="", help="Path input file")
  parser.add_argument("--pathout", default="", help="Path output file")
  args = parser.parse_args()

  if not args.gatesin:
    print("Must specify gates input file (--gatesin)")

  main(args.gatesin, args.pathin, args.pathout)
