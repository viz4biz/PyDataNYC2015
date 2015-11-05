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
        VTKRenderController.__init__(self, *args, **kwargs)
        self.surfaces = []
        self.data = kwargs.pop('data', [])
        remapData = kwargs.pop('remapData', False)
        if remapData:
            self.data = remap(self.data)
        renderers = kwargs.pop('numOfRenderers', 1)
        for i in xrange(renderers):
            self.surfaces.append(VTKSurface3D(self.data, parent=self, renderer=self.get_renderers()[i], **kwargs))

    def _observe__data(self, change):
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