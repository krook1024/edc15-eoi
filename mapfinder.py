import sys
import clr
import os
from edcmap import Map
from dataclasses import dataclass, field
from tabulate import tabulate

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "\\lib")
clr.AddReference("EDCSuite.Parsers")
clr.AddReference("EDCSuiteBaseLibrary")
clr.AddReference("System.Collections")

import EDCSuiteParsers
import EDCSuiteBaseLibrary
from System.Collections.Generic import List


@dataclass
class Maps:
    soi: Map
    selector: Map
    durations: list[Map] = field(default_factory=list)


@dataclass
class Symbol:
    CodeBlock: int
    Flash_start_address: int
    Length: int
    Start_address: int
    Varname: str
    XaxisUnits: str
    X_axis_address: int
    X_axis_descr: str
    X_axis_ID: int
    X_axis_length: int
    YaxisAssigned: bool
    YaxisUnits: str
    Y_axis_address: int
    Y_axis_descr: str
    Y_axis_ID: int
    Y_axis_length: int
    Z_axis_descr: str
    flash_start_address: int
    length: int


def to_symbol(symbolHelper) -> Symbol:
    return Symbol(
        symbolHelper.CodeBlock,
        symbolHelper.Flash_start_address,
        symbolHelper.Length,
        symbolHelper.Start_address,
        symbolHelper.Varname,
        symbolHelper.XaxisUnits,
        symbolHelper.X_axis_address,
        symbolHelper.X_axis_descr,
        symbolHelper.X_axis_ID,
        symbolHelper.X_axis_length,
        symbolHelper.YaxisAssigned,
        symbolHelper.YaxisUnits,
        symbolHelper.Y_axis_address,
        symbolHelper.Y_axis_descr,
        symbolHelper.Y_axis_ID,
        symbolHelper.Y_axis_length,
        symbolHelper.Z_axis_descr,
        symbolHelper.Flash_start_address,
        symbolHelper.Length,
    )


def get_parser(filename: str):
    filetype = str(EDCSuiteBaseLibrary.Tools().DetermineFileType(filename, True))
    return getattr(EDCSuiteParsers, filetype + "FileParser")()


def parse_symbols(filename: str, cb: int) -> list[Symbol]:
    result = get_parser(filename).parseFile(filename, None, None)
    return [
        to_symbol(symbolHelper)
        for symbolHelper in filter(lambda x: x.CodeBlock == int(cb), result[0])
    ]


def get_eoi_maps(filename: str, cb: int, soi_map_number: int) -> Maps:
    symbols = parse_symbols(filename, cb)

    return Maps(
        get_soi(symbols, filename, soi_map_number),
        get_selector(symbols, filename),
        get_durations(symbols, filename),
    )


def get_bip_maps(filename: str, cb: int) -> tuple[Map, Map]:
    symbols = list(filter(lambda x: "BIP" in x.Varname, parse_symbols(filename, cb)))
    bip1 = Map(
        file=filename,
        config={
            "start": symbols[0].Flash_start_address,
            "fun": lambda x: x,
            "inv": lambda x: x,
            "x": symbols[0].X_axis_address,
            "x_fun": lambda x: x * 20.372434017595,
            "x_fun_inv": lambda x: x * 0.049085936375415,
        },
    )
    bip2 = Map(
        file=filename,
        config={
            "start": symbols[1].Flash_start_address,
            "fun": lambda x: x / 256,
            "inv": lambda x: x * 256,
            "x": symbols[1].X_axis_address,
            "x_fun": lambda x: x,
            "x_fun_inv": lambda x: x,
            "y": symbols[1].Y_axis_address,
            "y_fun": lambda x: (x * 0.0234375) - 78,
            "y_fun_inv": lambda x: -42.6667 * (-x - 78),
        },
    )
    return bip1, bip2


def get_soi(symbols: list[Symbol], filename: str, soi_map_number: int = 9) -> Map:
    symbols = sorted(
        list(filter(lambda x: "Start of" in x.Varname, symbols)),
        key=lambda x: x.Varname
    )
    if len(symbols) > soi_map_number:
        symbol = symbols[soi_map_number]
    else:
        symbol = symbols[len(symbols) - 1]
    return Map(
        file=filename,
        config={
            "start": symbol.Flash_start_address,
            "fun": lambda x: x * -0.023437 + 78,
            "inv": lambda x: 42.6676 * (78 - x),
            "x": symbol.X_axis_address,
            "x_fun": lambda x: x,
            "x_fun_inv": lambda x: x,
            "y": symbol.Y_axis_address,
            "y_fun": lambda x: x * 0.01,
            "y_fun_inv": lambda x: x * 100,
        },
    )


