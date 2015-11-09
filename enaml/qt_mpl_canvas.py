#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, Str

from enaml.widgets.mpl_canvas import ProxyMPLCanvas

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT

from .QtCore import Qt
from .QtGui import QFrame, QVBoxLayout

from .qt_control import QtControl

# define correct toolbat locations
VALID_LOCATIONS = ( 'top', 'bottom' )
VALID_EVENTS = ( 'button_press_event',
    'button_release_event',
    'draw_event',
    'key_press_event',
    'key_release_event',
    'motion_notify_event',
    'pick_event',
    'resize_event',
    'scroll_event',
    'figure_enter_event',
    'figure_leave_event',
    'axes_enter_event',
    'axes_leave_event',
    'close_event', )


class QtMPLCanvas(QtControl, ProxyMPLCanvas):
    """ A Qt implementation of an Enaml ProxyMPLCanvas.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QFrame)
    last_location = Str('top')

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying widget.

        """
        widget = QFrame(self.parent_widget())
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        widget.setLayout(layout)
        self.widget = widget

    def init_layout(self):
        """ Initialize the layout of the underlying widget.

        """
        super(QtMPLCanvas, self).init_layout()
        self._refresh_mpl_widget()

    #--------------------------------------------------------------------------
    # ProxyMPLCanvas API
    #--------------------------------------------------------------------------
    def set_figure(self, figure):
        """ Set the MPL figure for the widget.

        """
        with self.geometry_guard():
            self._refresh_mpl_widget()

    def set_event_actions(self, actions):
        """ Set event action on the canvas
        """
        if not callable( actions[1] ):
            raise Exception( 'Action must be a function' )
        with self.geometry_guard():
            pass

    def set_toolbar_location(self, location):
        """ Set toolbar location
        """
        if location not in VALID_LOCATIONS:
            raise Exception( 'Invalid value for toolbar_location: %s', location)
        layout = self.widget.layout()
        if layout.count() == 2:
            with self.geometry_guard():
                if self.last_location == 'top':
                    toolbar = layout.itemAt(0).widget()
                    canvas = layout.itemAt(1).widget()
                else:
                    toolbar = layout.itemAt(1).widget()
                    canvas = layout.itemAt(0).widget()
                if location == 'top':
                    layout.addWidget(toolbar)
                    layout.addWidget(canvas)
                else:
                    layout.addWidget(canvas)
                    layout.addWidget(toolbar)
                self.last_location = location

    def set_toolbar_visible(self, visible):
        """ Set the toolbar visibility for the widget.

        """
        layout = self.widget.layout()
        if layout.count() == 2:
            with self.geometry_guard():
                if self.declaration.toolbar_location == 'top':
                    toolbar = layout.itemAt(0).widget()
                else:
                    toolbar = layout.itemAt(1).widget()
                toolbar.setVisible(visible)

    def draw(self):
        """ Request draw on the Figure """
        layout = self.widget.layout()
        for i in xrange(layout.count()):
            item = layout.itemAt(i).widget()
            if isinstance(item, FigureCanvasQTAgg):
                item.draw()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _refresh_mpl_widget(self):
        """ Create the mpl widget and update the underlying control.

        """
        # Delete the old widgets in the layout, it's just shenanigans
        # to try to reuse the old widgets when the figure changes.
        widget = self.widget
        layout = widget.layout()
        while layout.count():
            layout_item = layout.takeAt(0)
            layout_item.widget().deleteLater()

        # Create the new figure and toolbar widgets. It seems that key
        # events will not be processed without an mpl figure manager.
        # However, a figure manager will create a new toplevel window,
        # which is certainly not desired in this case. This appears to
        # be a limitation of matplotlib. The canvas is manually set to
        # visible, or QVBoxLayout will ignore it for size hinting.
        figure = self.declaration.figure
        if figure:
            canvas = FigureCanvasQTAgg(figure)
            canvas.setParent(widget)
            canvas.setFocusPolicy(Qt.ClickFocus)
            canvas.setVisible(True)
            canvas.setFocus()
            toolbar = NavigationToolbar2QT(canvas, widget)
            toolbar.setVisible(self.declaration.toolbar_visible)
            if self.declaration.toolbar_location == 'top':
                layout.addWidget(toolbar)
                layout.addWidget(canvas)
            else:
                layout.addWidget(canvas)
                layout.addWidget(toolbar)
            self.last_location = self.declaration.toolbar_location
            if self.declaration.event_actions:
                for event_name, event_action in self.declaration.event_actions:
                    try:
                        if event_name in VALID_EVENTS:
                            canvas.mpl_connect(event_name, event_action)
                    except:
                        pass


