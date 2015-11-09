'''
Demo
'''

import enaml
from enaml.qt.qt_application import QtApplication


def run_demo():
    with enaml.imports():
        #from mplot_demo_ui import Main
        #from griddata_demo_ui import Main
        #from mplot_lines_demo import Main
        #from mplot_lines_dynamic import Main
        #from mplot_demo_dynamic import Main
        #from mplot_demo_realtime import Main
        #from mplot_demo_multi import Main
        #from mplot_demo_docks import Main
        from mplot_demo_controls import Main

    app = QtApplication()

    view = Main(custom_title='Matplotlib demo', mplot_style='darkish')
    view.show()

    # Start the application event loop
    app.start()


run_demo()
