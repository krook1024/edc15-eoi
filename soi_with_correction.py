#!/usr/bin/env python3

from edcmap import Map
from mapfinder import get_eoi_maps, get_soi_correctors
import pandas as pd
import argparse


def get_args():
    parser = argparse.ArgumentParser(
        prog="edc15-soi-with-correction",
        description="calculates a recommended soi correction map for edc15 ecus",
    )
    parser.add_argument(
        "-c",
        "--codeblock",
        action="store",
        help="select codeblock",
        required=True,
    )
    parser.add_argument(
        "-f", "--filename", action="store", help="specify the filename", required=True
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    pd.options.display.float_format = "{:,.2f}".format

    maps = get_eoi_maps(args.filename, args.codeblock)
    soi_water_temp_correction, soi_water_temp_correction_factor = get_soi_correctors(
        args.filename, args.codeblock
    )

    print(
        f"SOI WATER TEMP CORRECTION FACTOR at {hex(soi_water_temp_correction_factor.start)}"
    )
    print(soi_water_temp_correction_factor)
    print()

    print(f"SOI WATER TEMP CORRECTION at {hex(soi_water_temp_correction.start)}")
    print(soi_water_temp_correction)
    print()

    for temp in soi_water_temp_correction_factor.x:
        print(f"SOI MAP FOR {temp} *C")

        lines = []
        for i in range(len(maps.soi.x)):
            line = []
            curr_rpm = maps.soi.x[i]
            for j in range(len(maps.soi.y)):
                curr_iq = maps.soi.y[j]
                curr_soi = maps.soi.lines[i][j]
                corrected_soi = curr_soi + (
                    soi_water_temp_correction_factor.at(curr_iq, temp)
                    * soi_water_temp_correction.at(curr_iq, curr_rpm)
                )
                line.append(round(corrected_soi, 2))
            lines.append(line)

        map = Map(x=maps.soi.x, y=maps.soi.y, lines=lines)
        print(map)
        print()

    print("SUGGESTED SOI CORRECTION MAP FOR 10 *BTDC ADVANCE AT 100%")

    lines = []
    for i in range(len(soi_water_temp_correction.x)):
        curr_rpm = soi_water_temp_correction.x[i]
        line = []
        for j in range(len(soi_water_temp_correction.y)):
            curr_iq = soi_water_temp_correction.y[j]
            target = 10
            correction = max(0, round(target - maps.soi.at(curr_iq, curr_rpm), 2))
            line.append(correction)
        lines.append(line)

    suggested_soi_corr = Map(
        x=soi_water_temp_correction.x, y=soi_water_temp_correction.y, lines=lines
    )
    print(suggested_soi_corr)

    # soi_water_temp_correction.lines = suggested_soi_corr.lines
    # soi_water_temp_correction.write_to_file()
