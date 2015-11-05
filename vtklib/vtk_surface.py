"""
Pawel Potocki - vtk surface canvas
"""

import copy
import math
import numpy
import vtk
import logging
import functools32 as func
import colors


logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.DEBUG)


def colorAsFloatValues(color):
    """ convert color values """
    return color[0] / 255., color[1] / 255., color[2] / 255.


def calcStep(step):
    """ calculate step """
    if step == 0:
        return 1

    fact = math.floor(math.log10(step))
    fraction = float(step) / math.pow(10, fact)

    if fraction < 1.5:
        fraction = 1
    elif fraction < 3:
        fraction = 2
    elif fraction < 7:
        fraction = 5
    else:
        fraction = 10

    final_step = math.pow(10, fact) * fraction

    return final_step


class VTKSurfaceConfig(object):
    """ VTK Canvas configurations  """

    def __init__(self):
        """ default init """
        self._labelFormat = '%6.4g'
        self._xLabelsFormat = '%6.4g'
        self._yLabelsFormat = '%6.4g'
        self._zLabelsFormat = '%6.4g'
        self._xLabel = 'X'
        self._yLabel = 'Y'
        self._zLabel = 'Z'
        self._nLabels = 5
        self._lookupTables = colors.load_colormaps()
        self._rotateX = '30'
        self._rotateY = '30'
        self._debug = True
        self._colorMaps = colors.COLOR_MAPS

    def Debug(self):
        """ debug on/off flag """
        return self._debug

    def RotateX(self):
        """ rotate angle by X axis """
        return self._rotateX

    def RotateY(self):
        """  rotate angle by Y axis """
        return self._rotateY

    def LabelFormat(self):
        """ get labels format """
        return self._labelFormat

    def XLabelsFormat(self):
        """ get x labels format """
        return self._xLabelsFormat

    def YLabelsFormat(self):
        """ get y labels format """
        return self._yLabelsFormat

    def ZLabelsFormat(self):
        """ get z labels format """
        return self._zLabelsFormat

    def XLabel(self):
        """ get x label """
        return self._xLabel

    def YLabel(self):
        """ get y label """
        return self._yLabel

    def ZLabel(self):
        """ get z label """
        return self._zLabel

    def NLabels(self):
        """ get number of labels """
        return self._nLabels

    def LookupTables(self):
        """ get lookup tables """
        return self._lookupTables

    def ColorMaps(self):
        """ color maps """
        return self._colorMaps


def printColorMaps():
    config = VTKSurfaceConfig()
    for c in config.ColorMaps():
        print '\t' + c


def getColorMaps():
    config = VTKSurfaceConfig()
    return config.ColorMaps()


def remap(data):
    """ simple remapping - take x and y as natural indexes from 2D numpy array """
    if isinstance(data, (list, tuple)):
        return data

    ndim = data.ndim
    shape = data.shape
    if ndim != 2 and len(shape) != 2:
        return []

    return [(x, [(y, data[x, y]) for y in xrange(0, shape[1])]) for x in xrange(0, shape[0])]


def convertData(x_yzv_pairs, **kwargs):
    """ convert x_yzv value pars to vtk compatible data """

    if x_yzv_pairs is None:
        return [], [], [], []

    x = []
    y = []
    z = []
    v = []

    hasV = False
    try:
        if len(x_yzv_pairs[0][1][0]) == 3:
            hasV = True
    except:
        hasV = False

    row = 0

    for d in x_yzv_pairs:
        x.append(d[0])
        for yzv in d[1]:
            if row == 0:
                y.append(yzv[0])
            z.append(yzv[1])
            if hasV:
                v.append(yzv[2])
        row += 1

    x = numpy.array(x)
    y = numpy.array(y)
    z = numpy.array(z).reshape(x.size, y.size)
    if v:
        v = numpy.array(v).reshape(x.size, y.size)

    return x, y, z, v


