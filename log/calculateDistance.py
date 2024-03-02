'''
    calculatedistance.py
    read excel file and then do some dead reckoning.
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy.signal import butter, lfilter

freq = 60
period = 1/freq
infile = sys.argv[1]
datafile = 'excel/' + infile

x_dist = []
y_dist = []


def get_data_from_file(input, col):
    file = pd.read_excel(input)
    file.columns = ['', 'sampletimefine', 'dq_w', 'dq_x', 'dq_y', 'dq_z',
                    'dv_x', 'dv_y', 'dv_z']
    return file[col].dropna().values


def plot_figure(dv_x, dv_y, dv_z, distance):
    dotSize = 4
    x_axis = np.arange(1, len(dv_x) + 1)
    velocityFig, velSub = plt.subplots(4, sharex=True)

    velSub[0].scatter(x_axis, dv_x, color='red', s=dotSize)
    velSub[1].scatter(x_axis, dv_y, color='green', s=dotSize)
    velSub[2].scatter(x_axis, dv_z, color='orange', s=dotSize)
    velSub[3].scatter(x_axis, distance, color='blue', s=dotSize)

    plt.show()
    plt.savefig('./dead-reckoning.png')


def plot_xy():
    fig, ax = plt.subplots()
    ax.plot(x_dist, y_dist)
    ax.grid()

    plt.xlabel('x', fontsize=20)
    plt.ylabel('y', fontsize=20)

    plt.axis('equal')
    plt.savefig('./plot.png')

    plt.show()


def rotate(x, y, theta):
    c, s = np.cos(theta), np.sin(theta)
    rotation = [[c, -s], [s, c]]
    x, y = rotation @ np.c_[x, y].t
    return x, y


def calculate_distance(v_x, v_y, dv_x, dv_y, dv_z, period):
    '''
    The distance IMU has traveled in the period.
    '''
    scale = 3.2/0.24
    dv_x, dv_y = norm_matrix(dv_x, dv_y)
    v_x += np.abs(dv_x)
    v_y += np.abs(dv_y)

    x = 0.5 * v_x * period * scale
    x_dist.append(x)

    y = 0.5 * v_y * period * scale
    y_dist.append(y)

    distance = np.sqrt(x**2 + y**2)
    return distance, v_x, v_y

# TODO: Add some filter for data
# TODO: Add complementary filter, plot according to x, y
# TODO: norm xac dinh van toc bang khong, chon epsilon khi imu dung yen


def butter_lowpass(cutoff, fs, order=5):
    return butter(order, cutoff, fs=fs, btype='low', analog=False)


def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


def filtered(x, y, z):
    # Filter requirements.
    order = 5
    fs = 60.0    # sample rate, Hz
    cutoff = 15  # desired cutoff frequency of the filter, Hz

    x_ret = butter_lowpass_filter(x[300:], cutoff, fs, order)
    y_ret = butter_lowpass_filter(y[300:], cutoff, fs, order)
    z_ret = butter_lowpass_filter(z[300:], cutoff, fs, order)

    return x_ret, y_ret, z_ret


def norm_matrix(x, y, stand_still_case=0.002):
    matrix = [x, y]
    ret = np.linalg.norm(matrix)
    if ret <= stand_still_case:
        x = 0
        y = 0

    return x, y


def main():
    dv_x = get_data_from_file(datafile, 'dv_x')
    dv_y = get_data_from_file(datafile, 'dv_y')
    dv_z = get_data_from_file(datafile, 'dv_z')

    dv_x_fil, dv_y_fil, dv_z_fil = filtered(dv_x, dv_y, dv_z)

    totalDistance = 0
    v_x, v_y = 0, 0
    distance = []
    for i in range(len(dv_x_fil)):
        ret, v_x, v_y = calculate_distance(v_x, v_y, dv_x_fil[i],
                                           dv_y_fil[i],
                                           dv_z_fil[i],
                                           period)
        totalDistance += ret
        distance.append(totalDistance)

    # last  = np.sqrt(x_dist[-1] ** 2 + y_dist[-1] ** 2)
    # print(khoangcach)

    scale = 3.2/0.24

    print(str(totalDistance))
    # plot_figure(dv_x_fil, dv_y_fil, dv_z_fil, distance)
    plot_xy()


if __name__ == "__main__":
    main()
