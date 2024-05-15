from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import start_xvfb, stop_xvfb
import sys
import os
import time
import requests
import logging
import subprocess as sub
import socket
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# HOME = "/home/daniela_lopes"
HOME = "/home/dcastro"

NETWORK_INTERFACE = "ens4"


def RESTCall(host, method, args=""):
    url='http://' + host + ':5005/' + method

    #Ensure that we will not continue through the experiment while
    # we do not properly communicate with onion hosts.
    #Backoff until a max of 16s between repeated requests

    r = None
    backoff = 1
    while(r is None):
        try:
            logging.info("********* url: " + url)
            logging.info("********* args: " + args)
            r = requests.post(url, data=args)
        except requests.exceptions.RequestException as e:
            logging.debug(e)
            logging.debug("Sleeping for backoff time: %ds"%backoff)
            time.sleep(backoff)
            if(backoff < 16):
                backoff = backoff * 2


'''
def start_traffic_capture(capture_folder, sample_name):
    logging.debug("Start traffic capture - %s%s"%(capture_folder,sample_name))
    cmd = 'sudo tcpdump  -i ' + NETWORK_INTERFACE + ' -W 1 -w ' + capture_folder + "\"" + sample_name + "\"" + '_client.pcap'
    #May configure -s96 as an option to gather packet to 96 B snaplen
    sub.Popen(cmd, shell=True)
'''

def start_traffic_capture(capture_folder, sample_name): 
    if not os.path.exists(capture_folder):
        os.makedirs(capture_folder)

    logging.debug("Starting Traffic Capture - " + capture_folder + sample_name)
    cmd = 'sudo tcpdump -i ' + NETWORK_INTERFACE + ' -W 1 -w ' + capture_folder + sample_name + '_client.pcap (tcp port not 22) and not (src 127.0.0.1 and dst 127.0.0.1)'
    #May configure -s96 as an option to gather packet to 96 B snaplen
    sub.Popen(cmd, shell=True)
    return cmd

'''
def stop_traffic_capture():
    cmd = "sudo pkill -9 -f tcpdump"
    sub.Popen(cmd, shell=True)
'''

def stop_traffic_capture(cmd = ''):
    if cmd == '':
        os.system('sudo pkill -15 -f tcpdump')
        #logging.debug('sudo pkill -15 -f tcpdump')
    else:
        os.system('sudo pkill -15 -f "'+cmd+'"')
        #logging.debug('sudo pkill -15 -f "'+cmd+'"')



def getOnionPageThroughSelenium(driver, address, hostname, target_node, onion_service_real_ip, sample_name, client_cap_folder):
    
    #Instruct pcap to start on the onion service's end
    onion_cap_folder = "pcap-folder/" + hostname + "-" + target_node + "/"
    RESTCall(onion_service_real_ip, "startTrafficCapture", onion_cap_folder + "," + sample_name)

    #Instruct pcap to start locally
    cmd = start_traffic_capture(client_cap_folder, sample_name)
    time.sleep(0.5)

    #Refresh the cache
    #Place request towards the HS
    driver.refresh()

    #Instruct pcap to stop locally
    time.sleep(0.5)
    logging.debug("Stopping traffic capture...")
    stop_traffic_capture(cmd[5:])

    #Instruct pcap to stop on the onion service's end
    RESTCall(onion_service_real_ip, "stopTrafficCapture", onion_cap_folder + "," + sample_name)
    #RESTCall(onion_service_real_ip, "stopTrafficCapture")


def parse_inventory():

    start_traffic_capture(HOME + "/"+client_cap_folder, sample_name)

    onion_cap_folder = "pcap-folder/" + hostname + "-" + target_node + "/"
    RESTCall(onion_service_real_ip, "startTrafficCapture", onion_cap_folder + "," + sample_name)


    #Place the request via tor
    address = "http://" + onion_service_address + "/onion_pages/" + onion_page + "/index.html"

    #Make a first request to the HS to build the circuit
    driver.get(address)

    #Wait a few seconds for selenium spurious traffic 
    time.sleep(10)
    
    #Cycle request_iterations times through the HS list and place requests
    for i in range(0,request_iterations):
        logging.debug("Iteration number: %d"%i)

        #Use a fresh Tor circuit for each iteration
        #rebuild_tor_circuit()

        sample_name = hostname + "_" + target_node + "_" + onion_page + "_" + str(i)
        
        #place_request_via_tor(address, hostname, target_node, onion_service_real_ip, sample_name, "/home/danielalopes97/"+client_cap_folder)
        getOnionPageThroughSelenium(driver, address, hostname, target_node, onion_service_real_ip, sample_name, "/home/dcastro/"+client_cap_folder)

        #Wait a sec
        time.sleep(1)

    print("************ ADDRESS OF REQUEST TO TOR: ***********: " + address)

    os.system('sudo lsof -i -P -n > '+"/home/dcastro/"+client_cap_folder+hostname + "_" + target_node + "_" + onion_page+'_info')
    stop_traffic_capture()

    driver.quit()

    stop_xvfb(xvfb_display)


# Execute $ python3 get_onion_with_selenium.py
if __name__ == '__main__':
    target_node = sys.argv[1]
    onion_page = sys.argv[2]
    request_iterations = sys.argv[3]

    connect_to_onions(target_node, onion_page, int(request_iterations))
