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
from tbselenium.tbdriver import FirefoxDriver
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.proxy import Proxy, ProxyType
from tbselenium.utils import start_xvfb, stop_xvfb
from bs4 import BeautifulSoup


#logging.disable(logging.DEBUG)
#logging.basicConfig(filename = 'file.log',
#                    level = logging.DEBUG,
#                    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s')



    cmd = f'tcpdump -i {NETWORK_INTERFACE} -s 66 -W 1 -w {pcap_filename(capture_folder, sample_name)} \'(port not 22) and not (src 127.0.0.1 and dst 127.0.0.1)\' '

    # cmd = cd + ' && tcpdump -i ' + NETWORK_INTERFACE + ' -s 66 -W 1 port not 22 -w - | (gzip -9 -c > ' + capture_folder + sample_name + '_client.pcap.gz & )'
    #cmd = 'tcpdump -s 66 -W 1 -w ' + capture_folder + sample_name + '_client.pcap port not 22'
    #May configure -s96 as an option to gather packet to 96 B snaplen
    #sub.Popen(cmd, shell=True)
    os.system(f'docker exec -u 0 -d tor_client{client_id} sh -c "{cd + cmd}"')
    logging.debug("---> AFTER starting capture ...")
    return cmd


def stop_traffic_capture():
    os.system(f'docker exec -u 0 tor_client{client_id} sh -c "sleep 1s; pkill tcpdump"')
    # if cmd == '':
    #     os.system('docker exec -u 0 tor_client' + str(client_id) + ' sh -c \"pkill tcpdump')
    #     #logging.debug('pkill -15 -f tcpdump')
    # else:
    #     os.system('docker exec -u 0 tor_client' + str(client_id) + ' sh -c \"pkill "'+cmd+'"')
    #     #logging.debug('pkill -15 -f "'+cmd+'"')


def parse_inventory(nOnions):
    inventory_file_name = 'inventory.cfg'
    data_loader = DataLoader()
    inventory = InventoryManager(loader = data_loader,
                             sources=[inventory_file_name])

    inventory.parse_sources()
    
    os_nodes = []
    for host in inventory.get_hosts():
        # Ensures coordinator is not added
        if('os-' in host.vars["node_name"]):
            for i in range(nOnions):
                tmp = {}
                tmp["onion_idx"] = i + 1
                tmp["node_name"] = host.vars["node_name"]
                tmp["ansible_host"] = host.vars["ansible_host"]
                tmp["onion_page"] = host.vars["onion_page{}".format(i+1)]
                tmp["onion_address"] = host.vars["onion_address{}".format(i+1)]
                tmp["onion_popularity"] = host.vars["onion_popularity{}".format(i+1)]
                os_nodes.append(tmp)

    return os_nodes


# This can be executed offline without Tor
def get_website_possible_urls(url):
    # https://www.geeksforgeeks.org/extract-all-the-urls-from-the-webpage-using-python/

    reqs = ""
    driver = None
    if USE_TOR_BROWSER:
        driver = start_selenium_driver(driver)
        driver.get(url)
        reqs = driver.find_element_by("html").get_attribute("innerHTML")
        driver = close_selenium_driver(driver)
        logging.error("text {}".format(reqs))
    else:
        try:
            reqs = requests.get(url).text
        except Exception as ex:
            logging.error("Url {} was not reachable".format(url))
            return []
    soup = BeautifulSoup(reqs, 'html.parser')
    
    website_urls = [''] # There's always the possibility of going back to the frontpage
    # get all <a> anchor tags
    for link in soup.find_all('a'):
        # exclude external links to open web or other OSes
        path = link.get('href')

        # For instance, chinese websites may not have the word 'href', so path would be None
        if path:
            if '.onion' not in path and 'http' not in path and not(path.startswith('//')) \
                    and path != '/' and 'javascript:' not in path:
                website_urls.append(path)
    
    # remove duplicate paths
    return list(dict.fromkeys(website_urls))


def get_node_random(nodes, popularities):
    # sum_pop = sum(popularities) # already done below
    # popularities = [p / sum_pop for p in popularities]
    # logging.debug("nodes: {}".format(str(nodes)))
    # logging.debug("popularities: {}".format(str(popularities)))
    index = np.random.choice(len(nodes), 1, p=popularities)[0]
    logging.debug("nodes[{}]: {}".format(index, nodes[index]))
    return nodes[index]


def parse_alexa_pages():
    alexa_pages = []
    alexa_pages_file_name = 'alexa_top_50_2022.txt'
    with open(alexa_pages_file_name, 'r') as f:
        for line in f:
            alexa_pages.append(line[:-1])
    return alexa_pages


