#!/bin/sh

cd "$(dirname "$0")"

python2 weather-transit-script.py

rsvg-convert --background-color=white -o weather-script-output-current.png weather-script-output-current.svg
convert weather-script-output-current.png -rotate 270 weather-script-output-current-rotated.png
pngcrush -c 0 weather-script-output-current-rotated.png weather-script-output-current-final.png
cp -f weather-script-output-current-final.png /var/www/weather-script-output-current.png


rsvg-convert --background-color=white -o weather-script-output-hourly.png weather-script-output-hourly.svg
convert weather-script-output-hourly.png -rotate 270 weather-script-output-hourly-rotated.png
pngcrush -c 0 weather-script-output-hourly-rotated.png weather-script-output-hourly-final.png
cp -f weather-script-output-hourly-final.png /var/www/weather-script-output-hourly.png
