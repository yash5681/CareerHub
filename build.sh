#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Collect static files with compression
python manage.py collectstatic --no-input

# Run database schema migrations
python manage.py migrate

# Seed initial categories, skills, and admin accounts if fresh
python manage.py seed_data
