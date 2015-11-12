# PyDataNYC2015
PyData NYC 2015 tutorial examples

Code examples for visualization tutorial at PyData 2015 conference in New York
in November 2015. Please feel free to download and use it.

Here are VTK and Matplotlib code samples, both Python and Enaml files.
All code works with newest Anaconda Python distribution.
You need VTK 6.1 or newer to run VTK examples (curent version of VTK in Anaconda
for MacOS is 6.3).

In order to run tutorial examples you need to copy following files from enaml
folder into enaml folder in your anaconda distribution:


###Installation


```sh
$cp mpl_canvas.py vtk_canvas.py anaconda/lib/python2.7/site-packages/enaml/widgets
$cp qt_mpl_canvas.py qt_vtk_canvas.py anaconda/lib/python2.7/site-packages/enaml/qt
```

You need to edit constants.py file in tutorial folder to reflect icons and data
location on your machine.


###Content

 - tutorial: this folder contains all the tutorial files
 - enaml: this folder contains updates to core Enaml files - to be submitted
to enaml team
 - vtklib: this contains VTK surface visualization related source code
 - data: this folder contains some data files used in this tutorial
 - icons: various icons
 - slides: slides from the presentation
