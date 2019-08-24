#!/bin/bash
TEMPER=`sudo /home/pi/TEMPered/utils/tempered | head -n 1 | awk '{ print $4 }'`

cd /home/pi/temperature_monitor/
python3 handle_temperature.py $TEMPER
