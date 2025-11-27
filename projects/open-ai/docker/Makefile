EXAMPLE_NAME := open-ai
HOST_PORT ?= 8083
CONTAINER_PORT ?= 8083

# Include common makefile logic
include ../../../common.mk

# Phony targets specific to this project
.PHONY: run try-request

# Runs the container with the .env file, ensuring it's stopped first.
run: stop build
	@echo "Running container '$(CONTAINER_NAME)' with .env file..."
	@docker run --rm --name $(CONTAINER_NAME) --env-file .env -p $(HOST_PORT):$(CONTAINER_PORT) -e APP_PORT=$(CONTAINER_PORT) $(TAG)

# Sends a test request to the running container.
try-request:
	@echo "Sending a test request to http://localhost:$(HOST_PORT)/computation"
	@curl -s -X POST -H "Content-Type: application/json" \
	-d '{"model": "gpt-4o", "prompt": "What is noosphere?"}' \
	http://localhost:$(HOST_PORT)/computation