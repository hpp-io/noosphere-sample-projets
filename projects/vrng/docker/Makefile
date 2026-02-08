EXAMPLE_NAME := vrng
HOST_PORT ?= 8085
CONTAINER_PORT ?= 8085

# Include common makefile logic
include ../../../common.mk

# Phony targets specific to this project
.PHONY: run try-commit try-reveal

# Runs the container with the .env file, ensuring it's stopped first.
run: stop build
	@echo "Running container '$(CONTAINER_NAME)' with .env file..."
	@docker run --rm --name $(CONTAINER_NAME) --env-file .env -p $(HOST_PORT):$(CONTAINER_PORT) -e APP_PORT=$(CONTAINER_PORT) $(TAG)

# Sends a test commit request to the running container.
try-commit:
	@echo "Sending a COMMIT request for game_id=0..."
	@curl -s -X POST -H "Content-Type: application/json" \
	-d '{"input": {"action": "commit", "game_id": 0}}' \
	http://localhost:$(HOST_PORT)/computation
	@echo ""

# Sends a test reveal request to the running container.
try-reveal:
	@echo "Sending a REVEAL request for game_id=0..."
	@curl -s -X POST -H "Content-Type: application/json" \
	-d '{"input": {"action": "reveal", "game_id": 0}}' \
	http://localhost:$(HOST_PORT)/computation
	@echo ""

# Verify commit-reveal integrity: keccak256(reveal) should equal commit
try-verify:
	@echo "Verifying commit-reveal integrity for game_id=0..."
	@COMMIT=$$(curl -s -X POST -H "Content-Type: application/json" \
	-d '{"input": {"action": "commit", "game_id": 0}}' \
	http://localhost:$(HOST_PORT)/computation) && \
	REVEAL=$$(curl -s -X POST -H "Content-Type: application/json" \
	-d '{"input": {"action": "reveal", "game_id": 0}}' \
	http://localhost:$(HOST_PORT)/computation) && \
	echo "Commit: $$COMMIT" && echo "Reveal: $$REVEAL"
