#!/bin/sh

# Run database migrations
flask db upgrade

# Start the Flask app
exec "$@"
