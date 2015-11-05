"""
Demo
"""

import enaml
from enaml.qt.qt_application import QtApplication


def run_demo():
    with enaml.imports():
        from demo_ui import Main

    app = QtApplication()

    view = Main(message='Hello World, from Python!')
    view.show()

    # Start the application event loop
    app.start()


run_demo()