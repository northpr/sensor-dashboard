# Makefile for Water Quality Sensor Dashboard

.PHONY: setup run generate clean
.ONESHELL:
SHELL := /bin/bash
# Setup the environment
install:
	conda install -y pip
	pip install -r requirements.txt

# Run the dashboard
run:
	cd app && python run_dashboard.py

# Generate sample data
generate:
	cd app && python generate_data.py

# Clean generated data
clean:
	rm -rf app/data/*

# Help command
help:
	@echo "Available commands:"
	@echo "  make setup     - Install required dependencies"
	@echo "  make run       - Run the Streamlit dashboard"
	@echo "  make generate  - Generate sample sensor data"
	@echo "  make clean     - Remove all generated data files"
