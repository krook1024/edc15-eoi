#!/usr/bin/env python3

from edcmap import Map
from maps import soi
from termcolor import colored

filename = "CURRENT.bin"

soi_water_temp_correction_factor = Map(
    file=filename,
    config={
        "start": 0x7891A,
        "fun": lambda x: x * 0.0001,
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
        "fun": lambda x: round(x * -0.023437, 2),
        "inv": lambda x: round(x / -0.023437, 0),

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
    print(colored(map, 'red'))
    print()