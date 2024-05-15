
# Elemets of the cloud such as virtual servers,
# networks, firewall rules are created as resources
# syntax is: resource RESOURCE_TYPE RESOURCE_NAME
# https://www.terraform.io/docs/configuration/resources.html


#resource "google_compute_firewall" "frontend_rules" {
#    name    = "frontend"
#    network = "default"

#    allow {
#        protocol = "icmp"
#    }

#    allow {
#        protocol = "tcp"
# With no port specified, this rule applies to connections through any port
  #      ports = ["22", "80", "443", "5005", "8080"]
    #}

#    source_ranges = ["0.0.0.0/0"]
# No target_tags specified means the firewall rule applies to 
# all instances on the network
#    target_tags = ["node"]
#}
