declare -A template_vars=( )

template_vars["T_EXP_NAME"]=$(echo "$NAME_EXP" | tr '[:upper:]' '[:lower:]')
template_vars["T_GCP_OS_MACHINE_TYPE"]="n1-standard-4"
template_vars["T_GCP_CLIENT_MACHINE_TYPE"]="n1-standard-4"
template_vars["T_GCP_JOB_MACHINE_TYPE"]="n1-standard-1"
template_vars["T_ANSIBLE_INVENTORY"]="terraform/inventory_model.cfg"
template_vars["T_DISK_SIZE"]="20"
template_vars["T_DISK_SIZE_CLIENT"]="50"
template_vars["T_DISK_SIZE_ONION"]="80"
template_vars["T_DISK_SIZE_JOB_COORDINATOR"]="80"
template_vars["T_NB_NODES_ONION"]="1"
template_vars["T_NB_NODES_CLIENT"]="1"
template_vars["T_CLIENTS_PER_NODE"]="4"
template_vars["T_ONIONS_PER_NODE"]="4"
template_vars["T_REQUESTS_PER_CLIENT"]="20"

# escape \n with sed ':a;N;$!ba;s/\n/\\n/g'
template_vars["T_NODES_CLIENT_REGIONS"]=$(cat $CUR_PATH/launch_template/parameters/NODE_CLIENT_REGIONS | tr -d '\n')
template_vars["T_NODES_ONION_REGIONS"]=$(cat $CUR_PATH/launch_template/parameters/NODE_ONION_REGIONS | tr -d '\n')
template_vars["T_NODES_ONION_PAGES"]=$(cat $CUR_PATH/launch_template/parameters/NODE_ONION_PAGES | tr -d '\n')
template_vars["T_NODES_ONION_POPULARITY"]=$(cat $CUR_PATH/launch_template/parameters/NODE_ONION_POPULARITY | tr -d '\n')
