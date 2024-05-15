# How to define variables in terraform:
# https://www.terraform.io/docs/configuration/variables.html

# Name of the project, replace "XX" for your
# respective group ID
variable "GCP_PROJECT_NAME" {
    default = "{{=== T_GCP_PROJECT_NAME ===}}"
}

# A list of machine types is found at:
# https://cloud.google.com/compute/docs/machine-types
# prices are defined per region, before choosing an instance
# check the cost at: https://cloud.google.com/compute/pricing#machinetype
# Minimum required is N1 type = "n1-standard-1, 1 vCPU, 3.75 GB RAM"
variable "GCP_OS_MACHINE_TYPE" {
    default = "{{=== T_GCP_OS_MACHINE_TYPE ===}}"
}

variable "GCP_CLIENT_MACHINE_TYPE" {
    default = "{{=== T_GCP_CLIENT_MACHINE_TYPE ===}}"
}

variable "GCP_JOB_MACHINE_TYPE" {
    default = "{{=== T_GCP_JOB_MACHINE_TYPE ===}}"
}

# Minimum required
variable "DISK_SIZE" {
    default = "20"
}

variable "DISK_SIZE_ONION" {
    default = "{{=== T_DISK_SIZE_ONION ===}}"
}

variable "DISK_SIZE_CLIENT" {
    default = "{{=== T_DISK_SIZE_CLIENT ===}}"
}

variable "DISK_SIZE_JOB_COORDINATOR" {
    default = "{{=== T_DISK_SIZE_JOB_COORDINATOR ===}}"
}

variable "GCP_REGION1" {
    default = "europe-west4-a"
}

variable "CLIENTS_PER_NODE" {
    default = "{{=== T_CLIENTS_PER_NODE ===}}"
}

variable "REQUESTS_PER_CLIENT" {
    default = "{{=== T_REQUESTS_PER_CLIENT ===}}"
}

variable "ONIONS_PER_NODE" {
    default = "{{=== T_ONIONS_PER_NODE ===}}"
}

variable "USER" {
    default = "{{=== T_USER ===}}"
}

variable "LOCAL_PROJECT_DIR" {
    default = "{{=== T_LOCAL_PROJECT_DIR ===}}"
}

variable "PUBLIC_KEY_PATH" {
    default = "{{=== T_ANSIBLE_PUBLIC_KEY ===}}"
}

variable "PRIVATE_KEY_PATH" {
    default = "{{=== T_ANSIBLE_KEY ===}}"
}

variable "SSH_KEY" {
    default = "{{=== T_ANSIBLE_KEY ===}}"
}

variable "JOB_COORDINATOR_NAME" {
    default = "job-coordinator-{{=== T_EXP_NAME ===}}"
}

variable "NB_NODES_ONION" {
  type    = number
  default = {{=== T_NB_NODES_ONION ===}}       
}

variable "NODES_ONION_NAMES" {
  type    = list(string)
  default = {{=== T_NODES_ONION_NAMES ===}}       
}

variable "NODES_ONION_REGIONS" {
  type    = list(string)
  default = {{=== T_NODES_ONION_REGIONS ===}}
}

variable "NODES_ONION_PAGES" {
  type    = list(list(string))
  default = {{=== T_NODES_ONION_PAGES ===}}
}

variable "NODES_ONION_IPS" {
  type    = list(string)
  default = {{=== T_NODES_ONION_IPS ===}}
}

variable "NODES_ONION_POPULARITY" {
 type    = list(list(string))
 default = {{=== T_NODES_ONION_POPULARITY ===}}
}

variable "NB_NODES_CLIENT" {
  type    = number
  default = {{=== T_NB_NODES_CLIENT ===}}       
}

variable "NODES_CLIENT_NAMES" {
  type    = list(string)
  default = {{=== T_NODES_CLIENT_NAMES ===}}
}

variable "NODES_CLIENT_REGIONS" {
  type    = list(string)
  default = {{=== T_NODES_CLIENT_REGIONS ===}}
}

variable "NODES_CLIENT_IPS" {
  type    = list(string)
  default = {{=== T_NODES_CLIENT_IPS ===}}
}

variable "CLIENT_USE_BRIDGE" {
  type    = list(string)
  default = ["0", 
    "0", 
    "0",
    "0",
    "0",
    "0",
    "0",
    "0",
    "0",
    "0"]
}

# set this in order to have much more "agressive" clients
variable "CLIENT_IS_ATTACKER" {
  type    = list(string)
  default = ["0", 
    "0", 
    "0",
    "0",
    "0",
    "0",
    "0",
    "0",
    "0",
    "0"]
}
