import os, sys
import subprocess as sub
import time
import socket
import requests
import random
import numpy as np
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from tbselenium.tbdriver import TorBrowserDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from tbselenium.utils import start_xvfb, stop_xvfb
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
import signal
import traceback
import logging

# disable default logging for previously imported modules
import logging.config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})


HTTP_PORT = 8001
REST_PORT = 5005

home_folder = "/app/"
pathToTorBrowser = '/tor-browser'
driver = None # selenium browser

#NETWORK_INTERFACE = "eth0"
NETWORK_INTERFACE = "any"

MAX_CONNECTION_TIME = 60 * 5 # seconds
MAX_CURL_TIME = 60 * 1 # seconds

global MAX_SESSION_TIME
MAX_SESSION_TIME = 60 * 100
global MAX_STAY_TIME
MAX_STAY_TIME = 60 * 10

# set this to true to attack the OSes, else behaves as client
global IS_ATTACKER
global CURRENT_OS_IDX
IS_ATTACKER = False
CURRENT_OS_IDX = 0

#seconds
time_to_wait_after_tor_relaunch = 10 

#keep track of session time each session should take a full minute more or less
session_start_time = 0 

alexa_probability = 0.5

MIN_PATHS = 3

tcp_procs = {}


def client_folder():
    return home_folder + "pcap-folder/client" + str(client_id) + "/"


def handle_sigchld(signum, frame):
    # Reap zombie processes (sh <defunct>)
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
        except OSError:
            break
        if pid == 0:
            break
        print(f"Child process {pid} exited with status {status}")

# Register signal handler for SIGCHLD
signal.signal(signal.SIGCHLD, handle_sigchld)


def is_subdomain(url):
    try:
        result = urlparse(url)
        domain_parts = result.netloc.split('.')
        return len(domain_parts) > 2 and domain_parts[-2] != 'www'
    except ValueError:
        return False
    
def clean_url(url):
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, parsed_url.hostname, parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))
    

def well_formed_url(url):
    new_url = url

    if 'http://' in new_url:
        new_url = new_url.split('http://')[-1]
    if 'https://' in new_url:
        new_url = new_url.split('https://')[-1]
    if new_url.startswith('www.'):
        new_url = new_url.split('www.')[-1]

    if is_subdomain(url):
        new_url = "http://{}".format(new_url)
    else:
        new_url = "http://www.{}".format(new_url)

    #logging.debug("++++ WELL FORMED URL: {}".format(clean_url(new_url)))
    return clean_url(new_url)


def get_base_url(base_url):
    if '.onion' in base_url:
        if '/index.html' in base_url:
            orig_base_url = base_url.split('/index.html')[0]
        else:
            orig_base_url = base_url
        #logging.debug("---- orig_base_url.split('/'): {}".format(orig_base_url.split('/')))
        base_url_splits =orig_base_url.split('/')
        #orig_base_url = base_url_splits[-2]
        orig_base_url = base_url_splits[2]+'/'+base_url_splits[3]+'/'+base_url_splits[-1]
        #logging.debug("++++ ONION BASE URL: {}".format(orig_base_url))
    else:
        orig_base_url = base_url
        parsed_url = urlparse(orig_base_url)
        orig_base_url = parsed_url.netloc
        if orig_base_url.startswith('www.') and orig_base_url.count('.') > 1:
            orig_base_url = orig_base_url.split('www.')[-1]
       # logging.debug("++++ CLEARNET BASE URL: {}".format(orig_base_url))
    
    return clean_url(orig_base_url)
    

def filter_urls(base_url, url, tmp_links, tmp_hrefs):
    links_to_add = []
    hrefs_to_add = []
    #logging.debug("----> base_url: {}".format(base_url))
    orig_base_url = get_base_url(base_url)
    #logging.debug("---- orig_base_url AFTER: {}".format(orig_base_url))
    #logging.debug("----> tmp_hrefs: {}".format(tmp_hrefs))
    for i in range(len(tmp_hrefs)):
        # skip visits to outside websites
        if orig_base_url not in tmp_hrefs[i]:
            if "http" in tmp_hrefs[i]:
                continue
            if ".onion" in tmp_hrefs[i]:
                continue
            if "javascript:" in tmp_hrefs[i]:
                continue
            if tmp_hrefs[i].startswith('//'):
                continue
        #else:
        #    logging.debug("---- these are still added: {}".format(tmp_hrefs[i]))
        
        #logging.debug(f"tmp_links[i] {tmp_links[i]}")
        if "http" not in tmp_hrefs[i]:
            #tmp_hrefs[i] = url + "/" + href
            #logging.debug("-- url: {}".format(url))
            #logging.debug("--- tmp_hrefs[i]: {}".format(tmp_hrefs[i]))
            if url.endswith('/') or tmp_hrefs[i].startswith('/'):
                tmp_hrefs[i] = url + tmp_hrefs[i]
            else:
                tmp_hrefs[i] = url + '/' + tmp_hrefs[i]
            #logging.debug("---- new href: {}".format(tmp_hrefs[i]))

        # It's ok to have repeats, then their probability is greater, which is realistic
        #if tmp_hrefs[i] in hrefs:
        #    continue

        tmp_hrefs[i].rstrip().rstrip("/")
        
        links_to_add.append(tmp_links[i])
        hrefs_to_add.append(tmp_hrefs[i])
        #logging.debug("---- ADDED {}".format(tmp_hrefs[i]))

    return links_to_add, hrefs_to_add


