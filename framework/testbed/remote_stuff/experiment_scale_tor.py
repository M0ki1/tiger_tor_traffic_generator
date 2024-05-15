import os, sys
import subprocess as sub
import logging
import time
import socket
import requests
import random
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import start_xvfb, stop_xvfb

logging.disable(logging.DEBUG)

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

home_folder = "/home/dcastro/"
pathToTorBrowser = '/home/dcastro/tor-browser_en-US'


# home_folder = "/home/daniela_lopes/"
# pathToTorBrowser = '/home/daniela_lopes/tor-browser_en-US'


NETWORK_INTERFACE = "ens4"

#seconds +1 second due to waits to ensure onion restcalls arrive before requests
time_between_requests = 4
interval_random_between_base_time_requests = (-1,1)

#seconds
time_to_wait_after_tor_relaunch = 10 

#keep track of session time each session should take a full minute more or less
session_start_time = 0 

alexa_probability = 0.25

def retrieve_coordinator_IP():
    inventory_file_name = home_folder+'inventory.cfg'
    data_loader = DataLoader()
    inventory = InventoryManager(loader = data_loader, sources=[inventory_file_name])

    inventory.parse_sources()
    
    coordinator_ip = ""
    for host in inventory.get_hosts():
        if(host.vars["node_name"] == "job-coordinator"):
            coordinator_ip = host.vars["ansible_host"]

    return coordinator_ip


def RESTCall(host, method, args=""):
    url='http://' + host + ':5005/' + method

    #Ensure that we will not continue through the experiment while
    # we do not properly communicate with onion hosts.
    #Backoff until a max of 16s between repeated requests

    r = None
    backoff = 1
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

def signal_termination(job_coordinator_ip):
    RESTCall(job_coordinator_ip, "signalTermination", socket.gethostname())


def rebuild_tor_circuit():
    logging.debug("Rebuilding Tor circuit")
    sub.call("sudo killall -HUP tor", shell=True)
    
    


def place_request_via_tor(os_node, request_iterations, session_sample_name):
    
    #Cycle request_iterations times through the HS list and place requests
    for i in range(0,request_iterations):
        logging.debug("Iteration number: %d"%i)

        #Use a fresh Tor circuit for each iteration
        #rebuild_tor_circuit()

        sample_name = session_sample_name + "_request_" + str(i)
        

        #Instruct pcap to start on the onion service's end
        onion_cap_folder = home_folder+"pcap-folder/" + hostname + "-" + os_node['node_name'] + "/"
        RESTCall(os_node['ansible_host'], "startTrafficCapture", onion_cap_folder + "," + sample_name)

        #Instruct pcap to start locally
        cmd = start_traffic_capture(client_cap_folder, sample_name)
        time.sleep(0.5)

        #Place the request via tor
        address = "http://" + os_node['onion_address'] + "/onion_pages/" + os_node['onion_page'] + "/index.html"


        try:
            #If first make a get
            #if(driver.current_url + '==' + address):
            if(i > 0):
                logging.debug("Repeating request with refresh()")
                driver.refresh()
            #If same url refresh full page
            else:
                logging.debug("First request with get()")
                driver.get(address)
        except Exception as e:
            logging.debug("Request failed...")
            logging.debug(e)

        #Instruct pcap to stop locally
        time.sleep(0.5)
        logging.debug("Stopping traffic capture...")
        stop_traffic_capture(cmd[5:])

        #Instruct pcap to stop on the onion service's end
        RESTCall(os_node['ansible_host'], "stopTrafficCapture", onion_cap_folder + "," + sample_name)
        #RESTCall(onion_service_real_ip, "stopTrafficCapture")


        #Wait a sec
        time.sleep(time_between_requests+random.uniform(interval_random_between_base_time_requests[0], interval_random_between_base_time_requests[1]))
    
