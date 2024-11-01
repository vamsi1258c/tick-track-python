#!/bin/sh

# Run database migrations
flask db migrate
flask db upgrade

# Start the Flask app
exec "$@"
