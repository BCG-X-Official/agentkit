#!/usr/bin/make

include .env

define SERVERS_JSON
{
	"Servers": {
		"1": {
			"Name": "fastapi-alembic",
			"Group": "Servers",
			"Host": "$(DATABASE_HOST)",
			"Port": 5432,
			"MaintenanceDB": "postgres",
			"Username": "$(DATABASE_USER)",
			"SSLMode": "prefer",
			"PassFile": "/tmp/pgpassfile"
		}
	}
}
endef
export SERVERS_JSON

help:
	@echo "make"
	@echo "    install"
	@echo "        Install all packages of poetry project locally."
	@echo "    run-dev-build"
	@echo "        Run development docker compose and force build containers."
	@echo "    run-dev"
	@echo "        Run development docker compose."
	@echo "    stop-dev"
	@echo "        Stop development docker compose."
	@echo "    run-prod"
	@echo "        Run production docker compose."
	@echo "    stop-prod"
	@echo "        Run production docker compose."
	@echo "    init-db"
	@echo "        Init database with sample data."
	@echo "    add-dev-migration"
	@echo "        Add new database migration using alembic."
	@echo "    formatter"
	@echo "        Apply black formatting to code."
	@echo "    lint"
	@echo "        Lint code with ruff, and check if black formatter should be applied."
	@echo "    lint-watch"
	@echo "        Lint code with ruff in watch mode."
	@echo "    lint-fix"
	@echo "        Lint code with ruff and try to fix."

install:
	cd backend/app && \
	poetry shell && \
	poetry install

run-dev-build:
	docker compose -f docker-compose-dev.yml up --build

run-dev:
	docker compose -f docker-compose-dev.yml up

stop-dev:
	docker compose -f docker-compose-dev.yml down

run-prod:
	docker compose up

stop-prod:
	docker compose down

create-celery-db:
	if ! docker compose -f docker-compose-dev.yml exec database psql -U ${DATABASE_USER} -h localhost -lqt | cut -d \| -f 1 | grep -qw ${DATABASE_CELERY_NAME}; then \
		docker compose -f docker-compose-dev.yml exec database createdb -U ${DATABASE_USER} -W ${DATABASE_PASSWORD} -h localhost -O ${DATABASE_USER} ${DATABASE_CELERY_NAME}; \
	fi

add-dev-migration:
	docker compose -f docker-compose-dev.yml exec fastapi_server alembic revision --autogenerate && \
	docker compose -f docker-compose-dev.yml exec fastapi_server alembic upgrade head && \
	echo "Migration added and applied."

install-pre-commit:
	cp "pre-commit/pre-commit.git" ".git/hooks/pre-commit"

pre-commit:
	exec docker-compose -f docker-compose-dev.yml run pre-commit

##############################################################################################
# CREATING THE ENVIRONMENT                                                                   #
##############################################################################################
PYTHON = python3.10
PROJECT_NAME = AgentKit
APP_FOLDER = backend/app
SOURCE_FOLDER = app

.PHONY: env-create
env-create:
	$(PYTHON) -m venv $(APP_FOLDER)/.venv --prompt $(PROJECT_NAME)
	cd $(APP_FOLDER) \
		&& . .venv/bin/activate \
		&& pip install "poetry~=1.7.0" \
		&& poetry install --no-ansi --with dev
	# Don't forget to activate the environment before proceeding! You can run:
	# source .venv/bin/activate


.PHONY: env-update
env-update:
	cd $(APP_FOLDER) && poetry update --with dev


.PHONY: env-delete
env-delete:
	rm -rf $(APP_FOLDER)/.venv


##############################################################################################
# BUILD STEPS: LINTING, TESTING, COVERAGE, DOCS                                              #
##############################################################################################

.PHONY: build-all
build-all: clean lint build


.PHONY: clean
clean:
	cd $(APP_FOLDER) && find $(SOURCE_FOLDER) -name __pycache__ | xargs rm -rf
	cd $(APP_FOLDER) && find $(SOURCE_FOLDER) -name '*.pyc' -delete
	cd $(APP_FOLDER) && rm -rf reports .coverage
	cd $(APP_FOLDER) && rm -rf .*cache


.PHONY: reformat
reformat:
	$(PYTHON) -m isort --sp $(APP_FOLDER)/pyproject.toml $(APP_FOLDER)/$(SOURCE_FOLDER)
	$(PYTHON) -m black --config $(APP_FOLDER)/pyproject.toml  $(APP_FOLDER)/$(SOURCE_FOLDER)


.PHONY: lint
lint:
	$(PYTHON) -m pycodestyle --config $(APP_FOLDER)/setup.cfg --exclude '.venv,setup.py,docs/*,notebooks/.' $(APP_FOLDER)/$(SOURCE_FOLDER)
	$(PYTHON) -m isort --check-only --settings-path $(APP_FOLDER)/pyproject.toml --sp $(APP_FOLDER) $(APP_FOLDER)/$(SOURCE_FOLDER)
	$(PYTHON) -m black --check --config $(APP_FOLDER)/pyproject.toml  $(APP_FOLDER)/$(SOURCE_FOLDER)
	$(PYTHON) -m pylint --rc-file  $(APP_FOLDER)/.pylintrc $(APP_FOLDER)/$(SOURCE_FOLDER)
	$(PYTHON) -m mypy --config-file $(APP_FOLDER)/setup.cfg $(APP_FOLDER)/$(SOURCE_FOLDER)


.PHONY: test
test:
	cd $(APP_FOLDER) && CONFIG_PATH=tests/config $(PYTHON) -m pytest -c tests/pytest.ini


.PHONY: radon
radon:
	cd $(APP_FOLDER) && radon cc $(SOURCE_FOLDER) --min c
	cd $(APP_FOLDER) && xenon --max-absolute C --max-modules C --max-average A $(SOURCE_FOLDER)/


.PHONY: coverage
coverage:
	cd $(APP_FOLDER) && \
		CONFIG_PATH=tests/config $(PYTHON) -m pytest tests/ -m 'not system' \
		--junitxml=reports/test-result-all.xml \
		--cov=$(SOURCE_FOLDER) \
		--cov-report term-missing \
		--cov-report html:reports/coverage-all.html \
		--cov-report xml:reports/coverage-all.xml


.PHONY: build
build:
	poetry build
