# AgentKit Application Development Guide

This document serves as an overview for linting and testing the AgentKit application, which consists of both frontend and backend components. It includes instructions for individual and integrated execution of tests using various tools.

This guide outlines the steps needed to maintain high code quality and ensure the correctness of functionalities in the AgentKit project. Utilize the provided commands and make adjustments based on project specifics or personal development workflow preferences.

## Table of Contents

- [Frontend Development](#frontend-development)
  - [Linting](#linting)
  - [Testing with Cypress](#testing-with-cypress)
- [Backend Development](#backend-development)
  - [Linting and Formatting](#linting-and-formatting)
  - [Testing with Pytest](#testing-with-pytest)
- [Using the Makefile](#using-the-makefile)
- [Optional Tools](#optional-tools)
  - [Pre-commit Hooks](#pre-commit-hooks)
  - [Pytest](#pytest-1)

## Frontend Development

Navigate to the `/frontend` folder to begin with frontend development tasks.

### Linting

To ensure code quality and consistency, this project utilizes ESLint and Prettier.

- **Linting**: Run `pnpm lint` to identify coding standard issues.
- **Auto-fix Linting Issues**: Execute `pnpm lint:fix` to automatically resolve fixable issues.
- **Prettier Check**: Use `pnpm prettier` to check for formatting inconsistencies.
- **Prettier Fix**: Apply `pnpm prettier:fix` to automatically format the code according to project standards.

### Testing with Cypress

Cypress is used for end-to-end testing of the frontend.

- **Open Cypress**: Use `pnpm cypress:open` for interactive testing.
- **Run Cypress Tests**: Execute `pnpm cypress:run` to run tests in headless mode.

Refer to the provided Cypress Guide documentation above for detailed usage and test structure.
We have further instructions on cypress in the [acceptance tests guidelines](docs/advanced/aat_guidelines.md).

## Backend Development

Switch to the `/backend/app` directory for backend tasks or to execute only backend specific linting and tests. E.g. For a direct approach to run pytest without Makefile:

```shell
cd backend/app
poetry run python3.10 -m pytest -c tests/pytest.ini
```

However, we mostly use the makefile for simplicity. The Makefile offers a simplified way to run common tasks for both frontend and backend parts of the project.

### Linting and Formatting

The backend leverages tools like Black, Pycodestyle, and isort for linting and formatting.

- **Format Code**: Run `make reformat` to apply Black and isort formatters.
- **Linting**: Execute `make lint` to perform a comprehensive linting check using various tools.

### Testing with Pytest

Pytest is used for running automated Python tests.

- Run `make test` to execute the backend test suite. It handles preconditions and uses the configured settings.

## Pre-commit Hooks

- **Installation**: Use `make install-pre-commit` or follow the optional steps to set up pre-commit hooks locally to automatically run lint and tests on commit.
