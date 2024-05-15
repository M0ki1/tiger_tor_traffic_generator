import os, sys
import subprocess as sub
import logging
import time
import socket
import requests
import random
import numpy as np
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import start_xvfb, stop_xvfb
from bs4 import BeautifulSoup

REST_PORT = 5005

def RESTCall(host, method, args=""):
    url='http://' + host + ':{}/'.format(REST_PORT) + method
    r = None
    backoff = 1
    logging.debug(" --- SIGNAL TERMINATION --- ", url)
    while(r is None):
        try:
            r = requests.post(url, data=args)
        except requests.exceptions.RequestException as e:
            logging.debug(e)
            logging.debug("Sleeping for backoff time: %ds"%backoff)
            # It can stop here ...
            time.sleep(backoff)
            if(backoff < 16):
                backoff = backoff * 2

def retrieve_coordinator_IP():
    inventory_file_name = '/app/inventory.cfg'
    data_loader = DataLoader()
    inventory = InventoryManager(loader = data_loader, sources=[inventory_file_name])

    inventory.parse_sources()
    
    coordinator_ip = ""
    for host in inventory.get_hosts():
        if "job-coordinator" in host.vars["node_name"]:
            coordinator_ip = host.vars["ansible_host"]

    return coordinator_ip

def signal_termination(job_coordinator_ip):
    RESTCall(job_coordinator_ip, "signalTermination", socket.gethostname())

if __name__ == '__main__':
  job_coordinator_ip = retrieve_coordinator_IP()
  signal_termination(job_coordinator_ip)