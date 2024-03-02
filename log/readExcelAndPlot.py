import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

infile = sys.argv[1]
outfile = sys.argv[2]

inputFile = 'csv/' + infile
outputFile = 'excel/' + outfile

plt.rcParams.update({'font.size': 12})

# Read csv file
df = pd.read_csv(inputFile)

# Save the file content to excel file
df.to_excel(outputFile, engine='openpyxl')

file = pd.read_excel(outputFile)
file.columns = ['', 'SampleTimeFine', 'dq_W', 'dq_X', 'dq_Y', 'dq_Z',
                'dv_X', 'dv_Y', 'dv_Z']

dq_w = file['dq_W']
dq_x = file['dq_X']
dq_y = file['dq_Y']
dq_z = file['dq_Z']

lenX = len(dq_x)
xAxis = np.arange(1, lenX + 1)

dv_x = file['dv_X']
dv_y = file['dv_Y']
dv_z = file['dv_Z']

dotSize = 4
orientationFig, oriSub = plt.subplots(4, sharex=True)

oriSub[0].scatter(xAxis, dq_w, color='orange', s=dotSize)
oriSub[1].scatter(xAxis, dq_x, color='red', s=dotSize)
oriSub[2].scatter(xAxis, dq_y, color='green', s=dotSize)
oriSub[3].scatter(xAxis, dq_z, color='blue', s=dotSize)
orientationFig.suptitle('Orientation Increment', fontsize=16)


velocityFig, velSub = plt.subplots(3, sharex=True)
velSub[0].scatter(xAxis, dv_x, color='red', s=dotSize)
velSub[1].scatter(xAxis, dv_y, color='green', s=dotSize)
velSub[2].scatter(xAxis, dv_z, color='blue', s=dotSize)
velocityFig.suptitle('Velocity Increment', fontsize=16)


# Set the y-axis labels for each subplot
oriSub[0].set_ylabel('Quat Incre W')
oriSub[1].set_ylabel('Quat Incre X')
oriSub[2].set_ylabel('Quat Incre Y')
oriSub[3].set_ylabel('Quat Incre Z')

velSub[0].set_ylabel('Velocity Incre X')
velSub[1].set_ylabel('Velocity Incre Y')
velSub[2].set_ylabel('Velocity Incre Z')

plt.show()
