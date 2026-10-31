.PHONY: local-up local-down dev-up dev-down prod-up prod-down clean ollama-run

local-up:
	docker compose --env-file .env -f compose.local.yaml up -d --build

local-down:
	docker compose -f compose.local.yaml down

dev-up:
	docker compose --env-file .env.dev -f compose.dev.yaml up -d --build

dev-down:
	docker compose -f compose.dev.yaml down

prod-up:
	docker compose --env-file .env.prod -f compose.prod.yaml up -d --build

prod-down:
	docker compose -f compose.prod.yaml down

ollama-run:
	docker exec -it library-ollama-local ollama run tinyllama

clean:
	docker system prune -f
