# include this after parameters.sh

### setup this with your credentials then change its name to account.sh
template_vars["T_USER"]="<username>"
T_ANSIBLE_KEY="~/.ssh/<your_key_here>"
T_ANSIBLE_PUBLIC_KEY="~/.ssh/<your_key_here.pub>"
T_VM_HOME_FOLDER="/home/<username>"
T_LOCAL_PROJECT_DIR="/path/to/project/cloud_dataset/"

### name of the project
template_vars["T_GCP_PROJECT_NAME"]="master-plane-281409"

### your credential .json file
template_vars["T_GCLOUD_CREDENTIALS_JSON"]="credentials/master-plane-281409-57659dc08d14.json"

