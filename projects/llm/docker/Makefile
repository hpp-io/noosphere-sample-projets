DOCKER_ORG := noosphere
EXAMPLE_NAME := llm
TAG := $(DOCKER_ORG)/example-$(EXAMPLE_NAME)-noosphere:latest

HOST_PORT ?= 8082
CONTAINER_PORT ?= 8082
CONTAINER_NAME := $(EXAMPLE_NAME)
.PHONY: build run stop build-multiplatform try-request try-request-openai

build:
	@echo "Building Docker image: $(TAG)"
	@docker build -t $(TAG) --build-arg index_url=$(index_url) -f Dockerfile .

run: stop build
	@echo "Running Docker container with .env file..."
	@docker run --rm --name $(CONTAINER_NAME) --env-file .env -p $(HOST_PORT):$(CONTAINER_PORT) -e APP_PORT=$(CONTAINER_PORT) $(TAG)

stop:
	@echo "Stopping and removing container '$(CONTAINER_NAME)'..."
	@docker stop $(CONTAINER_NAME) > /dev/null 2>&1 || true
	@docker rm $(CONTAINER_NAME) > /dev/null 2>&1 || true
# You may need to set up a docker builder, to do so run:
# docker buildx create --name mybuilder --bootstrap --use
# refer to https://docs.docker.com/build/building/multi-platform/#building-multi-platform-images for more info
build-multiplatform:
	@echo "Building and pushing multi-platform image: $(TAG)"
	@docker buildx build --platform linux/amd64,linux/arm64 -t $(TAG) --build-arg index_url=$(index_url) -f Dockerfile . --push

try-request:
	@echo "Sending a test request to the running container..."
	@curl -s -X POST -H "Content-Type: application/json" \
	-d '{"model": "ollama/gpt-oss:120b", "prompt": "What is noosphere?"}' \
	http://localhost:$(HOST_PORT)/computation
try-request-gemini:
	@echo "Sending a test request to the running container..."
	@curl -s -X POST -H "Content-Type: application/json" \
	-d '{"model": "gemini/gemini-2.5-pro", "prompt": "What is noosphere?"}' \
	http://localhost:$(HOST_PORT)/computation