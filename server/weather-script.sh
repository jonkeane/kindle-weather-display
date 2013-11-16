#!/bin/sh

cd "$(dirname "$0")"

python2 weather-transit-script.py
rsvg-convert --background-color=white -o weather-script-output.png weather-script-output.svg
convert weather-script-output.png -rotate 90 weather-script-output-rotated.png
pngcrush -c 0 weather-script-output-rotated.png weather-script-output-final.png
cp -f weather-script-output-final.png /var/www/weather-script-output.png
