#!/bin/sh

# Patch existing enaml distribution with updated files required by this tutorial
# edit to provide your current location

PATCH_DIR=/Users/pawel/src/PyDataNYC2015/enaml
ANACONDA_HOME=/Users/pawel/anaconda
ENAML_HOME=$ANACONDA_HOME/lib/python2.7/site-packages/enaml

# backup qt files
cp $ENAML_HOME/qt/qt_mpl_canvas.py $ENAML_HOME/qt/qt_mpl_canvas.py.bak
cp $ENAML_HOME/qt/qt_vtk_canvas.py $ENAML_HOME/qt/qt_vtk_canvas.py.bak

# copy qt patches
cp $PATCH_DIR/qt_mpl_canvas.py $ENAML_HOME/qt
cp $PATCH_DIR/qt_vtk_canvas.py $ENAML_HOME/qt

# backup widget files
cp $ENAML_HOME/widgets/mpl_canvas.py $ENAML_HOME/widgets/mpl_canvas.py.bak 
cp $ENAML_HOME/widgets/vtk_canvas.py $ENAML_HOME/widgets/vtk_canvas.py.bak 


# copy widget patches
cp $PATCH_DIR/mpl_canvas.py $ENAML_HOME/widgets
cp $PATCH_DIR/vtk_canvas.py $ENAML_HOME/widgets

