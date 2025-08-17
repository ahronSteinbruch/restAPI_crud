
```markdown
# FastAPI MongoDB CRUD Service for OpenShift

## 1. Overview

This project is a complete, production-ready microservice built with FastAPI. It provides a full CRUD (Create, Read, Update, Delete) API for managing "item" documents stored in a MongoDB database.

The entire infrastructure, including the MongoDB database and the FastAPI application, is designed to be deployed and managed on an OpenShift cluster using declarative YAML manifests and a fully automated deployment script. The project emphasizes clean architecture, security best practices (using Secrets), and automation.

This repository serves as a comprehensive template and guide for deploying stateful Python applications on OpenShift.

## 2. Core Technologies

- **Backend Framework**: Python 3.11 with **FastAPI**
- **Database**: **MongoDB** (deployed on OpenShift)
- **Asynchronous Driver**: **Motor**
- **Object-Document Mapper (ODM)**: **Beanie**
- **Containerization**: **Docker**
- **Orchestration Platform**: **OpenShift** / Kubernetes

## 3. Project Structure

The project follows a clean architecture to separate concerns:

```text
fastapi-mongo-crud/
├── app/                  # Contains all the application source code
│   ├── api/              # API endpoint routers (e.g., items.py)
│   ├── core/             # Application settings and configuration
│   ├── db/               # Database connection logic
│   └── models/           # Data models and schemas (Beanie/Pydantic)
├── docs/                 # In-depth guides explaining each development stage
├── infrastructure/
│   └── k8s/              # All OpenShift/Kubernetes YAML manifests
├── scripts/
│   ├── deploy.bat        # Automated deployment script for Windows
│   └── deploy.sh         # Automated deployment script for Linux/macOS
├── .gitignore
├── Dockerfile
└── requirements.txt
```

## 4. Deployment to OpenShift (Automated)

This project is designed to be deployed from start to finish with a single script.

### Prerequisites

1.  Access to an OpenShift cluster.
2.  The `oc` (OpenShift CLI) command-line tool installed and authenticated.
3.  A Docker Hub account.
4.  Docker Desktop (or Docker daemon) installed, running, and authenticated (`docker login`).

### Deployment Steps

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd fastapi-mongo-crud
    ```

2.  **Select Your OpenShift Project:**
    Ensure you are in the correct OpenShift project where you want to deploy the resources.
    ```bash
    # View available projects
    oc projects
    
    # Switch to your desired project
    oc project <your-project-name>
    ```

3.  **Run the Deployment Script:**
    Execute the script from the root directory of the project. It will handle everything: building and pushing the image, and applying all the OpenShift manifests.

    First, make the script executable:
    ```bash
    chmod +x scripts/deploy.sh
    ```
    Then, run it from the project root directory, **providing your Docker Hub username as an argument**:
    ```bash
    ./scripts/deploy.sh your-dockerhub-username
    ```
    The script will guide you through the process and print the final application URL upon completion.

## 5. API Endpoints

Once deployed, the service will be available at the URL provided by the script. The API endpoints are under the `/api/v1/items` prefix.

| Method | Path                  | Description                |
|--------|-----------------------|----------------------------|
| `POST` | `/`                   | Create a new item.         |
| `GET`  | `/`                   | Retrieve all items.        |
| `GET`  | `/{item_id}`          | Retrieve a single item.    |
| `PUT`  | `/{item_id}`          | Update an existing item.   |
| `DELETE`| `/{item_id}`          | Delete an item.            |

You can access the interactive Swagger UI documentation at `http://<your-route-url>/docs`.

## 6. Development Stages Documentation

For a detailed, step-by-step explanation of how this project was built, including technical decisions and alternatives considered, please refer to the guides in the `/docs` directory.
```
