#!/usr/bin/env python3

from maps import soi, selector, durations
from edcmap import Map

import matplotlib.pyplot as plt
import pandas as pd
import argparse
import copy

pd.options.display.float_format = "{:,.2f}".format


def select_duration_at(soi):
    for i in range(len(selector.x)):
        if selector.x[i] <= soi:
            return i

    return len(selector.x) - 1


def get_actual_duration(soi):
    duration_lines = []
    n_lines = []

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

        duration_lines.append(actual_duration_line)
        n_lines.append(duration_n_line)

    return duration_lines, n_lines


def get_eoi(soi, actual_duration):
    eoi_lines = soi.np() - actual_duration.np()
    return Map(x=soi.x, y=soi.y, lines=eoi_lines.tolist())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="edc15-eoi",
        description="calculates the time of the end of injection event for diesel engines",
    )
    parser.add_argument("-p", "--plot", action="store_true")
    args = parser.parse_args()

    fig, axs = plt.subplots(3, 3, subplot_kw={"projection": "3d"})
    axs = axs.flatten().tolist()

    print("SOI")
    print(soi)
    soi.show_graph(axs[0])
    axs[0].set_title("SOI")
    print()

    print("SELECTOR")
    print(selector)
    print()

    for i in range(len(durations)):
        print(f"DURATION {i}")
        print(durations[i])
        print()
        axs[i + 1].set_title(f"DURATION {i}")
        durations[i].show_graph(axs[i + 1])

    for i in range(1, len(axs) - 1):
        axs[i].shareview(axs[0])

    actual_duration_lines, duration_n_lines = get_actual_duration(soi)
    actual_duration = Map(x=soi.x, y=soi.y, lines=actual_duration_lines)
    duration_n = Map(x=soi.x, y=soi.y, lines=duration_n_lines)

    print("SELECTED DURATION MAP")
    print(duration_n)
    print()

    print("ACTUAL DURATION")
    print(actual_duration)
    actual_duration.show_graph(axs[7])
    axs[7].set_title("ACTUAL DURATION")
    print()

    eoi = get_eoi(soi, actual_duration)

    print("EOI")
    print(eoi)
    eoi.show_graph(axs[8], plt.get_cmap("magma").reversed())
    axs[8].set_title("EOI")
    print()

    plt.tight_layout()
    plt.subplots_adjust(left=0, right=1, bottom=0, top=0.96, wspace=0, hspace=0)
    if args.plot:
        plt.show()

    target_eoi = None
    with open("CURRENT.bin", "r+b") as bin:
        target_eoi = Map(
            file=bin,
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
        )

        target_eoi.x = eoi.x
        target_eoi.y = eoi.y
        # target_eoi.lines = eoi.lines
        # target_eoi.write_to_file()

    print("TARGET EOI")
    print(target_eoi)
    print()

    corrected_soi_lines = soi.np() + (target_eoi.np() - eoi.np())
    corrected_soi = copy.copy(soi)
    corrected_soi.lines = corrected_soi_lines.tolist()

    print("NEW SOI")
    print(corrected_soi)
    print()

    print("NEW EOI")
    actual_duration_new, _ = get_actual_duration(corrected_soi)
    new_eoi = get_eoi(corrected_soi, Map(x=soi.x, y=soi.y, lines=actual_duration_new))
    print(new_eoi)
    print()

    print("NEW ACTUAL DURATION")
    print(Map(x=soi.x, y=soi.y, lines=actual_duration_new))
    print()

    print(
        "ERROR (mainly due to different selector being selected after changing soi, also floating point calculations)"
    )
    lines = new_eoi.np() - eoi.np()
    print(Map(x=soi.x, y=soi.y, lines=lines))
    print()
