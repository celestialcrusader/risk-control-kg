# Pure RCKG Engine Makefile for Development & Testing

.PHONY: help test test-env-up test-env-down clean

help:
	@echo "Available commands:"
	@echo "  make test-env-up    - Spin up isolated Docker Compose test containers"
	@echo "  make test-env-down  - Tear down Docker Compose test containers"
	@echo "  make test           - Run full pytest test suite"

test-env-up:
	docker compose -f docker-compose.test.yml up -d

test-env-down:
	docker compose -f docker-compose.test.yml down -v

test:
	pytest backend/tests -v
