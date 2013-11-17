#!/bin/sh

cd "$(dirname "$0")"

rm weather-script-output-current.png
rm weather-script-output-hourly.png
#eips -c
eips -c

wget http://192.168.100.111:8080/weather-script-output-current.png
wget http://192.168.100.111:8080/weather-script-output-hourly.png

eips -c
eips -c
if [ -f weather-script-output-current.png ]; then
	eips -g weather-script-output-current.png
else
	eips -g weather-image-error.png
fi
sleep 10

eips -c
if [ -f weather-script-output-hourly.png ]; then
	eips -g weather-script-output-hourly.png
else
	eips -g weather-image-error.png
fi
sleep 10

eips -c
if [ -f weather-script-output-current.png ]; then
	eips -g weather-script-output-current.png
else
	eips -g weather-image-error.png
fi
sleep 10

eips -c
if [ -f weather-script-output-hourly.png ]; then
	eips -g weather-script-output-hourly.png
else
	eips -g weather-image-error.png
fi
sleep 10

eips -c
if [ -f weather-script-output-current.png ]; then
	eips -g weather-script-output-current.png
else
	eips -g weather-image-error.png
fi
sleep 10

eips -c
if [ -f weather-script-output-hourly.png ]; then
	eips -g weather-script-output-hourly.png
else
	eips -g weather-image-error.png
fi