def log_failed_request(request_sample_name):
    original_stdout = sys.stdout # Save a reference to the original standard output
    try:
        logging.debug(f"Logging failed request: {request_sample_name}")
        with open(client_folder() + 'failed_requests.log', 'a') as f:
            sys.stdout = f # Change the standard output to the file we created.
            print(request_sample_name)
            sys.stdout = original_stdout # Reset the standard output to its original value
    except Exception as e:
        logging.error(f"FAILED log_failed_request: {e}")
        logging.error(traceback.format_exc())


class BrowserRequestException(Exception):
    "Request failed!"
    pass


class FirstRequestTimeoutException(Exception):
    "First request in session timed out! Website might not be available!"
    pass


class FailedHTTPException(Exception):
    "Cannot contact onion services through HTTP to start and stop captures!"
    pass


class BrowserHandler:
    driver: TorBrowserDriver

    def __init__(self):
        self.links = []
        self.hrefs = []
        self.driver = start_selenium_driver(None)
        self.base_url = None
        self.current_url = None

    def go_to(self, url: str):
        logging.debug(f"**** selenium go to {url}")
        html = ""
        self.base_url = url
        try:
            if None == self.driver:
                self.driver = start_selenium_driver(self.driver)
            self.driver.get(url)
<<<<<<< HEAD

=======
>>>>>>> 5ced9b9768c2e0cf67dac428a4a4c61602503427
            ls = self.driver.find_elements(By.TAG_NAME, "a")
            tmp_links = [l for l in ls if (l is not None and l.get_attribute('href') is not None)]
            tmp_hrefs = [l.get_attribute('href') for l in tmp_links]
            #logging.info(f"tmp_hrefs BEFORE filter_urls: ({tmp_hrefs})")
            self.links, self.hrefs = filter_urls(self.base_url, url, tmp_links, tmp_hrefs)
            # add landing page
            self.hrefs.append(url)
            #logging.debug("---- self.hrefs: {}".format(self.hrefs))
            #logging.info(f"self.hrefs AFTER GO_TO: ({self.hrefs})")
            html = self.driver.page_source
            self.current_url = self.driver.current_url
        except TimeoutError as e:
            logging.error(f"FAILED go_to: First request timed out! {e}")
            logging.error(traceback.format_exc())
            raise FirstRequestTimeoutException
        except Exception as e:
            logging.error(f"FAILED go_to: {e}")
            logging.error(traceback.format_exc())
            # TODO: Should we actually make a get to the base_url?
            self.current_url = self.base_url
            raise BrowserRequestException
        #finally:
        #logging.debug(f"**** AFTER go_to")
        return html
    
    def random_access(self):
        href = ""
        url = ""
        try:
            logging.info(f"random_access: ({self.driver.current_url})")
            url = self.current_url

            for i in range(2): # if there are no links there may be some error loading the page
                logging.debug(f">>>>> BEFORE self.driver.find_elements")
                # Does not issue a new HTTP request, only uses the preivously gathered HTML page
                ls = self.driver.find_elements(By.TAG_NAME, "a")
                logging.debug(f">>>>> AFTER self.driver.find_elements")
                tmp_links = [l for l in ls if (l is not None and l.get_attribute('href') is not None)]
                tmp_hrefs = [l.get_attribute('href') for l in tmp_links]
                #logging.debug(f"tmp_links {tmp_links}")
                #logging.debug("---- self.hrefs BEFORE: {}".format(self.hrefs))
                #logging.debug("---- tmp_hrefs BEFORE: {}".format(tmp_hrefs))
                logging.debug(f">>>>> BEFORE filter_urls")
                links_to_add, hrefs_to_add = filter_urls(self.base_url, url, tmp_links, tmp_hrefs)
                logging.debug(f">>>>> AFTER filter_urls")
                    
                #logging.debug(f"tmp_links[i] after 2 {tmp_links[i]}")
                #logging.debug("---- hrefs_to_add AFTER: {}".format(hrefs_to_add))
                self.links.extend(links_to_add) # So that we keep track of the visitable links on other pages within the same site
                #self.hrefs.extend([link.get_attribute('href') for link in tmp_links])
                self.hrefs.extend(hrefs_to_add)
                if len(self.links) > 0:
                    break
                else:
                    # some error loading the current url? go to base
                    self.driver.get(self.base_url)
                    time.sleep(1)
                    self.current_url = self.base_url
                    url = self.base_url

            rand_idx = int(np.random.uniform(0, len(self.links)))
            logging.debug(f">>>>> rand_idx")
            #logging.debug(f"**** random_access self.links {self.links}")
            # logging.info(f"click_idx: {rand_idx} links: {self.links}")

            #logging.debug(f"self.links after {self.links}")
            #logging.debug(f"len(self.links) after {len(self.links)}")
            #logging.debug(f"rand_idx after {rand_idx}")

            link = self.links[rand_idx]
            #href = link.get_attribute("href")
            href = self.hrefs[rand_idx]
            #logging.debug(f"href: ({href})")
            previous_page = self.driver.current_url
            #logging.debug(f"self.driver.current_url BEFORE: ({self.driver.current_url})")
            #html = self.go_to(href)
            if IS_ATTACKER:
                self.driver.set_page_load_timeout(10) # attackers are impatient
            else:
                self.driver.set_page_load_timeout(60)
            logging.debug(f">>>>> BEFORE self.driver.get(href)")
            self.driver.get(href)
            logging.debug(f">>>>> AFTER self.driver.get(href)")
            time.sleep(1)
            logging.debug(f">>>>> AFTER time.sleep(1)")
            # logging.debug(f"html: ({html})")
            #logging.debug(f"self.driver.current_url AFTER: ({self.driver.current_url})")
            if previous_page == self.driver.current_url:
                logging.error(f"==== CLICK UNSUCCESSFUL!)")
            # Redirect to external website
            tmp_base_url = get_base_url(self.base_url)
            logging.debug(f">>>>> AFTER get_base_url")
            if tmp_base_url not in self.driver.current_url:
                logging.debug(f"EXTERNAL REDIRECT: {href} ; self.driver.current_url {self.driver.current_url} ; tmp_base_url {tmp_base_url}")
                self.links.remove(link)
                self.hrefs.remove(href)
                self.current_url = href
            else:
                self.current_url = self.driver.current_url
        except Exception as e:
            logging.error(f"FAILED random_access: {e}")
            logging.error(traceback.format_exc())
            #self.links.remove(link)
            #self.hrefs.remove(href)
            raise BrowserRequestException
        #finally:
        return True
        

    def __del__(self):
        close_selenium_driver(self.driver)

