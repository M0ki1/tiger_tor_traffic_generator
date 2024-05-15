# syntax=docker/dockerfile:1
FROM ubuntu:20.04
# COPY requirements.txt /app/requirements.txt
# COPY alexa_top_50.txt /app/alexa_top_50.txt
# COPY capture_traffic_scale_tor.py /app/capture_traffic_scale_tor.py
# COPY capture.sh /app/capture.sh
# needs to copy it after launch
# COPY inventory.cfg /app/inventory.cfg
ENV LANG C.UTF-8
RUN \
  (apt-get update && apt install -y gnupg software-properties-common debconf-utils \
  && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7EA0A9C3F273FCD8 \
  && add-apt-repository universe && add-apt-repository multiverse && apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y \
  python3 \
  python3-pip \
  wget \
  tar \
  xvfb \
  tor \
  screen \
  tcpdump \
  build-essential \
  libssl-dev \
  autoconf \
  make \
  libsodium-dev \
  gcc \
  && rm -rf /var/lib/apt/lists/*)
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

# CMD python /app/app.py
