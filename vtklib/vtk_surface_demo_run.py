"""
VTK surface demo run
"""

import enaml
from enaml.qt.qt_application import QtApplication
from datasources import zdata, dsin, dtx, dtv, nonedatarandom


def run():
    with enaml.imports():
        from vtk_surface_demo import Main

    app = QtApplication()

    view = Main(data=[dsin(), zdata(), dtx(), dtv(), nonedatarandom()])
    view.show()

    # Start the application event loop
    app.start()


run()
