# This is a common Makefile included by sub-projects.
# It expects the following variables to be set by the including Makefile:
#   - EXAMPLE_NAME
#   - HOST_PORT
#   - CONTAINER_PORT

# --- Image Naming Configuration ---
# Set your GitHub username or organization name here.
GH_OWNER ?= hpp-io

TAG := ghcr.io/$(GH_OWNER)/example-$(EXAMPLE_NAME)-noosphere:latest
CONTAINER_NAME := $(EXAMPLE_NAME)

# Declare all phony targets to prevent conflicts with file names.
.PHONY: build stop push build-multiplatform

# Builds the Docker image for the project.
build:
	@echo "Building Docker image: $(TAG)"
	@docker build -t $(TAG) --build-arg index_url=$(index_url) -f Dockerfile .

# Stops and removes the running container for the project.
stop:
	@echo "Stopping and removing container '$(CONTAINER_NAME)'..."
	@docker stop $(CONTAINER_NAME) > /dev/null 2>&1 || true
	@docker rm $(CONTAINER_NAME) > /dev/null 2>&1 || true

# Pushes the built image to the Docker registry.
push: build-multiplatform
	@echo "Pushing Docker image to registry: $(TAG)"
	@docker push $(TAG)

# Builds and pushes a multi-platform image (amd64, arm64).
# Requires docker buildx to be set up.
build-multiplatform:
	@echo "Building and pushing multi-platform image: $(TAG)"
	@docker buildx build --platform linux/amd64,linux/arm64 -t $(TAG) --build-arg index_url=$(index_url) -f Dockerfile . --push