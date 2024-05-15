FROM alpine
ENV LANG C.UTF-8

RUN apk update
RUN apk add \
  python3 \
  py3-pip \
  py3-numpy \
  py3-flask \
  py3-requests \
  wget \
  tar \
  xz \
  xvfb \
  tcpdump \
  tor \
  docker \
  bash \
  dbus-glib \
  screen 

RUN apk add --no-cache \
  glib \
  tzdata \
  libexif \
  udev \
  zlib-dev 

RUN python3 -m pip install --upgrade pip \
  && python3 -m pip install --user \
    tbselenium \
    ansible \
    python-dateutil \
    pyvirtualdisplay \
  && python3 -m pip cache purge

WORKDIR /app
