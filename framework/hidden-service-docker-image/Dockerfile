FROM debian:bullseye
LABEL maintainer "opsxcq@strm.sh"
# Base packages
RUN apt-get update && \
    apt-get -y install \
    procps \
    tcpdump \
    nginx \
    lsof \
    ntpdate \
    tor \
    torsocks
# Compile shallot
ADD ./mkp224o-1.5.0 /mkp224o-1.5.0
RUN apt-get update && \
    apt-get -y install \
    build-essential \
    libssl-dev \
    libsodium* && \
    cd /mkp224o-1.5.0 && \
    ./configure && \
    make && \
    mv ./mkp224o /bin && \
    cd / && \
    rm -Rf /mkp224o-1.5.0 && \
    apt-get -y purge build-essential libssl-dev && \
    rm -Rf /var/lib/apt/lists/*
# Security and permissions
RUN useradd --system --uid 666 -M --shell /usr/sbin/nologin hidden
# Configure nginx logs to go to Docker log collection (via stdout/stderr)
RUN ln --symbolic --force /dev/stdout /var/log/nginx/access.log
RUN ln --symbolic --force /dev/stderr /var/log/nginx/error.log
# Main script
ADD ./main.sh /main.sh
ADD ./generate.sh /generate.sh
ADD ./serve.sh /serve.sh
# Tor Config
ADD ./torrc /etc/tor/torrc
# Add nginx default configuration
ADD ./nginx.conf /etc/nginx/nginx.conf
# Configuration files and data output folder
VOLUME /web2
WORKDIR /web2
ENTRYPOINT ["/main.sh"]
#CMD ["serve"]
CMD ["torp"]