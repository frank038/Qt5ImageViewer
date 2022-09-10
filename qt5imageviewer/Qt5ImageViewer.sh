#!/bin/bash

thisdir=$(dirname "$0")
cd $thisdir
if [[ $# -eq 0 ]]; then
  python3 Qt5ImageViewer.py &
else
  python3 Qt5ImageViewer.py "$1" &
fi
cd $HOME
