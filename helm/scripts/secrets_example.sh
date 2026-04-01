#!/bin/bash

# Set the namespace variable - change this to your namespace
NAMESPACE="akit"

# Set the release name variable - change this to your release name
RELEASE_NAME="akitback"
FRONT_RELEASE_NAME="akitfrt"

# Static default values for secret environment variables
DEFAULT_OPENAI_API_KEY="sk-Sxxxxxx"
DEFAULT_OPENAI_ORGANIZATION="org-xxxxx"
DEFAULT_NEXTAUTH_SECRET="xxxxxxx"
DEFAULT_ENCRYPT_KEY="default_encrypt_key"
DEFAULT_SECRET_KEY="default_secret_key"
DEFAULT_MINIO_ROOT_PASSWORD="default_minio_root_password"

# Database credentials
POSTGRES_USERNAME="akituser"
POSTGRES_PASSWORD="akitpassword"
POSTGRES_DATABASE="akitdatabase"

