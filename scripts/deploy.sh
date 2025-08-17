#!/bin/bash
# This script automates the entire deployment process for the FastAPI MongoDB service.

# --- Configuration ---
# IMPORTANT: Before running, replace this with your actual Docker Hub username.
DOCKERHUB_USERNAME="YOUR_DOCKERHUB_USERNAME"
IMAGE_NAME="fastapi-mongo-crud"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="docker.io/${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

# Stop script on any error
set -e

# --- Functions ---
function print_header() {
  echo ""
  echo "================================================================================"
  echo "   $1"
  echo "================================================================================"
}

# --- Main Script ---

# Step 1: Build and Push Docker Image
print_header "Step 1: Building and Pushing Docker Image to Docker Hub"
echo "Image to be built: ${FULL_IMAGE_NAME}"
# Ensure you are logged into Docker Hub: docker login
docker buildx build --platform linux/amd64 -t "${FULL_IMAGE_NAME}" --push .
echo "Image successfully pushed to Docker Hub."

# Step 2: Apply Infrastructure to OpenShift
print_header "Step 2: Applying Infrastructure to OpenShift"

echo "INFO: Using current OpenShift project: $(oc project -q)"
echo "INFO: If this is not the correct project, press Ctrl+C to abort."
sleep 5

# Apply MongoDB manifests
print_header "--> Deploying MongoDB..."
oc apply -f ../infrastructure/k8s/01-mongo-secret.yaml
oc apply -f ../infrastructure/k8s/02-mongo-pvc.yaml
oc apply -f ../infrastructure/k8s/03-mongo-deployment.yaml
oc apply -f ../infrastructure/k8s/04-mongo-service.yaml
echo "Waiting for MongoDB to be ready..."
oc wait --for=condition=ready pod -l app=mongo --timeout=300s
echo "SUCCESS: MongoDB is ready."

# Apply FastAPI manifests
print_header "--> Deploying FastAPI Application..."
# We use 'sed' to replace the placeholder username in the YAML file on the fly
sed "s|YOUR_DOCKERHUB_USERNAME|${DOCKERHUB_USERNAME}|g" ../infrastructure/k8s/05-fastapi-deployment.yaml | oc apply -f -
oc apply -f ../infrastructure/k8s/06-fastapi-service.yaml
echo "Waiting for FastAPI to be ready..."
oc wait --for=condition=ready pod -l app=fastapi --timeout=300s
echo "SUCCESS: FastAPI Application is ready."

# Apply Route
print_header "--> Exposing FastAPI with a Route..."
oc apply -f ../infrastructure/k8s/07-fastapi-route.yaml
echo "SUCCESS: Route created."

# Final step: Display the route
print_header "Deployment Complete!"
ROUTE_URL=$(oc get route fastapi-route -o jsonpath='{.spec.host}')
echo "Your application is available at:"
echo "http://${ROUTE_URL}"
echo ""
echo "Test the API by navigating to:"
echo "http://${ROUTE_URL}/api/v1/items"
