# Terraform GCP
# To output variables, follow pattern:
# value = TYPE.NAME.ATTR

# example for a set of identical instances created with "count"
output "os_nodes_IPs1"  {
  value = formatlist("%s = %s", google_compute_instance.os-nodes[*].name, google_compute_instance.os-nodes[*].network_interface.0.access_config.0.nat_ip)
}

output "os_nodes_internal_IPs1"  {
  value = formatlist("%s = %s", google_compute_instance.os-nodes[*].name, google_compute_instance.os-nodes[*].network_interface.0.network_ip)
}

output "client_nodes_IPs1"  {
  value = formatlist("%s = %s", google_compute_instance.client-nodes[*].name, google_compute_instance.client-nodes[*].network_interface.0.access_config.0.nat_ip)
}

output "client_nodes_internal_IPs1"  {
  value = formatlist("%s = %s", google_compute_instance.client-nodes[*].name, google_compute_instance.client-nodes[*].network_interface.0.network_ip)
}

output "job_coordinator_IP1"  {
  value = formatlist("%s = %s", google_compute_instance.job-coordinator.name, google_compute_instance.job-coordinator.network_interface.0.access_config.0.nat_ip)
}


# Automaticaly create an inventory file with the returned IPs
resource "local_file" "ansible_inventory" {
  filename = "inventory_model.cfg"
  content = <<EOF
[os_nodes]
%{ for idx,instance in google_compute_instance.os-nodes[*] }
${instance.name} ansible_host=${instance.network_interface.0.access_config.0.nat_ip} static_docker_ip=${instance.labels["onion_ips"]} internal_ens4=${instance.network_interface.0.network_ip} ansible_user=${var.USER} ansible_ssh_private_key_file=${var.SSH_KEY} node_name=${instance.name} node_index=${idx+1} ansible_python_interpreter=/usr/bin/python3 %{ for inner_idx in range(0, var.ONIONS_PER_NODE) } onion_popularity${inner_idx + 1}=${var.NODES_ONION_POPULARITY[idx][inner_idx]} onion_page${inner_idx + 1}=${var.NODES_ONION_PAGES[idx][inner_idx]} onion_address${inner_idx + 1}=${trim(file("${var.LOCAL_PROJECT_DIR}/hidden-service-docker-image/onion_addresses_v3/node${idx * var.ONIONS_PER_NODE + inner_idx + 1}/hostname"), "\n")} %{ endfor } onion_pages='[%{ for inner_idx in range(0, var.ONIONS_PER_NODE - 1) } "${var.NODES_ONION_PAGES[idx][inner_idx]}", %{ endfor } "${var.NODES_ONION_PAGES[idx][var.ONIONS_PER_NODE - 1]}"]' 
%{ endfor }

[client_nodes]
%{ for idx,instance in google_compute_instance.client-nodes[*] }
${instance.name} ansible_host=${instance.network_interface.0.access_config.0.nat_ip} static_docker_ip=${instance.labels["client_ips"]} internal_ens4=${instance.network_interface.0.network_ip} ansible_user=${var.USER} ansible_ssh_private_key_file=${var.SSH_KEY} node_name=${instance.name} ansible_python_interpreter=/usr/bin/python3 is_attacker=${var.CLIENT_IS_ATTACKER[idx]} use_bridge=${var.CLIENT_USE_BRIDGE[idx]} 
%{ endfor }

[client_nodes:vars]
request_iterations=${var.REQUESTS_PER_CLIENT}
clients_per_node=${var.CLIENTS_PER_NODE}
onions_per_node=${var.ONIONS_PER_NODE}

[os_nodes:vars]
clients_per_node=${var.CLIENTS_PER_NODE}
onions_per_node=${var.ONIONS_PER_NODE}

[coordinator:vars]
clients_per_node=${var.CLIENTS_PER_NODE}
onions_per_node=${var.ONIONS_PER_NODE}
  
[coordinator]
job-coordinator		ansible_host=${google_compute_instance.job-coordinator.network_interface.0.access_config.0.nat_ip} 	ansible_user=${var.USER}   ansible_python_interpreter=/usr/bin/python3   ansible_ssh_private_key_file=${var.SSH_KEY} node_name=job-coordinator onion_address=none

EOF
}
