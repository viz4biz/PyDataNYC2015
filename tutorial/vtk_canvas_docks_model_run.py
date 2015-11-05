"""
Demo run
"""
import enaml
from enaml.qt.qt_application import QtApplication


def run():
    with enaml.imports():
        from vtk_canvas_docks_model import Main

    app = QtApplication()

    view = Main(custom_title='VTK Example')
    view.show()

    # Start the application event loop
    app.start()


run()

