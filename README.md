
# AURORA: Advanced User-driven Robotics Online Research and Assessment

AURORA is a software platform that facilitates scalable deployment of robotic simulations over the web for the Human-Robot Interaction (HRI) community. It allows researchers from different fields to easily provide HRI experiences by deploying online studies with robotic simulations paired with customizable surveys. AURORA is entirely open source and can be hosted locally, providing flexibility and control of the research environment.

The platform provides three main functionalities:
1. **Web Deployment of Simulations**: Enables researchers to deploy robotics simulations or other web-based applications online.
2. **Web Deployment of Surveys**: Allows researchers to conduct standalone surveys.
3. **Studies Integrating Simulations and Surveys**: Facilitates studies that integrate robotics simulations with surveys, providing a comprehensive HRI research experience.


![AURORA architecture](/docs/images/aurora_arch.png)


## System Requirements

Before installing AURORA, ensure you have the following tools installed.

### 1. **[Docker](https://www.docker.com/)**
Docker is a platform designed to help developers build, share, and run containerized applications. Install it using one of the following methods:

- **Windows**:
  1. Visit the [Docker installation page](https://docs.docker.com/desktop/setup/install/windows-install/).
  2. Download the installer.
  3. Run the installer and follow the setup wizard.

- **Linux**:
  1. Go to the [Docker installation page](https://docs.docker.com/desktop/setup/install/linux/).
  2. Scroll down, where you can select your distribution and follow the command-line installation steps.

- **Mac**:
  1. Visit the [Docker installation page](https://docs.docker.com/desktop/setup/install/mac-install/).
  2. Download the `.dmg` file.
  3. Open and run the installer.

### 2. **[k3d](https://k3d.io/)**
k3d is a lightweight Kubernetes implementation for local development. Choose one of the following methods to install:

- **GitHub Releases**:
  1. Visit the [k3d GitHub Releases](https://k3d.io/stable/#releases).
  2. Download the release for your system and follow the instructions.

- **Install Script**:
  1. Use `wget` or `curl` to run the [k3d install script](https://k3d.io/stable/#install-script).

- **Other Methods**:
  1. Refer to the [k3d installation documentation](https://k3d.io/stable/#other-installers) for additional OS-specific options.

### 3. **[Helm](https://helm.sh/)**
Helm is a Kubernetes package manager. You can install Helm using one of the following methods:

- **Binary Releases**:
  1. Visit the [Helm binary releases page](https://helm.sh/docs/intro/install/#from-the-binary-releases).
  2. Download and install the latest version manually.

- **Install Script**:
  1. Fetch the installation script using `curl`.
  2. Follow the [script installation instructions](https://helm.sh/docs/intro/install/#from-script).

- **Package Managers**:
  1. Use the package manager available for your OS.
  2. Check the [package manager installation guide](https://helm.sh/docs/intro/install/#through-package-managers).

### 4. **(Optional) [kubectl](https://kubernetes.io/docs/tasks/tools/)**
kubectl allows you to run commands against Kubernetes clusters. You can use kubectl to deploy applications, inspect and manage cluster resources, and view logs. You need to install it, if you want to manually deploy the AURORA platform or debug it. Install it using one of the following methods:

- **Linux**:
  - Use a [script or binary](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/).
  - Alternatively, install it via a [package manager](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-using-native-package-management).

- **Windows**:
  - [Download kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/) or use `curl`.
  - Alternatively, install it via a [package manager](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/#install-nonstandard-package-tools).

- **Mac**:
  - Use a [script or binary](https://kubernetes.io/docs/tasks/tools/install-kubectl-macos/#install-kubectl-on-macos).
  - Alternatively, install it via a [package manager](https://kubernetes.io/docs/tasks/tools/install-kubectl-macos/#install-kubectl-on-macos).


Ensure that all tools are installed and verified before proceeding with the installation of AURORA.

This platform uses Docker, providing a consistent runtime environment across different systems. As long as Docker and its prerequisites are installed, the platform should run regardless of the underlying operating system.

AURORA has been tested on Windows 10, Windows 11 (wsl) and Ubuntu 24.04.

## Installation Guide

### One-Line Installation

The easiest setup using the default configuration for local testing may be deployed using the provided install script and helm-chart. Only works on **Linux** (for now).

1. Clone this repository. (For HRI review process: The supplementary ZIP Folder, this README is in.)
2. Ensure **Docker** with **Docker Engine** is running.  
3. In the terminal, from the project's root directory, run the following command:

```
./install.sh
helm install survey-platform survey-platform-chart
```

This will set up the k3d cluster on your local machine, build, push and deploy the docker images from this repository.

Note: Make sure that your router does not block routing `localdev.me` to `127.0.0.1`. 
You may have to enable this in your router settings.

### Manual Installation

In **Windows**, **macOS** or **Linux** you also can set up AURORA manually:

1. Clone this repository. (For HRI review process: The supplementary ZIP Folder, this README is in.)
2. Ensure **Docker** with **Docker Engine** is running.  
3. In the terminal, from the project's root director, run the following commands:


#### 1. Create Kubernetes Cluster

Set up a Kubernetes cluster with a registry using k3d:

```bash
k3d cluster create -c ./config/k3d/k3d-config.yaml
```

#### 2.1 Build and Push Backend

Navigate to the `backend/` directory and run:

```bash
docker build -f Dockerfile -t localhost:5000/survey-platform-backend:latest .
docker push localhost:5000/survey-platform-backend:latest
```

#### 2.2 Build and Push jobs

Navigate to the `backend/` directory and run:

```bash
docker build -f Dockerfile.cleanup -t localhost:5000/cleanup-job:latest .
docker push localhost:5000/cleanup-job:latest
```

#### 2.3 Build and Push frontend

Navigate to the `frontend/` directory and run:

```bash
docker build -f Dockerfile -t localhost:5000/survey-platform-frontend:latest .
docker push localhost:5000/survey-platform-frontend:latest
```

#### 2.4 Build and Push survey operator

Navigate to the `survey-operator/` directory and run:

```bash
docker build -f survey.Dockerfile -t localhost:5000/survey-controller:latest .
docker push localhost:5000/survey-controller:latest
```

#### 2.5 Build and Push participation operator

Navigate to the `survey-operator/` directory and run:

```bash
docker build -f simulation.Dockerfile -t localhost:5000/simulation-orchestrator:latest .
docker push localhost:5000/simulation-orchestrator:latest
```

#### 3. Install Minio

We use MinIO for object storage within the cluster. Navigate to the root directory and run:

```bash
helm repo add minio-operator https://operator.min.io
helm install --namespace minio-operator --create-namespace operator minio-operator/operator
helm install --namespace minio-tenant --create-namespace --values ./config/minio/minio-values.yaml minio minio-operator/tenant
```

#### 4. (Optional) Installation on Server

To install AURORA on a server:

1. Ensure all [Prerequisites](#prerequisites) are met on the server.
2. Securely copy your project files to the server.
3. Follow the [Manual Installation](#manual-installation) steps on the server until step 3 [3. Install Minio](####3.-Install-Minio) 
4. Configure HTTPS 

If you want to host your application in a production environment, we strongly recommend to enable https. This requires a wildcard tls certificate for all subdomains following the scheme `*.example.com` (with `exmple.com` being your own domain). While we provide an example using [cert-manager](https://cert-manager.io/) and [letsencrypt](https://letsencrypt.org/) as a certificate provider, the wildcard subdomain requires a more complex DNS-01 challenge to be resolved (see [challenge-types](https://letsencrypt.org/docs/challenge-types/)). To resolve this challenge, you need to have API access to the dns configuration of your domain. Some DNS/domain providers are supported out of the box by cert-manager, others are included using external webhook plugins. In our example, our domain is reqistered with netcup.eu and we use the corresponding [cert-manager-webhook-netcup](https://github.com/aellwein/cert-manager-webhook-netcup) plugin. Please see the [cert-manager documentation on dns01 challenges](https://cert-manager.io/docs/configuration/acme/dns01/) and the [issuer template in our helm chart](survey-platform-chart/templates/issuer.yaml). Corresponding changes may need to be provided to the helm chart, see the next chapter.

Independent of your DNS provider, you need to add and install the cert-manager helm chart:
```
helm repo add jetstack https://charts.jetstack.io --force-update
helm install   cert-manager jetstack/cert-manager   --namespace cert-manager   --create-namespace   --version v1.16.0   --set crds.enabled=true
```

For our specific configuration using netcup.eu, the following commands need to be executed:

```
helm repo add cert-manager-webhook-netcup https://aellwein.github.io/cert-manager-webhook-netcup/charts/
kubectl create secret generic netcup-secret -n cert-manager --from-literal=customer-number=<your-netcup-customer-number> --from-literal=api-key=<your-netcup-api-key> --from-literal=api-password=<your-netcup-api-key>
helm install cert-manager-webhook-netcup cert-manager-webhook-netcup/cert-manager-webhook-netcup --namespace cert-manager
```

#### 5. Deploy Application

We provide a helm file for deployment. 
You may configure the deployment using the `survey-platform-chart/values.yaml` file. 
We recommend to change the User Name and Password for Login.
Or provide the `--values <your-values>.yaml` values option to the following command in the root directory:

```bash
helm install survey-platform survey-platform-chart
```


## Getting Started

After installation on you local machine, it will take some time until you should be able to access the researcher-dashboard by navigating in your browser to `app.localdev.me/signin`. 

### Log In

1. Log in to the application with you previous specified credentials.

![Sign In Screenshot](/docs/images/signin.jpg)


## Demo
The following demo will guide you through adding survey items, creating a survey, configuring an application, and deploying everything using AURORA.

### Step 1: Creating a New Project

1. Navigate to app.localdev.me/projects
2. Click on **Create New Project**.
3. Enter the project name and submit.

![Create Project Screenshot](/docs/images/createproject.jpg)

After creating a new project, you will see the **Researcher Dashboard**, the central hub for managing surveys, configurations and publishings:


This is the central GUI for researchers, where you can access all functionalities needed to create and deploy surveys and applications.

### Step 2: Managing Survey Items

First, navigate to the **Item Manager** by clicking on the emblem right next to the **Project Selector**:

![Item Manager Root Screenshot](/docs/images/item-manager/root.jpeg)

Navigate to **Create Item**

![Item Manager Create Screenshot](/docs/images/item-manager/create.jpeg)

Here you can create various survey items. After creating them you can edit or remove them, when you navigate to  **Manage Items

![Item Manager Manage Screenshot](/docs/images/item-manager/manage.jpeg)

### Step 3: Creating a Survey

After creating survey items, head to you project via the **Project Selector** and navigate to the  **Survey** tab and add a survey:

![Survey Manager Root Screenshot](/docs/images/survey/root.jpeg)

Once a survey is created, you can start adding pages to it:

![Survey Manager Page Screenshot](/docs/images/survey/addpage.jpeg)

If you have multiple pages, you can easily reorder or delete them to structure your survey logically:

![Survey Manager Added Page Screenshot](/docs/images/survey/addedpage.jpeg)

You can add the Items, which you have just created, to you page.

![Survey Manager Add Item Screenshot](/docs/images/survey/additem.jpeg)

After you have added Items, you can reorder or remove them from your Page:

![Survey Manager Added Items Screenshot](/docs/images/survey/addeditems.jpeg)

You can also reorder the items on each page to customize the flow of questions:
CAN YOU?

### Step 4: Previewing the Survey

After configuring your survey, you can preview it to see how it will look to participants:

![Survey Preview Screenshot](/docs/images/survey/preview.jpeg)

### Step 5: Configuring an Simulation

Next, create an **Simulation Configuration** for a ROS Gazebo web simulation. This configuration allows you to integrate the simulation into your survey:

Navigate to the Simulation Tab and submit a repository, which contains a ROS Gazebo web Simulation, after that you can Build it.

![Survey Preview Screenshot](/docs/images/simulation/root.jpeg)

As an example, we provide a reference repository at https://github.com/StarsThrowPublishedNice/gazebo-example which you can use to get started.

Clone the Git Repository URL: `https://github.com/StarsThrowPublishedNice/gazebo-example.git`, leave the authentication token empty in this case and set the branch name to `main`. Click on **Submit**.

Proceed by clicking on `Container` in the left menu. There you need to specify the containers and their port configuration required to work. 
Currently, the platform creates individual routes for each external port.

For our example repository, the following configuration results in a working simulation:
First Container:

```
Name: gzserver
Dockerfile: ./Dockerfile.gzserver
Port Mappings:
    - 11345:11345
    - 11311:11311
```

Second Container:
```
Name: gzweb
Dockerfile: ./Dockerfile.gzweb
Port Mappings:
    - 8080:8080
```

#### ros2 example project
A ros2 (humble) example project is hosted at `https://github.com/mmrrqq/gzweb-docker-test.git`.

The following configuration is necessary:

First Container:

```
Name: gzserver
Dockerfile: ./Dockerfile.gz
Port Mappings:
    - 9002:9002
```

Second Container:
```
Name: gzweb
Dockerfile: ./Dockerfile.gzweb
Port Mappings:
    - 8000:80
```

After configuration of the containers, go back to the previous page and click on build. Refreshing the page should update the status of the build.

After configuring the application, add it to a page in the **Survey Manager**:

![Simulation Container Screenshot](/docs/images/survey/addapplication.jpg)

### Step 6: Deploying the Survey

Navigate to the **Admin Dashboard**, you can deploy the survey to make it available to participants:

![Simulation Container Screenshot](/docs/images/dashboard/dashboard.jpeg)

In the publication form you can add a Name, a start and end date (when you want to publish the study directly just take the current date)

You can choose if you want to collect data. Also you can configure a redirect URL (for example to redirect back to Prolific)

When you allow anonymous participation, then you dont need parameter in the link and an ID is advised to you.
For testing we recommend using allwowing anonymous participation.

![Simulation Container Screenshot](/docs/images/dashboard/createpublication.jpeg)

Once deployed, you can access the survey via a generated link.

You should open the Link from a private Browser window, for testing.

For use with Prolific configure Prolific like this:
```bash
app.localdev.me/public/[UUID]?PARTICIPANT_ID={{%PROLIFIC_PID%}}&STUDY_ID={{%STUDY_ID%}}&SESSION_ID={{%SESSION_ID%}}
```


### Step 7: Downloading Data
While the survey is running or after its completion, you can download the survey data in the Data Hub:

You can download CSV files containing participant responses and rosbags from their interactions with the simulation. 


This demo showcases how AURORA makes it easy to manage surveys and web-based simulations in a unified platform, providing powerful tools for creating, deploying, and analyzing interactive studies.


## Specifications

### Item Manager
The Item Manager allows you to create and manage items. The types of items available include:

- **Text**: Presents informational or instructional content to participants as text, rendered in HTML to allow for diverse visual customization options.
- **Image**: Adds Images via URL.
- **Video**: Adds Videos via URL.
- **Question**: Collects participant responses through interactive formats.

#### Types of Questions

For **Question** items, the platform supports multiple formats to accommodate diverse data collection needs:

- **Open-ended Question**: Allows participants to provide free-form textual responses.
- **Multiple Choice Question**: Participants select one or more options from a predefined list.
- **Rating Scale Question**: Participants rate items along a numerical scale (e.g., from 1 to 100).
- **Matrix Question**: Participants evaluate multiple items using consistent response options in a grid format (e.g. Likert Scale).

## Example Project

We provide an example project containing ROS and a gazebo web simulation that can be cloned and deployed online using AURORA. This serves both as a test environment and a barebone framework for developing custom simulations.

## Development notes
- for local development within the cluster using `*.localdev.me`, flash notification (on entity save/update) may not work as your browser does not accept "secure" cookies using http for hosts other than `localhost`
- integrating the survey may not work when using `localhost` to access the application as cors will block all domains except the configured one
- while the helm chart configures the environment appropriately, you may have to set the following `auth.js` env variables for local development:

```
export AUTH_URL=http://api.localdev.me
export AUTH_SECRET=YOUR_SECRET
```

## Current Limitations and Future Work

- **Current Limitations**:
  - kubernetes nodes might experience disk pressure (e.g. no space left) when the host storage utilization is above 95% percent (regarless of the actual space left)

- **Future Work**:

  - There are still many features and functions we plan to implement to further support the HRI community in their research. From simplifying usage and offering more options for survey design to supporting additional simulation platforms, we aim to continuously enhance the platform. This is the first version, providing the core functionality as a foundation. We will build on this to continuously improve the AURORA platform.

## Further documentation
When the AURORA platform is running you can see further documentation about the FastAPI backend routes at:

[api.localdev.me/docs](api.localdev.me/docs)

## Code Maintenance

The code will be actively maintained, and we welcome contributions from the community. When the project is hosted on Github we will add Contribution Guidelines.

- Follow our [Contribution Guidelines](link_to_contribution_guidelines).
- Report issues via [GitHub Issues](link_to_issues_page).

## Dependencies

We use Poetry to install [dependencies](dependencies.md)

## License

For the HRI review process:
The LICENSE file can be found in the projects root directory.

This project is licensed under the [MIT License](LICENSE). 

