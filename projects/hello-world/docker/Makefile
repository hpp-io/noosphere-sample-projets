EXAMPLE_NAME := hello-world
HOST_PORT ?= 8081
CONTAINER_PORT ?= 8081

# Include common makefile logic
include ../../../common.mk

# Phony targets specific to this project
.PHONY: run try-request

# Runs the container, ensuring it's stopped first.
run: stop build
	@echo "Running container '$(CONTAINER_NAME)'..."
	@docker run --rm --name $(CONTAINER_NAME) -p $(HOST_PORT):$(CONTAINER_PORT) -e APP_PORT=$(CONTAINER_PORT) $(TAG)

# Sends a test request to the running container.
try-request:
	@echo "Sending a test request to http://localhost:$(HOST_PORT)/computation"
	@curl -s -X POST -H "Content-Type: application/json" \
	-d '{"input": "Gemini"}' \
	http://localhost:$(HOST_PORT)/computation