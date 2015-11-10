"""
Data sources
"""

import math
import numpy

ft = lambda n: n / 10.


def f(x, y):
    """
    sample func
    """
    return x * x - y * y


def fx(x, y):
    """
    sample func
    """
    return 2 * x - 2 * y


def g(x, y):
    """
    sample func
    """
    return math.exp(-(x * x + y * y)) * math.sin(x) * math.cos(y)


def sin(x, y):
    """
    sample func
    """
    return numpy.sin(x * y) / (x * y)


def dsin():
    """
    sample func
    """
    xr = numpy.arange(-7., 7.05, 0.1)
    yr = numpy.arange(-5., 5.05, 0.05)
    data = [(x, [(y, sin(x, y)) for y in yr]) for x in xr]
    return data


def nonedatarandom():
    """
    sample func
    """
    xr = xrange(100)
    yr = xrange(150)
    ran = numpy.random.randint(1, 100 * 150, 500)

    data = []

    ind = 0

    for x in xr:
        datax = []
        for y in yr:
            if ind in ran:
                datax.append((y, numpy.nan))
            else:
                datax.append((y, f(x, y)))
            ind = ind + 1
        data.append((x, datax))

    return data


def nonedata():
    """
    sample func
    """
    xr = xrange(100)
    yr = xrange(150)
    data = []

    for x in xr:
        datax = []
        for y in yr:
            if x % 5 == 0:
                datax.append((y, numpy.nan))
            else:
                datax.append((y, f(x, y)))
        data.append((x, datax))

    return data


def dv():
    data = [(x, [(y, f(x, y), fx(x, y)) for y in xrange(-5, 6)]) for x in xrange(-4, 5)]
    return data


def dt():
    data = [(x, [(y, f(x, y)) for y in xrange(-5, 6)]) for x in xrange(-4, 5)]
    return data


def dx():
    data = [(x, [(y, f(x, y)) for y in xrange(0, 10)]) for x in xrange(0, 20)]
    return data


def dtx():
    data = [(ft(x), [(ft(y), g(ft(x), ft(y))) for y in xrange(-50, 60)]) for x in xrange(-40, 50)]
    return data


def dtv():
    data = [(ft(x), [(ft(y), f(ft(x), ft(y)), fx(ft(x), ft(y))) for y in xrange(-50, 60)]) for x in xrange(-40, 50)]
    return data


# Example of data with 2D numpy array
def zdata():
    data = numpy.array([[(lambda x, y: x * x - y * y)(x, y) for y in xrange(0, 10)] for x in xrange(0, 20)])
    return data


def zerodata():
    data = [(x, [(0, f(x, y)) for y in xrange(0, 10)]) for x in xrange(0, 8)]
    return data


def flatdata():
    data = [(x, [(y, 1) for y in xrange(0, 10)]) for x in xrange(0, 8)]
    return data


def contdata():
    data = [(x, [(y, 1, f(x, y)) for y in xrange(0, 10)]) for x in xrange(0, 8)]
    return data


def timeData():
    """ sample random time data """
    import random
    import datetime
    import pytz

    t = datetime.datetime(2013, 5, 23, 12, 15, 15, 0, tzinfo=pytz.UTC)
    data = []

    for _ in xrange(100):
        t = t + datetime.timedelta(0, random.randint(10, 60), 0)
        d = random.randint(10, 100)
        data.append((t, d))

    return [data]


def timeTSData():
    """ sample random time data """
    import random
    import datetime
    import pytz

    t = datetime.datetime(2013, 5, 23, 12, 15, 15, 0, tzinfo=pytz.UTC)
    data = []

    for _ in xrange(100):
        t = t + datetime.timedelta(0, random.randint(10, 60), 0)
        d = random.randint(10, 100)
        data.append((t, d))

    return [data]


def grid_data(num_data=200):
    """
    sample grid data
    """
    from numpy.random import uniform, seed
    from matplotlib.mlab import griddata
    import numpy as np

    seed(0)
    npts = num_data
    x = uniform(-2, 2, npts)
    y = uniform(-2, 2, npts)
    z = x*np.exp(-x**2 - y**2)
    # define grid.
    xi = np.linspace(-2.1, 2.1, npts)
    yi = np.linspace(-2.1, 2.1, npts)
    # grid the data.
    zi = griddata(x, y, z, xi, yi, interp='linear')

    return xi, yi, zi

