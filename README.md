# 🛠️ Jenkins UI Setup Guide

## Step 1: Run Jenkins Container and Login Configuration Instructions

Run this command in your terminal (PowerShell or Git Bash on Windows):

**Run Docker Compose:**
```powershell
# Navigate to the jenkins directory
cd jenkins

# Start Jenkins
docker-compose up -d

# Verify that the container is running
docker ps
```

**Wait 30-60 seconds** for Jenkins to complete its startup.

---

## Step 1.1: Log in to Jenkins

Access: **http://localhost:8080**

### **First-time Jenkins Setup**

If this is your first time, Jenkins will ask for the **Initial Admin Password**:

```powershell
# Retrieve the initial admin password
docker exec jenkins-server cat /var/jenkins_home/secrets/initialAdminPassword
```

**Example Output:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Steps:**
1. Copy the password from the terminal.
2. Paste it into the **Administrator password** field on the Jenkins UI.
3. Click **Continue**.
4. Select **Install suggested plugins** (or **Select plugins to install** for customization).
5. Wait for the plugins to install.
6. Create an **Admin User** (username, password, email).
7. Click **Save and Continue** → **Start using Jenkins**.

---

## Step 2: Install Plugins

1. Go to **Manage Jenkins** (left sidebar).
2. Click **Plugins** (or **Manage Plugins**).
3. Select the **Available plugins** tab.
4. Search for and check the following plugins:
   - **Git plugin** 
   - **GitHub plugin**
   - **Docker plugin**
   - **Docker Pipeline**
   - **Pipeline**
   - **Pipeline: Stage View**

5. Click **Install** (no restart required).
6. Wait for the installation to complete.

---

## Step 3: Configure Docker Hub Credentials 

1. Go to **Manage Jenkins** → **Credentials**.
2. Click on the **(global)** domain.
3. Click **Add Credentials** (left side).
4. Fill in the information:
   - **Kind**: `Username with password`
   - **Scope**: `Global`
   - **Username**: `<your-dockerhub-username>`
   - **Password**: `<your-dockerhub-password or access-token>`
   - **ID**: `dockerhub-credentials` (IMPORTANT - must match this name exactly)
   - **Description**: `Docker Hub Credentials`
5. Click **Create**.

### How to get a Docker Hub Access Token:
1. Log in to https://hub.docker.com.
2. Go to **Account Settings** → **Security** → **Access Tokens**.
3. Click **Generate New Token**.
4. Copy the token and use it as your password.

---

## Step 4: Create a Pipeline Job 

1. From the Dashboard, click **New Item** (left side).
2. Fill in the information:
   - **Enter an item name**: `iris-ml-cicd` (or your preferred name)
   - **Type**: Select **Pipeline**.
3. Click **OK**.

---

## Step 5: Configure the Pipeline 

### A. General Section:
- Check **GitHub project**.
- **Project url**: `https://github.com/<your-username>/<your-repo>/`

### B. Build Triggers:
- Check **GitHub hook trigger for GITScm polling**.
  (To receive triggers from GitHub webhooks)

### C. Pipeline Section:
- **Definition**: Select `Pipeline script from SCM`.
- **SCM**: Select `Git`.
- **Repository URL**: `https://github.com/<your-username>/<your-repo>.git`
- **Credentials**: 
  - For public repos: leave empty.
  - For private repos: Add GitHub credentials.
- **Branch Specifier**: `*/main` (or `*/master` if using the master branch).
- **Script Path**: `Jenkinsfile`

### D. Save Configuration:
Click **Save** at the bottom of the page.

---

## Step 6: Update Jenkinsfile with Docker Hub Username 

1. Open the file `Jenkinsfile`.
2. Find the line:
   ```groovy
   DOCKER_IMAGE = 'your-dockerhub-username/iris-ml-api'
   ```
3. Replace `your-dockerhub-username` with your actual username:
   ```groovy
   DOCKER_IMAGE = 'myusername/iris-ml-api'
   ```
4. Save the file.

---

## Step 7: Push Code to GitHub 

```bash
# Initialize git (if not already done)
git init

# Add remote repository
git remote add origin https://github.com/<your-username>/<your-repo>.git

# Add and commit
git add .
git commit -m "Setup CI/CD pipeline with Jenkins"

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 8: Setup GitHub Webhook 

### Option A: Public Jenkins (with a domain or public IP)
1. Go to your GitHub repository → **Settings** → **Webhooks** → **Add webhook**.
2. Fill in:
   - **Payload URL**: `http://your-jenkins-url:8080/github-webhook/`
   - **Content type**: `application/json`
   - **Which events**: `Just the push event`
   -  Active
3. Click **Add webhook**.

### Option B: Local Jenkins (using ngrok) 

**If Jenkins is running on your local machine:**

1. Download ngrok: https://ngrok.com/download.
2. Run ngrok:
   ```bash
   ngrok http 8080
   ```
3. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`).
4. In the GitHub webhook settings, use: `https://abc123.ngrok.io/github-webhook/`

**Note**: The URL will change each time you restart ngrok (on the free version).

---

## Step 9: Test Pipeline Manually 

1. Go to the `iris-ml-cicd` job in Jenkins.
2. Click **Build Now**.
3. View **Console Output** to track progress.
4. The pipeline will run through the following stages:
   - ✅ Checkout
   - ✅ Setup Python Environment
   - ✅ Train Model
   - ✅ Test Model
   - ✅ Test API
   - ✅ Build Docker Image
   - ✅ Push to Docker Hub
   - ✅ Cleanup

---

## Step 10: Test GitHub Webhook 

1. Make a change to any file in the repo (e.g., README.md).
2. Commit and push:
   ```bash
   git add .
   git commit -m "Test webhook trigger"
   git push
   ```
3. Jenkins will **AUTOMATICALLY** trigger a build!
4. Check the Jenkins Dashboard.

---

## Troubleshooting

### Jenkins not building Docker image:
```bash
# Check if Jenkins has access to Docker
docker exec jenkins-server docker ps
```

### Permission denied when building:
```bash
docker exec -u root jenkins-server chmod 666 /var/run/docker.sock
docker exec -u root jenkins-server chown -R jenkins:jenkins /var/jenkins_home
```

### GitHub webhook not triggering:
- Check webhook delivery in GitHub Settings → Webhooks → Recent Deliveries.
- Ensure the Jenkins URL is accessible from the internet (use ngrok if local).
- Ensure "GitHub hook trigger" is checked in the job configuration.

### Build fails at "Push to Docker Hub" stage:
- Verify the credentials ID is exactly `dockerhub-credentials`.
- Log in to Docker Hub and check if the token is still valid.
- Try logging in manually: `docker login`.

### Python tests fail:
```bash
# Check if requirements.txt is complete
# Check Python version (requires >= 3.8)
```

---

## Results

After the setup is complete:
1. Every code push automatically triggers a Jenkins build.
2. The model is trained and tested.
3. The API is tested.
4. The Docker image is built and pushed to Docker Hub.
5. You can pull and run it: 
   ```bash
   docker pull your-username/iris-ml-api:latest
   docker run -p 8000:8000 your-username/iris-ml-api:latest
   ```
6. Access: http://localhost:8000/docs to test the API.
