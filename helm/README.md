
# Helm Charts Documentation

This documentation covers the deployment process for the backend and frontend Agentkit services using Helm charts. 
Below are the steps to follow for building Docker images and managing deployments with Helm.

Pre-requisites:

- Have Docker registry availlable to push the images
- Have Kubectl & Helm installed on your machine
- Have a Kubernetes cluster available and connectable from your machine

- Know what namespace you will use to deploy your services. In this documentation, we will use the namespace `akit` as an example. 
- Define the name of the release you want to use for backend and frontend services. In this documentation, we will use `akitfrt` and `akitback` as examples.




## Backend Service

### Building the Docker Image

To build the Docker image for the backend service, you need to run the following commands. 
Use the script `bash helm/scripts/build-docker-image.sh` for reference if needed.

```shell

# Define variables for registry, image name, and image tag
REGISTRY=your-registry
IMAGE_NAME=akitbackend
IMAGE_TAG=latest 

# Navigate to the backend directory where the Dockerfile is located
cd "$(dirname "$0")/../../backend"

# Build the Docker image
docker build -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .

# Push the image to the registry 
docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

```


### Deploying with Helm

After building the image, use the following Helm commands to manage your deployment:

```shell
# For the first time deployment
helm install -n akit akitback helm/backend 

# Updating the deployment
helm upgrade -n akit akitback helm/backend 
```

You may want to configure the deployment using a custom `values.yaml` file, by using --values flag in the Helm commands.

Alternatively, you can set the values directly in the command line; ex : `--set image.repository=your-registry/akitbackend,image.tag=latest`


## Frontend Service

### Building the Docker Image

To build the Docker image for the frontend service :

```shell
REGISTRY=your-registry 
IMAGE_NAME=agentkitfrt
IMAGE_TAG=latest


# Navigate to the frontend directory where the Dockerfile is located
cd "$(dirname "$0")/../../frontend"

# Build the Docker image
docker buildx build --no-cache --platform linux/amd64 -t ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .

# Push the image to a registry if needed, for example:
docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

echo "Docker image ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} built successfully."
```

### Deploying with Helm

Use the following Helm commands for the frontend service:

```shell
# For the first time deployment
helm install -n akit akitfrt helm/frontend 

# Updating the deployment
helm upgrade -n akit akitfrt helm/frontend  
```

## Secrets Management

Secrets should be managed securely and not stored in version control. Use Kubernetes secrets or a third-party secrets manager to inject secrets into your deployments.

You can use the script [set-secrets.sh](helm/scripts/set-secrets.sh) to create secrets in your Kubernetes cluster.

```shell
# copy the example secrets file
cp helm/scripts/secrets_example.sh helm/scripts/secrets.sh
# edit the secrets.sh file with your secrets
bash set-secrets.sh
```

Be carefull to match the namespace and the release name you are using for your deployment. In our example, the `secrets.sh` file should start like this:

```shell
# Set the namespace variable - change this to your namespace
NAMESPACE="akit"

# Set the release name variable - change this to your release name
RELEASE_NAME="akitback"
FRONT_RELEASE_NAME="akitfrt"
# rest of the file ...
```



## Routing and Ingress

Ingress routes should be defined to expose the services. Configure the `ingress.yaml` within each chart to specify the hostnames and paths for routing.

## Optional Dependencies

The backend service may optionally depend on `pgvectordb` and `rediscache`. These dependencies can be managed as sub-charts or separate deployments. Ensure that the connection details are configured correctly in the `values.yaml` file of the backend service.

To include these dependencies, set the appropriate flags in the `values.yaml` file or pass them as parameters during the Helm install/upgrade commands.

```shell
helm install backend-chart ./backend --set pgvectordb.enabled=true,rediscache.enabled=true
```

For more detailed configuration, refer to the individual chart `values.yaml` files.

