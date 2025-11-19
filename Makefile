index_url ?= ''
DOCKER_DIR_NAME ?= docker

build-container:
	$(MAKE) -C ./projects/$(project)/$(DOCKER_DIR_NAME) build index_url=$(index_url)

build-multiplatform:
	$(MAKE) -C ./projects/$(project)/$(DOCKER_DIR_NAME) build-multiplatform

stop-container:
	docker kill $(project) || true
	docker rm $(project) || true


run: build-container
	$(MAKE) -C ./projects/$(project)/$(DOCKER_DIR_NAME) run

try-request:
	$(MAKE) -C ./projects/$(project)/$(DOCKER_DIR_NAME) try-request