def parse_tranco_pages():
    tranco_pages = []
    tranco_pages_file_name = 'tranco_top_websites.csv'
    with open(tranco_pages_file_name, 'r') as f:
        for line in f:
            tranco_pages.append(line.split(',')[1][:-1]) # [-1] removes the /n at the end
    return tranco_pages


def get_alexa_page_random(alexa_pages):
    mypageid = random.randint(0, len(alexa_pages)-1)
    logging.debug("alexa_pages[mypageid] {}".format(alexa_pages[mypageid]))
    return alexa_pages[mypageid]

# def docker_run_str():
#     exposed_ports = "-p " + port1() + ":9050 -p " + port2() + ":9051"
#     docker_client_ip = os.popen('docker network inspect clients -f \"{{ range.Containers}}{{.IPv4Address}}{{end}}\"').read().strip()
#     network = "--net clients --ip " + docker_client_ip[:docker_client_ip.rfind(".")] + "." + str(10 + client_id)
#     return "docker run -it --rm " + network + " " + exposed_ports + " -e PASSWORD=emptyPassword --volumes-from target -d --name tor_client" + str(client_id) + " dcastro93/dpss:tor_client:1.5"

def start_selenium_driver(driver):
    if USE_TOR_BROWSER and driver == None:
        logging.debug("Starting new Tor Browser Selenium")
        #### TODO: this is only available within tor_clientX
        client_profile = "./TorBrowserProfile_client"+str(client_id)
        os.popen(f"mkdir -p {client_profile}/preferences/")
        docker_client_network = os.popen('docker inspect -f \"{{ range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}\" tor_client' + str(client_id)).read().strip()
        docker_client_ip = docker_client_network[:docker_client_network.rfind(".")] + "." + str(10 + client_id)
        pref_dict = {
            "network.proxy.type": 1,
            "network.proxy.socks": docker_client_ip,
            "network.proxy.socks_port": 9050
        }
        # logging.debug(f"preferences: {pref_dict}")
        # tb_binary = os.path.join(pathToTorBrowser, 'Browser/firefox')
        # tb_profile = os.path.join(pathToTorBrowser, 'Browser/TorBrowser/Data/Browser/profile.default')
        # binary = FirefoxBinary(tb_binary)
        # profile = FirefoxProfile(tb_profile)
        options = FirefoxOptions()
        options.add_argument('-proxy')
        options.add_argument({
                'http': f'socks5h://{docker_client_ip}:9050',
                'https': f'socks5h://{docker_client_ip}:9050',
                'connection_timeout': 10
            })
        # options = {
        #     'proxy': {
        #         'http': f'socks5h://{docker_client_ip}:9050',
        #         'https': f'socks5h://{docker_client_ip}:9050',
        #         'connection_timeout': 10
        #     }
        # }
        logging.debug(f"options: {options}")
        # driver = webdriver.Firefox(firefox_profile=profile,
        #                    firefox_binary=binary,
        #                    options=options)

        driver = TorBrowserDriver(pathToTorBrowser,
                                  tbb_logfile_path="headless_tor_browser.log",
                                  tbb_profile_path=client_profile,
                                  options=options,
                                  pref_dict=pref_dict,
                                  use_custom_profile=True)
    return driver

def close_selenium_driver(driver):
    if driver != None:
        driver.close()
        driver = None

def start_session(client_cap_folder, hostname, os_node, session_sample_name):
    print("**** start_session")
    #start browser and Tor
    logging.debug("Starting new Tor system process")
    # os.system(docker_run_str())
    #os.system("docker run -it --rm -p 9050:9050 -p 9051:9051 -e PASSWORD=emptyPassword --volumes-from target -d --name tor_client dcastro93/dpss:tor_client")
    #os.system("docker run -it --rm -p 9050:9050 -p 9051:9051 -e PASSWORD=emptyPassword -d --name tor_client andreas4all/tor-client:latest")
    #os.system("docker run -it --rm  -e PASSWORD=emptyPassword --net container:target -d --name tor_client andreas4all/tor-client:latest")
    logging.debug("After running client container")

    #Wait a few seconds for selenium spurious traffic 
    time.sleep(time_to_wait_after_tor_relaunch)

    #Instruct pcap to start on the onion service's end
    onion_cap_folder = client_folder() + hostname + "-" + os_node['node_name'] + "/"
    RESTCall(os_node['ansible_host'], "startTrafficCapture", onion_cap_folder + "," + str(os_node['onion_idx']) + "," + session_sample_name)

    driver = None
    driver = start_selenium_driver(driver)
    
    #start new capture for full session live cycle
    start_traffic_capture(client_cap_folder, session_sample_name)
    
    return driver


