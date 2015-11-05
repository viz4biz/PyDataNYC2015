"""
vtk docks model
"""

from atom.api import Dict, Str, observe, Value, Int
from renderers import VTKRenderController
from enaml.application import deferred_call
from scenes import visquad


class DocksRenderController(VTKRenderController):
    """ Docks model
    """

    backgrounds = Dict()

    def __init__(self, view=None, bgColor=None, callbacks=None):
        """
        default init
        """
        super(DocksRenderController, self).__init__(view=view, bgColor=bgColor, callbacks=callbacks)
        self.addActors(visquad())

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

