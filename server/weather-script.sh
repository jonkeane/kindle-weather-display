#!/bin/sh

cd "$(dirname "$0")"

python2 weather-transit-script.py
rsvg-convert --background-color=white -rotate 90 -o weather-script-output.png weather-script-output.svg
pngcrush -c 0 -ow weather-script-output.png
cp -f weather-script-output.png /path/to/web/server/directory/weather-script-output.png
