# Qt5ImageViewer
A simple image viewer using PIL with basic features. V. 0.7.7

Requires:
- pyqt5
- PIL (image magick binding)

This program use PIL to render the image files, but can also use pyqt5 directly, e.g. for the svg images. A filter for bypassing PIL is set at line 15 in the main program, if the case. This program uses the file extensions to identify the file type with the open file dialog, but also loads images without any extensions. More supported extensions can be added at line 12, if the case.

Features:
- opens images from command line and dialog;
- supports animated gifs;
- zoom;
- normal size;
- image mouse dragging;
- rotation, by using the UP and DOWN arrow keys, or the menu;
- next and previous images (folder navigation), by using the LEFT and RIGHT arrow keys;
- basic info about the image: name, size, colour depth, mimetype;
- custom actions support for external operations by using the bash script.

A screenshot:

![My image](https://github.com/frank038/Qt5ImageViewer/blob/main/screenshot1.png)
