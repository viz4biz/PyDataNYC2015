# PyDataNYC2015
PyData NYC 2015 tutorial examples

Code examples for visualization tutorial at PyData 2015 conference in New York
in November 2015. Please feel free to download and use it.

More resources about this talk at PyData 2015: http://nyc2015.pydata.org/schedule/presentation/9/
and video: https://www.youtube.com/watch?v=wUtMuQScZTY

Here are VTK and Matplotlib code samples, both Python and Enaml files.
All code works with newest Anaconda Python distribution.
You need VTK 6.1 or newer to run VTK examples (curent version of VTK in Anaconda
for MacOS is 6.3). Matplotlib examples were tested with matplotlib version 1.5.1

In order to run tutorial examples you need to copy following files from enaml
folder into enaml folder in your anaconda distribution:


###Installation


```sh
$ cp mpl_canvas.py vtk_canvas.py anaconda/lib/python2.7/site-packages/enaml/widgets
$ cp qt_mpl_canvas.py qt_vtk_canvas.py anaconda/lib/python2.7/site-packages/enaml/qt

or run provided script: enaml_patch.sh after editing your directory location.
```

You need to edit constants.py file in tutorial and vtklib folders to reflect icons and data
location on your machine.

You can also copy provided custom matplotlib style - darkish.mplstyle into matplotlib resource
directory:

```sh
$ cp darkish.mplstyle anaconda/lib/python2.7/site-packages/matplotlib/mpl-data/stylelib
```

###Contents

 - tutorial: this folder contains all the tutorial files
 - enaml: this folder contains updates to core Enaml files - to be submitted
to enaml development team
 - vtklib: this contains VTK surface visualization library and related source code
 - data: this folder contains some data files used in this tutorial
 - icons: various icons
 - slides: slides from the presentation
 - images: images for this README file

###Matplotlib Examples

 1. Scatter plot animation - mplot_demo1.py
 ![alt text](https://github.com/viz4biz/PyDataNYC2015/blob/master/images/mplotlib_demo1.png "Scatter Plot Animation")

 2. Simple scatter plot - mplot_demo2.py
 ![alt text](https://github.com/viz4biz/PyDataNYC2015/blob/master/images/mplotlib_demo2.png "Scatter Plot")

 3. Multi line plot with controls - mplot_demo3.py
 ![alt text](https://github.com/viz4biz/PyDataNYC2015/blob/master/images/mplotlib_demo3.png "Multiline Plot with controls")

 4. Multi line plot - mplot_demo4.py
 ![alt text](https://github.com/viz4biz/PyDataNYC2015/blob/master/images/mplotlib_demo4.png "Multiline Plot")

###VTK Examples

1. Multi window example - vtk_multi_window_run.py
![alt text](https://github.com/viz4biz/PyDataNYC2015/blob/master/images/vtk_multi_window_demo1.png "Multi window plot")

2. Multi docking example - vtk_canvas_docks_model_run.py
![alt text](https://github.com/viz4biz/PyDataNYC2015/blob/master/images/vtk_docking_demo11.png "Multi docking plot")

3. Surface example - vtk_surface_run.py
![alt text](https://github.com/viz4biz/PyDataNYC2015/blob/master/images/vtk_surface_demo1.png "Surface plot")

4. Grid example - vtk_simple_grid_run.py
![alt text](https://github.com/viz4biz/PyDataNYC2015/blob/master/images/vtk_grid_demo1.png "Grid plot")
