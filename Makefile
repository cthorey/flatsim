SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:
.SUFFIXES:

PKG_PATH = ~/workdir/flatsim
NAME = flatsim
DOCKERFILE = ./Dockerfile
VERSION = latest
NETWORK = bridge

DOCKER_RUN_ARGS = \
	--platform linux/amd64 \
	--volume $(PKG_PATH):/workdir


.PHONY: help
help:
	$(info Available make targets:)
	@egrep '^(.+)\:\ ##\ (.+)' ${MAKEFILE_LIST} | column -t -c 2 -s ':#'


.PHONY: build
build: ## Build the docker image
	$(info *** Building docker image: $(NAME):$(VERSION))
	@DOCKER_BUILDKIT=1 docker build \
		--tag $(NAME):$(VERSION) \
		--file $(DOCKERFILE) \
		.

.PHONY: serve
serve: ## Launch the app
	$(info *** Launch the app)
	@docker run --rm -d \
		--network=$(NETWORK) \
		--name=$(NAME) \
		-p 8501:8501 \
	  $(DOCKER_RUN_ARGS) \
		$(NAME):$(VERSION)
