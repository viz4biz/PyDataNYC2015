"""
vtk extract runner
"""

import enaml
from enaml.qt.qt_application import QtApplication


def run():
    with enaml.imports():
        from vtk_extract_view import Main

    app = QtApplication()

    view = Main(custom_title='VTK Geometry Extract Example')
    view.show()

    # Start the application event loop
    app.start()


run()
