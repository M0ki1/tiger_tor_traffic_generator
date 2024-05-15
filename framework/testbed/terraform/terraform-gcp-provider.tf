# Terraform google cloud multi tier deployment

# check how configure the provider here:
# https://www.terraform.io/docs/providers/google/index.html
provider "google" {
    # Create/Download your credentials from:
    # Google Console -> "APIs & services -> Credentials"
    # Choose create- > "service account key" -> compute engine service account -> JSON

    # credentials = file("master-plane-281409-0f9ef3fbebba.json") # DAnon project
    #credentials = file("credentials/master-plane-281409-57659dc08d14.json") # DAnon dcastro key
    credentials = file("credentials/{{=== T_GCLOUD_CREDENTIALS_JSON ===}}")

    project = var.GCP_PROJECT_NAME
    zone = var.GCP_REGION1
}
