#!/bin/bash


address=$(cat hostname)

mkdir /web
cp -r /web2/* /web

echo '[+] Generating nginx configuration for site '$address
echo 'server {' > /web/site.conf
echo '  listen 127.0.0.1:8080;' >> /web/site.conf
echo '  root /web/www/;' >> /web/site.conf
echo '  index index.html index.htm index.php;' >> /web/site.conf
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