def start_session_alexa(client_cap_folder, session_sample_name):
    print("**** start_session_alexa")
    #start browser and Tor
    logging.debug("Starting new Tor system process")
    # os.system(docker_run_str())
    #os.system("docker run -it --rm -p 9050:9050 -p 9051:9051 -e PASSWORD=emptyPassword --volumes-from target -d --name tor_client dcastro93/dpss:tor_client")
    #os.system("docker run -it --rm -p 9050:9050 -p 9051:9051 -e PASSWORD=emptyPassword -d --name tor_client andreas4all/tor-client:latest")
    #os.system("docker run -it --rm  -e PASSWORD=emptyPassword --net container:target -d --name tor_client andreas4all/tor-client:latest")
    #time.sleep(1)
    #start new capture for full session live cycle
    start_traffic_capture(client_cap_folder, session_sample_name)

    driver = None
    driver = start_selenium_driver(driver)

    #Wait a few seconds for selenium spurious traffic 
    time.sleep(time_to_wait_after_tor_relaunch)

    return driver


def end_session(driver, hostname, os_node):
    print("**** end_session")
    # os.system('lsof -i -P -n > '+client_cap_folder+session_sample_name+'_connections_info')

    #stop Tor Browser and Tor process
    # os.system('docker container stop tor_client' + str(client_id) + ' || true')
    # os.system('docker container rm tor_client' + str(client_id) + ' || true')
    stop_traffic_capture()

    onion_cap_folder = client_folder() + hostname + "-" + os_node['node_name'] + "/"
    RESTCall(os_node['ansible_host'], "stopTrafficCapture", onion_cap_folder + "," + str(os_node['onion_idx']) + "," + session_sample_name)
    
    driver = close_selenium_driver(driver)


def end_session_alexa(driver):
    print("**** end_session_alexa")
    # os.system('lsof -i -P -n > '+client_cap_folder+session_sample_name+'_connections_info')

    # os.system('docker container stop tor_client' + str(client_id) + ' || true')
    # os.system('docker container rm tor_client' + str(client_id) + ' || true')
    stop_traffic_capture()
    driver = close_selenium_driver(driver)


actions = {'new_site': 0.2,
            'navigate': 0.8}

