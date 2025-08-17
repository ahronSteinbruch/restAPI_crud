#!/bin/bash
# This script automates the entire deployment process for the FastAPI MongoDB service.

# --- Setup: Find the project's root directory ---
PROJECT_ROOT=$(git rev-parse --show-toplevel)
if [ -z "$PROJECT_ROOT" ]; then
    echo "ERROR: This is not a git repository. Cannot determine project root."
    exit 1
fi
echo "INFO: Project root identified at: $PROJECT_ROOT"

# --- Configuration ---
if [ -z "$1" ]; then
    echo "ERROR: Docker Hub username must be provided as the first argument."
    echo "Usage: ./deploy.sh <your-dockerhub-username>"
    exit 1
fi
DOCKERHUB_USERNAME="$1"
IMAGE_NAME="fastapi-mongo-crud"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="docker.io/${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

set -e

function print_header() {
  echo ""
  echo "================================================================================"
  echo "   $1"
  echo "================================================================================"
}

# --- Main Script ---

# Step 1: Build and Push Docker Image (Run from project root)
print_header "Step 1: Building and Pushing Docker Image"
echo "Image to be built: ${FULL_IMAGE_NAME}"
(cd "$PROJECT_ROOT" && docker buildx build --platform linux/amd64 -t "${FULL_IMAGE_NAME}" --push .)
echo "Image successfully pushed to Docker Hub."

# Step 2: Apply Infrastructure to OpenShift
print_header "Step 2: Applying Infrastructure to OpenShift"
echo "INFO: Using current OpenShift project: $(oc project -q)"

K8S_DIR="$PROJECT_ROOT/infrastructure/k8s"

# Apply MongoDB manifests
print_header "--> Deploying MongoDB..."
oc apply -f "$K8S_DIR/01-mongo-secret.yaml"
oc apply -f "$K8S_DIR/02-mongo-pvc.yaml"
oc apply -f "$K8S_DIR/03-mongo-deployment.yaml"
oc apply -f "$K8S_DIR/04-mongo-service.yaml"
echo "Waiting for MongoDB to be ready..."
oc wait --for=condition=ready pod -l app=mongo-db --timeout=300s
echo "SUCCESS: MongoDB is ready."

# Apply FastAPI manifests
print_header "--> Deploying FastAPI Application..."
sed "s|YOUR_DOCKERHUB_USERNAME|${DOCKERHUB_USERNAME}|g" "$K8S_DIR/05-fastapi-deployment.yaml" | oc apply -f -
oc apply -f "$K8S_DIR/06-fastapi-service.yaml"
echo "Waiting for FastAPI to be ready..."
oc wait --for=condition=ready pod -l app=mongo-api --timeout=300s
echo "SUCCESS: FastAPI Application is ready."

# Apply Route
print_header "--> Exposing FastAPI with a Route..."
oc apply -f "$K8S_DIR/07-fastapi-route.yaml"
echo "SUCCESS: Route created."

# Final step: Display the route
print_header "Deployment Complete!"
ROUTE_URL=$(oc get route mongo-api-route -o jsonpath='{.spec.host}')
echo "Your application is available at:"
echo "http://${ROUTE_URL}"
echo ""
echo "Test the API by navigating to:"
echo "http://${ROUTE_URL}/api/v1/items"