def get_selector(symbols: list[Symbol], filename: str) -> Map:
    try:
        symbol = sorted(
            list(filter(lambda x: "Selector for" in x.Varname, symbols)),
            key=lambda x: x.Varname,
        )[0]
    except IndexError:
        symbol = list(
            filter(
                lambda x: x.X_axis_length == 6
                and x.Y_axis_length == 1
                and x.YaxisUnits == "Grad KW",
                symbols,
            )
        )[0]

    return Map(
        file=filename,
        config={
            "start": symbol.Flash_start_address,
            "fun": lambda x: round(x / 256, 0),
            "x": symbol.X_axis_address,
            "x_fun": lambda x: round(x * -0.023437 + 78),
        },
    )


def get_durations(symbols: list[Symbol], filename: str) -> list[Map]:
    symbols = sorted(
        list(filter(lambda x: "Injector duration" in x.Varname, symbols)),
        key=lambda x: x.Varname,
    )
    return [
        Map(
            file=filename,
            config={
                "start": symbol.Flash_start_address,
                "fun": lambda x: x * 0.023437,
                "x": symbol.X_axis_address,
                "x_fun": lambda x: x * 0.01,
                "y": symbol.Y_axis_address,
                "y_fun": lambda x: x,
            },
        )
        for symbol in symbols
    ]


def get_soi_correctors(filename: str, cb: int) -> tuple[Map, Map]:
    symbols = parse_symbols(filename, cb)

    factor_symbol = list(
        filter(
            lambda x: x.X_axis_length == x.Y_axis_length == 9
            and x.XaxisUnits == "mg/st"
            and x.YaxisUnits == "°C",
            symbols,
        )
    )[0]

    factor = Map(
        file=filename,
        config={
            "start": factor_symbol.Flash_start_address,
            "fun": lambda x: round(x * 0.0001, 1),
            "inv": lambda x: x * 10000,
            "x": factor_symbol.X_axis_address,
            "x_fun": lambda x: round(x * 0.1 - 273.1, 2),
            "x_fun_inv": lambda x: -10 * (-x - 273.1),
            "y": factor_symbol.Y_axis_address,
            "y_fun": lambda x: x * 0.01,
            "y_fun_inv": lambda x: x * 100,
        },
    )

    correction_symbol = sorted(
        list(
            filter(
                lambda x: x.X_axis_length == x.Y_axis_length == 10
                and x.XaxisUnits == "mg/st"
                and x.YaxisUnits == "rpm",
                symbols,
            )
        ),
        key=lambda x: x.Flash_start_address,
        reverse=True,
    )[0]

    correction = Map(
        file=filename,
        config={
            "start": correction_symbol.Flash_start_address,
            "fun": lambda x: x * -0.0234375,
            "inv": lambda x: x / -0.0234375,
            "x": correction_symbol.X_axis_address,
            "x_fun": lambda x: x,
            "x_fun_inv": lambda x: x,
            "y": correction_symbol.Y_axis_address,
            "y_fun": lambda x: x * 0.01,
            "y_fun_inv": lambda x: x * 100,
        },
    )

    return correction, factor


def list_codeblocks(filename: str) -> None:
    print(f"Available codeblocks in {filename}")

    _, cbs, _ = get_parser(filename).parseFile(
        filename,
        List[EDCSuiteBaseLibrary.CodeBlock](),
        List[EDCSuiteBaseLibrary.AxisHelper](),
    )
    blocks = [
        [
            cb.CodeID,
            hex(cb.StartAddress),
            hex(cb.EndAddress),
            hex(cb.AddressID),
            ["Automatic", "Manual", "4WD"][cb.BlockGearboxType],
        ]
        for cb in cbs
    ]
    print(
        tabulate(
            blocks,
            headers=["CodeBlock ID", "Start", "End", "ID location", "Gearbox type"],
            tablefmt="rounded_grid",
        )
    )
