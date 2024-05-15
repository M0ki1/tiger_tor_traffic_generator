# syntax=docker/dockerfile:1
FROM ubuntu:18.04
ENV LANG C.UTF-8
#apt-get update && apt install -y gnupg software-properties-common debconf-utils build-essential \
RUN \
  apt-get update && apt install -y gnupg software-properties-common debconf-utils \
  && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7EA0A9C3F273FCD8 \
  && add-apt-repository universe && add-apt-repository multiverse && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
  python3 \
  python3-pip \
  wget \
  tar \
  xvfb \
  tcpdump \
  tor \
  screen \
  libdbus-glib-1-2 \
  packagekit-gtk3-module \
  && rm -rf /var/lib/apt/lists/*
  #  zlib1g-dev \

#RUN \
#  wget https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tar.xz &&\
#  tar -xf Python-3.9.7.tar.xz && \
#  cd Python-3.9.7 && \
#  ./configure --enable-optimizations && \
#  make && \
#  make install
  #make install && \
  #apt-get install -y python3-pip

RUN python3 -m pip install --upgrade pip && python3 -m pip install --user flask tbselenium ansible requests pyvirtualdisplay numpy && \
  ((wget https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz \
  && tar -xvzf geckodriver-v0.27.0-linux64.tar.gz && chmod 0755 geckodriver && rm geckodriver-v0.27.0-linux64.tar.gz && mv geckodriver /usr/local/bin/) && \
  (wget https://dist.torproject.org/torbrowser/12.0.2/tor-browser-linux64-12.0.2_ALL.tar.xz \
  && tar -xf tor-browser-linux64-12.0.2_ALL.tar.xz && rm tor-browser-linux64-12.0.2_ALL.tar.xz) ) 
