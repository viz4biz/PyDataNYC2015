"""
vtk surface runner
"""

import enaml
from enaml.qt.qt_application import QtApplication


def run():
    with enaml.imports():
        from vtk_surface_view import Main

    app = QtApplication()

    view = Main(custom_title='VTK Surface Example')
    view.show()

    # Start the application event loop
    app.start()


run()
