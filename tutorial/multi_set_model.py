"""
Multi set model
"""

from renderers import VTKRenderController
from enaml.application import deferred_call
import vtk


class RenderViewController(VTKRenderController):

    def __init__(self, view=None, bgColor=None, callbacks=None, actors=None):
        """
        default init
        """
        super(RenderViewController, self).__init__(view=view, bgColor=bgColor, callbacks=callbacks)
        self.addActors(actors)

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


def get_all_actors():
    """ vtk sample scene with iso contours """

    # VTK supports implicit functions of the form f(x,y,z)=constant. These
    # functions can represent things spheres, cones, etc. Here we use a
    # general form for a quadric to create an elliptical data field.
    quadric = vtk.vtkQuadric()
    quadric.SetCoefficients(.5, 1, .2, 0, .1, 0, 0, .2, 0, 0)

    # vtkSampleFunction samples an implicit function over the x-y-z range
    # specified (here it defaults to -1,1 in the x,y,z directions).
    sample = vtk.vtkSampleFunction()
    sample.SetSampleDimensions(30, 30, 30)
    sample.SetImplicitFunction(quadric)

    # Create five surfaces F(x,y,z) = constant between range specified. The
    # GenerateValues() method creates n isocontour values between the range
    # specified.
    contours = vtk.vtkContourFilter()
    contours.SetInputConnection(sample.GetOutputPort())
    contours.GenerateValues(10, 0.0, 1.2)

    contMapper = vtk.vtkPolyDataMapper()
    contMapper.SetInputConnection(contours.GetOutputPort())
    contMapper.SetScalarRange(0.0, 1.2)

    contActor = vtk.vtkActor()
    contActor.SetMapper(contMapper)

    # We'll put a simple outline around the data.
    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(sample.GetOutputPort())

    outlineMapper = vtk.vtkPolyDataMapper()
    outlineMapper.SetInputConnection(outline.GetOutputPort())

    outlineActor = vtk.vtkActor()
    outlineActor.SetMapper(outlineMapper)
    outlineActor.GetProperty().SetColor(0.5, 0.5, 0.5)

    # extract data from the volume along z
    extract_z = vtk.vtkExtractVOI()
    extract_z.SetInputConnection(sample.GetOutputPort())
    extract_z.SetVOI(0, 29, 0, 29, 15, 15)
    extract_z.SetSampleRate(1, 2, 3)

    contours_z = vtk.vtkContourFilter()
    contours_z.SetInputConnection(extract_z.GetOutputPort())
    contours_z.GenerateValues(10, 0.0, 1.2)

    contMapperZ = vtk.vtkPolyDataMapper()
    contMapperZ.SetInputConnection(contours_z.GetOutputPort())
    contMapperZ.SetScalarRange(0.0, 1.2)

    contActorZ = vtk.vtkActor()
    contActorZ.SetMapper(contMapperZ)

    extract_x = vtk.vtkExtractVOI()
    extract_x.SetInputConnection(sample.GetOutputPort())
    extract_x.SetVOI(0, 29, 15, 15, 0, 29)
    extract_x.SetSampleRate(1, 2, 3)

    contours_x = vtk.vtkContourFilter()
    contours_x.SetInputConnection(extract_x.GetOutputPort())
    contours_x.GenerateValues(10, 0.0, 1.2)

    contMapperX = vtk.vtkPolyDataMapper()
    contMapperX.SetInputConnection(contours_x.GetOutputPort())
    contMapperX.SetScalarRange(0.0, 1.2)

    contActorX = vtk.vtkActor()
    contActorX.SetMapper(contMapperX)

    return contActor, contActorZ, contActorX, outlineActor, contours, contours_z, contours_x, extract_z, extract_x