class VTKSurface3D(object):
    def __init__(self, x_yzv_pairs, **kwargs):
        """
        default init
        """
        self.reset()
        self.kwargs = kwargs
        self.parent = kwargs.get('parent', None)
        self.bgColor = kwargs.get('bgColor', colors.GRAY)
        self.fgColor = colorAsFloatValues(kwargs.get('fgColor', colors.WHITE))
        self.config = kwargs.get('config', VTKSurfaceConfig())
        self.appName = kwargs.get('appName', 'vtkApp')
        self.Points = None
        self.Colors = None
        self.actors = []
        self.autoZRange = kwargs.get('autoZRange', False)
        self.customZRange = kwargs.get('customZRange', None)
        self.rotateX = kwargs.get('rotateX', 30)
        self.rotateY = kwargs.get('rotateY', 30)
        self.rotateZ = kwargs.get('rotateZ', 120)
        self.posFactor = kwargs.get('posFactor', 1)
        self.zoomFactor = kwargs.get('zoomFactor', 1)
        self.fontFactor = kwargs.get('fontFactor', 0.75)
        self.opacitySlice = kwargs.get('opacitySlice', 0.55)
        self.callbacks = copy.copy(kwargs.get('callbacks', {}))
        self.logToFile = kwargs.get('logToFile', False)
        self.renderer = kwargs.get('renderer', None)
        self.doRender = kwargs.get('doRender', True)
        self.bounds = None
        self.center = None
        self.geom = None
        self.out = None
        self.mapper = None
        self.warp = None

        if self.renderer is None:
            raise Exception('No renderer defined ')

        if self.logToFile:
            self.setupLogging()

        if self.doRender:
            self.render_surface(x_yzv_pairs, **kwargs)
            if self.hasData:
                self.calculatePositions()
                self.setDefaultView()

    def SetValue(self, x_yzv_pairs, **kwargs):
        self.config = kwargs.get('config', VTKSurfaceConfig())
        self.clear()
        self.render_surface(x_yzv_pairs, **kwargs)
        if self.hasData:
            self.calculatePositions()
            self.setDefaultView()

    def fireCallbacks(self, callback=None):
        callFunc = self.callbacks.get(callback, None)
        if callFunc and callable(callFunc):
            if callback == 'OnDataRange':
                callFunc(self.getDataRanges())
            if callback == 'OnCutterDataSet':
                callFunc(self.getCutterData())
        else:
            for callback, callFunc in self.callbacks.iteritems():
                if callback == 'OnDataRange' and callable(callFunc):
                    callFunc(self.getDataRanges())
                if callback == 'OnCutterDataSet' and callable(callFunc):
                    callFunc(self.getCutterData())

    def redraw( self ):
        """ invalidate graph """
        if self.parent:
            self.parent.invalidate()

    def clear(self):
        """
        clear current actors
        """
        for a in self.actors:
            self.renderer.RemoveActor(a)
        self.actors = []

    def getActors(self):
        """ get current modeled actors """
        return self.actors

    def render_surface(self, x_yzv_pairs, **kwargs):
        """ render surface with data """
        self.reset()
        doRemap = kwargs.get('remapData', False)
        if doRemap:
            x_yzv_pairs = remap( x_yzv_pairs )
        (x, y, z, v) = convertData(x_yzv_pairs, **kwargs)
        if self.render_geometry(x, y, z, v, **kwargs):
            self.render(**kwargs)

    def re_render_surface(self):
        """ re render the surface """
        nargs = copy.copy(self.kwargs)
        self.render(**nargs)

    def getActiveCamera(self):
        """ get active camera """
        return self.renderer.GetActiveCamera()

    def resetCamera(self):
        """ reset camera """
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.redraw()

    def calculatePositions(self):
        """ calcualte position """
        self.bounds = self.mapper.GetBounds()
        self.center = self.mapper.GetCenter()

        xx = max(self.bounds[1] - self.center[0], self.center[0] - self.bounds[0])
        yy = max(self.bounds[3] - self.center[1], self.center[1] - self.bounds[2])
        zz = max(self.bounds[5] - self.center[2], self.center[2] - self.bounds[4])

        if self.zoomFactor <= 0:
            self.zoomFactor = 1

        p = max(xx, yy, zz)
        d = 5 * self.posFactor

        self.distance = d * p
        self.position = (0, self.distance, self.center[2])

    def setDefaultView(self):
        """ set default view """
        cam = vtk.vtkCamera()
        cam.ParallelProjectionOff()
        cam.SetViewUp(0, 0, 1)
        cam.SetPosition(self.position)
        cam.SetFocalPoint(self.center)
        cam.Azimuth(self.rotateZ)
        cam.Elevation(self.rotateX)
        self.renderer.SetActiveCamera(cam)
        self.renderer.ResetCamera()
        cam.Zoom(self.zoomFactor)
        self.renderer.ResetCameraClippingRange()
        self.redraw()

    def setYAxisView(self):
        """ set y axis view """
        cam = vtk.vtkCamera()
        cam.ParallelProjectionOff()
        cam.SetViewUp(0, 0, 1)
        cam.SetPosition(0, -self.distance, 0)
        cam.SetFocalPoint(0, -self.center[2], 0)
        self.renderer.SetActiveCamera(cam)
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.redraw()

    def setZAxisView(self):
        """ set z axis view """
        cam = vtk.vtkCamera()
        cam.ParallelProjectionOff()
        cam.SetViewUp(0, 1, 0)
        cam.SetPosition(0, 0, self.distance)
        cam.SetFocalPoint(0, 0, -self.center[2])
        self.renderer.SetActiveCamera(cam)
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.redraw()

    def setXAxisView(self):
        """ set x axis view """
        cam = vtk.vtkCamera()
        cam.ParallelProjectionOff()
        cam.SetViewUp(0, 0, 0)
        cam.SetPosition(self.distance, 0, 0)
        cam.SetFocalPoint(self.center[2], 0, 0)
        cam.Roll(270)
        self.renderer.SetActiveCamera(cam)
        self.renderer.ResetCamera()
        self.renderer.ResetCameraClippingRange()
        self.redraw()

    def setupLogging(self):
        """ setup local login """
        import os
        temp = os.path.split(os.tempnam())[0]
        app = ''.join(c for c in self.appName if 'a' <= c.lower() <= 'z') + '.log.'
        logName = os.path.join(temp, app)

        fileOutputWindow = vtk.vtkFileOutputWindow()
        fileOutputWindow.SetFileName(logName)

        outputWindow = vtk.vtkOutputWindow().GetInstance()
        if outputWindow:
            outputWindow.SetInstance(fileOutputWindow)

    def reset(self):
        """ clear all properties """
        self.distance = 1.0
        self.position = 1.0
        self.XScale = 1.0
        self.YScale = 1.0
        self.ZScale = 1.0
        self.XLimit = (0, 0)
        self.YLimit = (0, 0)
        self.ZLimit = (0, 0)
        self.hasData = False
        self.gridfunc = None
        self.mapper = None
        self.Points = None
        self.Colors = None
        self.XCutterTransform = None
        self.YCutterTransform = None
        self.ZCutterTransform = None
        self.xplane = None
        self.yplane = None
        self.zplane = None
        self.XCutter = None
        self.YCutter = None
        self.ZCutter = None
        self.XCutterMapper = None
        self.YCutterMapper = None
        self.ZCutterMapper = None
        self.XCutterFactor = 1
        self.YCutterFactor = 1
        self.ZCutterFactor = 1
        self.XCutterDelta = None
        self.YCutterDelta = None
        self.ZCutterDelta = None
        self.rotateX = 30
        self.rotateY = 30
        self.rotateZ = 120
        self.zoomFactor = 1
        self.posFactor = 1

    def getCutterData(self):
        """
        Return Cutters data
        """
        return self.getXCutterData(), self.getYCutterData()

    @func.lru_cache
    def _getXScale(self):
        """ calculate limit factor and cache it """
        dlim = self.YLimit
        plim = (self.XCutterMapper.GetBounds()[2], self.XCutterMapper.GetBounds()[3])
        scl = (plim[1] - plim[0]) / (dlim[1] - dlim[0])

        if scl < 0:
            scl = 1

        return scl

    def getXCutterData(self):
        """ Return X Cutters data """

        if not self.XCutterMapper:
            return None

        scl = self._getXScale()

        def scale(p):
            return p / scl

        self.XCutterMapper.Update()
        out = self.XCutterMapper.GetInput()
        data = [(scale(out.GetPoint(i)[1]), out.GetPoint(i)[2]) for i in xrange(out.GetNumberOfPoints())]
        data = sorted(data, key=lambda s: s[0])

        return data

    @func.lru_cache
    def _getYscale(self):
        """ calculate limit factor and cache it """
        dlim = self.XLimit
        plim = (self.YCutterMapper.GetBounds()[0], self.YCutterMapper.GetBounds()[1])
        scl = (plim[1] - plim[0]) / (dlim[1] - dlim[0])

        if scl < 0:
            scl = 1

        return scl

    def getYCutterData(self):
        """ Return Y Cutters data """

        if not self.YCutterMapper:
            return None

        scl = self._getYscale()

        def scale(p):
            return p / scl

        self.YCutterMapper.Update()
        out = self.YCutterMapper.GetInput()
        data = [(scale(out.GetPoint(i)[0]), out.GetPoint(i)[2]) for i in xrange(out.GetNumberOfPoints())]
        data = sorted(data, key=lambda s: s[0])

        return data

    @func.lru_cache
    def _getXYScale(self):
        """ calculate limit factor and cache it """

        bounds = self.mapper.GetBounds()

        xlim = self.XLimit
        xplim = (bounds[0], bounds[1])
        xscl = (xplim[1] - xplim[0]) / (xlim[1] - xlim[0])

        if xscl < 0:
            xscl = 1

        ylim = self.YLimit
        yplim = (bounds[2], bounds[3])
        yscl = (yplim[1] - yplim[0]) / (ylim[1] - ylim[0])

        if yscl < 0:
            yscl = 1

        return xscl, yscl

    def getZCutterData(self):
        """ Return Z Cutters data """

        if not self.ZCutterMapper:
            return None

        xscale, yscale = self._getXYScale()

        def scalex(p):
            return p / xscale

        def scaley(p):
            return p / yscale

        self.ZCutterMapper.Update()
        out = self.ZCutterMapper.GetInput()
        data = [(scalex(out.GetPoint(i)[0]), scaley(out.GetPoint(i)[1])) for i in xrange(out.GetNumberOfPoints())]
        data = sorted(data, key=lambda s: s[0])

        return data

    def getDataRanges(self):
        """ Return data ranges """

        return self.XLimit, self.YLimit, self.ZLimit

    def computeScale(self, shape):
        bounds = shape.GetBounds()

        bx = bounds[1] - bounds[0]
        by = bounds[3] - bounds[2]
        bz = bounds[5] - bounds[4]
        mx = min(bx, by)
        zs = float(bz) / float(mx)

        return zs

    def render_geometry(self, vx, vy, vz, mv, **kwargs):
        """ create geometry """

        self.hasData = False
        gridData = kwargs.get('gridData', True)

        if gridData:
            self.gridfunc = vtk.vtkStructuredGrid()
        else:
            self.gridfunc = vtk.vtkRectilinearGrid()

        # check data structure
        if type(vx) is not numpy.ndarray or type(vy) is not numpy.ndarray:
            logging.error('X,Y vectors must be numpy arrays')
            return False

        if type(vz) is not numpy.ndarray:
            logging.error('Z vector must be numpy array')
            return False

        if isinstance(mv, (list, tuple)) and len(mv) > 0:
            logging.error('V scalars must be numpy array')
            return False

        if len(vx) == 0 or len(vy) == 0 or len(vz) == 0:
            logging.error('Zero size data')
            return False

        mva = isinstance(mv, numpy.ndarray) and mv.any()

        if vz.ndim != 2:
            logging.error('Z must be 2 dimensional numpy matrix')
            return False

        if vz[0].size != vy.size:
            logging.error('Y dimension not match')
            return False

        if vz.transpose()[0].size != vx.size:
            logging.error('X dimension not match')
            return False

        if mva:
            if mv.size != vz.size or vz[0].size != mv[0].size or vz[1].size != mv[1].size:
                logging.error('Z and V dimension not match')
                return False

        Nx = vx.size
        Ny = vy.size
        Nz = vz.size

        # put data, z, into a 2D structured grid
        self.Points = vtk.vtkPoints()
        [self.Points.InsertNextPoint(vx[i], vy[j], vz[i, j]) for j in xrange(Ny) for i in xrange(Nx)]

        if gridData:
            self.gridfunc.SetDimensions(Nx, Ny, 1)
            self.gridfunc.SetPoints(self.Points)
        else:
            xCoords = vtk.vtkFloatArray()
            [xCoords.InsertNextValue(vx[i]) for i in xrange(Nx)]

            yCoords = vtk.vtkFloatArray()
            [yCoords.InsertNextValue(vy[j]) for j in xrange(Ny)]

            s = list(vz.flatten())
            vz = numpy.array(s)
            # vz.sort()
            Nz = vz.size

            zCoords = vtk.vtkFloatArray()
            [zCoords.InsertNextValue(vz[k]) for k in xrange(Nz)]

            vCoords = vtk.vtkFloatArray()
            [vCoords.InsertNextValue(n) for n in xrange(1)]

            self.gridfunc.SetDimensions(Nx, Ny, 1)
            self.gridfunc.SetXCoordinates(xCoords)
            self.gridfunc.SetYCoordinates(yCoords)
            self.gridfunc.SetZCoordinates(vCoords)

        # get scalar field from z/v-values
        self.Colors = vtk.vtkFloatArray()
        self.Colors.SetNumberOfComponents(1)
        self.Colors.SetNumberOfTuples(Nx * Ny)

        pt = mv if mva else vz
        [self.Colors.InsertComponent(i + j * Nx, 0, pt[i, j]) for j in xrange(Ny) for i in xrange(Nx)]

        self.gridfunc.GetPointData().SetScalars(self.Colors)
        self.hasData = True

        # scaling
        Xrange = vx.max() - vx.min()
        Yrange = vy.max() - vy.min()

        # filter none
        Zrange = numpy.nanmax(vz) - numpy.nanmin(vz)

        # must have x or y ranges
        if 0 in (Xrange, Yrange):
            logging.error('Zero X or Y Axis Range: %s', (Xrange, Yrange))
            self.hasData = False
            raise Exception('Zero X or Y Axis Range: %s', (Xrange, Yrange))

        self.XLimit = (vx.min(), vx.max())
        self.YLimit = (vy.min(), vy.max())
        self.ZLimit = (numpy.nanmin(vz), numpy.nanmax(vz))

        # check for constant Z range
        if Zrange == 0:
            Zrange = max(Xrange, Yrange)

        self.XScale = float(Zrange) / float(Xrange)
        self.YScale = float(Zrange) / float(Yrange)
        self.ZScale = float(Zrange) / float(Zrange)

        # fire callbacks
        if self.hasData:
            self.fireCallbacks(callback='OnDataRange')

        logging.debug('Parameters: %s' % str((
            Nx, Ny, Nz, ':', Xrange, Yrange, Zrange, ':', self.XScale, self.YScale,
            self.ZScale, ':', self.XLimit, self.YLimit, self.ZLimit)))

        return self.hasData

    def buildColormap(self, color='blue-red', reverse=True):
        clut = vtk.vtkLookupTable()
        luts = self.config.LookupTables() if self.config else {}

        if color in luts:
            lut = luts[color]
            if reverse:
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
            if reverse:
                hue_range = 0.0, 0.6667
                saturation_range = 1.0, 1.0
                value_range = 1.0, 1.0
            else:
                hue_range = 0.6667, 0.0
                saturation_range = 1.0, 1.0
                value_range = 1.0, 1.0
        elif color.lower() == 'black-white':
            if reverse:
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

    def makeCustomAxes(self, outline, outlinefilter):
        """ create custom axes """
        prop = vtk.vtkProperty()
        prop.SetColor(self.fgColor)

        x = vtk.vtkAxisActor()
        x.SetAxisTypeToX()
        # x.SetAxisPositionToMinMin()
        x.SetCamera(self.renderer.GetActiveCamera())
        x.SetBounds(outline.GetBounds())
        x.SetProperty(prop)
        x.SetRange(self.XLimit)
        x.SetPoint1(outline.GetBounds()[0], outline.GetBounds()[2], outline.GetBounds()[4])
        x.SetPoint2(outline.GetBounds()[1], outline.GetBounds()[2], outline.GetBounds()[4])

        return x

    def makeAxes(self, outline, outlinefilter):
        """ create axes """
        tprop = vtk.vtkTextProperty()
        tprop.SetColor(self.fgColor)
        tprop.ShadowOff()

        prop = vtk.vtkProperty2D()
        prop.SetColor(self.fgColor)

        zax = vtk.vtkCubeAxesActor()
        zax.SetBounds(outline.GetBounds()[0], outline.GetBounds()[1], outline.GetBounds()[2], outline.GetBounds()[3],
                      outline.GetBounds()[4], outline.GetBounds()[4])
        zax.SetDragable(False)
        zax.SetCamera(self.renderer.GetActiveCamera())
        zax.SetFlyModeToOuterEdges()
        zax.DrawXGridlinesOn()
        zax.DrawYGridlinesOn()
        zax.DrawZGridlinesOn()
        zax.SetXTitle('')
        zax.SetYTitle('')
        zax.SetZTitle('')
        zax.SetXAxisMinorTickVisibility(0)
        zax.SetYAxisMinorTickVisibility(0)
        zax.SetZAxisMinorTickVisibility(0)
        zax.SetXAxisLabelVisibility(0)
        zax.SetYAxisLabelVisibility(0)
        zax.SetZAxisLabelVisibility(0)

        axes = vtk.vtkCubeAxesActor2D()
        axes.SetDragable(False)
        axes.SetInputConnection(outlinefilter.GetOutputPort())

        axes.SetCamera(self.renderer.GetActiveCamera())
        axes.SetLabelFormat(self.config.LabelFormat())
        axes.SetFlyModeToOuterEdges()
        axes.SetFontFactor(self.fontFactor)
        axes.SetNumberOfLabels(self.config.NLabels())
        axes.SetXLabel(self.config.XLabel())
        axes.SetYLabel(self.config.YLabel())
        axes.SetZLabel(self.config.ZLabel())
        axes.SetRanges(self.out.GetBounds())
        axes.SetUseRanges(True)
        axes.SetProperty(prop)
        axes.SetAxisTitleTextProperty(tprop)
        axes.SetAxisLabelTextProperty(tprop)

        return zax, axes

    def _calculateYCutterDelta(self, bounds):
        if self.YCutterDelta is None:
            self.YCutterDelta = (bounds[3] - bounds[2]) / ((self.YLimit[1] - self.YLimit[0]) * self.YCutterFactor)
        return self.YCutterDelta

    def _calculateYCutterPos(self, value):
        if self.YCutterFactor < 1:
            self.YCutterFactor = 1

        if value > self.YLimit[1] * self.YCutterFactor:
            value = self.YLimit[1] * self.YCutterFactor

        if value < self.YLimit[0] * self.YCutterFactor:
            value = self.YLimit[0] * self.YCutterFactor

        bounds = self.mapper.GetBounds()
        delta = self._calculateYCutterDelta(bounds)

        npos = bounds[2] + (value - self.YLimit[0] * self.YCutterFactor) * delta
        return npos

    def moveYCutter(self, value):
        if self.YCutterFactor < 1:
            self.YCutterFactor = 1

        if not self.YCutterTransform:
            logging.error('YCutter not enabled')
            return

        if value > self.YLimit[1] * self.YCutterFactor or value < self.YLimit[0] * self.YCutterFactor:
            logging.error('Y: Value is outside limits %s' % ((value, self.YLimit, self.YCutterFactor),))
            return

        npos = self._calculateYCutterPos(value)
        ypos = self.YCutterTransform.GetPosition()[1]
        move = npos - ypos

        if self.yplane:
            (x, _y, z) = self.yplane.GetOrigin()
            self.yplane.SetOrigin(x, npos, z)

        self.YCutterTransform.Translate(0, move, 0)
        self.redraw()

    def makeYCutter(self, bounds, scaleFactor, value):
        # create y plane cutter

        npos = self._calculateYCutterPos(value)
        self.yplane = vtk.vtkPlane()
        self.yplane.SetOrigin(0, npos, 0)
        self.yplane.SetNormal(0, 1, 0)

        self.YCutter = vtk.vtkCutter()
        self.YCutter.SetInputConnection(self.warp.GetOutputPort())
        self.YCutter.SetCutFunction(self.yplane)
        self.YCutter.GenerateCutScalarsOff()

        self.YCutterMapper = vtk.vtkPolyDataMapper()
        self.YCutterMapper.SetInputConnection(self.YCutter.GetOutputPort())

        # visual plane to move
        plane = vtk.vtkPlaneSource()
        plane.SetResolution(50, 50)
        plane.SetCenter(0, 0, 0)
        plane.SetNormal(0, 1, 0)

        tran = vtk.vtkTransform()
        tran.Translate((bounds[1] - bounds[0]) / 2. - (0 - bounds[0]), npos,
                       (bounds[5] - bounds[4]) / 2. - (0 - bounds[4]))
        tran.Scale((bounds[1] - bounds[0]), 1, bounds[5] - bounds[4])
        tran.PostMultiply()

        self.YCutterTransform = tran

        tranf = vtk.vtkTransformPolyDataFilter()
        tranf.SetInputConnection(plane.GetOutputPort())
        tranf.SetTransform(tran)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tranf.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.9, 0.9, 0.9)
        actor.GetProperty().SetOpacity(self.opacitySlice)

        return actor

    def moveZCutter(self, value):
        if not self.ZCutterTransform:
            logging.error('ZCutter not enabled')
            return

        if value > self.ZLimit[1] * self.ZCutterFactor or value < self.ZLimit[0] * self.ZCutterFactor:
            logging.error('Z: Value is outside limits %s' % ((value, self.ZLimit, self.ZCutterFactor),))
            return

        npos = self._calculateZCutterPos(value)
        zpos = self.ZCutterTransform.GetPosition()[2]
        move = npos - zpos

        if self.zplane:
            (x, y, _z) = self.zplane.GetOrigin()
            self.zplane.SetOrigin(x, y, npos)

        self.ZCutterTransform.Translate(0, 0, move)
        self.redraw()

    def _calculateZCutterDelta(self, bounds):
        if self.ZCutterDelta is None:
            self.ZCutterDelta = (bounds[5] - bounds[4]) / ((self.ZLimit[1] - self.ZLimit[0]) * self.ZCutterFactor)
        return self.ZCutterDelta

    def _calculateZCutterPos(self, value):
        if self.ZCutterFactor < 1:
            self.ZCutterFactor = 1

        if value > self.ZLimit[1] * self.ZCutterFactor:
            value = self.ZLimit[1] * self.ZCutterFactor

        if value < self.ZLimit[0] * self.ZCutterFactor:
            value = self.ZLimit[0] * self.ZCutterFactor

        bounds = self.mapper.GetBounds()
        delta = self._calculateZCutterDelta(bounds)

        npos = bounds[4] + (value - self.ZLimit[0] * self.ZCutterFactor) * delta
        return npos

    def makeZCutter(self, bounds, scaleFactor, value):
        """ create z cutter plane """

        npos = self._calculateZCutterPos(value)
        self.zplane = vtk.vtkPlane()
        self.zplane.SetOrigin(0, 0, npos)
        self.zplane.SetNormal(0, 0, 1)

        self.ZCutter = vtk.vtkCutter()
        self.ZCutter.SetInputConnection(self.warp.GetOutputPort())
        self.ZCutter.SetCutFunction(self.zplane)
        self.ZCutter.GenerateCutScalarsOff()

        self.ZCutterMapper = vtk.vtkPolyDataMapper()
        self.ZCutterMapper.SetInputConnection(self.ZCutter.GetOutputPort())

        # visual plane to move
        plane = vtk.vtkPlaneSource()
        plane.SetResolution(50, 50)
        plane.SetCenter(0, 0, 0)
        plane.SetNormal(0, 0, 1)

        tran = vtk.vtkTransform()
        tran.Translate((bounds[1] - bounds[0]) / 2. - (0 - bounds[0]), (bounds[3] - bounds[2]) / 2. - (0 - bounds[2]),
                       npos)
        tran.Scale((bounds[1] - bounds[0]), (bounds[3] - bounds[2]), 1)
        tran.PostMultiply()

        self.ZCutterTransform = tran

        tranf = vtk.vtkTransformPolyDataFilter()
        tranf.SetInputConnection(plane.GetOutputPort())
        tranf.SetTransform(tran)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tranf.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.9, 0.9, 0.9)
        actor.GetProperty().SetOpacity(self.opacitySlice)

        return actor

    def _calculateXCutterDelta(self, bounds):
        if self.XCutterDelta is None:
            self.XCutterDelta = (bounds[1] - bounds[0]) / ((self.XLimit[1] - self.XLimit[0]) * self.XCutterFactor)
        return self.XCutterDelta

    def _calculateXCutterPos(self, value):
        if self.XCutterFactor < 1:
            self.XCutterFactor = 1

        if value > self.XLimit[1] * self.XCutterFactor:
            value = self.XLimit[1] * self.XCutterFactor

        if value < self.XLimit[0] * self.XCutterFactor:
            value = self.XLimit[0] * self.XCutterFactor

        bounds = self.mapper.GetBounds()
        delta = self._calculateXCutterDelta(bounds)

        npos = bounds[0] + (value - self.XLimit[0] * self.XCutterFactor) * delta
        return npos

    def moveXCutter(self, value):
        if not self.XCutterTransform:
            logging.error('XCutter not enabled')
            return

        if value > self.XLimit[1] * self.XCutterFactor or value < self.XLimit[0] * self.XCutterFactor:
            logging.error('X: Value is outside limits %s' % ((value, self.XLimit, self.XCutterFactor),))
            return

        npos = self._calculateXCutterPos(value)
        xpos = self.XCutterTransform.GetPosition()[0]
        move = npos - xpos

        if self.xplane:
            (_x, y, z) = self.xplane.GetOrigin()
            self.xplane.SetOrigin(npos, y, z)

        self.XCutterTransform.Translate(move, 0, 0)
        self.redraw()

    def makeXCutter(self, bounds, scaleFactor, value):
        # create X plane cutter

        npos = self._calculateXCutterPos(value)
        self.xplane = vtk.vtkPlane()
        self.xplane.SetOrigin(npos, 0, 0)
        self.xplane.SetNormal(1, 0, 0)

        self.XCutter = vtk.vtkCutter()
        self.XCutter.SetInputConnection(self.warp.GetOutputPort())
        self.XCutter.SetCutFunction(self.xplane)
        self.XCutter.GenerateCutScalarsOff()

        self.XCutterMapper = vtk.vtkPolyDataMapper()
        self.XCutterMapper.SetInputConnection(self.XCutter.GetOutputPort())

        # visual plane to move
        plane = vtk.vtkPlaneSource()
        plane.SetResolution(50, 50)
        plane.SetCenter(0, 0, 0)
        plane.SetNormal(1, 0, 0)

        tran = vtk.vtkTransform()
        tran.Translate(npos, (bounds[3] - bounds[2]) / 2. - (0 - bounds[2]),
                       (bounds[5] - bounds[4]) / 2. - (0 - bounds[4]))
        tran.Scale(1, (bounds[3] - bounds[2]), bounds[5] - bounds[4])
        tran.PostMultiply()

        self.XCutterTransform = tran

        tranf = vtk.vtkTransformPolyDataFilter()
        tranf.SetInputConnection(plane.GetOutputPort())
        tranf.SetTransform(tran)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(tranf.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.9, 0.9, 0.9)
        actor.GetProperty().SetOpacity(self.opacitySlice)

        return actor

    def makeColorbar(self):
        """ create colorbar """

        colorbar = vtk.vtkScalarBarActor()
        colorbar.SetLookupTable(self.mapper.GetLookupTable())
        colorbar.SetWidth(0.085)
        colorbar.SetHeight(0.8)
        colorbar.SetPosition(0.9, 0.1)
        colorbar.SetLabelFormat(self.config.LabelFormat())
        colorbar.SetNumberOfLabels(5)

        text_prop_cb = colorbar.GetLabelTextProperty()
        text_prop_cb.SetFontFamilyAsString('Arial')
        text_prop_cb.SetFontFamilyToArial()
        text_prop_cb.SetColor(self.fgColor)
        text_prop_cb.SetFontSize(1)
        text_prop_cb.ShadowOff()
        colorbar.SetLabelTextProperty(text_prop_cb)

        return colorbar

    def parseArgs(self, **args):
        """ parse class args """
        self.XCutterFactor = args.get('XCutterFactor', 1)
        self.YCutterFactor = args.get('YCutterFactor', 1)
        self.ZCutterFactor = args.get('ZCutterFactor', 1)
        self.rotateX = args.get('rotateX', 30)
        self.rotateY = args.get('rotateY', 30)
        self.rotateZ = args.get('rotateZ', 120)
        self.zoomFactor = args.get('zoomFactor', 1)
        self.posFactor = args.get('posFactor', 1)

    def render(self, **args):
        """ main function to render all required objects """

        gridData = args.get('gridData', True)
        drawSurface = args.get('drawSurface', True)
        drawAxes = args.get('drawAxes', True)
        drawColorBar = args.get('drawColorBar', True)
        drawLegend = args.get('drawLegend', True)
        wireSurface = args.get('wireSurface', False)
        drawBox = args.get('drawBox', True)
        scaleFactor = args.get('scaleFactor', (1, 1, 1))
        autoscale = args.get('autoScale', True)
        colorMap = args.get('colorMap', 'blue-red')
        reverseMap = args.get('reverseMap', False)
        drawGrid = args.get('drawGrid', False)
        resolution = args.get('gridResolution', 10)
        xtics = args.get('xtics', 0)
        ytics = args.get('ytics', 0)
        ztics = args.get('ztics', 0)
        planeGrid = args.get('planeGrid', True)
        xCutterOn = args.get('XCutterOn', True)
        yCutterOn = args.get('YCutterOn', True)
        zCutterOn = args.get('ZCutterOn', True)
        xCutterPos = args.get('XCutterPos', 2)
        yCutterPos = args.get('YCutterPos', 2)
        zCutterPos = args.get('ZCutterPos', 0)

        self.parseArgs(**args)

        if gridData:
            geometry = vtk.vtkStructuredGridGeometryFilter()
        else:
            geometry = vtk.vtkRectilinearGridGeometryFilter()

        geometry.SetInputData(self.gridfunc)
        geometry.SetExtent(self.gridfunc.GetExtent())

        if gridData:
            wzscale = self.computeScale(self.gridfunc)
            self.out = geometry.GetOutput()
        else:
            geometry.SetExtent(self.gridfunc.GetExtent())
            geometry.GetOutput().SetPoints(self.Points)
            geometry.GetOutput().GetPointData().SetScalars(self.Colors)
            geometry.GetOutput().Update()

            self.out = geometry.GetOutput()
            self.out.SetPoints(self.Points)
            self.out.GetPointData().SetScalars(self.Colors)
            self.out.Update()
            wzscale = self.computeScale(self.out)

        x = self.XScale if autoscale else self.XScale * scaleFactor[0]
        y = self.YScale if autoscale else self.YScale * scaleFactor[1]
        z = 0.5 * self.ZScale if autoscale else self.ZScale * scaleFactor[2]

        transform = vtk.vtkTransform()
        transform.Scale(x, y, z)
        trans = vtk.vtkTransformPolyDataFilter()
        trans.SetInputConnection(geometry.GetOutputPort())
        trans.SetTransform(transform)

        localScale = wzscale if wzscale < 1 else 1 / wzscale

        self.warp = vtk.vtkWarpScalar()
        self.warp.XYPlaneOn()
        self.warp.SetInputConnection(trans.GetOutputPort())
        self.warp.SetNormal(0, 0, 1)
        self.warp.UseNormalOn()
        self.warp.SetScaleFactor(localScale)

        tmp = self.gridfunc.GetScalarRange()

        # map gridfunction
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.warp.GetOutputPort())

        # calculate ranges
        if self.customZRange:
            self.mapper.SetScalarRange(*self.customZRange)
        elif self.autoZRange:
            mx = max(abs(tmp[0]), abs(tmp[1]))
            self.mapper.SetScalarRange(-mx, mx)
        else:
            self.mapper.SetScalarRange(tmp[0], tmp[1])

        wireActor = None
        bounds = self.mapper.GetBounds()

        # wire mapper
        if planeGrid:
            if not gridData:
                self.plane = vtk.vtkRectilinearGridGeometryFilter()
                self.plane.SetInput(self.gridfunc)
                self.plane.SetExtent(self.gridfunc.GetExtent())
                x_, y_ = x, y
            else:
                self.plane = vtk.vtkPlaneSource()
                self.plane.SetXResolution(resolution)
                self.plane.SetYResolution(resolution)
                x_, y_ = bounds[1] - bounds[0], bounds[3] - bounds[2]

            pltr = vtk.vtkTransform()
            pltr.Translate((bounds[1] - bounds[0]) / 2. - (0 - bounds[0]),
                           (bounds[3] - bounds[2]) / 2. - (0 - bounds[2]), bounds[4])
            pltr.Scale(x_, y_, 1)
            pltran = vtk.vtkTransformPolyDataFilter()
            pltran.SetInputConnection(self.plane.GetOutputPort())
            pltran.SetTransform(pltr)

            cmap = self.buildColormap('black-white', True)

            rgridMapper = vtk.vtkPolyDataMapper()
            rgridMapper.SetInputConnection(pltran.GetOutputPort())
            rgridMapper.SetLookupTable(cmap)

            wireActor = vtk.vtkActor()
            wireActor.SetMapper(rgridMapper)
            wireActor.GetProperty().SetRepresentationToWireframe()
            wireActor.GetProperty().SetColor(self.fgColor)

        # xcutter actor
        xactor = None
        if xCutterOn:
            xactor = self.makeXCutter(bounds, scaleFactor, xCutterPos)

        # ycutter actor
        yactor = None
        if yCutterOn:
            yactor = self.makeYCutter(bounds, scaleFactor, yCutterPos)

        # zcutter actor
        zactor = None
        if zCutterOn:
            zactor = self.makeZCutter(bounds, scaleFactor, zCutterPos)

        # create plot surface actor
        surfplot = vtk.vtkActor()
        surfplot.SetMapper(self.mapper)
        if wireSurface:
            surfplot.GetProperty().SetRepresentationToWireframe()

        # color map
        clut = self.buildColormap(colorMap, reverseMap)
        self.mapper.SetLookupTable(clut)

        # create outline
        outlinefilter = vtk.vtkOutlineFilter()
        outlinefilter.SetInputConnection(self.warp.GetOutputPort())

        outlineMapper = vtk.vtkPolyDataMapper()
        outlineMapper.SetInputConnection(outlinefilter.GetOutputPort())
        outline = vtk.vtkActor()
        outline.SetMapper(outlineMapper)
        outline.GetProperty().SetColor(self.fgColor)

        # make axes
        zax, axes = self.makeAxes(outline, outlinefilter)

        # setup axes
        xaxis = axes.GetXAxisActor2D()
        yaxis = axes.GetYAxisActor2D()
        zaxis = axes.GetZAxisActor2D()

        xaxis.SetLabelFormat(self.config.XLabelsFormat())
        xaxis.SetAdjustLabels(1)
        xaxis.SetNumberOfMinorTicks(xtics)

        yaxis.SetLabelFormat(self.config.YLabelsFormat())
        yaxis.SetNumberOfMinorTicks(ytics)
        yaxis.SetAdjustLabels(1)

        zaxis.SetLabelFormat(self.config.ZLabelsFormat())
        zaxis.SetNumberOfMinorTicks(ztics)
        zaxis.SetAdjustLabels(1)

        # create colorbar
        colorbar = self.makeColorbar()

        # renderer
        if drawSurface:
            self.renderer.AddActor(surfplot)
            self.actors.append(surfplot)
        if drawGrid:
            self.renderer.AddViewProp(zax)
            self.actors.append(zax)
        if planeGrid:
            self.renderer.AddActor(wireActor)
            self.actors.append(wireActor)
        if drawBox:
            self.renderer.AddActor(outline)
            self.actors.append(outline)
        if drawAxes:
            self.renderer.AddViewProp(axes)
            self.actors.append(axes)
        if drawColorBar or drawLegend:
            self.renderer.AddActor(colorbar)
            self.actors.append(colorbar)

        self._addPlaneCutters(xactor, yactor, zactor, xCutterOn, yCutterOn, zCutterOn)

    def _addPlaneCutters(self, xactor, yactor, zactor, xCutterOn, yCutterOn, zCutterOn):
        ''' add plane cutters  '''

        if xCutterOn and xactor:
            self.renderer.AddActor(xactor)
            self.actors.append(xactor)

        if yCutterOn and yactor:
            self.renderer.AddActor(yactor)
            self.actors.append(yactor)

        if zCutterOn and zactor:
            self.renderer.AddActor(zactor)
            self.actors.append(zactor)

    def renderToPng(self, path=None):
        if not path:
            return

        renWin = self.getRenderWindow()
        w2i = vtk.vtkWindowToImageFilter()
        w2i.SetMagnification(1)
        w2i.SetInputBufferTypeToRGBA()
        w2i.SetInput(renWin)
        w2i.Update()

        pngfile = vtk.vtkPNGWriter()

        pngfile.SetInputConnection(w2i.GetOutputPort())
        pngfile.SetFileName(path)

        self.redraw()
        pngfile.Write()

