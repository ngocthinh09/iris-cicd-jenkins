terraform {
	required_providers {
		google = {
			source = "hashicorp/google"
			version = "~> 6.0"
		}
	}
}

provider "google" {
	credentials = file("gcp-key.json")
	project = "jenkinscicd-494404"
	region = "asia-southeast1"
	zone = "asia-southeast1-a"
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
		ssh-keys = "ngocthinh09:${file("~/.ssh/gcp_ssh_key.pub")}"
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
	location = "asia-southeast1-a"

	initial_node_count = 1
	remove_default_node_pool = true

	node_config {
		machine_type = "e2-medium"
	}
}

resource "google_container_node_pool" "primary_nodes" {
	name = "main-node-pool"
	location = "asia-southeast1-a"
	cluster = google_container_cluster.primary.name
	node_count = 1

	node_config {
		machine_type = "e2-medium"
		oauth_scopes = [
			"https://www.googleapis.com/auth/cloud-platform"
		]
	}
}