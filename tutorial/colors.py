"""
Colors database
"""
import cPickle as pickle
import vtk

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

LINE_COLORS = ['#AB51BA', '#CC7832', '#628759', '#4674A9', '#B53B48', '#808080', '#30a2da', '#fc4f30',
               '#e5ae38', '#6d904f', '#8b8b8b']

COLOR_MAPS = ['Accent', 'Blues', 'BrBG', 'BuGn', 'BuPu', 'Dark2', 'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges', 'PRGn',
              'Paired', 'Pastel1', 'Pastel2', 'PiYG', 'PuBu', 'PuBuGn', 'PuOr', 'PuRd', 'Purples', 'RdBu', 'RdGy',
              'RdPu', 'RdYlBu', 'RdYlGn', 'Reds', 'Set1', 'Set2', 'Set3', 'Spectral', 'YlGn', 'YlGnBu', 'YlOrBr',
              'YlOrRd', 'autumn', 'binary', 'bone', 'cool', 'copper', 'flag', 'gist_earth', 'gist_gray', 'gist_heat',
              'gist_ncar', 'gist_rainbow', 'gist_stern', 'gist_yarg', 'gray', 'hot', 'hsv', 'jet', 'pink', 'prism',
              'spectral', 'spring', 'summer', 'winter']


def load_colormaps():
    """
    load color maps
    """
    return pickle.load(open('colormaps.ser'))


def load_colormap(name='hot'):
    """
    load color map
    """
    maps = load_colormaps()
    return maps.get(name, [])


def buildColormap(color='blue-red', reversed=True):
        clut = vtk.vtkLookupTable()
        luts = load_colormaps()

        if color in luts:
            lut = luts[color]
            if reversed:
                lut.reverse()
            clut.SetNumberOfColors(len(lut))
            clut.Build()
            for i in xrange(len(lut)):
                lt = lut[i]
                clut.SetTableValue(i, lt[0], lt[1], lt[2], lt[3])

            return clut

        hue_range = 0.0, 0.6667
        saturation_range = 1.0, 1.0
        value_range = 1.0, 1.0

        if color.lower() == 'blue-red':
            if reversed:
                hue_range = 0.0, 0.6667
                saturation_range = 1.0, 1.0
                value_range = 1.0, 1.0
            else:
                hue_range = 0.6667, 0.0
                saturation_range = 1.0, 1.0
                value_range = 1.0, 1.0
        elif color.lower() == 'black-white':
            if reversed:
                hue_range = 0.0, 0.0
                saturation_range = 0.0, 0.0
                value_range = 1.0, 0.0
            else:
                hue_range = 0.0, 0.0
                saturation_range = 0.0, 0.0
                value_range = 0.0, 1.0

        clut.SetHueRange(hue_range)
        clut.SetSaturationRange(saturation_range)
        clut.SetValueRange(value_range)
        clut.Build()

        return clut
