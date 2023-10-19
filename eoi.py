#!/usr/bin/env python3

from maps import soi, selector, durations
from edcmap import Map

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from pandas import DataFrame as df

def select_duration_at(soi):
    for i in range(len(selector.x)):
        if selector.x[i] <= soi:
            return i

    return len(selector.x) - 1

def get_actual_duration(soi):
    actual_duration_lines = []
    duration_n_lines = []
    for i in range(len(soi.x)):
        actual_duration_line = []
        duration_n_line = []
        curr_rpm = soi.x[i]
        for j in range(len(soi.y)):
            curr_iq = soi.y[j]
            curr_soi = soi.lines[i][j]
            dura_index = select_duration_at(curr_soi)

            actual_duration_line.append(durations[dura_index].at(curr_rpm, curr_iq))
            duration_n_line.append(dura_index)

        actual_duration_lines.append(actual_duration_line)
        duration_n_lines.append(duration_n_line)
    return (actual_duration_lines, duration_n_lines)

if __name__ == '__main__':
    fig, axs = plt.subplots(3, 3, subplot_kw={'projection': '3d'})
    axs = axs.flatten().tolist()

    print('SOI')
    print(soi)
    soi.show_graph(axs[0])
    axs[0].set_title('SOI')
    print()

    print('SELECTOR')
    print(selector)
    print()

    for i in range(len(durations)):
        #print(f'DURATION {i}')
        #print(durations[i])
        #print()
        axs[i+1].set_title(f'DURATION {i}')
        durations[i].show_graph(axs[i+1])

    for i in range(1, len(axs)-1):
        axs[i].shareview(axs[0])

    actual_duration_lines, duration_n_lines = get_actual_duration(soi)
    actual_duration = Map(x=soi.x, y=soi.y, lines=actual_duration_lines)
    duration_n = Map(x=soi.x, y=soi.y, lines=duration_n_lines)
    eoi_lines = np.array(soi.lines) - np.array(actual_duration.lines).reshape(len(soi.x), len(soi.y)).tolist()
    eoi = Map(x=soi.x, y=soi.y, lines=eoi_lines)

    print('ACTUAL DURATION')
    print(actual_duration)
    print()

    print('SELECTED DURATION MAP')
    print(duration_n)
    print()

    print('EOI')
    print(eoi)
    print()

    actual_duration.show_graph(axs[7])
    eoi.show_graph(axs[8])
    axs[7].set_title('ACTUAL DURATION')
    axs[8].set_title('EOI')

    plt.tight_layout()
    plt.subplots_adjust(left=0, right=1, bottom=0, top=.96, wspace=0, hspace=0)
    plt.show()