class SessionHandler:
    browser: BrowserHandler
    cap_folder: str
    sample_name: str
    session_capture_cmd: str

    def __init__(self, client_cap_folder, session_sample_name):
        self.cap_folder = client_cap_folder
        self.sample_name = session_sample_name
        logging.info(f"init SessionHandler({client_cap_folder}, {session_sample_name})")
        self.browser = BrowserHandler()

    def start(self, client_id):
        logging.debug("**** start_session")
        #start new capture for full session live cycle
        #self.session_capture_cmd = start_traffic_capture(self.cap_folder, self.sample_name, client_id)
        self.session_capture_cmd = start_traffic_capture(client_id, self.cap_folder, self.sample_name)

    def go_to(self, url, request_sample_name, client_id):
        return self.go_to_internal(url, lambda self,url: self.browser.go_to(url), request_sample_name, client_id)

    def random_access(self, request_sample_name, client_id):
        return self.go_to_internal("", lambda self,url: self.browser.random_access(), request_sample_name, client_id)
    
    # 
    def go_to_internal(self, url, req_fn, request_sample_name, client_id):
        soup = ""
        logging.info(f"SessionHandler.go_to_internal({url}, {request_sample_name})")
        #cmd = start_traffic_capture(self.cap_folder, request_sample_name, client_id)
        cmd = start_traffic_capture(client_id, self.cap_folder, request_sample_name)
        if not IS_ATTACKER:
            time.sleep(0.5)
        try:
            #logging.info("---> URL: {}".format(url))
            req_fn(self, url)
            soup = self.browser.driver.page_source
            logging.info(f"Request to: {url}\nStatus: {soup.find('title')}")
        except FirstRequestTimeoutException:
            raise FirstRequestTimeoutException
        except BrowserRequestException:
            #logging.debug("log_failed_request")
            log_failed_request(request_sample_name)
        except Exception as e:
            logging.error(f"\n---- Request failed...\n{e}")
            logging.error(traceback.format_exc())
        finally:
            if not IS_ATTACKER:
                time.sleep(0.5)
            logging.debug("Stopping traffic capture...")
            #stop_traffic_capture(client_id, cmd)
            stop_traffic_capture(cmd)
        return soup

    def end(self, session_sample_name, client_id):
        logging.debug("**** end_session {}".format(session_sample_name))
        #stop_traffic_capture(client_id, self.session_capture_cmd)
        stop_traffic_capture(self.session_capture_cmd)

    def __del__(self):
        del self.browser
    
