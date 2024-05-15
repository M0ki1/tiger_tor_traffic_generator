# Elemets of the cloud such as virtual servers,
# networks, firewall rules are created as resources
# syntax is: resource RESOURCE_TYPE RESOURCE_NAME
# https://www.terraform.io/docs/configuration/resources.html



###########  Nodes serving onion urls   #############
# This method creates as many identical instances as the "count" index value
resource "google_compute_instance" "os-nodes" {
    count = var.NB_NODES_ONION
    name = var.NODES_ONION_NAMES[count.index]
    machine_type = var.GCP_OS_MACHINE_TYPE
    zone = var.NODES_ONION_REGIONS[count.index]

    #description = var.NODES_ONION_URLS[count.index] # description contains onion_url
    description = "${file("${var.LOCAL_PROJECT_DIR}/hidden-service-docker-image/onion_addresses_v3/node${count.index + 1}/hostname")}" # description contains onion_url
              
    labels = {
      # "onion_popularity": var.NODES_ONION_POPULARITY[count.index],  ### outputs checks the vars directly
      # "onion_page": var.NODES_ONION_PAGES[count.index],
      "onion_ips": var.NODES_ONION_IPS[count.index]
    }

    boot_disk {
        initialize_params {
        # image list can be found at:
        # https://cloud.google.com/compute/docs/images
        #image = "ubuntu-1804-bionic-v20201116"
        #image = "debian-10-buster-v20211209"
        image = "cos-cloud/cos-101-lts"
        size = 50
        }
    }

    network_interface {
        network = "default"
        access_config {
          
        }
    }

    metadata = {
      ssh-keys = "${var.USER}:${file("${var.PUBLIC_KEY_PATH}")}"
    }

    # Copies onion url files
    ### TODO: provisioner "file" seems to not be working
    # provisioner "file" {
    #   source      = "${var.LOCAL_PROJECT_DIR}/hidden-service-docker-image/onion_addresses_v3/node${count.index + 1}/hostname"
    #   destination = "/home/${var.USER}/hostname"

    #   connection {
    #     type    = "ssh"
    #     user    = var.USER
    #     private_key = file("${var.PRIVATE_KEY_PATH}")
    #     host = self.network_interface.0.access_config.0.nat_ip
    #   }
    # }

    # provisioner "file" {
    #   source      = "${var.LOCAL_PROJECT_DIR}/hidden-service-docker-image/onion_addresses_v3/node${count.index + 1}/hs_ed25519_public_key"
    #   destination = "/home/${var.USER}/hs_ed25519_public_key"

    #   connection {
    #     type    = "ssh"
    #     user    = var.USER
    #     private_key = file("${var.PRIVATE_KEY_PATH}")
    #     host = self.network_interface.0.access_config.0.nat_ip
    #   }
    # }

    # provisioner "file" {
    #   source      = "${var.LOCAL_PROJECT_DIR}/hidden-service-docker-image/onion_addresses_v3/node${count.index + 1}/hs_ed25519_secret_key"
    #   destination = "/home/${var.USER}/hs_ed25519_secret_key"

    #   connection {
    #     type    = "ssh"
    #     user    = var.USER
    #     private_key = file("${var.PRIVATE_KEY_PATH}")
    #     host = self.network_interface.0.access_config.0.nat_ip
    #   }
    # }
    
  tags = ["node"]
}


###########  Nodes accessing onion urls   #############
# This method creates as many identical instances as the "count" index value
resource "google_compute_instance" "client-nodes" {
    count = var.NB_NODES_CLIENT
    name = var.NODES_CLIENT_NAMES[count.index]
    machine_type = var.GCP_CLIENT_MACHINE_TYPE
    zone = var.NODES_CLIENT_REGIONS[count.index]

    boot_disk {
        initialize_params {
        # image list can be found at:
        # https://cloud.google.com/compute/docs/images
        #image = "ubuntu-1804-bionic-v20201116"
        # image = "debian-10-buster-v20211209"
        image = "cos-cloud/cos-101-lts"
        size = 30
        }
    }

    labels = {
      "client_ips": var.NODES_ONION_IPS[count.index]
    }

    network_interface {
        network = "default"
        access_config {
        }
    }

    # provisioner "remote-exec" {
    #   # cos does not allow script execution (all stuff in dockers)
    #   # inline = ["echo 'Wait until SSH is ready'",
    #   #     "sudo cloud-init status --wait",]

    #   connection {
    #     type    = "ssh"
    #     user    = var.USER
    #     private_key = file("${var.PRIVATE_KEY_PATH}")
    #     host = self.network_interface.0.access_config.0.nat_ip
    #   }
    # }

    metadata = {
      ssh-keys = "${var.USER}:${file("${var.PUBLIC_KEY_PATH}")}"
    }
    
  tags = ["node"]
}



###########  Job coordinator node   #############
resource "google_compute_instance" "job-coordinator" {
    name = var.JOB_COORDINATOR_NAME
    machine_type = var.GCP_JOB_MACHINE_TYPE
    zone = var.GCP_REGION1

    boot_disk {
        initialize_params {
        # image list can be found at:
        # https://cloud.google.com/compute/docs/images
        #image = "ubuntu-1804-bionic-v20201116"
        image = "cos-cloud/cos-101-lts"
        size = 20
        }
    }

    network_interface {
        network = "default"
        access_config {
        }
    }

    metadata = {
      ssh-keys = "${var.USER}:${file("${var.PUBLIC_KEY_PATH}")}"
    }

  tags = ["node"]
}

###########  Web app node  #############
# resource "google_compute_instance" "web-app" {
#     name = var.WEBAPP_NAME
#     machine_type = var.GCP_WEBAPP_MACHINE_TYPE
#     zone = var.GCP_REGION1
#     boot_disk {
#         initialize_params {
#         # image list can be found at:
#         # https://cloud.google.com/compute/docs/images
#         #image = "ubuntu-1804-bionic-v20201116"
#         image = "cos-cloud/cos-101-lts"
#         size = 100
#         }
#     }
#     network_interface {
#         network = "default"
#         access_config {
#         }
#     }
#     metadata = {
#       ssh-keys = "${var.USER}:${file("${var.PUBLIC_KEY_PATH}")}"
#     }
#   tags = ["node"]
# }
