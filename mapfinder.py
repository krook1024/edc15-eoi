import sys
import clr
import os
from edcmap import Map
from dataclasses import dataclass, field

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


def cwd() -> str:
    return os.path.dirname(os.path.realpath(__file__))


def get_maps(filename: str, cb: int) -> Maps:
    sys.path.append(cwd() + "\\lib")
    clr.AddReference("EDCSuite.Parsers")
    clr.AddReference("EDCSuiteBaseLibrary")

    import EDCSuiteParsers
    import EDCSuiteBaseLibrary

    filetype = str(EDCSuiteBaseLibrary.Tools().DetermineFileType(filename, True))
    print(">> Identified {} as {}".format(filename, filetype))

    parser = getattr(EDCSuiteParsers, filetype + "FileParser")()
    result = parser.parseFile(filename, None, None)
    symbols = [
        to_symbol(symbolHelper)
        for symbolHelper in filter(lambda x: x.CodeBlock == int(cb), result[0])
    ]

    return Maps(
        get_soi(symbols, filename),
        get_selector(symbols, filename),
        get_durations(symbols, filename),
    )


def get_soi(symbols: list[Symbol], filename: str) -> Map:
    symbol = sorted(
        list(filter(lambda x: "Start of" in x.Varname, symbols)),
        key=lambda x: x.Varname,
        reverse=True,
    )[0]
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
