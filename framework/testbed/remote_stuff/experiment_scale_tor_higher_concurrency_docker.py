import os, sys
import subprocess as sub
import logging
import time
import socket
import requests
import random
from flask import Flask
from flask import request


# TODO: this is not finished! Still needs lots of changes to work with docker
logging.disable(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

home_folder = "/home/dcastro/"
pathToTorBrowser = '/home/dcastro/tor-browser_en-US'

NETWORK_INTERFACE = "docker0"

#seconds +1 second due to waits to ensure onion restcalls arrive before requests
time_between_requests = 4
interval_random_between_base_time_requests = (-1,1)

#seconds
time_to_wait_after_tor_relaunch = 10 

#keep track of session time each session should take a full minute more or less
session_start_time = 0 

app = Flask(__name__)
  

def capture_traffic(capture_folder, sample_name):
    if not os.path.exists(capture_folder):
        os.makedirs(capture_folder)

    print("Starting Traffic Capture - " + capture_folder + sample_name)
    cmd = 'sudo tcpdump -i ' + NETWORK_INTERFACE + ' -W 1 -w ' + capture_folder + sample_name + '_hs.pcap'
    #May configure -s96 as an option to gather packet to 96 B snaplen
    print(cmd)
    sub.Popen(cmd, shell=True)

def stop_capture(capture_folder, sample_name):
    cmd = 'tcpdump -i ' + NETWORK_INTERFACE + ' -W 1 -w ' + capture_folder + sample_name + '_hs.pcap'
    os.system('sudo pkill -15 -f "'+cmd+'"')
    print('sudo pkill -15 -f "'+cmd+'"')

def stop_capture_all():
    os.system("sudo pkill -15 -f tcpdump")


@app.route('/startTrafficCapture', methods=['POST'])
def start_traffic_capture():
    capture_folder, sample_name = str(request.data.decode("utf-8")).split(",")
    capture_traffic(capture_folder, sample_name)

    return "Starting Traffic Capture - " + capture_folder + sample_name


@app.route('/stopTrafficCapture', methods=['POST'])
def stop_traffic_capture():
    if len(str(request.data.decode("utf-8")).split(",")) > 0:
        capture_folder, sample_name = str(request.data.decode("utf-8")).split(",")
        stop_capture(capture_folder, sample_name)
    else:
        stop_capture_all()
    return "Stopping Traffic Capture"


if __name__ == '__main__':
    request_iterations = int(sys.argv[1])
    session_iterations = int(sys.argv[2])

    hostname = socket.gethostname()


    #Create directory for holding pcaps
    client_cap_folder = home_folder+"pcap-folder/captures-" + hostname + "/"
    os.system("mkdir -p %s"%client_cap_folder)

    os.system('docker container stop torp-client')
    os.system('docker container rm torp-client')

    startTime = time.time()

    os.system('docker run -it --rm --entrypoint /experiment_docker.sh -d --name torp-client torp-client')
    
    app.run(debug=False, host='0.0.0.0', port=5005)

    logging.debug("Total time: " + str(time.time() - startTime))
