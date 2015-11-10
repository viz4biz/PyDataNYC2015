"""
VTK surface model
"""
from atom.api import List, Value
from renderers import VTKRenderController
from vtk_surface import VTKSurface3D, remap
from enaml.application import deferred_call


class VTKSurface3DModelController(VTKRenderController):
    """ vtk surface 3D model controller """

    surfaces = List()
    data = Value()

    def __init__(self, *args, **kwargs):
        """ default init """
        print '>>> new model'
        VTKRenderController.__init__(self, *args, **kwargs)
        self.surfaces = []
        self.data = kwargs.pop('data', [])
        remapData = kwargs.pop('remapData', False)
        if remapData:
            self.data = remap(self.data)
        if self.renderers:
            for i in xrange(len(self.renderers)):
                self.surfaces.append(VTKSurface3D(self.data, parent=self, renderer=self.renderers[i], **kwargs))
                print '>>> creating surface into renderer ', i

    def get_surfaces(self):
        """
        get surfaces
        """
        return self.surfaces

    def get_surface(self):
        """
        get main surface
        """
        if self.surfaces:
            return self.surfaces[0]

    def _observe_data(self, change):
        """ observe data change """
        if change:
            type_ = change.get('type')
            if type_ != 'create':
                data = change.get('value')
                if data:
                    pass

    def invalidate(self):
        """ invalidate model """
        if self.view:
            deferred_call(self.view.render)

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