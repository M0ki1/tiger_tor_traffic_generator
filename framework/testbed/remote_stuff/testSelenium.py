from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import start_xvfb, stop_xvfb
import logging
import sys
from bs4 import BeautifulSoup

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

xvfb_display = start_xvfb()

firefox_options = Options()

geckodriver_path = Service('geckodriver')
PROXY = "socks5://localhost:9050" # IP:PORT or HOST:PORT
user_agent = 'Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
firefox_options.add_argument('--proxy-server=%s' % PROXY)
firefox_options.add_argument('-headless')
firefox_options.set_capability("marionette", False)
# firefox_options.add_argument("--no-sandbox")
# firefox_options.add_argument("--disable-logging")
# firefox_options.add_argument("--disable-dev-shm-usage")
# firefox_options.add_argument("--disable-web-security")
# firefox_options.add_argument("--allow-running-insecure-content")
# firefox_options.add_argument("--log-level=0")
# firefox_options.add_argument("--user-agent="+user_agent)
# firefox_options.add_argument("--remote-debugging-port=9222") # fixes some bug

logging.disable(1000)

# driver = webdriver.Firefox(service=geckodriver_path, options=firefox_options)
driver = TorBrowserDriver("/tor-browser", options=firefox_options)
logging.disable(0)


url = "http://www.google.pt"
driver.get(url)
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')
links = soup.find_all('a')
logging.info(f"page {url} has {len(links)} links")

url = "http://torpkvf6bf47435zdeb74oquneb4v7t6zd4c4dh3funjzgyw4hai23yd.onion:80/onion_pages/b4bbcjkuimxggedoqahicvimcw7xutwmp4omh2lz7cskuaaxoxog6cad"
driver.get(url)
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')
links = soup.find_all('a')
logging.info(f"page {url} has {len(links)} links")


driver.close()

stop_xvfb(xvfb_display)