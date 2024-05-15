FROM kylemanna/bitcoind

RUN apt update
RUN apt upgrade -y
RUN apt install -y tor
COPY torrc /etc/tor/torrc

# needs to run as user 101
RUN su - debian-tor -c 'tor &'

# adds the current bitcoin blockchain
ADD data /bitcoin/.bitcoin

