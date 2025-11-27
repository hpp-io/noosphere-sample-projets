index_url ?= ''
DOCKER_DIR_NAME ?= docker

# .PHONY: build-container build-multiplatform push-container stop-container run try-request
# It's good practice to declare phony targets.
.PHONY: build-container build-multiplatform push-container stop-container run try-request

# Delegates the 'build' command to the specified project's Makefile.
build-container:
	$(MAKE) -C ./projects/$(project)/$(DOCKER_DIR_NAME) build index_url=$(index_url)

# Delegates the 'build-multiplatform' command.
build-multiplatform:
	$(MAKE) -C ./projects/$(project)/$(DOCKER_DIR_NAME) build-multiplatform

# Delegates the 'push' command.
push-container:
	$(MAKE) -C ./projects/$(project)/$(DOCKER_DIR_NAME) push

# Delegates the 'stop' command.
stop-container:
	$(MAKE) -C ./projects/$(project)/$(DOCKER_DIR_NAME) stop

# Delegates the 'run' command after ensuring the container is built.
run: build-container
	@echo "Executing 'run' for project '$(project)'..."
	$(MAKE) -C ./projects/$(project)/$(DOCKER_DIR_NAME) run

# Delegates the 'try-request' command.
try-request:
	$(MAKE) -C ./projects/$(project)/$(DOCKER_DIR_NAME) try-request