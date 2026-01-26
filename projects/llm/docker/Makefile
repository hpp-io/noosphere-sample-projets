EXAMPLE_NAME := llm
HOST_PORT ?= 8082
CONTAINER_PORT ?= 8082

# Include common makefile logic
include ../../../common.mk

# Phony targets specific to this project
.PHONY: run try-request try-request-gemini try-request-image

# Runs the container with the .env file, ensuring it's stopped first.
run: stop build
	@echo "Running container '$(CONTAINER_NAME)' with .env file..."
	@docker run --rm --name $(CONTAINER_NAME) --env-file .env -p $(HOST_PORT):$(CONTAINER_PORT) -e APP_PORT=$(CONTAINER_PORT) $(TAG)

# Sends a test request for a gateway-routed model.
try-request:
	@echo "Sending a test request for an LLMRouter model..."
	@time curl -s -X POST -H "Content-Type: application/json" \
	-d '{"model": "openai/gpt-5", "prompt": "O Holy Night 힌글버전 가사 알려줘"}' \
	http://localhost:$(HOST_PORT)/computation

# Sends a test request specifically for a Gemini model.
try-request-gemini:
	@echo "Sending a test request for a Gemini model..."
	@time curl -s -X POST -H "Content-Type: application/json" \
	-d '{"model": "gemini/gemini-2.5-flash", "prompt": "블로코(주)의 본사 주소"}' \
	http://localhost:$(HOST_PORT)/computation

# Sends a test request for image generation.
try-request-image:
	@echo "Sending a test request for image generation..."
	@time curl -s -X POST -H "Content-Type: application/json" \
	-d '{"model": "gpt-image-1", "prompt": "A cute cat playing with a ball of yarn", "size": "1024x1024", "quality": "auto", "n": 1}' \
	http://localhost:$(HOST_PORT)/images/generations | jq '.created, .data[0].b64_json[:100]'