class SessionHandlerToOSes(SessionHandler):
    os_nodes: dict
    hostname: str

    def __init__(self, client_cap_folder, session_sample_name, os_nodes, hostname):
        self.os_nodes = os_nodes
        self.hostname = hostname
        logging.info(f"init SessionHandlerToOSes({client_cap_folder}, {session_sample_name}, {hostname})")
        super().__init__(client_cap_folder, session_sample_name)

    def start(self, client_id):
        #Instruct pcap to start on the onion service's end
        logging.info(f"SessionHandlerToOSes.start()")
        RESTCall(self.os_nodes['ansible_host'], "startTrafficCapture", f"{self.cap_folder},{self.os_nodes['onion_idx']},{self.sample_name}")
        super().start(client_id)

    def go_to(self, url, request_sample_name, client_id):
        return self.go_to_OS_internal(url, lambda self,url,reqN: self.go_to(url, reqN, client_id), request_sample_name)
   
    def random_access(self, request_sample_name, client_id):
        return self.go_to_OS_internal("", lambda self,url,reqN: self.random_access(reqN, client_id), request_sample_name)

    def go_to_OS_internal(self, url, req_fn, request_sample_name):
        RESTCall(self.os_nodes['ansible_host'], "startTrafficCapture", f"{self.cap_folder},{self.os_nodes['onion_idx']},{request_sample_name}")
        address = f"http://{self.os_nodes['onion_address']}/onion_pages/{self.os_nodes['onion_page']}/{url}"
        logging.info(f"SessionHandlerToOSes.go_to_OS_internal({url}, {request_sample_name})")
        soup = ""
        try:
            soup = req_fn(super(), address, request_sample_name)
        except Exception as e:
            logging.error(f"SessionHandlerToOSes.go_to_OS_internal: {e}")
            logging.error(traceback.format_exc())
        #finally:
        RESTCall(self.os_nodes['ansible_host'], "stopTrafficCapture", f"{self.cap_folder},{self.os_nodes['onion_idx']},{request_sample_name}")
        return soup

    def end(self, session_sample_name, client_id):
        logging.info(f"SessionHandlerToOSes.end()")
        super().end(session_sample_name, client_id)
        logging.info("==== END SESSION: {}".format(session_sample_name))
        RESTCall(self.os_nodes['ansible_host'], "stopTrafficCapture", f"{self.cap_folder},{self.os_nodes['onion_idx']},{session_sample_name}")


def RESTCall(host, method, args=""):
    url='http://' + host + ':{}/'.format(REST_PORT) + method

    #Ensure that we will not continue through the experiment while
    # we do not properly communicate with onion hosts.
    #Backoff until a max of 16s between repeated requests
    #n_retries = 20
    n_retries = 200
    i = 0
    r = None
    backoff = 1
    while(r is None and i < n_retries):
        try:
            i += 1
            r = requests.post(url, data=args)
            logging.debug("After requests.post():".format(r))
        except requests.exceptions.RequestException as e:
            logging.debug(e)
            logging.debug("Sleeping for backoff time: %ds"%backoff)
            logging.debug("retry number: %d"%i)
            # It can stop here ...
            time.sleep(backoff)
            if(backoff < 16):
                backoff = backoff * 2

    if r is None:
        raise FailedHTTPException


def pcap_filename(capture_folder, sample_name):
    return f"{capture_folder}{sample_name}_client.pcap"

"""
def start_traffic_capture(capture_folder, sample_name, client_id): 
    logging.debug("Starting Traffic Capture - " + capture_folder + sample_name)
    if not os.path.exists(capture_folder):
        os.makedirs(capture_folder)
    cmd = f'tcpdump -i {NETWORK_INTERFACE} -s 66 -W 1 -w {pcap_filename(capture_folder, sample_name)} \'(port not 22) and not (src 127.0.0.1 and dst 127.0.0.1)\' '
    tcp_procs[cmd] = sub.Popen(cmd, shell=True)
    logging.debug(f"---> AFTER {cmd}...")
    return cmd


def stop_traffic_capture(client_id, cmd = None):
    if cmd != None:
        try:
            proc = tcp_procs[cmd]
            pid = proc.pid
            kill_cmd = f'kill --verbose -TERM {pid}'
            sub.call(kill_cmd, shell=True)
            tcp_procs.pop(cmd)

        except Exception as e:
            logging.error("Could not kill process: {}\nException: {}".format(cmd, e))
            logging.error(traceback.format_exc())
    else:
        try:
            os.system(f"pkill tcpdump")
        except Exception as e:
            logging.error("Could not kill all tcpdump processes\nException: {}".format(e))
            logging.error(traceback.format_exc())
"""

