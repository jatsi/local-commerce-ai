#!/usr/bin/env bash
set -e
cp .env.example .env || true
docker compose up --build
