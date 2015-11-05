"""
Sample VTK grid model
"""


import vtk
from atom.api import Atom, Dict, Value, Int
from renderers import VTKRenderController
from enaml.application import deferred_call

VTK_DATA_ROOT = '/Users/pawel/src/VTKData'


class RenderViewController(VTKRenderController):
    """ render view controller
    """

    slice_factor = Int(default=30)
    backgrounds = Dict()
    surface_model = Value()

    def __init__(self, view=None, bgColor=None, callbacks=None):
        """
        default init
        """
        super(RenderViewController, self).__init__(view=view, bgColor=bgColor, callbacks=callbacks)
        self.surface_model = SurfaceModel(slice_factor=self.slice_factor)
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

    def _observe_slice_factor(self, change):
        """ observe change in factor """
        if change:
            type_ = change.get('type')
            if type_ != 'create':
                value = change['value']
                self.surface_model.slice_factor = value
                deferred_call(self.view.render)


class SurfaceModel(Atom):

    slice_factor = Int()
    surface_actor = Value()
    outline_actor = Value()
    extract_model = Value()

    def __init__(self, slice_factor=30):
        self.slice_factor = slice_factor
        self.make_models()

    def _observe_slice_factor(self, change):
        """ observe change in factor """
        if change:
            type_ = change.get('type')
            if type_ != 'create':
                value = change['value']
                self.extract_model.SetVOI(value, value, -1000, 1000, -1000, 1000)


    def get_actors(self):
        """
        return current actors
        """
        return [self.surface_actor, self.outline_actor]

    def make_models(self):
        """
        make models
        """

        # Read some structured data.
        pl3d = vtk.vtkMultiBlockPLOT3DReader()
        pl3d.SetXYZFileName(VTK_DATA_ROOT + "/Data/combxyz.bin")
        pl3d.SetQFileName(VTK_DATA_ROOT + "/Data/combq.bin")
        pl3d.SetScalarFunctionNumber(100)
        pl3d.SetVectorFunctionNumber(202)
        pl3d.Update()
        pl3d_output = pl3d.GetOutput().GetBlock(0)

        # Here we subsample the grid. The SetVOI method requires six values
        # specifying (imin,imax, jmin,jmax, kmin,kmax) extents. In this
        # example we extracting a plane. Note that the VOI is clamped to zero
        # (min) and the maximum i-j-k value; that way we can use the
        # -1000,1000 specification and be sure the values are clamped. The
        # SampleRate specifies that we take every point in the i-direction;
        # every other point in the j-direction; and every third point in the
        # k-direction. IncludeBoundaryOn makes sure that we get the boundary
        # points even if the SampleRate does not coincident with the boundary.
        extract = vtk.vtkExtractGrid()
        extract.SetInputData(pl3d_output)
        extract.SetVOI(self.slice_factor, self.slice_factor, -1000, 1000, -1000, 1000)
        extract.SetSampleRate(1, 2, 3)
        extract.IncludeBoundaryOn()

        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputConnection(extract.GetOutputPort())
        mapper.SetScalarRange(.18, .7)
        self.surface_actor = vtk.vtkActor()
        self.surface_actor.SetMapper(mapper)

        outline = vtk.vtkStructuredGridOutlineFilter()
        outline.SetInputData(pl3d_output)
        outlineMapper = vtk.vtkPolyDataMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())
        self.outline_actor = vtk.vtkActor()
        self.outline_actor.SetMapper(outlineMapper)
        self.outline_actor.GetProperty().SetColor(0, 0, 0)

        self.extract_model = extract
