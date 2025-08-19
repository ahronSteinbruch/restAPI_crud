# Stage 1: Use an official Python runtime as a parent image.
# Using a 'slim' version is a good practice as it reduces the final image size.
FROM python:3.11-slim

# Set the working directory inside the container to /data_loader.
# All subsequent commands (COPY, RUN, CMD) will be executed from this path.
WORKDIR /app

# Copy the dependencies file to the working directory.
# We copy this file first to leverage Docker's layer caching.
# If this file doesn't change, Docker will reuse the cached layer where dependencies are installed,
# speeding up subsequent builds.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt.
# --no-cache-dir reduces layer size.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire 'data_loader' directory (our source code) into the container at /data_loader/data_loader.
COPY ./services /app/services

# Expose port 8080 to the outside world. This is a common convention for cloud platforms
# like OpenShift, which often expect applications to listen on this port.
EXPOSE 8080

# The command to run the application when the container starts.
# We bind to '0.0.0.0' to make the server accessible from outside the container.
# The path to the data_loader object is 'data_loader.main:data_loader'.
CMD ["uvicorn", "services.data_loader.main:app", "--host", "0.0.0.0", "--port", "8080"]
