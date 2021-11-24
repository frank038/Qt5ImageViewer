#!/bin/bash

thisdir=$(dirname "$0")
cd $thisdir
if [[ $# -eq 0 ]]; then
  ./Qt5ImageViewer.py
else
  ./Qt5ImageViewer.py "$1"
fi