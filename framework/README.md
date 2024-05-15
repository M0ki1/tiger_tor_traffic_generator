# TIGER framework

## Template setup

Run the `lauch_experiment.sh` to setup the run. There are a bunch of parameters
that you can setup in `launch_template/`. Set your credentials in `launch_template/credentials/account.sh`.

## Terraform and gcloud setup
* zones error: https://serverfault.com/questions/1000746/gce-required-compute-zones-list-permission-for-projects-someproject/1000760

```
gcloud config set project onion-service-torpedo-337211

gcloud iam service-accounts keys create key.json \
--iam-account onion-service-torpedo@onion-service-torpedo-337211.iam.gserviceaccount.com

gcloud projects add-iam-policy-binding onion-service-torpedo-337211 \
--member serviceAccount:onion-service-torpedo@onion-service-torpedo-337211.iam.gserviceaccount.com \
--role=roles/compute.admin

gcloud auth activate-service-account --key-file=key.json
```


## Generate Onion Addresses
* Only needs to be done once, pass the number of onion addresses that you wish to generate:
```
cd hidden-service-docker-image/
sudo chmod +x generate_v3_onion_address.sh 

./generate_v3_onion_address.sh 20
```


## Run an experiment on Google Cloud
In local machine:
1. Add the necessary credentials for terraform. (Terraform is not necessary, it is just a way to automatize launching several VMs, but it can be configured manually in the Google Cloud Dashboard.) Edit testbed/terraform-cgp-variables.tf and testbed/terraform-cgp-servers.tf. It's currently setup to launch 20 client VMs and 15 OS VMs, 5 request iterations and 60 sessions. This also generates the `inventory_model.cfg` needed for ansible.

2. Execute following commands:
```
terraform init
terraform plan
terraform apply
ansible-playbook run_collection.yml -i inventory_model.cfg --tags "setup_packages"
```

3. Access the job coordinator machine via ssh with the public IP indicated in the `inventory_model.cfg` file.

Inside the job coordinator machine:

4. Execute command: (wait a few minutes or check for file decompressDone.txt inside job-coordinator container)
```
docker exec target bash -c "cd /app && while [ ! -f decompressDone.txt ] ; do sleep 1s ; done && python3 job_coordinator_scale_tor.py"
```

```
docker exec target bash -c "cd /app && python3 job_coordinator_scale_tor.py"
```

Wait for the decompression to be done before calling it, or just add the wait as in the following:
```
docker exec target bash -c "cd /app && while [ ! -f decompressDone.txt ] ; do sleep 1s ; done && python3 job_coordinator_scale_tor.py"
```

5. Exit job coordinator, and in local machine:
``` 
ansible-playbook run_collection.yml -i inventory_model.cfg --tags "fetch_dataset"
```

6. At the end, also in local machine:
```
terraform destroy
```


## Add containers to Docker Hub
```
docker build -t danielalopes:tor-client-tcpdump .

docker tag e8b9a1c9d43e danielalopes/tor-client-tcpdump:1.3

docker push danielalopes/tor-client-tcpdump:1.3
```

## Debug
```
docker rm target 

docker run -it -v /home/daniela_lopes/:/app -d --name target -h coordinator -p 5005:5005 dcastro93/dpss:danon_job_manager bash

docker container list
docker exec -it <container name> /bin/bash
docker exec -it target /bin/bash
docker exec -it torp-onion-service /bin/bash
```

```
docker run -it --rm -p 9050:9050 -p 9051:9051 -e PASSWORD=emptyPassword --volumes-from target -d --name tor_client danielalopes/tor-client-tcpdump:1.4

docker exec -it tor_client /bin/bash

docker exec -u 0 tor_client sh -c "tcpdump"
```

chmod 700 /web



