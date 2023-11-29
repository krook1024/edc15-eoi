#!/usr/bin/env python3

from edcmap import Map
from maps import soi
import pandas as pd 

pd.options.display.float_format = "{:,.2f}".format

filename = "CURRENT.bin"

soi_water_temp_correction_factor = Map(
    file=filename,
    config={
        "start": 0x7891A,
        "fun": lambda x: round(x * 0.0001, 1),
        "inv": lambda x: x * 10000,

        "x": 0x788f2,
        "x_fun": lambda x: round(x * 0.1 - 273.1, 2),
        "x_fun_inv": lambda x: -10 * (- x - 273.1),

        "y": 0x78908,
        "y_fun": lambda x: x * 0.01,
        "y_fun_inv": lambda x: x * 100
    },
)

print("SOI WATER TEMP CORRECTION FACTOR")
print(soi_water_temp_correction_factor)
print()

soi_water_temp_correction = Map(
    file=filename,
    config={
        "start": 0x78A34,
        "fun": lambda x: x * -0.0234375,
        "inv": lambda x: x / -0.0234375,

        "x": 0x78a08,
        "x_fun": lambda x: x,
        "x_fun_inv": lambda x: x,

        "y": 0x78a20,
        "y_fun": lambda x: x * 0.01,
        "y_fun_inv": lambda x: x * 100
    },
)

print("SOI WATER TEMP CORRECTION")
print(soi_water_temp_correction)
print()

for temp in soi_water_temp_correction_factor.x:
    print(f"SOI MAP FOR {temp} *C")

    lines = []
    for i in range(len(soi.x)):
        line = []
        curr_rpm = soi.x[i]
        for j in range(len(soi.y)):
            curr_iq = soi.y[j]
            curr_soi = soi.lines[i][j]
            corrected_soi = curr_soi + (soi_water_temp_correction_factor.at(curr_iq, temp) * soi_water_temp_correction.at(curr_iq, curr_rpm))
            line.append(round(corrected_soi, 2))
        lines.append(line)

    map = Map(x=soi.x, y=soi.y, lines=lines)
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
        correction = max(0, round(target - soi.at(curr_iq, curr_rpm), 2))
        line.append(correction)
    lines.append(line)

suggested_soi_corr = Map(x=soi_water_temp_correction.x, y=soi_water_temp_correction.y, lines=lines)
print(suggested_soi_corr)

#soi_water_temp_correction.lines = suggested_soi_corr.lines
#soi_water_temp_correction.write_to_file()