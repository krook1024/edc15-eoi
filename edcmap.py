from struct import unpack
import numpy as np
import pandas as pd
from matplotlib import cm
from scipy.interpolate import RegularGridInterpolator

def unp(byte):
    return unpack('<h', byte)[0]

class RegularGridInterpolatorNNextrapol:
    def __init__(self, points, values):
        self.interp = RegularGridInterpolator(points, values, bounds_error=False,
                fill_value=np.nan)
        self.nearest = RegularGridInterpolator(points, values, method='nearest',
                bounds_error=False, fill_value=None)

    def __call__(self, xi):
        vals = self.interp(xi)
        idxs = np.isnan(vals)
        vals[idxs] = self.nearest(xi)
        return vals

class Map:
    def __init__(self, file=None, config=None, x=None, y=None, lines=None):
        if file is not None and config is not None:
            self.file = file

            self.start = config['start']
            self.fun = config['fun']

            self.x_start = config['x']
            self.x_fun = config['x_fun']

            if 'y' in config:
                self.y_start = config['y']
                self.y_fun = config['y_fun']

            self.load()

        if x is not None and y is not None and lines is not None:
            self.x = x
            self.y = y
            self.lines = lines

    def load_axis(self, start, fun):
        self.file.seek(start - 2)
        size = unp(self.file.read(2))
        axis = []
        for i in range(0, size):
            axis.append(fun(unp(self.file.read(2))))
        return axis

    def load(self):
        self.x = self.load_axis(self.x_start, self.x_fun)
        if hasattr(self, 'y_start'):
            self.y = self.load_axis(self.y_start, self.y_fun)

        self.lines = []
        self.file.seek(self.start)
        for i in range(0, len(self.x)):
            line = []
            for j in range(0, len(self.y) if hasattr(self, 'y') else 1):
                line.append(self.fun(unp(self.file.read(2))))
            self.lines.append(line)

    def __str__(self):
        if hasattr(self, 'y'):
            X = np.array(self.x).reshape(len(self.x), 1)
            Y = np.array(self.y)
            Z = np.array(self.lines)
            df = pd.DataFrame(Z, columns=Y, index=self.x)
        else:
            df = pd.DataFrame(self.lines, index=self.x)
        return str(df)

    def at(self, x, y):
        X = np.array(self.x).flatten()
        Y = np.array(self.y).flatten()
        Z = np.array(self.lines).reshape(len(self.x), len(self.y))

        interp = RegularGridInterpolatorNNextrapol((X, Y), Z)

        return interp((y, x)).item()

    def show_graph(self, ax):
        X = np.array(self.x).reshape(len(self.x), 1)
        Y = np.array(self.y)
        Z = np.array(self.lines)
        ax.plot_surface(X, Y, Z, cmap=cm.RdYlGn)