"""
def start_traffic_capture(capture_folder, sample_name, client_id): 
    logging.debug("Starting Traffic Capture - " + capture_folder + sample_name)
    if not os.path.exists(capture_folder):
        os.makedirs(capture_folder)
    cmd = f'tcpdump -i {NETWORK_INTERFACE} -s 66 -W 1 -w {pcap_filename(capture_folder, sample_name)} port not 22 '
    #os.system(cmd)
    tcp_procs[cmd] = sub.Popen(cmd, shell=True)
    logging.debug(f"---> AFTER {cmd}...")
    return cmd


def stop_traffic_capture(client_id, cmd = None):
    if cmd != None:
        try:
            proc = tcp_procs[cmd]
            pid = proc.pid
            #kill_cmd = f'kill --verbose -TERM {pid}'
            kill_cmd = f'kill -TERM {pid}'
            sub.call(kill_cmd, shell=True)
            tcp_procs.pop(cmd)
            #os.system(f'pkill -f \"{cmd}\"')

        except Exception as e:
            logging.error("Could not kill process: {}\nException: {}".format(cmd, e))
            logging.error(traceback.format_exc())
    else:
        try:
            os.system(f"pkill tcpdump")
        except Exception as e:
            logging.error("Could not kill all tcpdump processes\nException: {}".format(e))
            logging.error(traceback.format_exc())

    #logging.debug("---> AFTER stopping capture ...")
"""


def start_traffic_capture(client_id, capture_folder, sample_name): 
    logging.debug("Starting Traffic Capture - " + capture_folder + sample_name)
    if not os.path.exists(capture_folder):
        os.makedirs(capture_folder)
    cmd = f'docker run --rm --net=container:tor_client{client_id} --name {sample_name} --volumes-from target kaazing/tcpdump -i any -s 66 -W 1 -w {pcap_filename(capture_folder, sample_name)} \'(port not 22) and not (src 127.0.0.1 and dst 127.0.0.1)\' '
    logging.debug(cmd)
    try:
        sub.Popen(cmd, shell=True)
    except Exception as e:
        logging.debug("Could not start capture {}\nException: {}".format(sample_name, e))
    
    return sample_name


def stop_traffic_capture(sample_name):
    try:
        p = sub.Popen(f'docker stop {sample_name}', shell=True)
        logging.debug(f'docker stop {sample_name}')
        p.wait()
        logging.debug('after wait')

    except Exception as e:
        logging.debug("Could not kill process: {}\nException: {}".format(sample_name, e))



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

    logging.info(f"get_website_possible_urls({url}) starting selenium")
    i = 0
    nb_retries = 3

    website_urls = [''] # There's always the possibility of going back to the frontpage
    links = []
    new_url = url
    while i < nb_retries:
        if ".onion" in url:
            try:
                b = BrowserHandler()
                soup = BeautifulSoup(b.go_to(url), "html.parser")
                del b
            except Exception as ex:
                logging.error(f"Url {url} was not reachable")
                logging.error(traceback.format_exc())
                #return []
                i += 1
                continue
        else:
            try:
                response = requests.get(url, timeout=(3, 5))
                # Detect whether url gets redirected so that we can determine the right base url
                html = response.text
                if response.history:
                    new_url = response.url
                    logging.debug(f"Url {url} was redirected to {new_url}")
                soup = BeautifulSoup(html, "html.parser")
            except Exception as ex:
                logging.error(f"Url {url} was not reachable")
                logging.error(traceback.format_exc())
                #return []
                i += 1
                continue
        
        # get all <a> anchor tags
        links = soup.find_all('a')
        logging.info(f"page {url} has {len(links)} links")
        i += 1
        if len(links) != 0:
            break
        # no links? try again
        else:
            logging.info(f"got no links on attemp {i}: trying again...")
    
    try:
        #logging.info(f"!!!!! len(links) {len(links)}")
        tmp_links = [l for l in links if (l is not None and l.get('href') is not None)]
        #logging.info(f"!!!!! len(tmp_links) {len(tmp_links)}")
        tmp_hrefs = [l.get('href') for l in tmp_links]
        #logging.info(f"!!!!! tmp_hrefs {tmp_hrefs}")
        #logging.info(f"!!!!! new_url {new_url}")
        #logging.info(f"!!!!! url {url}")
        _, website_urls = filter_urls(new_url, url, tmp_links, tmp_hrefs)
        #for link in links:
            # exclude external links to open web or other OSes
        #   path = link.get('href')

            # For instance, chinese websites may not have the word 'href', so path would be None
        #    if path:
        #        if '.onion' not in path and 'http' not in path and not(path.startswith('//')) \
        #                and path != '/' and 'javascript:' not in path:
        #            website_urls.append(path)
    except Exception as e:
        logging.error(f"Could not get all landing page links for page {new_url}\nError: {e}")
        logging.error(traceback.format_exc())
    
    new_url = get_base_url(new_url)

    # remove duplicate paths
    #return list(dict.fromkeys(website_urls)), new_url
    return website_urls, new_url

def sleep_stay_time(time_s):
    logging.info("--- Stay time: {}".format(time_s))
    time.sleep(min(time_s, MAX_STAY_TIME)) # in seconds

