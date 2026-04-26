# 🚀 Iris MLOps CI/CD: From Infrastructure to Deployment

This project demonstrates a complete MLOps pipeline for the Iris dataset, covering infrastructure provisioning, automated configuration, CI/CD, and deployment to Kubernetes on Google Cloud Platform (GCP).

## 🏗️ Project Architecture
The pipeline follows these steps:
1.  **Infrastructure**: Provisioned using **Terraform** (Jenkins VM & GKE Cluster).
2.  **Configuration**: Automated using **Ansible** (Install Docker, Jenkins, etc.).
3.  **CI/CD**: Orchestrated by **Jenkins** (Train -> Test -> Build -> Push -> Deploy).
4.  **Deployment**: Managed via **Helm** on **Google Kubernetes Engine (GKE)**.

---

## 🛠️ Phase 1: Prerequisites & Setup

Before you begin, ensure you have the following installed and configured:

### 1. Tools Required
*   [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install)
*   [Terraform](https://developer.hashicorp.com/terraform/downloads)
*   [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) (Linux or WSL recommended)
*   [Git](https://git-scm.com/downloads)
*   [Docker](https://www.docker.com/products/docker-desktop/)

### 2. Google Cloud Platform (GCP) Setup
1.  **Create a Project**: Create a new project in the [GCP Console](https://console.cloud.google.com/).
2.  **Enable APIs**: Enable Compute Engine, Kubernetes Engine, and Cloud Resource Manager APIs.
3.  **Service Account**:
    *   Go to **IAM & Admin** > **Service Accounts**.
    *   Create a service account with **Editor** or **Owner** role.
    *   Create and download a JSON Key. Rename it to `gcp-key.json` and place it in `infrastructure/terraform/`.
    *   **WARNING**: Do NOT commit this file to GitHub. It is already added to `.gitignore`.

### 3. SSH Key for VM Access
Create an SSH key pair to allow Ansible and Terraform to access your Jenkins VM:
```bash
ssh-keygen -t rsa -f ~/.ssh/gcp_ssh_key -C "ubuntu"
```
By default, the project uses `ubuntu` as the user and `~/.ssh/gcp_ssh_key.pub` as the key. You can customize these in `infrastructure/terraform/terraform.tfvars`:
*   `ssh_user`: Your preferred SSH username.
*   `ssh_pub_key_path`: The path to your public key file.

---

## 🛰️ Phase 2: Infrastructure Provisioning (Terraform)

In this phase, we will use Terraform to create the Google Cloud resources: a Compute Engine VM for Jenkins and a Google Kubernetes Engine (GKE) cluster.

### 1. Initialize Terraform
Navigate to the terraform directory and initialize the provider plugins:
```bash
cd infrastructure/terraform
terraform init
```

### 2. Review and Customize
Before applying, open `infrastructure/terraform/terraform.tfvars` and set your GCP Project ID:
```hcl
gcp_project_id = "your-actual-project-id"
```
Then, verify the plan:
```bash
terraform plan
```

### 3. Apply the Infrastructure
Create the resources on GCP:
```bash
terraform apply -auto-approve
```
*Note: This process may take 5-10 minutes as it provisions a GKE cluster.*

### 4. Note the Outputs
After a successful apply, Terraform will output the public IP of your Jenkins server.
*   **Jenkins VM IP**: You will need this for the next phase (Ansible configuration).
*   **GKE Cluster**: The cluster `iris-cluster` will be ready for deployment.

---

## 🛠️ Phase 3: Server Configuration (Ansible)

Now that the VM is running, we will use Ansible to automatically install Docker, Jenkins, and other dependencies.

### 1. Update Inventory
Navigate to the ansible directory and open `inventory.ini`. Replace the placeholder IP with your Jenkins VM IP:
```ini
[jenkins_server]
jenkins_vm ansible_host=<YOUR_VM_IP> ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/gcp_ssh_key
```

### 2. Run the Playbook
Execute the Ansible playbook to configure the server:
```bash
cd infrastructure/ansible
ansible-playbook -i inventory.ini setup_jenkins.yml
```
*This playbook will install and configure:*
*   **Java 21** (Required for Jenkins)
*   **Python 3.12** (For training and testing)
*   **Docker Engine**
*   **Jenkins** (Installed directly on the host)
*   **Google Cloud SDK** (`gcloud`, `kubectl`, GKE auth plugin)
*   **Helm** (For GKE deployment)
*   **Permissions**: Automatically adds the `jenkins` user to the `docker` group.

### 3. Verify Jenkins Access
Open your browser and navigate to:
`http://<YOUR_VM_IP>:8080`

If you see the Jenkins login screen, your server is ready!

---

## 🔑 Phase 4: Jenkins Initial Setup & Credentials

This phase is critical for connecting Jenkins to your code (GitHub), your registry (Docker Hub), and your deployment target (GKE).

### 1. Unlock Jenkins
Jenkins is secured with a temporary password. To retrieve it, run this command on your **local terminal**:
```bash
ssh -i ~/.ssh/gcp_ssh_key ubuntu@<YOUR_VM_IP> "sudo cat /var/lib/jenkins/secrets/initialAdminPassword"
```
Copy the password and paste it into the Jenkins UI at `http://<YOUR_VM_IP>:8080`.

### 2. Initial Setup Wizard
1.  **Plugins**: Select **"Install suggested plugins"**.
2.  **Admin User**: Create your admin account (Username, Password, Full Name, Email).
3.  **Instance Configuration**: Confirm the Jenkins URL and click **"Save and Finish"**.

### 3. Install Additional Plugins
Ensure the following plugins are installed for the MLOps pipeline:
1.  Go to **Manage Jenkins** > **Plugins** > **Available plugins**.
2.  Search and install:
    *   `Docker`
    *   `Docker Pipeline`
    *   `GCloud SDK`
    *   `Kubernetes`
3.  Click **"Install without restart"**.

### 4. Configure Credentials (CRITICAL)
You need to add two sets of credentials for the pipeline to work:

#### A. Docker Hub Credentials
1.  Go to **Manage Jenkins** > **Credentials** > **(global)** > **Add Credentials**.
2.  **Kind**: `Username with password`.
3.  **Username**: Your Docker Hub username.
4.  **Password**: Your Docker Hub Access Token (or password).
5.  **ID**: `dockerhub-credentials` (MUST match this ID exactly).
6.  **Description**: `Docker Hub Login`.
7.  Click **Create**.

#### B. GCP Service Account (for GKE)
1.  Go to **Add Credentials** again.
2.  **Kind**: `Secret file`.
3.  **File**: Upload the `gcp-key.json` file you downloaded in Phase .
4.  **ID**: `gcp-auth` (MUST match the ID in your Jenkinsfile).
5.  Click **Create**.

---

## 🚀 Phase 5: Pipeline Configuration

In this phase, we will create the actual CI/CD job in Jenkins and link it to your GitHub repository.

### 1. Create a New Pipeline Job
1.  From the Jenkins Dashboard, click **"New Item"**.
2.  **Name**: `iris-ml-cicd`.
3.  **Type**: Select **"Pipeline"**.
4.  Click **"OK"**.

### 2. General Settings
1.  In the **General** tab, check the box **"GitHub project"**.
2.  **Project url**: `https://github.com/<YOUR_USERNAME>/iris-cicd-jenkins/`.

### 3. Configure Pipeline Source
Scroll down to the **Pipeline** section:
1.  **Definition**: Select **"Pipeline script from SCM"**.
2.  **SCM**: Select **"Git"**.
3.  **Repository URL**: `https://github.com/<YOUR_USERNAME>/iris-cicd-jenkins.git`.
4.  **Branch Specifier**: `*/main` (or `*/master`).
5.  **Script Path**: `Jenkinsfile`.
6.  Click **"Save"**.

### 4. Setup GitHub Webhook (Auto-Trigger)
To make Jenkins build automatically whenever you push code:

#### In GitHub:
1.  Go to your repository **Settings** > **Webhooks** > **Add webhook**.
2.  **Payload URL**: `http://<YOUR_VM_IP>:8080/github-webhook/`.
3.  **Content type**: `application/json`.
4.  **Events**: `Just the push event`.
5.  Click **"Add webhook"**.

#### In Jenkins (Job Config):
1.  Go back to your `iris-ml-cicd` job > **Configure**.
2.  Under **Build Triggers**, check **"GitHub hook trigger for GITScm polling"**.
3.  Click **"Save"**.

---

## 🏁 Phase 6: Running the Pipeline & Verification

### 1. Trigger the Build
You can trigger the pipeline in two ways:
*   **Manual**: Click **"Build Now"** on the left sidebar of your `iris-ml-cicd` job.
*   **Automated**: Make a small change to any file (e.g., `README.md`) and push it to GitHub:
    ```bash
    git add .
    git commit -m "Test automated pipeline"
    git push origin main
    ```

### 2. Monitor Progress
Open the job and click on the current build. You can watch the **Pipeline Steps** or **Console Output**:
*   ✅ **Checkout**: Pulls code from GitHub.
*   ✅ **Train Model**: Runs `src/train_model.py`.
*   ✅ **Test Model/API**: Runs `pytest`.
*   ✅ **Build & Push**: Creates Docker image and pushes to Docker Hub.
*   ✅ **Deploy to GKE**: Uses **Helm** to deploy the app to your cluster.

### 3. Verify Deployment
Once the pipeline finishes successfully, verify the app is running on GKE.

**Note**: You must be authenticated with GCP to run these commands.
*   **On your local machine**: Run `gcloud auth login`.
*   **Using Service Account**: Run `gcloud auth activate-service-account --key-file=path/to/gcp-key.json`.

```bash
# Get credentials for your cluster
gcloud container clusters get-credentials iris-cluster --zone <YOUR_ZONE> --project <YOUR_PROJECT_ID>

# Check if pods are running
kubectl get pods

# Get the External IP of the Service
kubectl get svc iris-app
```

### 4. Test the ML API
Copy the **EXTERNAL-IP** from the `kubectl get svc` command and open it in your browser:
`http://<EXTERNAL_IP>/docs`

You can now use the FastAPI Swagger UI to send prediction requests to your Iris model!

---

## 🧹 Cleanup
To avoid ongoing GCP costs after you're done:
```bash
cd infrastructure/terraform
terraform destroy -auto-approve
```
