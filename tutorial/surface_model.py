"""
Surface model
"""

import vtk
from atom.api import Atom, Float, Dict, Value, Int
from renderers import VTKRenderController
from enaml.application import deferred_call
from math import exp, sqrt, sin, cos


class RenderViewController(VTKRenderController):
    """ render view controller
    """

    scale_factor = Int(default=50)
    resolution = Int(default=100)
    factor = Float(default=10.0)
    backgrounds = Dict()
    surface_model = Value()

    def __init__(self, view=None, bgColor=None, callbacks=None):
        """
        default init
        """
        super(RenderViewController, self).__init__(view=view, bgColor=bgColor, callbacks=callbacks)
        self.surface_model = SurfaceModel(scale_factor=self.scale_factor/100., resolution=self.resolution, factor=self.factor)
        self.addActors(self.surface_model.get_actors())

    def set_background(self, background):
        """
        set models background
        """
        self.bgColor = background
        if self.view:
            deferred_call(self.view.render)

    def set_interactor_style(self, style):
        """
        set interactor style
        """
        self.setInteractorStyle(style)

    def on_close(self):
        """
        on close
        """
        pass

    def _observe_factor(self, change):
        """ observe change in factor """
        if change:
            type_ = change.get('type')
            if type_ != 'create':
                value = change['value']
                self.surface_model.factor = value
                deferred_call(self.view.render)

    def _observe_resolution(self, change):
        """ observe change in resolution """
        if change:
            type_ = change.get('type')
            if type_ != 'create':
                value = change['value']
                self.surface_model.plane.SetXResolution(value)
                self.surface_model.plane.SetYResolution(value)
                deferred_call(self.view.render)

    def _observe_scale_factor(self, change):
        """ observe change in scale factor """
        if change:
            type_ = change.get('type')
            if type_ != 'create':
                value = change['value']
                self.surface_model.warp_geometry.SetScaleFactor(value/100.)
                deferred_call(self.view.render)


class SurfaceModel(Atom):

    resolution = Int()
    scale_factor = Float()
    surface_actor = Value()
    outline_actor = Value()
    warp_geometry = Value()
    plane = Value()
    factor = Float(default=10.)

    def __init__(self, scale_factor=0.5, resolution=100, factor=10.0):
        self.scale_factor = scale_factor
        self.resolution = resolution
        self.factor = factor
        self.make_models()

    def get_actors(self):
        """
        return current actors
        """
        return [self.surface_actor, self.outline_actor]

    def make_models(self):
        """
        make models
        """
        # We create a 100 by 100 point plane to sample
        self.plane = vtk.vtkPlaneSource()
        self.plane.SetXResolution(self.resolution)
        self.plane.SetYResolution(self.resolution)

        # We transform the plane by a factor of 10 on X and Y and 1 Z
        transform = vtk.vtkTransform()
        transform.Scale(10, 10, 1)
        transF = vtk.vtkTransformPolyDataFilter()
        transF.SetInputConnection(self.plane.GetOutputPort())
        transF.SetTransform(transform)

        # Compute Bessel function and derivatives. We'll use a programmable filter
        # for this. Note the unusual GetPolyDataInput() & GetOutputPort() methods.
        besselF = vtk.vtkProgrammableFilter()
        besselF.SetInputConnection(transF.GetOutputPort())

        # The SetExecuteMethod takes a Python function as an argument
        # In here is where all the processing is done.
        def bessel():
            inputs = besselF.GetPolyDataInput()
            numPts = inputs.GetNumberOfPoints()
            newPts = vtk.vtkPoints()
            derivs = vtk.vtkFloatArray()

            for i in xrange(0, numPts):
                x = inputs.GetPoint(i)
                x0, x1 = x[:2]

                r = sqrt(x0*x0+x1*x1)
                x2 = exp(-r)*cos(self.factor*r)
                deriv = -exp(-r)*(cos(self.factor*r)+self.factor*sin(self.factor*r))

                newPts.InsertPoint(i, x0, x1, x2)
                derivs.InsertValue(i, deriv)

            besselF.GetPolyDataOutput().CopyStructure(inputs)
            besselF.GetPolyDataOutput().SetPoints(newPts)
            besselF.GetPolyDataOutput().GetPointData().SetScalars(derivs)

        besselF.SetExecuteMethod(bessel)

        # We warp the plane based on the scalar values calculated above
        warp = vtk.vtkWarpScalar()
        warp.SetInputConnection(besselF.GetOutputPort())
        warp.XYPlaneOn()
        warp.SetScaleFactor(self.scale_factor)

        # We create a mapper and actor as usual. In the case we adjust the
        # scalar range of the mapper to match that of the computed scalars
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(warp.GetOutputPort())
        mapper.SetScalarRange(besselF.GetPolyDataOutput().GetScalarRange())
        carpet = vtk.vtkActor()
        carpet.SetMapper(mapper)

        self.surface_actor = carpet

        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(warp.GetOutputPort())

        outline_mapper = vtk.vtkPolyDataMapper()
        outline_mapper.SetInputConnection(outline.GetOutputPort())

        self.outline_actor = vtk.vtkActor()
        self.outline_actor.SetMapper(outline_mapper)
        self.outline_actor.GetProperty().SetColor(0, 0, 0)

        self.warp_geometry = warp
