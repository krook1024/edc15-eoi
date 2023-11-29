import pandas as pd
import colorama
from edcmap import Map

def color_values(val: str, first, second, third) -> str:
    if val <= first:
        color = colorama.Fore.GREEN
    elif val <= second:
        color = colorama.Fore.YELLOW
    elif val <= third:
        color = colorama.Fore.MAGENTA
    else:
        color = colorama.Fore.RED

    return f'{color}{val}{colorama.Style.RESET_ALL}'

def print_df_colored(map: Map) -> None: 
    colorama.init()
    df = map.df()
    qs = [q(df, 0.3), q(df, 0.6), q(df, 0.8)]
    colored_df = df.map(lambda x: color_values(x, qs[0], qs[1], qs[2]))
    colorama.deinit()
    print(colored_df.to_string())

def q(df, v) -> float:
    return df.quantile(v, interpolation='nearest', method='table').mean()