```
docker exec target bash -c "ansible-playbook run_collection.yml -i inventory.cfg --tags \"rm_pcaps\""


## Obtain client graphical interface
* Using Chrome Remote Desktop: https://ubuntu.com/blog/launch-ubuntu-desktop-on-google-cloud 


## Run no concurrency pages with multiple pages
### Get websites code 
```
wget -r -p -U Mozilla https://nomadicsamuel.com/
```

### Capture commands
* Whole capture: 
```
sudo tcpdump -i ens4 -W 1 -w pcap-folder/captures-client-simulator/full-capture_client.pcap port not 22
```
```
sudo tcpdump -i docker0 -W 1 -w pcap-folder/captures-os-amsterdam-new/full-capture_hs.pcap port not 22
```

* Session capture:
```
sudo tcpdump -i ens4 -W 1 -w pcap-folder/captures-client-simulator/client-simulator_os-amsterdam-new_session_0_client.pcap port not 22
```
```
sudo tcpdump -i docker0 -W 1 -w pcap-folder/captures-os-amsterdam-new/client-simulator_os-amsterdam-new_session_0_hs.pcap port not 22
```

* Request capture: 
```
sudo tcpdump -i ens4 -W 1 -w pcap-folder/captures-client-simulator/client-simulator_os-amsterdam-new_session_0_request_0_client.pcap port not 22
```
```
sudo tcpdump -i docker0 -W 1 -w pcap-folder/captures-os-amsterdam-new/client-simulator_os-amsterdam-new_session_0_request_0_hs.pcap port not 22
```

### Experiment (accessing pages)
* --------- os-amsterdam-new ------------
* session_0
* torpi2ilvqpdecszx5a23idf5jv3cjuzj5jv7odgyjvkd5vp6g4n5bad.onion/onion_pages/f2fv76wtuwdvbpci_400_4/index.html * 10

* New identity 

* session_1
* torpi2ilvqpdecszx5a23idf5jv3cjuzj5jv7odgyjvkd5vp6g4n5bad.onion/onion_pages/f2fv76wtuwdvbpci_400_4/index.html * 10

* New identity 

* session_2
* torpi2ilvqpdecszx5a23idf5jv3cjuzj5jv7odgyjvkd5vp6g4n5bad.onion/onion_pages/f2fv76wtuwdvbpci_400_4/index.html * 10

* New identity 

* --------------- os-finland-new --------------

* session_0
* torpikhvsvfbx43z7q6h3tb75kjemtqz2qtlwgj5xaybr6kiwgqgl5id.onion/onion_pages/ig2ioz6j2vpcmz27nlqmfdrscijqeqnjv6ku3pkpte7pm53gxeal5hqd_700_9/index.html * 10

* New identity 

* session_1
* torpikhvsvfbx43z7q6h3tb75kjemtqz2qtlwgj5xaybr6kiwgqgl5id.onion/onion_pages/ig2ioz6j2vpcmz27nlqmfdrscijqeqnjv6ku3pkpte7pm53gxeal5hqd_700_9/index.html * 10

* New identity 

* torpikhvsvfbx43z7q6h3tb75kjemtqz2qtlwgj5xaybr6kiwgqgl5id.onion/onion_pages/ig2ioz6j2vpcmz27nlqmfdrscijqeqnjv6ku3pkpte7pm53gxeal5hqd_700_9/index.html * 10

* New identity 

* -------------- os-london-new ---------------

* torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/jeh4ftzegnmcx75poa3dvzime7yyp2ay6vskfhgis6ikkv3fvzim7sad_100_2/index.html * 10

* New identity 

* torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/jeh4ftzegnmcx75poa3dvzime7yyp2ay6vskfhgis6ikkv3fvzim7sad_100_2/index.html * 10

* New identity

* torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/index.html * 10

* New identity

* torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/index.html * 10

* New identity
0
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/index.html
1
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/category/index.html
2
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/city-guides/index.html
3
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/country-guides/index.html
4
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/destinations/index.html
5
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/interviews/index.html
6
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/motivation/index.html
7
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/musings/index.html
8
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/photo-essays/index.html
9
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/photo-essays/index.html


* New identity
0
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/index.html
1
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/category/index.html
2
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/city-guides/index.html
3
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/country-guides/index.html
4
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/destinations/index.html
5
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/interviews/index.html
6
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/motivation/index.html
7
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/musings/index.html
8
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/photo-essays/index.html
9
* http://torpopvdhfvao4xoidwna6dkdhmvvoklijemk573f7hodbkuzhruyyid.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/photo-essays/index.html


* New identity

* -------------- os-los-angeles-new -----------------

* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/iyh4h3xzh2aeqsta_500_11/index.html * 10

* New identity

* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/iyh4h3xzh2aeqsta_500_11/index.html * 10

* New identity

* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/index.html * 10

* New identity

* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/index.html * 10

* New identity
0
* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/index.html
1
* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/category/index.html
2
* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/city-guides/index.html
3
* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/country-guides/index.html
4
* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/destinations/index.html
5
* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/interviews/index.html
6
* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/motivation/index.html
7
* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/musings/index.html
8
* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/photo-essays/index.html
9
* http://torpyklj7hyofjube3iqfruhu5fsauxfhs5wk563tk3sawktljqvxeqd.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/photo-essays/index.html

* New identity


* -------------- os-singapore-new -----------------

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/jnwllvrbzw5nrke6_600_19/index.html * 10

* New identity

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/jnwllvrbzw5nrke6_600_19/index.html * 10

* New identity

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/index.html * 10

* New identity

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/index.html * 10

* New identity

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/index.html

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/category/index.html

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/city-guides/index.html

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/country-guides/index.html

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/destinations/index.html

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/interviews/index.html

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/motivation/index.html

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/musings/index.html

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/photo-essays/index.html

* http://torppjz5w7oyjhn3yeqohxnbehutu32ucdkq4rogmzd75ulrgkge3cad.onion/onion_pages/multiple_pages/multiplePages/wgetBlog/nomadicsamuel.com/photo-essays/index.html
>>>>>>> 12e9440529 (added websites with multiple pages for manual experiment)
=======
>>>>>>> fd2392d898 (updated onion pages for 2022)
=======
Problem in client "No screen session found":
After pip3 install numpy:
```
          self.distribution.run_command(command)
        File "/usr/lib/python3.10/distutils/dist.py", line 985, in run_command
          cmd_obj.run()
        File "/tmp/pip-install-tip38s2j/numpy_01fcb2754ab04867ae34b6f7f94a6274/numpy/distutils/command/build.py", line 62, in run
          old_build.run(self)
        File "/usr/lib/python3.10/distutils/command/build.py", line 135, in run
          self.run_command(cmd_name)
        File "/usr/lib/python3.10/distutils/cmd.py", line 313, in run_command
          self.distribution.run_command(command)
        File "/usr/lib/python3.10/distutils/dist.py", line 985, in run_command
          cmd_obj.run()
        File "/tmp/pip-install-tip38s2j/numpy_01fcb2754ab04867ae34b6f7f94a6274/numpy/distutils/command/build_src.py", line 144, in run
          self.build_sources()
        File "/tmp/pip-install-tip38s2j/numpy_01fcb2754ab04867ae34b6f7f94a6274/numpy/distutils/command/build_src.py", line 155, in build_sources
          self.build_library_sources(*libname_info)
        File "/tmp/pip-install-tip38s2j/numpy_01fcb2754ab04867ae34b6f7f94a6274/numpy/distutils/command/build_src.py", line 288, in build_library_sources
          sources = self.generate_sources(sources, (lib_name, build_info))
        File "/tmp/pip-install-tip38s2j/numpy_01fcb2754ab04867ae34b6f7f94a6274/numpy/distutils/command/build_src.py", line 378, in generate_sources
          source = func(extension, build_dir)
        File "/tmp/pip-install-tip38s2j/numpy_01fcb2754ab04867ae34b6f7f94a6274/numpy/core/setup.py", line 758, in get_mathlib_info
          raise RuntimeError(
      RuntimeError: Broken toolchain: cannot link a simple C program.
      [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for numpy
Failed to build numpy
ERROR: Could not build wheels for numpy, which is required to install pyproject.toml-based projects
```


>>>>>>> 0e98c63265 (added logs for client request status)
=======
chmod 700 /web
>>>>>>> 19bcb2eec1 (Still some issues to be fixed, like os container not working)
=======
```
>>>>>>> 600aab5b50 (big experience mostly working)