def place_request_via_tor_alexa(alexa_page, request_iterations, session_sample_name):
    
    try:
        startAlexaTime = time.time()
        #Cycle request_iterations times through the HS list and place requests
        for i in range(0,request_iterations):
            logging.debug("Iteration number: %d"%i)

            #Use a fresh Tor circuit for each iteration
            #rebuild_tor_circuit()

            sample_name = session_sample_name + "_request_" + str(i)
            
            #Instruct pcap to start locally
            cmd = start_traffic_capture(client_cap_folder, sample_name)
            time.sleep(0.5)

            #Place the request via tor
            address = "http://" + alexa_page

            #If first make a get
            #if(driver.current_url + '==' + address):
            if(i > 0):
                logging.debug("Repeating request with refresh()")
                driver.refresh()
            #If same url refresh full page
            else:
                logging.debug("First request with get()")
                driver.get(address)

            #Instruct pcap to stop locally
            time.sleep(0.5)
            logging.debug("Stopping traffic capture...")
            stop_traffic_capture(cmd[5:])

            #check if we crossed one minute if so break
            if time.time() - startAlexaTime > 55:
                break

            #Wait a sec
            time.sleep(time_between_requests+random.uniform(interval_random_between_base_time_requests[0], interval_random_between_base_time_requests[1]))
    
    except:
        logging.debug('Skipping alexa site, not reachable by tor...')

def start_traffic_capture(capture_folder, sample_name): 
    if not os.path.exists(capture_folder):
        os.makedirs(capture_folder)

    logging.debug("Starting Traffic Capture - " + capture_folder + sample_name)
    cmd = 'sudo tcpdump -i ' + NETWORK_INTERFACE + ' -W 1 -w ' + capture_folder + sample_name + '_client.pcap port not 22'
    #May configure -s96 as an option to gather packet to 96 B snaplen
    sub.Popen(cmd, shell=True)
    return cmd


def stop_traffic_capture(cmd = ''):
    if cmd == '':
        os.system('sudo pkill -15 -f tcpdump')
        #logging.debug('sudo pkill -15 -f tcpdump')
    else:
        os.system('sudo pkill -15 -f "'+cmd+'"')
        #logging.debug('sudo pkill -15 -f "'+cmd+'"')


def parse_inventory():
    inventory_file_name = 'inventory.cfg'
    data_loader = DataLoader()
    inventory = InventoryManager(loader = data_loader,
                             sources=[inventory_file_name])

    inventory.parse_sources()
    
    os_nodes = []
    for host in inventory.get_hosts():
        print("HOST: " + str(host))
        if('os-' in host.vars["node_name"]):
            tmp = {}
            tmp["node_name"] = host.vars["node_name"]
            print("node_name: " + str(host.vars["node_name"]))
            tmp["onion_page"] = host.vars["onion_page"]
            print("onion_page: " + str(host.vars["onion_page"]))
            tmp["onion_address"] = host.vars["onion_address"]
            print("onion_address: " + str(host.vars["onion_address"]))
            tmp["onion_popularity"] = host.vars["onion_popularity"]
            print("onion_popularity: " + str(host.vars["onion_popularity"]))
            tmp["ansible_host"] = host.vars["ansible_host"]
            print("ansible_host: " + str(host.vars["ansible_host"]))
            os_nodes.append(tmp)

    return os_nodes

def get_node_random(nodes):
    
    return_node = None

    while return_node == None:
        sorted_nodes = sorted(nodes, key=lambda node: node['onion_popularity'])
        my_random = random.randint(0, 10000)
        cumulative_sum = 0
        for i in sorted_nodes:
            cumulative_sum += i['onion_popularity']*10000
            if my_random < cumulative_sum:
                return_node = i
                break
        
        if return_node == None:
            print('My_random:', my_random)
            print('Cumulative_sum:', cumulative_sum)
            # TODO: when this situation happens, the script stops, should we choose
            # a random one or just move to the next iteration? because this could distort the results???

    return return_node

def parse_alexa_pages():
    alexa_pages = []
    alexa_pages_file_name = 'alexa_top_50.txt'
    f = open(alexa_pages_file_name, 'r')
    for line in f:
        alexa_pages.append(line[:-1])
    return alexa_pages

