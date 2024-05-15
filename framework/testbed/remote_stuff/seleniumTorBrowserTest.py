from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import start_xvfb, stop_xvfb
import time


#pathToTorBrowser = '/home/dmbb/tor-browser_en-US'
pathToTorBrowser = '/home/danielalopes97/tor-browser_en-US'
    

def getOnionPage(url):
    #out_img = "/home/dmbb/headless_screenshot.png"
    out_img = "/home/danielalopes97/headless_screenshot.png"

    xvfb_display = start_xvfb()

    with TorBrowserDriver(pathToTorBrowser) as driver:
        print("*********** BEFORE GET")
        driver.get(url)
        print("*********** AFTER GET")
        driver.get_screenshot_as_file(out_img)
        print("*********** AFTER SCREENSHOT")
        stop_xvfb(xvfb_display)
        print("*********** AFTER stop_xvfb()")


# This url doesn't work
#url = 'http://dragonccmlb5cd7w.onion/'
url = 'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/'
getOnionPage(url)

