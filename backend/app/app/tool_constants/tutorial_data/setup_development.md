# Development Setup (hot reload)

There are two additional setups available in this development setup guide:
1. Local frontend mode: This allows for an easy set-up, while having the flexibility of local development tools for the frontend.

2. Full Local Mode: Use when you want to run both backend and frontend apps entirely locally without Docker. Suitable for local development without Docker, development on machines without Docker support, or quick prototyping.

## Local frontend

### Prerequisites
Before you begin, make sure you have the following installed on your machine:
- Docker: Docker: https://www.docker.com/get-started
- Node.js and pnpm: https://pnpm.io/installation

### Installation Steps

1. Clone the repository containing the source code for the backend and frontend apps.

2. Copy the `.env.example` file in the root directory of the repository and change the name to .env.
   - Change the OPENAI_API_KEY and OPENAI_ORGANIZATION to your own (n.b. OPENAI_ORGANIZATION should be your OpenAI 'Organization ID', not 'Organization name'):
      ```sh
      OPENAI_API_KEY=<your_openai_api_key>
      OPENAI_ORGANIZATION=<your_openai_organization>
      ```
3. Copy the `frontend/.env.example` file in the frontend directory and change the name to `.env`. Change the `DB_PORT` and `DB_HOST` variables as follows:
   - `DB_PORT`: Change to 5732.
   - `DB_HOST`: Change to localhost

   If needed, change the following variable (not required for a succesfull demo installation):
   - `NEXT_PUBLIC_USE_AUTH`: Set to `true` if you would like to add an identity layer using Next Auth.
   - `NEXTAUTH_SECRET`: Generate a secret key and replace `# TODO: Generate a secret and add it here` with the secret key.
   - `GITHUB_ID` and `GITHUB_SECRET`: If you want to enable GitHub authentication, replace the corresponding values with your GitHub app credentials.
   - `DB_USER`, `DB_PASSWORD`, `DB_HOST`,`DB_USER`,`DB_PORT` and `DB_NAME`: If you want to customize the database connection settings, update these values accordingly.

4. In the root directory, create a file `docker-compose-local.yml` and paste the docker setup template from below:
   <details><summary>docker-compose-local.yml</summary>

      ```sh
      version: '3.8'

      services:
        fastapi_server:
          container_name: fastapi_server
          build: ./backend
          restart: always
          command: "sh -c 'alembic upgrade head && uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 9090'"
          volumes:
            - ./backend/app:/code
          expose:
            - 9090
          env_file: ".env"
          depends_on:
            - database

        database:
          image: ankane/pgvector:v0.4.1
          restart: always
          container_name: database
          env_file: ".env"
          user: root
          volumes:
            - ./db_docker:/var/lib/postgresql
            - ./scripts/create-dbs.sql:/docker-entrypoint-initdb.d/create-dbs.sql
          ports:
            - 5732:5432 # Remove this on production, use same port as in .env for fastapi_db
          expose:
            - 5732
          environment:
            - POSTGRES_USERNAME=${DATABASE_USER}
            - POSTGRES_PASSWORD=${DATABASE_PASSWORD}
            - POSTGRES_DATABASE=${DATABASE_NAME}
            - POSTGRES_HOST_AUTH_METHOD= "trust"

        redis_server:
          image: redis:alpine
          container_name: redis_server
          restart: always
          ports:
            - 6379:6379 # Remove this on production
          expose:
            - 6379
          env_file: .env
        langchain-playground:
          image: langchain/${_LANGSMITH_IMAGE_PREFIX-}langchainplus-playground@sha256:f61ce9762babcb4a51af3e5b0cc628453ac7087237c5fc8694834de49b56d16e
        langchain-frontend:
          image: langchain/${_LANGSMITH_IMAGE_PREFIX-}langchainplus-frontend@sha256:e0ab157b2b9cb7f75743d45237f0d8ede75a3811d913f234585484255afe5b5a
          ports:
            - 9091:80
          expose:
            - 9091
          environment:
            - NEXT_PUBLIC_BACKEND_URL=http://langchain-backend:1984
          depends_on:
            - langchain-backend
            - langchain-playground
          volumes:
            - ./conf/nginx.conf:/etc/nginx/default.conf:ro
        langchain-backend:
          image: langchain/${_LANGSMITH_IMAGE_PREFIX-}langchainplus-backend@sha256:1196c12308b450548195c10927d469963c7d8e62db0e67f8204c83adb91f9031
          environment:
            - PORT=1984
            - LANGCHAIN_ENV=local_docker
            - LOG_LEVEL=warning
            - OPENAI_API_KEY=${OPENAI_API_KEY}
          ports:
            - 1984:1984
          depends_on:
            - langchain-db
            - langchain-redis
        langchain-db:
          image: postgres:14.1
          command:
            [
              "postgres",
              "-c",
              "log_min_messages=WARNING",
              "-c",
              "client_min_messages=WARNING"
            ]
          environment:
            - POSTGRES_PASSWORD=postgres
            - POSTGRES_USER=postgres
            - POSTGRES_DB=postgres
          volumes:
            - langchain-db-data:/var/lib/postgresql/data
          ports:
            - 5433:5432
        langchain-redis:
          image: redis:7
          ports:
            - 63791:6379
          volumes:
            - langchain-redis-data:/data
        langchain-queue:
          image: langchain/${_LANGSMITH_IMAGE_PREFIX-}langchainplus-backend@sha256:1196c12308b450548195c10927d469963c7d8e62db0e67f8204c83adb91f9031
          environment:
            - LANGCHAIN_ENV=local_docker
            - LOG_LEVEL=warning
          entrypoint: "rq worker --with-scheduler -u redis://langchain-redis:6379 --serializer lc_database.queue.serializer.ORJSONSerializer --worker-class lc_database.queue.worker.Worker --connection-class lc_database.queue.connection.RedisRetry --job-class lc_database.queue.job.AsyncJob"
          depends_on:
            - langchain-redis
        langchain-hub:
          image: langchain/${_LANGSMITH_IMAGE_PREFIX-}langchainhub-backend@sha256:73b4c2c3e7cd81729e766bb4eece2b28883bebf7c710567a21d1a6c114abff5a
          environment:
            - PORT=1985
            - LANGCHAIN_ENV=local_docker
            - LOG_LEVEL=warning
          ports:
            - 1985:1985
          depends_on:
            - langchain-db
            - langchain-redis
        caddy_reverse_proxy:
          container_name: caddy_reverse_proxy
          image: caddy:alpine
          restart: always
          ports:
            - 80:80
            - 9090:9090
            - 443:443
          environment:
            - EXT_ENDPOINT1=${EXT_ENDPOINT1}
            - LOCAL_1=${LOCAL_1}
            - LOCAL_2=${LOCAL_2}
          volumes:
            - ./caddy/Caddyfile:/etc/caddy/Caddyfile
            #- ./static:/code/static
            - caddy_data:/data
            - caddy_config:/config

      volumes:
        caddy_data:
        caddy_config:
        langchain-db-data:
        langchain-redis-data:
      ```
