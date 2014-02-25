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

rsvg-convert --background-color=white -o weather-script-output-daily.png weather-script-output-daily.svg
convert weather-script-output-daily.png -rotate 270 weather-script-output-daily-rotated.png
pngcrush -c 0 weather-script-output-daily-rotated.png weather-script-output-daily-final.png
cp -f weather-script-output-daily-final.png /var/www/weather-script-output-daily.png