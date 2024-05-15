# syntax=docker/dockerfile:1
FROM ubuntu:18.04
ENV LANG C.UTF-8
RUN \
  (apt-get update && apt install -y gnupg software-properties-common debconf-utils \
  && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7EA0A9C3F273FCD8 \
  && add-apt-repository universe && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
  python3 \
  ssh \
  rsync \
  python3-pip \
  ansible \
  && rm -rf /var/lib/apt/lists/*)
RUN python3 -m pip install --upgrade pip && \
  python3 -m pip install --user flask ansible docker docker-py numpy requests pyvirtualdisplay

CMD cp /app/ssh_key_file /root/.ssh/ssh_key_file
