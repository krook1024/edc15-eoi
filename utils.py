import numpy as np
import colorama
from edcmap import Map


def select_duration_at(current_soi, maps):
    line = np.array(maps.selector.lines).flatten().tolist()

    if current_soi > maps.selector.x[0]:
        return int(line[0]), int(line[0])

    if current_soi < maps.selector.x[-1]:
        return int(line[-1]), int(line[-1])

    for i in range(1, len(maps.selector.x)):
        if current_soi > maps.selector.x[i]:
            return int(line[i - 1]), int(line[i])


def get_actual_duration(maps):
    duration_lines = []
    n_lines = []

    for i in range(len(maps.soi.x)):
        actual_duration_line = []
        duration_n_line = []
        curr_rpm = maps.soi.x[i]
        for j in range(len(maps.soi.y)):
            curr_iq = maps.soi.y[j]
            curr_soi = maps.soi.lines[i][j]
            one_dura_index, other_dura_index = select_duration_at(curr_soi, maps)
            curr_dura = (
                maps.durations[one_dura_index].at(curr_rpm, curr_iq)
                + maps.durations[other_dura_index].at(curr_rpm, curr_iq)
            ) / 2

            actual_duration_line.append(curr_dura)
            if one_dura_index == other_dura_index:
                duration_n_line.append(f"{one_dura_index}")
            else:
                duration_n_line.append(f"{one_dura_index},{other_dura_index}")

        duration_lines.append(actual_duration_line)
        n_lines.append(duration_n_line)

    return duration_lines, n_lines

def get_actual_duration_with_dura_1_axes(maps):
    duration_lines = []

    dura1 = maps.durations[1]

    for i in range(len(dura1.y)):
        curr_rpm = dura1.y[i]
        actual_duration_line = []

        for j in range(len(dura1.x)):
            curr_iq = dura1.x[j]
            curr_soi = maps.soi.at(curr_iq, curr_rpm)

            one_dura_index, other_dura_index = select_duration_at(curr_soi, maps)
            curr_dura = (
                maps.durations[one_dura_index].at(curr_rpm, curr_iq)
                + maps.durations[other_dura_index].at(curr_rpm, curr_iq)
            ) / 2

            actual_duration_line.append(curr_dura)

        duration_lines.append(actual_duration_line)

    return duration_lines

def get_eoi(maps, actual_duration_map):
    eoi_lines = maps.soi.np() - actual_duration_map.np()
    return Map(x=maps.soi.x, y=maps.soi.y, lines=eoi_lines.tolist())


def color_values(val: str, first, second, third) -> str:
    if val <= first:
        color = colorama.Fore.GREEN
    elif val <= second:
        color = colorama.Fore.YELLOW
    elif val <= third:
        color = colorama.Fore.MAGENTA
    else:
        color = colorama.Fore.RED

    return f"{color}{val}{colorama.Style.RESET_ALL}"


def print_df_colored(map: Map) -> None:
    colorama.init()
    df = map.df()
    qs = [q(df, 0.3), q(df, 0.6), q(df, 0.8)]
    colored_df = df.map(lambda x: color_values(x, qs[0], qs[1], qs[2]))
    colorama.deinit()
    print(colored_df.to_string())


def q(df, v) -> float:
    return df.quantile(v, interpolation="nearest", method="table").mean()
