# Qt5ImageViewer
A simple image viewer using PIL with basic features. V. 0.5.1

Requires:
- pyqt5
- PIL (image magick binding)

This program use PIL to render the image files, but can also use pyqt5 directly, e.g. for the svg images. A filter for bypassing PIL is set at line 15 in the main program, if the case. This program uses the file extensions to identify the file type with the open file dialog, but also loads images without any extensions. More supported extensions can be added at line 12, if the case.

Features:
- opens images from command line and dialog;
- zoom;
- normal size and fit to window;
- mouse dragging (internal to the program only);
- rotation, by using the UP and DOWN arrow keys;
- next and previous images (folder navigation), by using the LEFT and RIGHT arrow keys;
- basic info about the image: name, size, colour depth, mimetype.