def get_node_random(nodes, popularities):
    # sum_pop = sum(popularities) # already done below
    # popularities = [p / sum_pop for p in popularities]
    # logging.debug("nodes: {}".format(str(nodes)))
    # logging.debug("popularities: {}".format(str(popularities)))
    global CURRENT_OS_IDX
    if IS_ATTACKER:
        index = CURRENT_OS_IDX
        CURRENT_OS_IDX = (CURRENT_OS_IDX + 1) % len(nodes)
    else:
        index = np.random.choice(len(nodes), 1, p=popularities)[0]
    logging.debug("nodes[{}]: {}".format(index, nodes[index]))
    return nodes[index]


def parse_tranco_pages(start_page, interleave_factor):
    tranco_pages = []
    tranco_pages_file_name = 'tranco_top_websites.csv'
    with open(tranco_pages_file_name, 'r') as f:
        lines = f.readlines()
        for page_index in range(start_page, len(lines), interleave_factor):
            page = lines[page_index].split(',')[1][:-1]  # [-1] removes the /n at the end
            if page.startswith('www.') and page.count('.') > 1:
                page = page.split('www.')[-1]
                #logging.debug("==== split: {}".format(page.split('www.')))
                #logging.debug("==== PAGE AFTER: {}\n".format(page))
            # TODO: Check why clients halt when visiting apple. Memory problem?
            if 'apple' not in page:
                tranco_pages.append(page)
    return tranco_pages


def get_alexa_page_random(alexa_pages):
    mypageid = random.randint(0, len(alexa_pages)-1)
    #logging.debug("alexa_pages[mypageid] {}".format(alexa_pages[mypageid]))
    return alexa_pages[mypageid]


def start_selenium_driver(driver) -> TorBrowserDriver:
    if driver == None:
        os.environ['WDM_LOG'] = '0'
        logging.debug("Starting new Tor Browser Selenium")
        try:
            firefox_options = Options()
            PROXY = "socks5://localhost:9050" # IP:PORT or HOST:PORT
            firefox_options.add_argument('--proxy-server=%s' % PROXY)
            firefox_options.log.level = "fatal"
            firefox_options.set_preference('browser.cache.disk.enable', False)
            firefox_options.set_preference('browser.cache.memory.enable', False)
            firefox_options.set_preference('browser.cache.offline.enable', False)
            firefox_options.set_preference('network.cookie.cookieBehavior', 2)
            firefox_options.add_argument('-headless')
            firefox_options.set_capability("marionette", False)
            driver = TorBrowserDriver("/tor-browser",
                                    options=firefox_options,
                                    #tbb_logfile_path="headless_tor_browser.log",
                                    tbb_logfile_path='/dev/null',
                                    #service_log_path=os.devnull,
                                    headless=True)
            # to be able to click
            #driver.set_window_size(1440, 900)
            #driver.set_window_size(1920, 1080)
            driver.set_page_load_timeout(60)
            driver.refresh()
        except Exception as e:
            logging.error("Could not start selenium: {}".format(e))
            logging.error(traceback.format_exc())
    return driver