def get_alexa_page_random(alexa_pages):
    mypageid = random.randint(0, len(alexa_pages)-1)
    return alexa_pages[mypageid]

if __name__ == '__main__':
    request_iterations = int(sys.argv[1])
    session_iterations = int(sys.argv[2])

    onion_services = parse_inventory()
    alexa_pages = parse_alexa_pages()
    hostname = socket.gethostname()


    #Create directory for holding pcaps
    client_cap_folder = home_folder+"pcap-folder/captures-" + hostname + "/"
    os.system("mkdir -p %s"%client_cap_folder)

    #start virtual display for Tor browser
    xvfb_display = start_xvfb()

    #ensure Tor is not running
    os.system('sudo pkill -15 -f /usr/bin/tor')
    os.system('sudo pkill -15 -f /etc/tor/torrc')

    startTime = time.time()
    
    #Restart browser and Tor for each browsing session
    #Start new capture before restarting Tor and Broswer
    for i in range(session_iterations):
        print("========== SESSION ITERATION ==========", i)
        session_start_time = time.time()

        #go to alexa or onion?
        alexa = False
        alexa_page = ''
        my_number = random.randint(0, 100)
        if my_number < alexa_probability*100:
            alexa = True
            #select alexa page randonmly
            alexa_page = get_alexa_page_random(alexa_pages)
            print("===== ALEXA: hostname: " + hostname + " ; alexa_page: " +  alexa_page + " ; i: " + str(i))
            session_sample_name = hostname + "_alexa_" + alexa_page + "_session_" + str(i)
            logging.debug("Session alexa: " + alexa_page)
        else:
            alexa = False 
            #select page to access 
            os_node = get_node_random(onion_services)
            print("===== ONION: hostname: " + hostname + " ; os_node['node_name']: " +  os_node['node_name'] + " ; os_node['onion_page']: " + os_node['onion_page'] +  " ; i:  " + str(i))
            session_sample_name = hostname + "_" + os_node['node_name'] + "_" + os_node['onion_page'] + "_session_" + str(i)
            logging.debug("Session onion: " + os_node['node_name'])

        
        #start new capture for full session live cycle
        start_traffic_capture(client_cap_folder, session_sample_name)

        #start browser and Tor
        logging.debug("Starting new Tor system process")
        os.system("/usr/bin/tor -f /etc/tor/torrc &")
        time.sleep(1)
        logging.debug("Starting new Tor Browser Selenium")
        driver = TorBrowserDriver(pathToTorBrowser, tbb_logfile_path="headless_tor_browser.log")

        #Wait a few seconds for selenium spurious traffic 
        time.sleep(time_to_wait_after_tor_relaunch)

        #perform browsing session 
        if alexa:
            place_request_via_tor_alexa(alexa_page, request_iterations, session_sample_name)
            print("**** place request to alexa_page: " + alexa_page)
        else:
            place_request_via_tor(os_node, request_iterations, session_sample_name)
            print("**** place request to tor OS: " + str(os_node))

        # os.system('sudo lsof -i -P -n > '+client_cap_folder+session_sample_name+'_connections_info')

        print("AFTER lsof")
        #stop Tor Browser and Tor process
        driver.quit()
        print("AFTER driver.quit()")
        os.system('sudo pkill -15 -f /usr/bin/tor')
        os.system('sudo pkill -15 -f /etc/tor/torrc')
        print("after pkill")
        stop_traffic_capture()
        print("AFTER stop_traffic_capture()")

        #wait to complete a full elapsed minute to proceed to next session
        #TODO
        while time.time() - session_start_time < 60:
            time.sleep(5)

    logging.debug("Total time: " + str(time.time() - startTime))

    #stop virtual display for Tor Browser
    stop_xvfb(xvfb_display)
    print("AFTER stop_xvfb")
    
    job_coordinator_ip = retrieve_coordinator_IP()
    signal_termination(job_coordinator_ip)

    print("AFTER signal_termination")

    #wait for 25 seconds to be killed by job terminator
    for i in range(5):
        time.sleep(5)