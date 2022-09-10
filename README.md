# Qt5ImageViewer
A simple image viewer using PIL with basic features. V. 0.8

Requires:
- pyqt5
- PIL (image magick binding): optional, to add unsupported image formats by Qt5.

Configuration in the config file.

This program can use PIL, as option, to render the image files not supported by pyqt5 directly. This program uses the file extensions to identify the file type with the open file dialog, but also loads images without any extensions.

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
