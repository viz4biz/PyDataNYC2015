"""
vtk - surface and countours
"""

import enaml
from enaml.qt.qt_application import QtApplication


def run():
    with enaml.imports():
        from vtk_canvas_views import Main

    app = QtApplication()

    view = Main(custom_title='VTK Demo Example')
    view.show()

    # Start the application event loop
    app.start()


run()