if __name__ == '__main__':
    if not (sys.argv[1].isdigit()):
        logging.error("nOnions is not valid!")
        exit()
    if not (sys.argv[2].isdigit()):
        logging.error("Number of requests is not valid!")
        exit()
    if not (sys.argv[3].isdigit()):
        logging.error("Client ID is not valid!")
        exit()

    driver = None
    nOnions = int(sys.argv[1])
    request_iterations = int(sys.argv[2])

    client_id = int(sys.argv[3])
    logging.basicConfig(filename = 'pcap-folder/client' + str(client_id) + '/file.log',level=logging.DEBUG,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

    onion_services = parse_inventory(nOnions)
    #alexa_pages = parse_alexa_pages()
    alexa_pages = parse_tranco_pages()
    alexa_pages_reachable = []
    hostname = socket.gethostname()

    #logging.debug("\n--- INITIAL alexa_pages: {}".format(alexa_pages))

    # This should be done before starting pcaps, otherwise this traffic will 
    # also be captured
    possible_paths = {}
    for node in onion_services:
        logging.debug("ansible node: {}".format(str(node)))
        possible_paths[node['onion_address']] = get_website_possible_urls('http://' + node['ansible_host'] + ':{}/hidden-service-docker-image/web-{}/www/onion_pages/'.format(HTTP_PORT, node['onion_idx']) + node['onion_page'])
        #if len(possible_paths[node['onion_address']]) < MIN_PATHS:
        #    logging.error("Removed OS {} for having less than {} paths".format(node['onion_address'], MIN_PATHS))
        #    exit()
    logging.debug("Retrieved possible paths for {} different OSes!".format(len(possible_paths)))

    possible_paths_alexa = {}
    logging.debug("Testing {} alexa_pages".format(len(alexa_pages)))
    limit_pages = 50
    count_pages = 0
    amount_of_pages = len(alexa_pages)

    for page in alexa_pages[:min(limit_pages, amount_of_pages)]: # collect only the first 50 pages
        count_pages += 1
        paths = get_website_possible_urls('http://' + page)
        if len(paths) < MIN_PATHS:
            logging.info("page{} --- Remove alexa page: {} for having less than {} paths".format(count_pages, page, MIN_PATHS))
        else:
            logging.info("page{} --- Add alexa page: {}".format(count_pages, page))
            alexa_pages_reachable.append(page)
            possible_paths_alexa[page] = paths
    if amount_of_pages > limit_pages: # pick an extra 50 pages at random
        sel_pages = []
        for page in range(limit_pages):
            page = alexa_pages[random.randrange(limit_pages, amount_of_pages)]
            if page in sel_pages:
                continue
            sel_pages += [page]
            count_pages += 1
            paths = get_website_possible_urls('http://' + page)
            if len(paths) < MIN_PATHS:
                logging.info("page{} --- Remove alexa page: {} for having less than {} paths".format(count_pages, page, MIN_PATHS))
            else:
                logging.info("page{} --- Add alexa page: {}".format(count_pages, page))
                alexa_pages_reachable.append(page)
                possible_paths_alexa[page] = paths

    logging.debug("Retrieved possible paths for {} different clearweb websites!".format(len(possible_paths_alexa)))
    
    logging.debug("\n--- nb alexa_pages_reachable: {}".format(len(alexa_pages_reachable)))
    logging.debug("\n--- nb possible_paths_alexa.keys(): {}".format(len(possible_paths_alexa.keys())))

    oses_addresses = []
    popularities = []
    for node in onion_services:
        oses_addresses.append(node['onion_address'])
        popularities.append(node['onion_popularity'])
    pop_sum = sum(popularities)
    popularities = [p / pop_sum for p in popularities]

    # Parameter taken from Oustralopithecus paper
    SHAPE = 0.75
    SCALE = 30
    stay_times = []
    while 1:
        try:
            stay_times  = np.random.weibull(a=SHAPE, size=request_iterations) * SCALE
        except Exception as e:
            logging.debug(f"Error np.random.weibull {str(e)}")
            continue
        break

    #Create directory for holding pcaps
    client_cap_folder = client_folder() + "captures-" + hostname + "/"
    logging.debug(f"make folder {client_cap_folder}")
    os.system("mkdir -p %s"%client_cap_folder)

    #start virtual display for Tor browser
    #xvfb_display = start_xvfb()

    #ensure Tor is not running
    # os.system('docker container stop tor_client' + str(client_id) + ' || true')
    # os.system('docker container rm tor_client' + str(client_id) + ' || true')
    

    session_id = 0
    request_id_per_session = 0
    # First request is always a new session
    # go to alexa or onion?
    alexa = False
    alexa_page = ''
    os_node = None
    my_number = random.randint(0, 100)
    logging.debug("my_number {}".format(my_number))
    if my_number < alexa_probability*100:
        alexa = True
        #select alexa page randonmly
        logging.debug("ALEXAA!")
        alexa_page = get_alexa_page_random(alexa_pages_reachable)
        logging.info("===== ALEXA: hostname: " + hostname + " ; alexa_page: " +  alexa_page + " ; request_id: 0")
        session_sample_name = hostname + "_alexa_" + alexa_page + "_session_" + str(session_id)
    else:
        alexa = False 
        logging.debug("NOT ALEXAA!")
        #select page to access 
        os_node = get_node_random(onion_services, popularities)
        logging.info("===== ONION: hostname: " + hostname + " ; os_node['node_name']: " + os_node['node_name'] + " ; os_node['onion_page']: " + os_node['onion_page'] + " ; i: 0")
        session_sample_name = hostname + "_" + os_node['node_name'] + "_" + os_node['onion_page'] + "_session_" + str(session_id)
    
    request_sample_name = session_sample_name + '_request_' + str(request_id_per_session)
    logging.debug("request_sample_name:" + request_sample_name)
    #perform browsing session 
    if alexa:
        driver = start_session_alexa(client_cap_folder, session_sample_name)
        place_request_via_tor_alexa(driver, alexa_page, request_sample_name)
        logging.info("**** place request to alexa_page: {}".format(alexa_page))
    else:
        driver = start_session(client_cap_folder, hostname, os_node, session_sample_name)
        place_request_via_tor(driver, os_node, request_sample_name, "index.html")
        logging.info("**** place request to tor OS: {}".format(os_node))

    # Webpage stay time
    stay_time = stay_times[0]
    logging.info("--- Stay time: {}".format(stay_time))
    time.sleep(stay_time) # in seconds
    
    #Restart browser and Tor for each browsing session
    #Start new capture before restarting Tor and Broswer
    for request_id in range(1, request_iterations):
        logging.info("========== REQUEST ITERATION ========== {}".format(request_id))
        logging.info("Request {} out of {}".format(request_id, request_iterations))
        next_action = np.random.choice(len(actions), 1, p=list(actions.values()))
        logging.info("next_action: {}".format(next_action))

        # New session, select next website to visit
        if next_action == 0:
            session_id += 1
            request_id_per_session = 0

            # end previous session
            if alexa == True:
                logging.info("BEFORE end_session_alexa")
                end_session_alexa(driver)
                logging.info("AFTER end_session_alexa")
            else:
                logging.info("BEFORE end_session")
                end_session(driver, hostname, os_node)
                logging.info("AFTER end_session")

            #go to alexa or onion?
            alexa = False
            alexa_page = ''
            my_number = random.randint(0, 100)
            logging.info("my_number")
            if my_number < alexa_probability*100:
                alexa = True
                #select alexa page randonmly
                logging.info("BEFORE get_alexa_page_random")
                alexa_page = get_alexa_page_random(alexa_pages_reachable)
                logging.info("===== ALEXA: hostname: " + hostname + " ; alexa_page: " +  alexa_page + " ; session_id: " + str(session_id) + " ; request_id: " + str(request_id)  + " ; request_id_per_session: " + str(request_id_per_session))
                session_sample_name = hostname + "_alexa_" + alexa_page + "_session_" + str(session_id)
                
            else:
                alexa = False 
                #select page to access 
                logging.info("BEFORE get_node_random")
                os_node = get_node_random(onion_services, popularities)
                logging.info("===== ONION: hostname: " + hostname + " ; os_node['node_name']: " +  os_node['node_name'] + " ; os_node['onion_page']: " + os_node['onion_page'] + " ; request_id: " + str(request_id)  + " ; request_id_per_session: " + str(request_id_per_session))
                session_sample_name = hostname + "_" + os_node['node_name'] + "_" + os_node['onion_page'] + "_session_" + str(session_id)

            request_sample_name = session_sample_name + "_request_" + str(request_id_per_session)
            #perform browsing session 
            if alexa:
                logging.info("BEFORE start_session_alexa")
                driver = start_session_alexa(client_cap_folder, session_sample_name)
                logging.info("AFTER start_session_alexa")
                place_request_via_tor_alexa(driver, alexa_page, request_sample_name)
                logging.info("**** place request to alexa_page: " + alexa_page)
            else:
                logging.info("BEFORE start_session")
                driver = start_session(client_cap_folder, hostname, os_node, session_sample_name)
                logging.info("AFTER start_session")
                place_request_via_tor(driver, os_node, request_sample_name, "index.html")
                logging.info("**** place request to tor OS: {}".format(os_node))

        # Get next page to visit within the website
        elif next_action == 1:
            request_id_per_session += 1
            request_sample_name = session_sample_name + "_request_" + str(request_id_per_session)
            if alexa == True:
                # get next page to visit within the website
                logging.debug("--- possible_paths_alexa: {}".format(possible_paths_alexa[alexa_page]))
                navigate_to = alexa_page + np.random.choice(possible_paths_alexa[alexa_page])
                logging.info("BEFORE place_request_via_tor_alexa")
                place_request_via_tor_alexa(driver, navigate_to, request_sample_name)
                logging.info("**** navigated to : {}, session: {}, request_id: {}, request_id_per_session: {}".format(navigate_to, session_id, request_id, request_id_per_session))
            else:
                # get next page to visit within the website
                #logging.debug("--- possible_paths[os_node] {}".format(possible_paths[os_node['onion_address']]))
                navigate_to = np.random.choice(possible_paths[os_node['onion_address']])
                logging.info("BEFORE place_request_via_tor")
                place_request_via_tor(driver, os_node, request_sample_name, navigate_to)
                logging.info("**** Tor navigated to : {}, session: {}, request_id: {}, request_id_per_session: {}".format(navigate_to, session_id, request_id, request_id_per_session))

        
        logging.info("BEFORE STAY TIME")
        # Webpage stay time between each action
        stay_time = stay_times[request_id]
        logging.info("--- Stay time: {}".format(stay_time))
        time.sleep(stay_time) # in seconds

        

        # Finish previous session at the end of the requests
        if alexa == True:
            logging.info(f"end_session_alexa: {request_id}")
            end_session_alexa(driver)
        else:
            logging.info(f"end_session: {request_id}")
            end_session(driver, hostname, os_node)


    #stop virtual display for Tor Browser
    #stop_xvfb(xvfb_display)
    
    job_coordinator_ip = retrieve_coordinator_IP()
    logging.info("job_coordinator_ip: {}".format(job_coordinator_ip))
    signal_termination(job_coordinator_ip)

    logging.info("FINISHED!!!!")



    #wait for 25 seconds to be killed by job terminator
    # for i in range(5):
    #     time.sleep(5)