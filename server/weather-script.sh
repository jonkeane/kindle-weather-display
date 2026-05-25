#!/bin/sh

set -eu

cd "$(dirname "$0")"

python3 weather_transit.py

output_dir="outputData"

render_view() {
    view="$1"
    svg_path="$output_dir/weather-script-output-$view.svg"
    rendered_png="$output_dir/weather-script-output-$view-rendered.png"
    rotated_png="$output_dir/weather-script-output-$view-rotated.png"
    final_png="$output_dir/weather-script-output-$view.png"

    rsvg-convert --background-color=white -o "$rendered_png" "$svg_path"
    convert "$rendered_png" -rotate 270 "$rotated_png"
    pngcrush -c 0 "$rotated_png" "$final_png"
    cp -f "$final_png" "/var/www/weather-script-output-$view.png"
}

for view in current hourly daily; do
    render_view "$view"
done
