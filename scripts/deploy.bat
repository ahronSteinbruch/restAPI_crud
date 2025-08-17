@echo off
REM This script automates the entire deployment process for the FastAPI MongoDB service.

REM --- Configuration ---
IF "%1"=="" (
    echo ERROR: Docker Hub username must be provided as the first argument.
    echo Usage: deploy.bat ^<your-dockerhub-username^>
    exit /b 1
)
SET DOCKERHUB_USERNAME=%1
SET IMAGE_NAME=fastapi-mongo-crud

REM --- NEW: Generate a unique image tag using a timestamp ---
REM This creates a tag like YYYYMMDD-HHMMSS
FOR /f "tokens=1-4 delims=/ " %%a in ("%date%") do (
    FOR /f "tokens=1-3 delims=:" %%e in ("%time%") do (
        SET IMAGE_TAG=%%c%%b%%a-%%e%%f%%g
    )
)
echo INFO: Using unique image tag: %IMAGE_TAG%
REM -------------------------------------------------------------

SET FULL_IMAGE_NAME=docker.io/%DOCKERHUB_USERNAME%/%IMAGE_NAME%:%IMAGE_TAG%

echo.
echo ================================================================================
echo    Step 1: Building and Pushing Docker Image
echo ================================================================================
echo Image to be built: %FULL_IMAGE_NAME%
docker buildx build --no-cache --platform linux/amd64 -t "%FULL_IMAGE_NAME%" --push .
echo Image successfully pushed to Docker Hub.

echo.
echo ================================================================================
echo    Step 2: Applying Infrastructure to OpenShift
echo ================================================================================
echo INFO: Using current OpenShift project:
oc project -q

cd ..\infrastructure\k8s

echo.
echo ---^> Deploying MongoDB...
oc apply -f 01-mongo-secret.yaml
oc apply -f 02-mongo-pvc.yaml
oc apply -f 03-mongo-deployment.yaml
oc apply -f 04-mongo-service.yaml
echo Waiting for MongoDB to be ready...
oc wait --for=condition=ready pod -l app=mongo-db --timeout=300s
echo SUCCESS: MongoDB is ready.

echo.
echo ---^> Deploying FastAPI Application...
REM --- UPDATED: Use PowerShell to replace both username AND tag ---
powershell -Command "(Get-Content 05-fastapi-deployment.yaml) -replace 'YOUR_DOCKERHUB_USERNAME', '%DOCKERHUB_USERNAME%' -replace ':latest', ':%IMAGE_TAG%' | oc apply -f -"
REM -----------------------------------------------------------------
oc apply -f 06-fastapi-service.yaml
echo Waiting for FastAPI to be ready...
oc wait --for=condition=ready pod -l app=mongo-api --timeout=300s
echo SUCCESS: FastAPI Application is ready.

echo.
echo ---^> Exposing FastAPI with a Route...
oc apply -f 07-fastapi-route.yaml
echo SUCCESS: Route created.

echo.
echo ================================================================================
echo    Deployment Complete!
echo ================================================================================
FOR /F "tokens=*" %%g IN ('oc get route mongo-api-route -o jsonpath="{.spec.host}"') do (SET ROUTE_URL=%%g)
echo Your application is available at:
echo http://%ROUTE_URL%
echo.
echo Test the API by navigating to:
echo http://%ROUTE_URL%/api/v1/items