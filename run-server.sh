#!/bin/bash
cd "$(dirname "$0")"
export FMP_API_KEY=$(op item get "FMP api key" --vault "Investment Team" --fields credential --reveal)
exec .venv/bin/python -m src.server "$@"
