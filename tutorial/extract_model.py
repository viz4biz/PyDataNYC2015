"""
vtk extract model
"""

import vtk
from atom.api import Atom, Float, Dict, Value, Int
from renderers import VTKRenderController
from enaml.application import deferred_call


class RenderViewController(VTKRenderController):
    """ render view controller
    """

    backgrounds = Dict()
    extract_model = Value()
    shrink_factor = Int()
    radius = Int()

    def __init__(self, view=None, bgColor=None, callbacks=None):
        """
        default init
        """
        super(RenderViewController, self).__init__(view=view, bgColor=bgColor, callbacks=callbacks)
        self.shrink_factor = 55
        self.radius = 25
        self.extract_model = ExtractModel(shrink_factor=self.shrink_factor/100., radius=self.radius/100.)
        self.addActors(self.extract_model.get_actors())

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

    def _observe_shrink_factor(self, change):
        """ observe change in shrink factor """
        if change:
            type_ = change.get('type')
            if type_ != 'create':
                value = change['value']
                self.extract_model.shrink_geom.SetShrinkFactor(value/100.)
                deferred_call(self.view.render)

    def _observe_radius(self, change):
        """ observe change in radius """
        if change:
            type_ = change.get('type')
            if type_ != 'create':
                value = change['value']
                self.extract_model.sphere_geom_1.SetRadius(value/100.)
                self.extract_model.sphere_geom_2.SetRadius(value/100.)
                deferred_call(self.view.render)


class ExtractModel(Atom):

    shrink_factor = Float()
    radius = Float()
    data_actor = Value()
    outline_actor = Value()
    shrink_geom = Value()
    sphere_geom_1 = Value()
    sphere_geom_2 = Value()

    def __init__(self, shrink_factor=0.55, radius=0.25):
        """
        default init
        """
        self.shrink_factor = shrink_factor
        self.radius = radius
        self.makeModels()

    def get_actors(self):
        """
        return current actors
        """
        return [self.data_actor, self.outline_actor]

    def makeModels(self):
        """
        make vtk model
        """

        # Here we create two ellipsoidal implicit functions and boolean them
        # together to form a "cross" shaped implicit function.
        quadric = vtk.vtkQuadric()
        quadric.SetCoefficients(.5, 1, .2, 0, .1, 0, 0, .2, 0, 0)

        sample = vtk.vtkSampleFunction()
        sample.SetSampleDimensions(50, 50, 50)
        sample.SetImplicitFunction(quadric)
        sample.ComputeNormalsOff()

        trans = vtk.vtkTransform()
        trans.Scale(1, .5, .333)
        sphere = vtk.vtkSphere()
        sphere.SetRadius(self.radius)
        sphere.SetTransform(trans)

        trans2 = vtk.vtkTransform()
        trans2.Scale(.25, .5, 1.0)
        sphere2 = vtk.vtkSphere()
        sphere2.SetRadius(self.radius)
        sphere2.SetTransform(trans2)

        self.sphere_geom_1 = sphere
        self.sphere_geom_2 = sphere2

        union = vtk.vtkImplicitBoolean()
        union.AddFunction(sphere)
        union.AddFunction(sphere2)
        union.SetOperationType(0)

        # Here is where it gets interesting. The implicit function is used to
        # extract those cells completely inside the function. They are then
        # shrunk to helpr show what was extracted.
        extract = vtk.vtkExtractGeometry()
        extract.SetInputConnection(sample.GetOutputPort())
        extract.SetImplicitFunction(union)
        shrink = vtk.vtkShrinkFilter()
        shrink.SetInputConnection(extract.GetOutputPort())
        shrink.SetShrinkFactor(self.shrink_factor)
        dataMapper = vtk.vtkDataSetMapper()
        dataMapper.SetInputConnection(shrink.GetOutputPort())

        self.shrink_geom = shrink

        # data actor
        self.data_actor = vtk.vtkActor()
        self.data_actor.SetMapper(dataMapper)

        # The outline gives context to the original data.
        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(sample.GetOutputPort())
        outlineMapper = vtk.vtkPolyDataMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())

        # outline actor
        self.outline_actor = vtk.vtkActor()
        self.outline_actor.SetMapper(outlineMapper)
        outlineProp = self.outline_actor.GetProperty()
        outlineProp.SetColor(0, 0, 0)
