
FROM ubuntu:20.04



WORKDIR /app

RUN apt-get update --fix-missing
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:longsleep/golang-backports
RUN apt-get update --fix-missing
# RUN DEBIAN_FRONTEND=noninteractive apt-get -y install wireshark
RUN apt-get install -y iptables iproute2 wget golang-go python3-pip xvfb
RUN apt-get install -y netcat screen
RUN pip3 install netifaces
RUN apt-get update && apt-get install -y iputils-ping docker.io

RUN python3 -m pip install selenium
RUN python3 -m pip install tbselenium
RUN python3 -m pip install pyvirtualdisplay
RUN python3 -m pip install stem
RUN python3 -m pip install loguru
RUN python3 -m pip install datetime
RUN python3 -m pip install requests
RUN python3 -m pip install argparse
RUN python3 -m pip install flask
RUN python3 -m pip install ansible
RUN python3 -m pip install numpy
RUN python3 -m pip install bs4
RUN python3 -m pip install validators
RUN python3 -m pip install python-dateutil
RUN apt-get install -y bzip2 libxtst6 libgtk-3-0 libx11-xcb-dev libdbus-glib-1-2 libxt6 libpci-dev

RUN apt-get install -y wget
RUN apt-get update --fix-missing
# RUN apt-get install -y firefox
RUN apt install -y tor
# COPY geckodriver-v0.31.0-linux64.tar.gz geckodriver-v0.31.0-linux64.tar.gz
# RUN mkdir /gecko
# RUN tar -zxf geckodriver-v0.31.0-linux64.tar.gz -C /gecko
# COPY tor-browser-linux64-12.0a3_en-US.tar.xz tor-browser-linux64-12.0a3_en-US.tar.xz
# RUN tar -xf tor-browser-linux64-12.0a3_en-US.tar.xz
RUN \
  wget https://github.com/mozilla/geckodriver/releases/download/v0.32.2/geckodriver-v0.32.2-linux64.tar.gz \
  && tar -xvzf geckodriver-v0.32.2-linux64.tar.gz \
  && chmod 0755 geckodriver && rm geckodriver-v0.32.2-linux64.tar.gz \
  && mv geckodriver /usr/local/bin/
RUN \
  wget https://dist.torproject.org/torbrowser/12.5a4/tor-browser-linux64-12.5a4_ALL.tar.xz \
  && tar -xf tor-browser-linux64-12.5a4_ALL.tar.xz \
  && mv tor-browser /tor-browser \
  && rm tor-browser-linux64-12.5a4_ALL.tar.xz
# COPY fingerprinting.py fingerprinting.py
# COPY webpages.py webpages.py
# COPY collector.py collector.py
# COPY interfacestoinet.py interfacestoinet.py
# COPY remote_stuff/tranco_top_websites.csv tranco_82GXV.csv
RUN apt-get install -y tcpdump
RUN apt-get install -y firefox
CMD exec tail -f /dev/null