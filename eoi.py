#!/usr/bin/env python3

from maps import soi, selector, durations
from edcmap import Map

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse

pd.options.display.float_format = "{:,.2f}".format


def select_duration_at(current_soi):
    line = np.array(selector.lines).flatten().tolist()

    if current_soi > selector.x[0]:
        return int(line[0]), int(line[0])

    if current_soi < selector.x[-1]:
        return int(line[-1]), int(line[-1])

    for i in range(1, len(selector.x)):
        if current_soi > selector.x[i]:
            return int(line[i - 1]), int(line[i])


def get_actual_duration(soi_map):
    duration_lines = []
    n_lines = []

    for i in range(len(soi_map.x)):
        actual_duration_line = []
        duration_n_line = []
        curr_rpm = soi_map.x[i]
        for j in range(len(soi_map.y)):
            curr_iq = soi_map.y[j]
            curr_soi = soi_map.lines[i][j]
            one_dura_index, other_dura_index = select_duration_at(curr_soi)
            curr_dura = (
                durations[one_dura_index].at(curr_rpm, curr_iq)
                + durations[other_dura_index].at(curr_rpm, curr_iq)
            ) / 2

            actual_duration_line.append(curr_dura)
            duration_n_line.append(one_dura_index)

        duration_lines.append(actual_duration_line)
        n_lines.append(duration_n_line)

    return duration_lines, n_lines


def get_eoi(soi_map, actual_duration_map):
    eoi_lines = soi_map.np() - actual_duration_map.np()
    return Map(x=soi_map.x, y=soi_map.y, lines=eoi_lines.tolist())


def get_args():
    parser = argparse.ArgumentParser(
        prog="edc15-eoi",
        description="calculates the time of the end of injection event for diesel engines",
    )
    parser.add_argument(
        "-p", "--plot", action="store_true", help="show plots of the maps from the file"
    )
    parser.add_argument(
        "-i",
        "--init",
        action="store_true",
        help="initialize a map with the current EOI to be used as target EOI later (i prefer to use EGR :P)",
    )
    parser.add_argument(
        "-w", "--write", action="store_true", help="write the corrected SOI to the file"
    )
    parser.add_argument(
        "-a", "--print-all", action="store_true", help="print all possible information"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    if args.print_all:
        nrows = 3
        ncols = 3
    else:
        nrows = 1
        ncols = 3

    fig, axs = plt.subplots(nrows, ncols, subplot_kw={"projection": "3d"})
    axs = axs.flatten().tolist()
    axc = 0

    print("SELECTOR")
    print(selector)
    print()

    actual_duration_lines, duration_n_lines = get_actual_duration(soi)
    actual_duration = Map(x=soi.x, y=soi.y, lines=actual_duration_lines)
    duration_n = Map(x=soi.x, y=soi.y, lines=duration_n_lines)

    print("SELECTED DURATION MAP")
    print(duration_n)
    print()

    print("SOI (positive means BTDC)")
    print(soi)
    soi.show_graph(axs[axc])
    axs[0].set_title("SOI")
    axc += 1
    print()

    for i in range(len(durations)):
        if args.print_all:
            print(f"DURATION {i}")
            print(durations[i])
            print()
            axs[axc].set_title(f"DURATION {i}")
            durations[i].show_graph(axs[i + 1])
            axc += 1

    print("ACTUAL DURATION")
    print(actual_duration)
    actual_duration.show_graph(axs[axc])
    axs[axc].set_title("ACTUAL DURATION")
    axc += 1
    print()

    eoi = get_eoi(soi, actual_duration)

    print("EOI (positive means BTDC)")
    print(eoi)
    eoi.show_graph(axs[axc], plt.get_cmap("RdYlGn"))
    axs[axc].set_title("EOI")
    axc += 1
    print()

    target_eoi = Map(
        file="CURRENT.bin",
        config={  # EGR map :D
            "start": 0x718A8,
            "fun": lambda x: x * -0.023437 + 78,
            "inv": lambda x: 42.6676 * (78 - x),
            "x": 0x7186A,
            "x_fun": lambda x: x,
            "x_fun_inv": lambda x: x,
            "y": 0x7188E,
            "y_fun": lambda x: x * 0.01,
            "y_fun_inv": lambda x: x * 100,
        },
        x=eoi.x,
        y=eoi.y,
    )

    if args.init:
        target_eoi.lines = eoi.lines
        target_eoi.write_to_file()

    if args.write:
        print("TARGET EOI")
        print(target_eoi)
        print()

        corrected_soi_lines = soi.np() + (target_eoi.np() - eoi.np())
        corrected_soi = Map(x=soi.x, y=soi.y, lines=corrected_soi_lines.tolist())
        if args.write:
            soi.lines = corrected_soi.lines
            soi.write_to_file()

        print("NEW SOI")
        print(corrected_soi)
        print()

        print("NEW EOI")
        new_actual_duration_lines, _ = get_actual_duration(corrected_soi)
        new_eoi = get_eoi(
            corrected_soi, Map(x=soi.x, y=soi.y, lines=new_actual_duration_lines)
        )
        print(new_eoi)
        print()

    if args.print_all:
        print("NEW ACTUAL DURATION")
        print(Map(x=soi.x, y=soi.y, lines=new_actual_duration_lines))
        print()

        print(
            "ERROR DURING EOI CALCULATIONS (mainly due to different selector being selected after changing soi, "
            "also floating point calculations)"
        )
        lines = new_eoi.np() - target_eoi.np()
        print(Map(x=soi.x, y=soi.y, lines=lines))
        print()

        print(
            "ERROR IN ACTUAL DURATION EOI CALCULATIONS (mainly due to different selector being selected after "
            "changing soi, also floating point calculations)"
        )
        lines = np.array(new_actual_duration_lines) - actual_duration.np()
        print(Map(x=soi.x, y=soi.y, lines=lines))
        print()

    if args.plot:
        for i in range(1, len(axs) - 1):
            axs[i].shareview(axs[0])
        plt.subplots_adjust(
            left=0, right=1, bottom=0.05, top=0.983, wspace=0, hspace=0.15
        )
        plt.show()
