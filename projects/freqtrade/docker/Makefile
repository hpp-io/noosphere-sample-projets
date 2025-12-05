EXAMPLE_NAME := freqtrade
HOST_PORT ?= 8084
CONTAINER_PORT ?= 8084

# Include common makefile logic
include ../../../common.mk

# Phony targets specific to this project
.PHONY: run try-request test

# Runs the container in the background (detached mode).
run: stop build
	@echo "Running container '$(CONTAINER_NAME)' in the background..."
	@docker run -d --rm --name $(CONTAINER_NAME) --env-file .env -p $(HOST_PORT):$(CONTAINER_PORT) -e APP_PORT=$(CONTAINER_PORT) $(TAG)

# Sends a test request to the running container.
try-request:
	@echo "Sending a test request to http://localhost:$(HOST_PORT)/computation"
	@curl -s -X POST -H "Content-Type: application/json" \
	-d '{"pair": "ETH/USDT", "timeframe": "15m"}' \
	http://localhost:$(HOST_PORT)/computation

# A convenience target to build, run, wait, and test all at once.
test: run
	@echo "Waiting for container and freqtrade bot to initialize..."
	@sleep 15
	@$(MAKE) try-request