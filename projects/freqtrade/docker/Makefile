DOCKER_ORG := noosphere
EXAMPLE_NAME := freqtrade
TAG := $(DOCKER_ORG)/example-$(EXAMPLE_NAME)-noosphere:latest

.PHONY: build run build-multiplatform try-request

build:
	@echo "Building Docker image: $(TAG)"
	@docker build -t $(TAG) --build-arg index_url=$(index_url) -f Dockerfile .

run: build
	@echo "Running Docker container..."
	@docker run --rm -p 3000:3000 $(TAG)

# You may need to set up a docker builder, to do so run:
# docker buildx create --name mybuilder --bootstrap --use
# refer to https://docs.docker.com/build/building/multi-platform/#building-multi-platform-images for more info
build-multiplatform:
	@echo "Building and pushing multi-platform image: $(TAG)"
	@docker buildx build --platform linux/amd64,linux/arm64 -t $(TAG) --build-arg index_url=$(index_url) -f Dockerfile . --push

try-request:
	@echo "Sending a test request to the running container..."
	@curl -X POST -H "Content-Type: application/json" \
	-d '{"input": "Gemini"}' \
	http://localhost:3000/computation
