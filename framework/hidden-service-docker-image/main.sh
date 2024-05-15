#!/bin/bash

# Generate v3 onion URL
if [ -f /web/hs_ed25519_secret_key ]
then
    echo '[-] You already have a private key, delete it if you want to generate a new key'
    exit -1
fi
if [ -z "$1" ]
then
    echo '[-] You didnt provided any mask, please inform an mask to generate your address'
    exit -1
else
    echo '[+] Generating the address with mask: '$1
    mkp224o $1 -n 1 -O onionNames
    address=$(head -n 1 onionNames)
    cp ./$address/* /web/.
    rm ./$address -r
    rm ./onionNames
fi

echo '[+] Generating nginx configuration for site '$address
echo 'server {' > /web/site.conf
echo '  listen 127.0.0.1:8080;' >> /web/site.conf
echo '  root /web/www/;' >> /web/site.conf
echo '  index index.html index.htm;' >> /web/site.conf
echo '  server_name '$address';' >> /web/site.conf
echo '}' >> /web/site.conf

echo '[+] Creating www folder'
mkdir /web/www
chmod 755 /web/
chmod 755 /web/www
echo '[+] Generating index.html template'
echo '<html><head><title>Torpedo Onion Service</title></head><body><h1>Simulating real onion service to generate Torpedo datasets</h1></body></html>' > /web/www/index.html
chown hidden:hidden -R /web/www


# Serve
if [ ! -f /web/hs_ed25519_secret_key ]
then
    echo '[-] Please run this container with generate argument to initialize your web page'
    exit -1
fi
echo '[+] Initializing local clock'
ntpdate -B -q 0.debian.pool.ntp.org
chmod -R 700 /web/
echo '[+] Starting tor'
tor -f /etc/tor/torrc &
sleep 5
chmod -R 755 /web/
echo '[+] Starting nginx'
nginx &
sleep 5
chmod -R o+rX /web/
# Monitor logs
sleep infinity

