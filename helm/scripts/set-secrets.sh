#!/bin/bash
# Exit on any error
set -e

# sourcing the real secrets 
source "$(dirname "$0")/secrets.sh"

# working on the backend secrets 

CHART_NAME="agentkit-backend"

DEFAULT_DATABASE_HOST="${RELEASE_NAME}-${CHART_NAME}-pgvector.${NAMESPACE}.svc.cluster.local"

# PostgreSQL database connection URI for the SQL tool
DEFAULT_SQL_TOOL_DB_URI="postgresql://${POSTGRES_USERNAME}:${POSTGRES_PASSWORD}@${DEFAULT_DATABASE_HOST}/${POSTGRES_DATABASE}?connect_timeout=10"

BACKEND_SECRET_NAME="${RELEASE_NAME}-${CHART_NAME}"

# set secrets in the cluster
kubectl create secret generic $BACKEND_SECRET_NAME \
  --from-literal=OPENAI_API_KEY=$DEFAULT_OPENAI_API_KEY \
  --from-literal=OPENAI_ORGANIZATION=$DEFAULT_OPENAI_ORGANIZATION \
  --from-literal=NEXTAUTH_SECRET=$DEFAULT_NEXTAUTH_SECRET \
  --from-literal=ENCRYPT_KEY=$DEFAULT_ENCRYPT_KEY \
  --from-literal=SECRET_KEY=$DEFAULT_SECRET_KEY \
  --from-literal=MINIO_ROOT_PASSWORD=$DEFAULT_MINIO_ROOT_PASSWORD \
  --from-literal=SQL_TOOL_DB_URI=$DEFAULT_SQL_TOOL_DB_URI \
  --from-literal=DATABASE_HOST=$DEFAULT_DATABASE_HOST \
  --namespace $NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Default secrets have been set in the cluster."



# PGVector secrets
PGVECTOR_SECRET_NAME="${RELEASE_NAME}-${CHART_NAME}-pgvector"

# Create or update the pgvector secret
kubectl create secret generic $PGVECTOR_SECRET_NAME \
  --from-literal=postgres-username=$POSTGRES_USERNAME \
  --from-literal=postgres-password=$POSTGRES_PASSWORD \
  --from-literal=postgres-database=$POSTGRES_DATABASE \
  --namespace $NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secrets have been set up successfully."


# Set the release name variable - change this to your release name

CHART_NAME="agentkit-frontend"

# Front secrets
FRONT_SECRET_NAME="${FRONT_RELEASE_NAME}-${CHART_NAME}"

DB_PORT=5432

DATABASE_URL="postgresql://${POSTGRES_USERNAME}:${POSTGRES_PASSWORD}@${DEFAULT_DATABASE_HOST}:${DB_PORT}/${POSTGRES_DATABASE}?pgbouncer=true&connect_timeout=10"
DIRECT_DATABASE_URL=postgresql://${POSTGRES_USERNAME}:${POSTGRES_PASSWORD}@${DEFAULT_DATABASE_HOST}:${DB_PORT}/${POSTGRES_DATABASE}?connect_timeout=10

# set secrets in the cluster
kubectl create secret generic $FRONT_SECRET_NAME \
  --from-literal=DATABASE_URL=$DATABASE_URL \
  --from-literal=DIRECT_DATABASE_URL=$DIRECT_DATABASE_URL \
  --from-literal=NEXTAUTH_SECRET=$DEFAULT_NEXTAUTH_SECRET \
  --namespace $NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Default secrets have been set in the cluster."