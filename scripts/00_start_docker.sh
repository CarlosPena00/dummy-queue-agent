#!/bin/bash
# Start all services defined in docker-compose.yml
# Use -d flag to run in detached mode if needed

docker compose up "$@"
