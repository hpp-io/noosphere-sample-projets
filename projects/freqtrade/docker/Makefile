DOCKER_ORG := noosphere
EXAMPLE_NAME := freqtrade
TAG := $(DOCKER_ORG)/example-$(EXAMPLE_NAME)-noosphere:latest

HOST_PORT ?= 8084
CONTAINER_PORT ?= 8084
CONTAINER_NAME := $(EXAMPLE_NAME)
.PHONY: build run stop test build-multiplatform try-request

build:
	@echo "Building Docker image: $(TAG)"
	@docker build -t $(TAG) --build-arg index_url=$(index_url) -f Dockerfile .

run: stop build
	@echo "Running Docker container..."
	@docker run --rm --name $(CONTAINER_NAME) --env-file .env -p $(HOST_PORT):$(CONTAINER_PORT) -e APP_PORT=$(CONTAINER_PORT) $(TAG)

stop:
	@echo "Stopping and removing container '$(CONTAINER_NAME)'..."
	@docker stop $(CONTAINER_NAME) > /dev/null 2>&1 || true
	@docker rm $(CONTAINER_NAME) > /dev/null 2>&1 || true

build-multiplatform:
	@echo "Building and pushing multi-platform image: $(TAG)"
	@docker buildx build --platform linux/amd64,linux/arm64 -t $(TAG) --build-arg index_url=$(index_url) -f Dockerfile . --push

try-request:
	@echo "Sending a test request to the running container..."
	@curl -s -X POST -H "Content-Type: application/json" \
	-d '{"pair": "BTC/USDT", "timeframe": "5m"}' \
	http://localhost:$(HOST_PORT)/computation

test: run
	@echo "Waiting for container to start..."
	@sleep 5
	@$(MAKE) try-request