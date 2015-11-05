"""
vtk renderer scenes
"""

import vtk
from math import exp, sqrt, sin, cos


def create_renderer():
    """
    vtk renderer with a sample scene
    """
    quadric = vtk.vtkQuadric()
    quadric.SetCoefficients(.5, 1, .2, 0, .1, 0, 0, .2, 0, 0)

    sample = vtk.vtkSampleFunction()
    sample.SetSampleDimensions(50, 50, 50)
    sample.SetImplicitFunction(quadric)

    contours = vtk.vtkContourFilter()
    contours.SetInputConnection(sample.GetOutputPort())
    contours.GenerateValues(5, 0.0, 1.2)

    contour_mapper = vtk.vtkPolyDataMapper()
    contour_mapper.SetInputConnection(contours.GetOutputPort())
    contour_mapper.SetScalarRange(0.0, 1.2)

    contour_actor = vtk.vtkActor()
    contour_actor.SetMapper(contour_mapper)

    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(sample.GetOutputPort())

    outline_mapper = vtk.vtkPolyDataMapper()
    outline_mapper.SetInputConnection(outline.GetOutputPort())

    outline_actor = vtk.vtkActor()
    outline_actor.SetMapper(outline_mapper)
    outline_actor.GetProperty().SetColor(0, 0, 0)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(contour_actor)
    renderer.AddActor(outline_actor)
    renderer.SetBackground(.75, .75, .75)

    return renderer


def visquad():
    """ vtk sample scene """

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
    contours.GenerateValues(5, 0.0, 1.2)

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
    outlineActor.GetProperty().SetColor(0, 0, 0)

    return [contActor, outlineActor]


def visQuadFunc():
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
    contours.GenerateValues(8, 0.0, 1.2)

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
    outlineActor.GetProperty().SetColor(1, 0.5, 0)

    # extract data from the volume
    extract = vtk.vtkExtractVOI()
    extract.SetInputConnection(sample.GetOutputPort())
    extract.SetVOI(0, 29, 0, 29, 15, 15)
    extract.SetSampleRate(1, 2, 3)

    contours2 = vtk.vtkContourFilter()
    contours2.SetInputConnection(extract.GetOutputPort())
    contours2.GenerateValues(8, 0.0, 1.2)

    contMapper2 = vtk.vtkPolyDataMapper()
    contMapper2.SetInputConnection(contours2.GetOutputPort())
    contMapper2.SetScalarRange(0.0, 1.2)

    contActor2 = vtk.vtkActor()
    contActor2.SetMapper(contMapper2)

    return contActor, contActor2, outlineActor, contours, contours2


def bessel_surface():
    """
    programmable surface
    """

    # We create a 100 by 100 point plane to sample
    plane = vtk.vtkPlaneSource()
    plane.SetXResolution(100)
    plane.SetYResolution(100)

    # We transform the plane by a factor of 10 on X and Y
    transform = vtk.vtkTransform()
    transform.Scale(10, 10, 1)
    transF = vtk.vtkTransformPolyDataFilter()
    transF.SetInputConnection(plane.GetOutputPort())
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
            x2 = exp(-r)*cos(10.0*r)
            deriv = -exp(-r)*(cos(10.0*r)+10.0*sin(10.0*r))

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
    warp.SetScaleFactor(0.5)

    # We create a mapper and actor as usual. In the case we adjust the
    # scalar range of the mapper to match that of the computed scalars
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(warp.GetOutputPort())
    mapper.SetScalarRange(besselF.GetPolyDataOutput().GetScalarRange())
    carpet = vtk.vtkActor()
    carpet.SetMapper(mapper)

    return carpet

