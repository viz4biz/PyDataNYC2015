"""
VTK surface properties helper class
"""

from atom.api import Atom, Str, Bool, Float, Typed, Dict
from vtk_surface import VTKSurfaceConfig


class VTKSurfaceProperties(Atom):

    Config = Typed(VTKSurfaceConfig)
    Title = Str('')
    CurrentColorMap = Str('rainbow')
    XCutterOn = Bool()
    YCutterOn = Bool()
    ZCutterOn = Bool()
    XCutterPos = Float()
    YCutterPos = Float()
    ZCutterPos = Float()
    XFactor = Float()
    YFactor = Float()
    ZFactor = Float()
    DrawBox = Bool()
    DrawGrid = Bool()
    DrawAxes = Bool()
    DrawLegend = Bool()
    ZoomFactor = Float()
    Autoscale = Bool()
    ScaleFactor = Float()
    AutoZRange = Bool()
    SurfaceProperties = Dict()

    def __init__(self, config):
        self.config = config or VTKSurfaceConfig()
        self.SurfaceProperties = self.surface_properties()

    def surface_properties(self):
            """ surface 3D attributes """
            return dict(
                    xlabel        = self.Config().XLabel(),
                    ylabel        = self.Config().YLabel(),
                    zlabel        = self.Config().ZLabel(),
                    title         = self.Title(),
                    colorMap      = self.CurrentColorMap,
                    XCutterOn     = self.XCutterOn,
                    XCutterPos    = self.XCutterPos,
                    XCutterFactor = self.XFactor,
                    YCutterOn     = self.YCutterOn,
                    YCutterPos    = self.YCutterPos,
                    YCutterFactor = self.YFactor,
                    ZCutterOn     = self.ZCutterOn,
                    ZCutterPos    = self.ZCutterPos,
                    ZCutterFactor = self.ZFactor,
                    drawBox       = self.DrawBox,
                    drawGrid      = self.DrawGrid,
                    drawAxes      = self.DrawAxes,
                    drawLegend    = self.DrawLegend,
                    rotateX       = 30,
                    rotateZ       = 180,
                    zoomFactor    = self.ZoomFactor,
                    xtics         = 1,
                    ytics         = 1,
                    ztics         = 1,
                    nlabels       = 5,
                    logToFile     = True,
                    autoScale     = self.Autoscale,
                    scaleFactor   = self.ScaleFactor,
                    autoZRange    = self.AutoZRange,
                    labelFormat   = '%6.2f',)
