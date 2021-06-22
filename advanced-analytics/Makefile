CONDA_EXE = ~/anaconda3/bin/conda
PROJECT_NAME := ipre-ml
PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
ENV_YAML := $(PROJECT_DIR)/environment.yaml

help:           	## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'	

create_environment:	## Create environment from yaml file.
	@echo "Creating conda environment."
	$(CONDA_EXE) env create -f $(ENV_YAML)

delete_environment:	## Delete environment.
	@echo "Deleting conda environment."
	$(CONDA_EXE) env remove -n $(PROJECT_NAME)

update_environment:	## Update existing environment.
	@echo "Updating conda environment."
	$(CONDA_EXE) env update -f $(ENV_YAML) --prune
