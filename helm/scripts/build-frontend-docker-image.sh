#!/bin/bash

# This script builds the Docker image for the nextjs_server service.

# Exit on any error
set -e

# REGISTRY=your-registry
# IMAGE_NAME=agentkitfrt
# IMAGE_TAG=latest
# NEXT_PUBLIC_API_URL='http://somehere.com/api/v1'

# Navigate to the frontend directory where the Dockerfile is located
cd "$(dirname "$0")/../../frontend"


NEXT_PUBLIC_API_URL="http://whereyouylikeit/api/v1"
NEXTAUTH_URL="http://localhost:3000"
GITHUB_ID=""
GITHUB_SECRET=""



# Build the Docker image
docker buildx build --no-cache --platform linux/amd64 \
  --build-arg NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL} \
  --build-arg NEXTAUTH_URL=${NEXTAUTH_URL} \
  --build-arg GITHUB_ID=${GITHUB_ID} \
  --build-arg GITHUB_SECRET=${GITHUB_SECRET} \
  -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .

# Push the image to a registry if needed, for example:
docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

echo "Docker image ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} built successfully."
