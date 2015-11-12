"""
Datetime field demo run
"""

import enaml
from enaml.qt.qt_application import QtApplication


def run_demo():
    with enaml.imports():
        from datetime_field import Main

    app = QtApplication()

    view = Main()
    view.show()

    # Start the application event loop
    app.start()


run_demo()