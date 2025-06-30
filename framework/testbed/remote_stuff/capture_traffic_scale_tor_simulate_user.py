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


logging.basicConfig(filename = 'file.log',level=logging.DEBUG,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

HTTP_PORT = 8001
REST_PORT = 5005

Handler = http.server.SimpleHTTPRequestHandler


#NETWORK_INTERFACE = "eth0"
NETWORK_INTERFACE = "any"


app = Flask(__name__)

def capture_cmd(capture_folder, sample_name):
    # return 'tcpdump -i ' + NETWORK_INTERFACE + ' -W 1 -w ' + capture_folder + sample_name + '_hs.pcap'
    # -s 128 captures only 128B of data (trucates the rest)

    # TODO: the parenthesis break the pkill
    cmd = cmd[:cmd.rfind("'(port not 22) and not (src 127.0.0.1 and dst 127.0.0.1)'")]
    logging.info("Stopping Traffic Capture - " + capture_folder + sample_name)

    docker_cmd = f'docker exec torp-onion-service-{onion_idx} sh -c "pkill -f \'{cmd}\'"'


    os.system(docker_cmd)
    logging.info(f'pkill -f \"{cmd}\"')


def stop_capture_all():
    for i in range(4):
        os.system(f'docker exec torp-onion-service-{i} sh -c "pkill tcpdump"')


# TODO Define capture_traffic to rune in here, its making that all colapsesMOKI

@app.route('/startTrafficCapture', methods=['POST'])
def start_traffic_capture():
    capture_folder, onion_idx, sample_name = str(request.data.decode("utf-8")).split(",")
    capture_traffic(capture_folder, onion_idx, sample_name)

    return "Starting Traffic Capture - " + capture_folder + sample_name


@app.route('/stopTrafficCapture', methods=['POST'])
def stop_traffic_capture():
    capture_folder, onion_idx, sample_name = "", -1, ""
    if len(str(request.data.decode("utf-8")).split(",")) > 0:
        capture_folder, onion_idx, sample_name = str(request.data.decode("utf-8")).split(",")
        print("=== capture_folder {}; sample_name {}".format(capture_folder, sample_name))
        stop_capture(capture_folder, onion_idx, sample_name)
    else:
        stop_capture_all()
    return "Stopping Traffic Capture - " + capture_folder + sample_name

@app.route('/test', methods=['GET'])
def test():
    return "test"

if __name__ == "__main__":


    if not (sys.argv[1].isdigit()):
        logging.error("nOnions is not valid!")
        exit()

    nOnions = int(sys.argv[1])
    pages = []
    for i in range(nOnions):
        pages.append(sys.argv[i + 2])

    logging.info("pages: {}".format(pages))

    hostname = socket.gethostname()
    host = '0.0.0.0'


    for i in range(nOnions):
        capture_traffic('pcap-folder/full-onion/', i + 1, hostname + '_' + pages[i])


    server = socketserver.TCPServer(("", HTTP_PORT), Handler)
    th = threading.Thread(name='httpwebsite', target=server.serve_forever, daemon=True)
    th.start()
    logging.info("---- Serving at port {}".format(HTTP_PORT))

    # Needs to be after since it runs one the main thread
    app.run(debug=False, host=host, port=REST_PORT)
