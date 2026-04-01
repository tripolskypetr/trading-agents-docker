#!/bin/bash
set -a
source .env
set +a
uv run python src/main.py
