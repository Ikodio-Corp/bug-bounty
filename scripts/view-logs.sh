#!/bin/bash

# View logs for all services or specific service

SERVICE=$1

if [ -z "$SERVICE" ]; then
    echo "📋 Viewing all logs..."
    docker-compose logs -f
else
    echo "📋 Viewing logs for $SERVICE..."
    docker-compose logs -f $SERVICE
fi
