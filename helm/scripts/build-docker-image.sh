#!/bin/bash

# This script builds the Docker image for the fastapi_server service.

# Exit on any error
set -e

# Define variables for registry, image name, and image tag
# REGISTRY=your-registry
# IMAGE_NAME=agentkitback
# IMAGE_TAG=latest

# Navigate to the backend directory where the Dockerfile is located
cd "$(dirname "$0")/../../backend"

# Build the Docker image
docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} . 

# Tag the image if needed, for example:
# No need to tag the image again as it's already tagged with the build command

# Push the image to a registry if needed, for example:
docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

echo "Docker image for fastapi_server built successfully."
