import sys, os
import subprocess as sub
import time, sched
import random
import threading
import requests
import socket
import logging
from flask import Flask
from flask import request
import http.server
import socketserver
import threading

## TODO : USE THIS AS INSP FOR THE TOR_SIMULATE USER MOKI
logging.basicConfig(filename = 'file.log',level=logging.DEBUG,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

HTTP_PORT = 8001
REST_PORT = 5005

Handler = http.server.SimpleHTTPRequestHandler


NETWORK_INTERFACE = "eth0"

app = Flask(__name__)

def capture_cmd(capture_folder, sample_name):
    # return 'tcpdump -i ' + NETWORK_INTERFACE + ' -W 1 -w ' + capture_folder + sample_name + '_hs.pcap'
    # -s 128 captures only 128B of data (trucates the rest)

    return 'tcpdump -i ' + NETWORK_INTERFACE + ' -s 66 -W 1 -w ' + capture_folder + sample_name + '_hs.pcap \'(port not 22) and not (src 127.0.0.1 and dst 127.0.0.1)\''


def capture_traffic(capture_folder, sample_name):
    if not os.path.exists(capture_folder):
        os.makedirs(capture_folder)

    print("Starting Traffic Capture - " + capture_folder + sample_name)
    cmd = capture_cmd(capture_folder, sample_name)
    #May configure -s96 as an option to gather packet to 96 B snaplen
    print(cmd)
    sub.Popen(cmd, shell=True)

def stop_capture(capture_folder, sample_name):
    cmd = capture_cmd(capture_folder, sample_name)
    os.system('pkill -15 -f "'+cmd+'"')
    print('pkill -15 -f "'+cmd+'"')
    #May configure -s96 as an option to gather packet to 96 B snaplen
    logging.info(cmd)
    sub.Popen(cmd, shell=True)

def stop_capture(capture_folder, sample_name):
    cmd = 'tcpdump -i ' + NETWORK_INTERFACE + ' -W 1 -w ' + capture_folder + sample_name + '_hs.pcap'
    os.system('sudo pkill -15 -f "'+cmd+'"')
    logging.info('sudo pkill -15 -f "'+cmd+'"')

def stop_capture_all():
    os.system("pkill -15 -f tcpdump")

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


if __name__ == "__main__":

    page = sys.argv[1]

    hostname = socket.gethostname()

    # docker kill $(docker ps -q)
    ### TODO: with this approach only ansible is allowed to start new dockers 
    ### I really dont like this

    capture_traffic('pcap-folder/full-onion/', hostname + '_' + page)

    app.run(debug=False, host='0.0.0.0', port=5005)
    os.system('docker run -it --rm -v /home/daniela_lopes/hidden-service-docker-image/web:/web2 -p 8080:8080 --entrypoint /serve.sh -d --name torp-onion-service torp-onion-service')

    server = socketserver.TCPServer(("", HTTP_PORT), Handler)
    th = threading.Thread(name='httpwebsite', target=server.serve_forever, daemon=True)
    th.start()
    logging.info("---- Serving at port {}".format(HTTP_PORT))

    # Needs to be after since it runs one the main thread
    app.run(debug=False, host='0.0.0.0', port=REST_PORT)
