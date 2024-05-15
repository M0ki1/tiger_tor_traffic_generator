#!/bin/bash


echo "nOnions: $1"
echo "Page1: $2"
echo "Page2: $3"

echo "Page3: $4"
echo "Page4: $5"
python3 capture_traffic_scale_tor_simulate_user.py $1 $2 $3 $4 $5


