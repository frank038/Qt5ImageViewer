#!/bin/bash

thisdir=$(dirname "$0")
cd $thisdir
./Qt5ImageViewer.py "$1"