def close_selenium_driver(driver):
    if driver != None:
        try:
            # driver.close()
            driver.quit()
        except Exception as e:
            logging.error(f"closing selenium driver: {e}")
            logging.error(traceback.format_exc())
        finally:
            driver = None
    return driver


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
    if len(sys.argv) > 4 and "--attacker" != sys.argv[4]:
        logging.error("arg 4 is an optional \"--attacker\"")
        exit()
    elif len(sys.argv) > 4 and "--attacker" == sys.argv[4]:
        IS_ATTACKER = True

    driver = None
    nOnions = int(sys.argv[1])
    request_iterations = int(sys.argv[2])

    client_id = int(sys.argv[3])
    os.popen(f"rm -f client{client_id}_is_done")
    logging.basicConfig(filename = 'pcap-folder/client' + str(client_id) + '/file.log',level=logging.DEBUG,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    #logging.basicConfig(filename = 'pcap-folder/client' + str(client_id) + '/file.log',level=logging.WARNING,format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

    # Required, otherwise it doesn't make the captures, needs to wait for image to be downloaded
    try:
        result = sub.run("docker pull kaazing/tcpdump", shell=True)
        if result.returncode == 0:
            logging.debug('Image downloaded successfully')
        else:
            logging.debug(f'Could not download image: {result.stderr.decode()}')
    except Exception as e:
        logging.error(f'Error downloading image: {result.stderr.decode()}')
        logging.error(traceback.format_exc())

    # start virtual display for Tor browser
    xvfb_display = start_xvfb()

    # Make sure different datasets visit different pages
    interleave_factor = 3
    # TODO: Change this for every dataset
    start_page = 2

    onion_services = parse_inventory(nOnions)
    alexa_pages = parse_tranco_pages(start_page, interleave_factor)
    alexa_pages_reachable = []
    hostname = socket.gethostname()

    #logging.debug("\n--- INITIAL alexa_pages: {}".format(alexa_pages))

    # This should be done before starting pcaps, otherwise this traffic will 
    # also be captured
    possible_paths = {}
    for node in onion_services:
        logging.debug("ansible node: {}".format(str(node)))
        driver = start_selenium_driver(driver)
        possible_paths[node['onion_address']], _ = get_website_possible_urls(f"http://{node['onion_address']}/onion_pages/{node['onion_page']}")
        driver = close_selenium_driver(driver)
        #if len(possible_paths[node['onion_address']]) < MIN_PATHS:
        #    logging.error("Removed OS {} for having less than {} paths".format(node['onion_address'], MIN_PATHS))
        #    exit()
    logging.debug(f"Retrieved possible paths for {len(possible_paths)} different OSes!")

    possible_paths_alexa = {}
    logging.debug("Testing {} alexa_pages".format(len(alexa_pages)))
    limit_pages = 50
    count_pages = 0
    amount_of_pages = len(alexa_pages)

    driver = None
    for page in alexa_pages[:min(limit_pages, amount_of_pages)]: # collect only the first 50 pages
        count_pages += 1
        paths, new_page = get_website_possible_urls('http://' + page)
        if len(paths) < MIN_PATHS:
            logging.info("page{} --- Remove alexa page: {} for having less than {} paths".format(count_pages, page, MIN_PATHS))
        else:
            logging.info("page{} --- Add alexa page: {}".format(count_pages, page))
            alexa_pages_reachable.append(new_page)
            possible_paths_alexa[page] = paths

    if amount_of_pages > limit_pages: # pick an extra 50 pages at random
        sel_pages = []
        for page in range(limit_pages):
            page = alexa_pages[random.randrange(limit_pages, amount_of_pages)]
            if page in sel_pages:
                continue
            sel_pages += [page]
            count_pages += 1
            paths, new_page = get_website_possible_urls('http://' + page)
            if len(paths) < MIN_PATHS:
                logging.info("page{} --- Remove alexa page: {} for having less than {} paths".format(count_pages, page, MIN_PATHS))
            else:
                logging.info("page{} --- Add alexa page: {}".format(count_pages, page))
                alexa_pages_reachable.append(new_page)
                possible_paths_alexa[page] = paths

    logging.debug("Retrieved possible paths for {} different clearweb websites!".format(len(possible_paths_alexa)))
    logging.debug("\n--- nb alexa_pages_reachable: {}".format(len(alexa_pages_reachable)))

    oses_addresses = []
    popularities = []
    for node in onion_services:
        oses_addresses.append(node['onion_address'])
        popularities.append(node['onion_popularity'])
    logging.debug("******* before popularities {}", popularities)
    pop_sum = sum(popularities)
    popularities = [p / pop_sum for p in popularities]
    logging.debug("******* popularities {}", popularities)

    # Parameter taken from Oustralopithecus paper
    SHAPE = 0.75
    SCALE = 30
    stay_times = []
    while 1:
        try:
            stay_times  = np.random.weibull(a=SHAPE, size=request_iterations) * SCALE
        except Exception as e:
            logging.debug(f"Error np.random.weibull {str(e)}")
            logging.error(traceback.format_exc())
            continue
        break

    #Create directory for holding pcaps
    client_cap_folder = client_folder() + "captures-" + hostname + "/"
    logging.debug(f"make folder {client_cap_folder}")
    os.system("mkdir -p %s"%client_cap_folder)

    session_id = 0
    request_id_per_session = 0
    # First request is always a new session
    # go to alexa or onion?
    alexa = False
    alexa_page = ''
    session_sample_name = ''
    os_node = None
    my_number = random.randint(0, 100)
    count_alexa_req = 0
    count_oses_req = 0

    request_counter = request_iterations
    average_session :float = 0.
    count_nb_sessions :int = 0
    average_requests :float = 0.
    count_nb_requests :int = 0
    aux_time_session :float = 0.
    aux_time_request :float = 0.

    attacker_probe_size = 1
    attacker_sessions_before_inc = 100 # attacker tries larger probe after this threshold
    attacker_current_nb_sessions = 0

    full_client_capture = start_traffic_capture(client_id, client_cap_folder, 'full-client{}.pcap'.format(client_id))
    #start_traffic_capture(client_cap_folder, 'full-client{}.pcap'.format(client_id), client_id)
    while request_counter > 0:
        # new session
        attacker_current_nb_requests = 0
        attacker_current_nb_sessions += 1
        if attacker_current_nb_sessions > attacker_sessions_before_inc:
            attacker_probe_size += 1 # after a while increases probe size
            attacker_current_nb_sessions = 0
        try:
            #logging.debug("=== my_number {}".format(my_number))
            request_counter -= 1
            request_id_per_session = 0
            request_id = request_iterations - request_counter
            alexa = my_number < alexa_probability*100
            if alexa and not IS_ATTACKER:
                logging.info("NEW SESSION TO ALEXA!")
                count_alexa_req += 1
                alexa_page = get_alexa_page_random(alexa_pages_reachable)
                session_sample_name = "{}_alexa_{}_session_{}".format(hostname, alexa_page, session_id)
                logging.info("alexa {}:".format(session_sample_name))
            else:
                logging.info("NEW SESSION TO OS")
                count_nb_sessions += 1
                count_nb_requests += 1
                aux_time_session = time.time()
                aux_time_request = aux_time_session
                os_node = get_node_random(onion_services, popularities)

                #session_sample_name = str(hostname) + "_" + str(os_node['node_name']) + "_" + str(os_node['onion_page']) + "_session_" + str(session_id)
                session_sample_name = "{}_os{}-{}_{}_session_{}".format(hostname, os_node['onion_idx'], os_node['node_name'], os_node['onion_page'], session_id)
                logging.info("os_node: {}".format(os_node))
            #request_sample_name = session_sample_name + '_request_' + str(request_id_per_session)
            request_sample_name = '{}_request_{}'.format(session_sample_name, request_id_per_session)
            
            #perform browsing session 
            session = SessionHandler(client_cap_folder, session_sample_name) if alexa else SessionHandlerToOSes(client_cap_folder, session_sample_name, os_node, hostname)
            session.start(client_id)
            session.go_to(well_formed_url(alexa_page) if alexa else "index.html", request_sample_name, client_id)

            logging.info("========== REQUEST ITERATION ========== {}".format(request_id))
            logging.info("Request {} out of {}".format(request_id, request_iterations))
            next_action = 1
            if not IS_ATTACKER:
                next_action = np.random.choice(len(actions), 1, p=list(actions.values()))
            #logging.info("next_action: {}".format(next_action))

            #stay_time = stay_times[0]
            stay_time = stay_times[request_id]
            # the attacker also waits when changing OS
            sleep_stay_time(stay_time)

            # new request within same session
            while next_action == 1:
                #logging.info("stay in same page")
                request_counter -= 1
                attacker_current_nb_requests += 1
                # We're out of requests for this experiment
                if request_counter == 0:
                    break
                request_id = request_iterations - request_counter
                if not IS_ATTACKER:
                    next_action = np.random.choice(len(actions), 1, p=list(actions.values()))
                else:
                    next_action = 0 if attacker_current_nb_requests > attacker_probe_size else 1
                if time.time() - aux_time_session > MAX_SESSION_TIME:
                    next_action = 0 # does not allow sessions longer than MAX_SESSION_TIME
                # visit within website
                request_id_per_session += 1
                request_sample_name = session_sample_name + "_request_" + str(request_id_per_session)
                session.random_access(request_sample_name, client_id)
                stay_time = stay_times[request_id]
                if not IS_ATTACKER:
                    sleep_stay_time(stay_time)
                if alexa and not IS_ATTACKER:
                    count_alexa_req += 1
                else:
                    count_oses_req += 1 
                    count_nb_requests += 1
                    now_time = time.time()
                    if next_action == 0:
                        diff = now_time - aux_time_session
                        average_session = average_session + (diff - average_session) / float(count_nb_sessions)
                        logging.info(f' ---- {count_nb_sessions} sessions with average duration {average_session}"')
                    diff = now_time - aux_time_request
                    aux_time_request = now_time
                    average_requests = average_requests + (diff - average_requests) / float(count_nb_requests)
                    logging.info(f' ---- {count_nb_requests} requests with average duration {average_requests}"')
                logging.info(f"--- {count_alexa_req} alexa_reqs, {count_nb_requests} oses_reqs")
            # new website
            session.end(session_sample_name, client_id)
            logging.info("--- END session_sample_name: {}".format(session_sample_name))
            del session
            session_id += 1

            # Decide if next session is clearweb or os
            my_number = random.randint(0, 100)

        except FirstRequestTimeoutException as e:
            logging.error("FirstRequestTimeoutException occurred during main while loop")
            logging.error(e)
            logging.error(traceback.format_exc())
            logging.debug("Resetting counters to repeat session that timed out")
            request_counter += 1
            if alexa:
                count_alexa_req -= 1
            else:
                count_nb_sessions -= 1
                count_nb_requests -= 1
            log_failed_request(request_sample_name)
        except FailedHTTPException as e:
            logging.error("FailedHTTPException occurred during main while loop")
            logging.error(e)
            logging.error(traceback.format_exc())
            logging.debug("Resetting counters to repeat session that timed out")
            log_failed_request(request_sample_name)
        except Exception as e:
            logging.error("Exception occurred during main while loop")
            logging.error(e)
            logging.error(traceback.format_exc())

    logging.info("========= FINISHED EXPERIMENT =========")
    #stop_traffic_capture(client_id)
    stop_traffic_capture(full_client_capture)
    stop_xvfb(xvfb_display)
    os.popen(f"touch client{client_id}_is_done")
    #wait for 25 seconds to be killed by job terminator
