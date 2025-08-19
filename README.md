# FastAPI MongoDB CRUD Service for OpenShift

## Overview

This project provides a robust, production-ready template for deploying a Python FastAPI application with a MongoDB backend on OpenShift. Originating as an exam assignment to fetch data via a `GET` request, this project has been significantly expanded to showcase a complete, best-practice architecture for building and deploying cloud-native microservices.

The entire infrastructure is defined using declarative Kubernetes manifests and can be deployed automatically with dedicated scripts for both Linux/macOS and Windows.

### Features & Best Practices Implemented

-   **Full CRUD API:** The API was extended from a single `GET` endpoint to full Create, Read, Update, and Delete functionality.
-   **Modular API Architecture:** Uses FastAPI's `APIRouter` and a dependency injection pattern to keep API logic clean, organized, and scalable, preventing circular dependencies.
-   **High-Performance DAL:** Implements a MongoDB **Connection Pool** (managed by the async driver) in the Data Access Layer (DAL).
-   **Declarative Infrastructure (IaC):** All OpenShift/Kubernetes resources are defined in standardized YAML manifests.
-   **Dual Deployment Strategies:** Provides manifests for deploying MongoDB using both a standard `Deployment` and an advanced `StatefulSet`.
-   **Advanced Configuration Management:** Clear separation between non-sensitive configuration (`ConfigMap`) and secrets (`Secret`).
-   **Reliability & Health Monitoring:** Includes **liveness and readiness probes** for both the API and the database.
-   **Resource Management:** Defines CPU and memory `requests` and `limits` to guarantee performance and prevent resource starvation.
-   **Full Automation:** Provides cross-platform deployment scripts (`.sh` and `.bat`) for a complete, one-command setup for both deployment strategies.

---

## Project Structure & In-Depth Documentation

The project is organized into distinct directories, each with its own detailed documentation (in Hebrew).

```
.
├── app/
│   ├── core/           # Core components like shared dependencies
│   ├── crud/           # APIRouters for CRUD operations
│   ├── dal.py          # Data Access Layer (DAL)
│   ├── main.py         # Main FastAPI application entrypoint
│   ├── models.py       # Pydantic data models
│   └── README.md       # ➡️ (Hebrew) In-depth explanation of the Python code architecture
├── infrastructure/
│   └── k8s/
│       ├── README.md   # ➡️ (Hebrew) In-depth explanation of all YAML manifests
│       └── ...         # All Kubernetes/OpenShift YAML manifests
├── scripts/
│   ├── deploy.sh       # Automated deployment script (Deployment strategy)
│   └── deploy-statefulset.sh # Automated deployment script (StatefulSet strategy)
├── Dockerfile
├── demo_guide.md       # ➡️ (Hebrew) Step-by-step manual deployment & usage guide
└── README.md           # This file
```

### Navigating the Documentation

*   To understand the **Python code architecture**, read the **[Python Architecture Guide (Hebrew)](./app/README.md)**.
*   To understand the **Kubernetes/OpenShift resources**, read the **[Infrastructure Manifests Guide (Hebrew)](./infrastructure/k8s/README.md)**.
*   For a **step-by-step manual deployment tutorial**, follow the **[Manual Deployment Guide (Hebrew)](./demo_guide.md)**.

---

## Automated Deployment

For a quick setup, use the provided automation scripts from the `scripts/` directory.

### Prerequisites

1.  Access to an OpenShift cluster and the `oc` CLI.
2.  A Docker Hub account (`docker login` executed).
3.  Docker Desktop (or Docker daemon) running.

### Instructions

Run the appropriate script for your desired deployment strategy, providing your Docker Hub username as the first argument.

#### Standard Deployment
```bash
# For Linux / macOS
chmod +x scripts/deploy.sh
./scripts/deploy.sh your-dockerhub-username

# For Windows
.\scripts\deploy.bat your-dockerhub-username
```

#### StatefulSet Deployment
```bash
# For Linux / macOS
chmod +x scripts/deploy-statefulset.sh
./scripts/deploy-statefulset.sh your-dockerhub-username

# For Windows
.\scripts\deploy-statefulset.bat your-dockerhub-username
```
The script will build the image, deploy all resources, and print the final application URL.