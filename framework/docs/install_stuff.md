## Install required software

```
#General tools
sudo apt-get update
sudo apt-get install xvfb tor python3-pip tmux htop git 

# Docker
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7EA0A9C3F273FCD8

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Pull Tor Hidden Services docker image
sudo docker pull strm/tor-hiddenservice-nginx

#Install geckodriver
wget https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz
tar -zxvf geckodriver-v0.27.0-linux64.tar.gz
sudo mv geckodriver /usr/local/bin/
rm geckodriver-v0.27.0-linux64.tar.gz

#Install tor browser bundle
wget https://www.torproject.org/dist/torbrowser/11.0.3/tor-browser-linux64-11.0.3_en-US.tar.xz    
tar -xf tor-browser-linux64-11.0.3_en-US.tar.xz
rm tor-browser-linux64-11.0.3_en-US.tar.xz

# update pip
python3 -m pip install --upgrade pip

#Install python packages
python3 -m pip install -r requirements.txt


#random command on all nodes
ansible -i inventory_model.cfg  all_nodes -m shell -a 'random command'

#command that was run to perform cap
python3 job_coordinator.py -o onion_pages/large.txt -i 100 -f n
``` 

## Fix for Docker in buster (debian 10)
* https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-debian-10
```
sudo apt update
sudo apt install apt-transport-https ca-certificates curl gnupg2 software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker-ce
sudo chmod 666 /var/run/docker.sock
```