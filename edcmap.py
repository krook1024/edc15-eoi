from struct import pack, unpack

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
from scipy.interpolate import RegularGridInterpolator


def unp(byte):
    return unpack("<h", byte)[0]


def p(byte):
    return pack("<h", byte)


class RegularGridInterpolatorNNextrapol:
    def __init__(self, points, values):
        self.interp = RegularGridInterpolator(
            points, values, bounds_error=False, fill_value=np.nan
        )
        self.nearest = RegularGridInterpolator(
            points, values, method="nearest", bounds_error=False, fill_value=None
        )

    def __call__(self, xi):
        vals = self.interp(xi)
        idxs = np.isnan(vals)
        vals[idxs] = self.nearest(xi)
        return vals


class Map:
    def __init__(self, file=None, config=None, x=None, y=None, lines=None):
        if file is not None and config is not None:
            self.file = open(file, "rb")

            self.start = config["start"]
            self.fun = config["fun"]

            self.x_start = config["x"]
            self.x_fun = config["x_fun"]

            if "y" in config:
                self.y_start = config["y"]
                self.y_fun = config["y_fun"]

            if "inv" in config:
                self.inv = config["inv"]

            if "x_fun_inv" in config:
                self.x_fun_inv = config["x_fun_inv"]

            if "y_fun_inv" in config:
                self.y_fun_inv = config["y_fun_inv"]

            self.load()

        if x is not None and y is not None and lines is not None:
            self.x = x
            self.y = y
            self.lines = lines

    def __del__(self):
        if hasattr(self, "file"):
            self.file.close()

    def load_axis(self, start, fun):
        self.file.seek(start - 2)
        size = unp(self.file.read(2))
        axis = []
        for i in range(0, size):
            axis.append(fun(unp(self.file.read(2))))
        return axis

    def load(self):
        self.x = self.load_axis(self.x_start, self.x_fun)
        if hasattr(self, "y_start"):
            self.y = self.load_axis(self.y_start, self.y_fun)

        self.lines = []
        self.file.seek(self.start)
        for i in range(0, len(self.x)):
            line = []
            for j in range(0, len(self.y) if hasattr(self, "y") else 1):
                line.append(self.fun(unp(self.file.read(2))))
            self.lines.append(line)

    def write_axis(self, file, start, values, inv_fn):
        file.seek(start)
        for val in values:
            val = int(round(inv_fn(val)))
            file.write(p(val))

    def write_to_file(self):
        with open(self.file.name, "rb+") as file:
            # self.write_axis(file, self.x_start, self.x, self.x_fun_inv)
            # self.write_axis(file, self.y_start, self.y, self.y_fun_inv)

            file.seek(self.start)
            for i in range(0, len(self.x)):
                for j in range(0, len(self.y)):
                    val = int(round(self.inv(self.lines[i][j])))
                    file.write(p(val))

    def np(self):
        return np.array(self.lines).reshape(len(self.x), len(self.y))

    def df(self):
        if hasattr(self, "y"):
            df = pd.DataFrame(self.np(), columns=np.array(self.y), index=self.x)
        else:
            df = pd.DataFrame(self.lines, index=self.x)

        return df

    def __str__(self):
        return str(self.df())

    def at(self, x, y):
        X = np.array(self.x).flatten()
        Y = np.array(self.y).flatten()
        Z = self.np()

        interp = RegularGridInterpolatorNNextrapol((X, Y), Z)

        return interp((y, x)).item()

    def show_graph(self, ax, cmap=None):
        ax.plot_surface(
            np.array(self.x).reshape(len(self.x), 1),
            np.array(self.y),
            self.np(),
            cmap=plt.get_cmap("RdYlGn").reversed() if cmap is None else cmap,
            edgecolors="black",
            linewidth=0.25,
        )
