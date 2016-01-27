#!/bin/sh

cd "$(dirname "$0")"

rm weather-script-output-current.png
rm weather-script-output-hourly.png
rm weather-script-output-daily.png

wget http://bet:8888/weather-script-output-current.png
wget http://bet:8888/weather-script-output-hourly.png
wget http://bet:8888/weather-script-output-daily.png

eips -c
eips -c
if [ -f weather-script-output-current.png ]; then
	eips -g weather-script-output-current.png
else
	eips -g weather-image-error.png
fi
sleep 10

eips -c
eips -c
if [ -f weather-script-output-hourly.png ]; then
	eips -g weather-script-output-hourly.png
else
	eips -g weather-image-error.png
fi
sleep 10

eips -c
eips -c
if [ -f weather-script-output-daily.png ]; then
	eips -g weather-script-output-daily.png
else
	eips -g weather-image-error.png
fi
sleep 10

eips -c
eips -c
if [ -f weather-script-output-current.png ]; then
	eips -g weather-script-output-current.png
else
	eips -g weather-image-error.png
fi
sleep 10

eips -c
eips -c
if [ -f weather-script-output-hourly.png ]; then
	eips -g weather-script-output-hourly.png
else
	eips -g weather-image-error.png
fi
sleep 10

eips -c
eips -c
if [ -f weather-script-output-daily.png ]; then
	eips -g weather-script-output-daily.png
else
	eips -g weather-image-error.png
fi

