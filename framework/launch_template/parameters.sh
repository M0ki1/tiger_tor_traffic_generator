

# Replaces the parameters in a file
# @param $1 path of file
function replace_parameters_on_file() {

  for p in "${!template_vars[@]}" ; do
    pattern="{{=== $p ===}}"

    grep "$pattern" $1 && sed -i  "s|$pattern|${template_vars[$p]}|g" $1
  done

  
  # generate T_NODES_ONION_NAMES
  base_onion_name="os-${template_vars['T_EXP_NAME']}-"
  pattern='{{=== T_NODES_ONION_NAMES ===}}'
  name_onion="["
  for i in $(seq ${template_vars['T_NB_NODES_ONION']}) ; do 
    name_onion="${name_onion}\"${base_onion_name}${i}\","
  done
  name_onion="${name_onion}\"${base_onion_name}$((${template_vars['T_NB_NODES_ONION']} + 1))\" ]"
  grep "$pattern" $1 && sed -i  "s|$pattern|${name_onion}|g" $1
  
  # generate T_NODES_CLIENT_NAMES
  base_client_name="client-${template_vars['T_EXP_NAME']}-"
  pattern='{{=== T_NODES_CLIENT_NAMES ===}}'
  name_client="["
  for i in $(seq ${template_vars['T_NB_NODES_CLIENT']}) ; do 
    name_client="${name_client}\"${base_client_name}${i}\","
  done
  name_client="${name_client}\"${base_client_name}$((${template_vars['T_NB_NODES_CLIENT']} + 1))\" ]"
  grep "$pattern" $1 && sed -i  "s|$pattern|${name_client}|g" $1
  
  # generate T_NODES_CLIENT_IPS
  pattern='{{=== T_NODES_CLIENT_IPS ===}}'
  list_of_ips="["
  nb_clients=$(( ${template_vars['T_NB_NODES_CLIENT']} * ${template_vars['T_CLIENTS_PER_NODE']} ))
  for i in $(seq 19 $(( 19 + $nb_clients )) ) ; do 
    list_of_ips="${list_of_ips}\"${i}\","
  done
  list_of_ips="${list_of_ips}\"$((19 + $nb_clients + 1))\" ]"
  grep "$pattern" $1 && sed -i  "s|$pattern|${list_of_ips}|g" $1

  # generate T_NODES_ONION_IPS
  pattern='{{=== T_NODES_ONION_IPS ===}}'
  list_of_ips="["
  nb_onions=$(( ${template_vars['T_NB_NODES_ONION']} * ${template_vars['T_ONIONS_PER_NODE']} ))
  for i in $(seq 120 $((120 + $nb_onions)) ) ; do 
    list_of_ips="${list_of_ips}\"${i}\","
  done
  list_of_ips="${list_of_ips}\"$((120 + $nb_onions + 1))\" ]"
  grep "$pattern" $1 && sed -i  "s|$pattern|${list_of_ips}|g" $1
  
}
