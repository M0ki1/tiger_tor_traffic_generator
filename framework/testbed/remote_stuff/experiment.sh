#!/bin/bash
#Run python script
echo "nOnions: $1"
echo "Number of requests: $2"
echo "Client ID: $3"
python3 experiment_scale_tor_simulate_user.py $1 $2 $3
echo "finished"