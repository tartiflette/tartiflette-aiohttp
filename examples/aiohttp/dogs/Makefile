# -*- mode: makefile -*-

COMPOSE = docker-compose -p ttftt_aiohttp_dogs


.PHONY: run
run:
	$(COMPOSE) build app
	$(COMPOSE) up app redis


.PHONY: down
down:
	$(COMPOSE) down --volumes --rmi=local
