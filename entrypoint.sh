#!/bin/bash
# Start the API server
exec uv run python -m goodanalysis.main api --host 0.0.0.0 --port 5000

