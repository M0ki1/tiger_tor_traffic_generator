#!/usr/bin/env bash

# Setup the parameters in launch_parameters/ and run this script
# Arguments:
#   $1 --> path where to store the experiment
#   $2 --> name of the experiment, e.g., "ostrain"

export CUR_PATH=$(pwd)
export PATH_EXP="../../DAnon_gcloud"
export NAME_EXP="expTest"

# replace pattern {{=== NAME_OF_VAR ===}} 
source launch_template/parameters/template_vars.sh
source launch_template/parameters.sh
# account.sh must come after
source launch_template/credentials/account.sh

if [ "$1" ] ; then
  PATH_EXP="$1"
fi
if [ "$2" ] ; then
  NAME_EXP="$2"
fi

if [ ! -d $PATH_EXP ] ; then
  echo "$PATH_EXP does not exist"
  exit 0
fi

EXP_FOLDER="${PATH_EXP}/gcloud-launch-${NAME_EXP}"
if [ -d "$EXP_FOLDER" ] ; then
  echo "Folder $EXP_FOLDER exists, check if experiment is running"
  exit 0
fi

# checking files:
if [ ! -f $T_GCLOUD_CREDENTIALS_JSON ] ; then
  echo "You have to have a .json file! Set template_vars[\"T_GCLOUD_CREDENTIALS_JSON\"]=/path/to/your/json in ./launch_template/credentials/account.sh"
  exit 0
fi

mkdir -p $EXP_FOLDER
cp -r testbed/remote_stuff $EXP_FOLDER/remote_stuff
cp -r testbed/terraform $EXP_FOLDER/terraform
cp -r testbed/templates $EXP_FOLDER/templates
cp -r hidden-service-docker-image $EXP_FOLDER/hidden-service-docker-image

# localhost ansible script:
cp testbed/ansible/ansible.cfg $EXP_FOLDER/ansible.cfg
cp testbed/ansible/run_collection.yml $EXP_FOLDER/run_collection.yml
# job_manager ansible script:
cp testbed/ansible/run_collection_job_manager.yml $EXP_FOLDER/run_collection_job_manager.yml

for f in $EXP_FOLDER/* $EXP_FOLDER/**/* ; do
  if [ -f $f ] ; then
    replace_parameters_on_file $f
  fi
done

mkdir -p $EXP_FOLDER/terraform/credentials
cp launch_template/credentials/${template_vars["T_GCLOUD_CREDENTIALS_JSON"]} $EXP_FOLDER/terraform/credentials/

cd $EXP_FOLDER/terraform
terraform init

echo "   Success!"
echo "   Go to $EXP_FOLDER/terraform and do:"
echo "\$ terraform apply"
echo "   to launch the experiment."
echo "   Then go to $EXP_FOLDER and execute the ansible scripts."
echo "   (note that the inventory file is in terraform/inventory_model.cfg)"
