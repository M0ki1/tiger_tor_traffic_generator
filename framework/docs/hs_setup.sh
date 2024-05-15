#Tor guide for setting up Hidden Services
#https://2019.www.torproject.org/docs/tor-onion-service.html.en

###########################
#Start a new Hidden Service
###########################

#Pull this docker image for generating Tor Hidden Services 
#https://hub.docker.com/r/strm/tor-hiddenservice-nginx
#https://github.com/opsxcq/docker-tor-hiddenservice-nginx
docker pull strm/tor-hiddenservice-nginx

#Generate the skeleton for the Tor HS with a given name pattern (ex. starting with tedo -> ^tedo)
#Longer name patterns will take more time to be generated
docker run -it --rm -v $(pwd)/web:/web strm/tor-hiddenservice-nginx generate ^torp

#Start up a container that runs the hidden service
docker run -d --restart=always --name torpedo_hs -v $(pwd)/web:/web strm/tor-hiddenservice-nginx

#Make the mounted directory and its contents publicly readable
#(Required so that nginx can serve files from within the container)
#https://github.com/nginxinc/docker-nginx/issues/177
# ToDo: Check if we can make this work by just setting the directory readable by the nginx group
sudo chmod -R o+rX web

# Reason for this not to work: The provided onionsite address is invalid. Please check that you entered it correctly.
# Details: 0xF6 — The provided .onion address is invalid. This error is returned due to one of the following reasons: the address checksum doesn't match, the ed25519 public key is invalid, or the encoding is invalid.

# https://www.bleepingcomputer.com/news/software/tor-browser-11-removes-v2-onion-url-support-adds-new-ui/
# However, the most significant change is the deprecation of V2 onion services, meaning TOR URLs using short 16 character hostnames domains are no longer supported.
# When attempting to open a V2 onion service, Tor Browser will show users an "Invalid Onionsite Address" with an error code of 0xF6.



################
#Useful Commands
################

#Check the ID of the container
docker ps

#Check the container logs (Useful for checking status of HS bootstrap)
docker logs <container_id>

#Get a shell in the container
docker run -it --rm -v $(pwd)/web:/web --entrypoint /bin/bash strm/tor-hiddenservice-nginx

#Stop the container (HS will be disabled)
docker stop <container_id>

#Restart the container (HS will restart automatically)
docker start <container_id>

#Remove the container (after stopping it)
docker rm <container_id>

#Delete HS data (on the docker host system)
sudo rm -rf web # also solves [-] You already have an private key, delete it if you want to generate a new key

###############
#Other comments
###############

#Automating access to Onion services:
#https://askubuntu.com/questions/499995/how-to-change-the-ip-address-which-is-given-by-tor-using-the-terminal

#Use tor via SOCKS listener on 127.0.0.1:9050
curl --socks5-hostname localhost:9050 ifconfig.me

#Rotate the established circuit
sudo killall -HUP tor
#or
service tor reload

#Rotating the guard node is probably not interesting for us.
#We can collect data for a period of time (e.g. predefined # of requests) and then close

#It's probably possible to split data by TCP connection
#https://medium.com/@asfandyar.khalil/tcp-stream-in-pcap-file-using-python-6991a8e7b524