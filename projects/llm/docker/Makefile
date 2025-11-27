EXAMPLE_NAME := llm
HOST_PORT ?= 8082
CONTAINER_PORT ?= 8082

# Include common makefile logic
include ../../../common.mk

# Phony targets specific to this project
.PHONY: run try-request try-request-gemini

# Runs the container with the .env file, ensuring it's stopped first.
run: stop build
	@echo "Running container '$(CONTAINER_NAME)' with .env file..."
	@docker run --rm --name $(CONTAINER_NAME) --env-file .env -p $(HOST_PORT):$(CONTAINER_PORT) -e APP_PORT=$(CONTAINER_PORT) $(TAG)

# Sends a test request for a gateway-routed model.
try-request:
	@echo "Sending a test request for an LLMRouter model..."
	@curl -s -X POST -H "Content-Type: application/json" \
	-d '{"model": "openai/gpt-4o", "prompt": "What is noosphere?"}' \
	http://localhost:$(HOST_PORT)/computation

# Sends a test request specifically for a Gemini model.
try-request-gemini:
	@echo "Sending a test request for a Gemini model..."
	@curl -s -X POST -H "Content-Type: application/json" \
	-d '{"model": "gemini/gemini-pro", "prompt": "What is noosphere?"}' \
	http://localhost:$(HOST_PORT)/computation