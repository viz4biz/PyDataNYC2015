"""
VTK render model
"""

import logging

from atom.api import Atom, Dict, Str, observe, Value, Int, Tuple, List
from functools import partial
import vtk


logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.DEBUG)


INTERACTION_STYLES = {
    'TrackBallActor': vtk.vtkInteractorStyleTrackballActor(),
    'TrackBallCamera': vtk.vtkInteractorStyleTrackballCamera(),  # default style
    'JoystickCamera': vtk.vtkInteractorStyleJoystickCamera(),
    'JoystickActor': vtk.vtkInteractorStyleJoystickActor(),
    'Terrain': vtk.vtkInteractorStyleTerrain(),
}


class VTKRenderController(Atom):
    """ vtk render controller - supply renderers to VTKCanvas  """

    zoomFactor = Value()
    numOfRenderers = Int()
    callbacks = Dict()
    customPorts = Dict()
    customBackgrounds = Dict()
    interactorStyle = Str()
    style = Value()
    bgColor = Tuple()
    motionFactor = Int()
    renderers = List()
    view = Value()
    appName = Str()
    logFile = Str()
    kwargs = Dict()

    def __init__(self, numOfRenderers=1, view=None, callbacks=None, bgColor=None, customPorts=None,
                 customBackgrounds=None, logToFile=True, logFile=None, appName=None,
                 interactorStyle=None, motionFactor=None, zoomFactor=None, **kwargs):
        """ default init
                numOfRenderers - how many renderers to create
                bgColor        - default background color
                customPorts    - custom view port params in form of tuple( x0,y0,x1,y1 ) where x and y between (0,1)
                customBackgrounds  - custom backgrounds for each of the view port
        """
        self.bgColor = bgColor or (0.25, 0.25, 0.25)
        self.callbacks = callbacks or {}
        self.numOfRenderers = numOfRenderers if numOfRenderers > 0 else 1
        self.customPorts = customPorts or {0: (0.0, 0.0, 1.0, 1.0), }
        self.customBackgrounds = customBackgrounds or {}
        self.motionFactor = motionFactor or 5
        self.interactorStyle = interactorStyle or 'TrackBallCamera'
        self.style = INTERACTION_STYLES.get(self.interactorStyle, vtk.vtkInteractorStyleTrackballCamera())
        self.zoomFactor = zoomFactor
        self.view = view
        self.renderers = []
        self.appName = appName or 'vtkApp'
        self.logFile = logFile or ''
        self.kwargs = kwargs
        if logToFile:
            self._setupLogging()
        self.activate()

    def activate(self):
        """ activate widget - called only when parent widget is activated """
        self._make_renderers()
        self._bindEvents()

    def _bindEvents(self):
        """ bind additional events """
        if self.view and self.view.proxy.vtk_widget:
            self.view.proxy.vtk_widget.AddObserver('LeftButtonPressEvent', partial(self._OnEventAction, event_type='OnLeftDown'))
            self.view.proxy.vtk_widget.AddObserver('MiddleButtonPressEvent', partial(self._OnEventAction, event_type='OnMiddleDown'))
            self.view.proxy.vtk_widget.AddObserver('RightButtonPressEvent', partial(self._OnEventAction, event_type='OnRightDown'))
            self.view.proxy.vtk_widget.AddObserver('KeyPressEvent', partial(self._OnEventAction, event_type='OnKeyDown'))

    def _OnEventAction(self, obj, event, event_type=None):
        """ on left down event """
        (x, y) = obj.GetEventPosition()
        obj.GetPicker().Pick(x,
                             y,
                             0,
                             obj.GetRenderWindow().GetRenderers().GetFirstRenderer())
        pos = obj.GetPicker().GetPickPosition()
        if self.callbacks:
            fn = self.callbacks.get(event_type)
            if fn and callable(fn):
                fn(position=pos, event=event)

    def _make_renderers(self):
        """ make rendereres """
        if self.view and self.view.proxy.vtk_widget:
            self.make_local_renderers()

    def make_local_renderers(self):
        """ make local renderers """
        self.renderers = [vtk.vtkRenderer() for _ in xrange(self.numOfRenderers)]

        if self.customBackgrounds and len(self.customBackgrounds) == self.numOfRenderers:
            for i in xrange(self.numOfRenderers):
                self.renderers[i].SetBackground(self.customBackgrounds.get(i, (0.1, 0.1, 0.1)))
        else:
            for rend in self.renderers:
                rend.SetBackground(self.bgColor)

        self.setViewPorts()
        self.setCamera()
        print '>>> done making renders ', len(self.renderers)

    def setViewPorts(self):
        """ set automatic viewports for renderers only for 2 and 4 """
        l = len(self.renderers)
        if self.customPorts and len(self.customPorts) == l:
            for i in xrange(l):
                port = self.customPorts.get(i)
                if port:
                    self.renderers[i].SetViewport(*port)
        else:
            if 0 < l < 5:
                if l == 2:
                    self.renderers[0].SetViewport(0.0, 0.0, 0.5, 1.0)
                    self.renderers[1].SetViewport(0.5, 0.0, 1.0, 1.0)
                if l == 3:
                    self.renderers[0].SetViewport(0.0, 0.0, 0.333, 1.0)
                    self.renderers[1].SetViewport(0.333, 0.0, 0.666, 1.0)
                    self.renderers[2].SetViewport(0.666, 0.0, 1.0, 1.0)
                if l == 4:
                    self.renderers[0].SetViewport(0.0, 0.0, 0.5, 0.5)
                    self.renderers[1].SetViewport(0.5, 0.0, 1.0, 0.5)
                    self.renderers[2].SetViewport(0.5, 0.5, 0.5, 1.0)
                    self.renderers[3].SetViewport(0.5, 0.5, 1.0, 1.0)

    def addActors(self, actors=None):
        """ add actors to renderers """
        if isinstance(actors, dict):
            renders = dict(enumerate(self.renderers))
            for ix, acts in actors.iteritems():
                rend = renders.get(ix)
                if rend:
                    for act in acts:
                        rend.AddActor(act)
        else:
            rend = self.renderers[0]
            for act in actors:
                rend.AddActor(act)

    def setCamera(self):
        """
        set camera settings
        """
        for ren in self.renderers:
            if self.zoomFactor:
                ren.ResetCamera()
                ren.GetActiveCamera().Zoom(self.zoomFactor)

    def get_renderers(self):
        """ return current renderers """
        return self.renderers

    def get_renderer(self):
        """
        return main renderer
        """
        return self.renderers[0]

    def setInteractorStyle(self, interactorStyle='TrackBallCamera'):
        """ set custom interactor style """
        self.interactorStyle = interactorStyle
        self.style = INTERACTION_STYLES.get(interactorStyle, vtk.vtkInteractorStyleTrackballCamera())
        self._setInteractorStyle()

    def _setInteractorStyle(self):
        """ set current intercator style """
        if self.view and self.style and self.view.proxy.vtk_widget:
            self.view.proxy.vtk_widget.SetInteractorStyle(self.style)

    def _setupLogging(self):
        """ setup local logging """
        if not self.logFile:
            import os
            import tempfile
            temp = tempfile.gettempdir()
            app = ''.join(c for c in self.appName if 'a' <= c.lower() <= 'z') + '.log.'
            self.logFile = os.path.join(temp, app)

        fileOutputWindow = vtk.vtkFileOutputWindow()
        fileOutputWindow.SetFileName(self.logFile)

        outputWindow = vtk.vtkOutputWindow().GetInstance()
        if outputWindow:
            outputWindow.SetInstance(fileOutputWindow)

    @observe(('bgColor',))
    def _onBGColorUpdated(self, change):
        """ update bg color """
        if self.renderers and change:
            type_ = change.get('type')
            if type_ != 'create':
                bgColor = change.get('value')
                if bgColor:
                    self.bgColor = bgColor
                    for rend in self.renderers:
                        rend.SetBackground(self.bgColor)

    @observe(('customBackgrounds',))
    def _onCustomColorsUpdated(self, change):
        """ update custom bg colors """
        if self.renderers and change:
            type_ = change.get('type')
            if type_ != 'create':
                customColors = change.get('value')
                if customColors:
                    self.customBackgrounds = customColors
                    renders = dict(enumerate(self.renderers))
                    for i, colors in self.customBackgrounds.iteritems():
                        rend = renders.get(i)
                        if rend:
                            rend.SetBackground(colors)
