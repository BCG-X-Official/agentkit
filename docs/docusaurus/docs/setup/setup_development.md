# Advanced set-ups (development)

There are two additional setups available:
1. Development set-up: Use during development so you can quickly see the changes you make reflected using hot reload.

2. Full local set-up: Use when you want to run both backend and frontend apps entirely locally without Docker. Suitable for local development without Docker, development on machines without Docker support, or quick prototyping.

## Development set-up

### Prerequisites
Before you begin, make sure you have the following installed on your machine:
- Docker: Docker: https://www.docker.com/get-started
- Node.js and pnpm: https://pnpm.io/installation

### Installation Steps

1. Copy the `.env.example` file in the root directory of the repository and change the name to .env.
   - Change the OPENAI_API_KEY and OPENAI_ORGANIZATION to your own (n.b. OPENAI_ORGANIZATION should be your OpenAI 'Organization ID', not 'Organization name'):
      ```sh
      OPENAI_API_KEY=<your_openai_api_key>
      OPENAI_ORGANIZATION=<your_openai_organization>
      ```
2. Copy the `frontend/.env.example` file in the frontend directory and change the name to `.env`. Change the `DB_PORT` and `DB_HOST` variables as follows:
   - `DB_PORT`: Change to 5732.
   - `DB_HOST`: Change to localhost

   If needed, change the following variable (not required for a succesfull demo installation):
   - `NEXT_PUBLIC_USE_AUTH`: Set to `true` if you would like to add an identity layer using Next Auth.
   - `NEXTAUTH_SECRET`: Generate a secret key and replace `# TODO: Generate a secret and add it here` with the secret key.
   - `NEXTAUTH_URL` and `NEXTAUTH_URL_INTERNAL`: Set to `http://localhost:3000`
   - `GITHUB_ID` and `GITHUB_SECRET`: If you want to enable GitHub authentication, replace the corresponding values with your GitHub app credentials.
   - `DB_USER`, `DB_PASSWORD`, `DB_HOST`,`DB_USER`,`DB_PORT` and `DB_NAME`: If you want to customize the database connection settings, update these values accordingly.

3. Build and start the Docker containers with
   ```
   docker-compose -f docker-compose-development.yml up -d
   ```

4. Navigate to the `frontend` directory and install the frontend app's dependencies and set up prisma using pnpm:
   ```
   pnpm install
   pnpm prisma:generate
   ```

5. Once the dependencies are installed, start the frontend app:
   ```
   pnpm dev
   ```

The frontend app (Next.js) will now be running locally at http://localhost:3000. The backend app (FastAPI) is still running inside the Docker container and can be accessed at http://localhost/api/v1.

Additional notes:
- The backend app will automatically reload whenever you make changes to the source code inside the `backend/app` directory. You can see the changes reflected by refreshing the backend app in your browser.
- The frontend app (Next.js) will also automatically reload whenever you make changes to the source code inside the `frontend` directory. You can see the changes reflected by refreshing the frontend app in your browser.
- (Optional) If you want to enable debug mode for the backend to set breakpoints, you can change the `command` in `docker-compose-development.yml` for the `fastapi_server`. Once changed, the backend will not start up fully after running `docker-compose -f docker-compose-development.yml up -d`. You will have to "attach to the process", in order to set breakpoints. For example you can use the predefined command "Debug: Attach to FastAPI Docker" in `.vscode/launch.json` to attach with VSCode.

## Full local set-up

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
   poetry install --with dev
   ```

4. In the root folder (make sure .env variables are applied):
   ```sh
   uvicorn "app.main:app" "--app-dir" "backend/app" "--reload" "--workers" "1" "--host" "0.0.0.0" "--port" "9090"
   ```

5. If you visit http://localhost:3000, you should be able to see the application!


## (Optional) Pre-commit

We are using pre-commit to automatically run some hygiene checks. Install this by running `make install-pre-commit`

There is also a dockerized service that can be run using `docker-compose run pre-commit`

To link this from a local python installation, run:
```sh
pip install pre-commit
cp pre-commit/.pre-commit-config.yaml .
pre-commit install
```

## (Optional) Pytest

Make sure to have the poetry dependencies installed with the `--with dev` flag.
Run the following commands to execute the tests:
```python3.10
cd backend/app
poetry run python3.10 -m pytest -c tests/pytest.ini
```