</details>

5. In the terminal, navigate to the root directory of the cloned repository. Build and start the Docker containers using the created `docker-compose-local.yml` configuration file:
   ```
   docker-compose -f docker-compose-local.yml up -d
   ```

6. Wait for the containers to build and start. This may take a few minutes depending on your system. While the Docker containers are running, open a new terminal window and navigate to the `frontend` directory.

7. Install the frontend app's dependencies and set up prisma using pnpm:
   ```
   pnpm install
   pnpm prisma:generate
   ```

8. Once the dependencies are installed, start the frontend app:
   ```
   pnpm dev
   ```

9. The frontend app (Next.js) will now be running locally at http://localhost:3000. The backend app (FastAPI) is still running inside the Docker container and can be accessed at http://localhost/api/v1.

10. You have successfully installed and run the apps using Docker for the backend and running the frontend locally with Next.js and pnpm! You can go to http://localhost:3000 to try AgentKit.

Additional notes:
- The backend app will automatically reload whenever you make changes to the source code inside the `backend/app` directory. You can see the changes reflected by refreshing the backend app in your browser.
- The frontend app (Next.js) will also automatically reload whenever you make changes to the source code inside the `frontend` directory. You can see the changes reflected by refreshing the frontend app in your browser.

Remember to stop the Docker containers when you're done:
```
docker-compose -f docker-compose-local-frontend.yml down
```

### Langchain tracing (Langsmith)

See https://docs.smith.langchain.com/ on how to set up LangSmith. Once you have set up LangSmith and the .env variables, you will be able to see the AgentKit traces in LangSmith.


## Full local mode setup (for non-docker users)

### Prerequisites
Version requirements:
* Python: **Python>=3.10**
* Poetry: **>=1.4.2**
* Nodejs: **>=18.16.0**

1. Make sure to create a postgresql database with the name *fastapi_db** (e.g. by running the script `/scripts/create_dbs.sql`).
Set up the .env files from the examples and change the database url in the .env file to:

   - for /frontend/.env file: Use /frontend/.env.example as an example and change the DB_PORT and possibly any other variables to your own:
      - `DB_PORT`: Change to 5732.
      - If needed, also change the following variables to your own:
         ```sh
         DB_USER=postgres
         DB_PASSWORD=postgres
         DB_HOST=database
         DB_PORT=5432
         DB_NAME=fastapi_db
         ```

   - for .env file: (use .env.example as an example) but change the DATABASE_HOST and DATABASE_PORT to your own
   ```sh
   DATABASE_HOST=<your_host>
   DATABASE_USER=postgres
   DATABASE_PASSWORD=postgres
   DATABASE_NAME=fastapi_db
   DATABASE_PORT=<your_port>
   ```
   - Also, change the OPENAI_API_KEY and OPENAI_ORGANIZATION to your own:
   ```sh
   OPENAI_API_KEY=<your_openai_api_key>
   OPENAI_ORGANIZATION=<your_openai_organization>
   ```

   Finally, apply the .env variables:
   ```sh
   export $(grep -v '^#' .env | sed 's/#.*$//' | xargs)
   ```

2. In the frontend folder:
   install dependencies and run the application:
   ```sh
   pnpm install
   ```
   then run the application:
   ```sh
   pnpm prisma:generate
   pnpm dev
   ```

3. In the backend/app folder:
   ```sh
   poetry config --local virtualenvs.in-project true
   poetry env use 3.10
   poetry install
   ```

4. In the root folder (make sure .env variables are applied):
   ```sh
   uvicorn "app.main:app" "--app-dir" "backend/app" "--reload" "--workers" "1" "--host" "0.0.0.0" "--port" "9090"
   ```

5. If you visit http://localhost:3000, you should be able to see the application!
