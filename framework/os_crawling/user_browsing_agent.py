from random import random
import weibull
import numpy as np
import requests
from bs4 import BeautifulSoup
import random
import requests
import time
from scipy.stats import weibull_min


np.set_printoptions(suppress=True)


# This can be executed offline without Tor
def get_website_possible_urls(url):
    # https://www.geeksforgeeks.org/extract-all-the-urls-from-the-webpage-using-python/

    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    
    website_urls = []
    # get all <a> anchor tags
    for link in soup.find_all('a'):
        # exclude external links to open web or other OSes
        url = link.get('href')
        if '.onion' not in url and 'http' not in url:
            website_urls.append(url)

    # remove duplicate paths
    return list(dict.fromkeys(website_urls))


# Our model contemplates only single tab browsing sessions, and each session is issued to a single website. When accessing a 
# different website, we consider this is done in a completely different session with a new circuit established
# However, we can consider sessions to the same website that have less requests than we need, but then disregard them in Torpedo
# Possible actions that the user can take
# The action the user takes is decided by the method random.choice in numpy
# This method has an optional parameter that sets the relative probabilities that each item in the list is chosen
# Dwell is also na action, but it is a particular action, the client always dwells between other actions, following a Weibull distribution
# Two main features that characterize any browsing session: 
# i) sequence of web pages visited or requested
# ii) stay time on each web page
# Probabilities taken from 'DOBBS: Towards a Comprehensive Dataset to Study the Browsing Behavior of Online Users': 
# https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=6689993 (They don't actually give these values, maybe they tested user sessions with their
# tools to obtain the values)
# Explicit inactivity: watching a video; Implicit inactivity: ?; background time: switching tabs
#actions = {'new_site': 0.33, # new_site()
#            'navigate': 0.67} # nav_link(), history(), download() -> since they all consist on making requests
                                                        # nop() and new_tab() probabilities are merged into navigate as well
actions = {'new_site': 0.2,
            'navigate': 0.8}


N_REQUESTS = 30


# a is the shape
# multiply by the scale of the output
# size is the amount of predictions made each time
# https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.weibull.html#numpy.random.Generator.weibull
SHAPE = 0.75
SCALE = 30
stay_times  = np.random.weibull(a=SHAPE, size=N_REQUESTS) * SCALE # taken from Oustral paper
print("stay_times: ", stay_times)

#x = weibull_min.rvs(SHAPE, loc=0, scale=SCALE, size=N_REQUESTS)
#print("x", x)

possible_websites = ['http://localhost/555eearzli4bilpjmwmy5n6qoh3jdtrqzt2345cwjj2x3e4cmvvneoad.onion',
                    'http://localhost/apu54lid4g46zzafhdxq63gsvppcri7nb7qobs53jnyx3nbqz45e4lad.onion',
                    'http://localhost/dbayuapytcowfz2nnfik3jayno4njibl45t77r3eartihtq6igtaqtqd.onion']


def user_session():
    url = random.choice(possible_websites)
    print("\n--- New site: ", url)
    requests.get(url) # go to landing page
    possible_paths = get_website_possible_urls(url)
    print("\n--- possible_paths: ", possible_paths)
    stay_time = stay_times[0]
    print("\n--- Dwell time: {:f}".format(stay_time))
    for i in range(1, N_REQUESTS):
        next_action = np.random.choice(len(actions), 1, p=list(actions.values()))
        if next_action == 0:
            # get next website to visit and finish session
            url = np.random.choice(possible_websites)
            print("\n--- New site: ", url)
            requests.get(url) # go to landing page
            possible_paths = get_website_possible_urls(url)
            print("\n--- possible_paths: ", possible_paths)
        elif next_action == 1:
            # get next page to visit within the website
            navigate_to = url + '/' + np.random.choice(possible_paths)
            print("\n--- Navigate to: ", navigate_to)
            requests.get(navigate_to)
        
        stay_time = stay_times[i]
        print("\n--- Dwell time: {:f}".format(stay_time))
        #time.sleep(stay_time) # in seconds


def main():
    # Input website to visit
    # To host website in mac:
    # Change website files to /usr/local/opt/httpd
    # Location of configuration file: /usr/local/etc/httpd/httpd.conf
    # sudo apachectl -k restart
    #url = 'http://localhost/555eearzli4bilpjmwmy5n6qoh3jdtrqzt2345cwjj2x3e4cmvvneoad.onion'
    #print(get_website_possible_urls(url))
    user_session()


if __name__ == "__main__":
    main()