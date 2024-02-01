FROM acdha/pre-commit:latest

COPY .pre-commit-config.yaml /code/
WORKDIR /code
RUN git init . && pre-commit install-hooks
