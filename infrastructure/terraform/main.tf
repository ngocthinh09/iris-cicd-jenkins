terraform {
	required_providers {
		google = {
			source = "hashicorp/google"
			version = "~> 6.0"
		}
	}
}

variable "gcp_project_id" {
	default = "jenkinscicd-494404"
}

variable "gcp_region" {
	default = "asia-southeast1"
}

variable "gcp_zone" {
	default = "asia-southeast1-a"
}

variable "ssh_user" {
	default = "ubuntu"
}

variable "ssh_pub_key_path" {
	default = "~/.ssh/gcp_ssh_key.pub"
}

provider "google" {
	credentials = file("gcp-key.json")
	project = var.gcp_project_id
	region = var.gcp_region
	zone = var.gcp_zone
}

resource "google_compute_instance" "jenkins_vm" {
	name = "jenkins-server-gcp"
	machine_type = "e2-medium"

	boot_disk {
		initialize_params {
			image = "ubuntu-os-cloud/ubuntu-2204-lts"
			size = 20
		}
	}

	network_interface {
		network = "default"
		access_config {	
		}
	}

	metadata = {
		ssh-keys = "${var.ssh_user}:${file(var.ssh_pub_key_path)}"
	}

	tags = [ "http-server", "jenkins-port" ]
}

resource "google_compute_firewall" "jenkins_firewall" {
	name = "allow-jenkins-8080"
	network = "default"

	allow {
		protocol = "tcp"
		ports = [ "8080", "22" ]
	}

	source_ranges = [ "0.0.0.0/0" ]
	source_tags = [ "jenkins-port" ]
}

resource "google_container_cluster" "primary" {
	name = "iris-cluster"
	location = var.gcp_zone
	deletion_protection = false

	initial_node_count = 1
	remove_default_node_pool = true

	node_config {
		machine_type = "e2-medium"
	}
}

resource "google_container_node_pool" "primary_nodes" {
	name = "main-node-pool"
	location = var.gcp_zone
	cluster = google_container_cluster.primary.name
	node_count = 1

	node_config {
		machine_type = "e2-medium"
		oauth_scopes = [
			"https://www.googleapis.com/auth/cloud-platform"
		]
	}
}	