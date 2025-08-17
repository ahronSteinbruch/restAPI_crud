#!/bin/bash
# This script deploys the application using the StatefulSet variation for MongoDB.

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
    echo "Usage: ./deploy-statefulset.sh <your-dockerhub-username>"
    exit 1
fi
DOCKERHUB_USERNAME="$1"
IMAGE_NAME="fastapi-mongo-crud"
IMAGE_TAG=$(git rev-parse --short HEAD || date +%s)
echo "INFO: Using unique image tag: $IMAGE_TAG"
FULL_IMAGE_NAME="docker.io/${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

set -e

function print_header() {
  echo ""
  echo "================================================================================
"
  echo "   $1"
  echo "================================================================================
"
}

# --- Main Script ---

# Step 1: Build and Push Docker Image
print_header "Step 1: Building and Pushing Docker Image"
(cd "$PROJECT_ROOT" && docker buildx build --no-cache --platform linux/amd64 -t "${FULL_IMAGE_NAME}" --push .)
echo "Image successfully pushed to Docker Hub."

# Step 2: Apply Infrastructure to OpenShift
print_header "Step 2: Applying StatefulSet Infrastructure to OpenShift"
echo "INFO: Using current OpenShift project: $(oc project -q)"

K8S_DIR="$PROJECT_ROOT/infrastructure/k8s"

# Apply MongoDB manifests for StatefulSet
print_header "--> Deploying MongoDB with StatefulSet..."
oc apply -f "$K8S_DIR/01-mongo-secret.yaml"
# NOTE: We DO NOT apply a separate PVC. The StatefulSet manages it.
oc apply -f "$K8S_DIR/03a-mongo-statefulset.yaml"
oc apply -f "$K8S_DIR/04a-mongo-headless-service.yaml"
echo "Waiting for MongoDB StatefulSet to be ready..."
oc wait --for=condition=ready pod -l app=mongo-db --timeout=300s
echo "SUCCESS: MongoDB is ready."

# Apply FastAPI manifests
print_header "--> Deploying FastAPI Application..."
sed -e "s|YOUR_DOCKERHUB_USERNAME|${DOCKERHUB_USERNAME}|g" \
    -e "s|:latest|:${IMAGE_TAG}|g" \
    "$K8S_DIR/05a-fastapi-deployment-for-statefulset.yaml" | oc apply -f - # Use the adapted deployment
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
