#!/usr/bin/env bash
# Exit on error
set -o errexit
pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsuperuser --username admin --email "6510615229@student.tu.ac.th" --noinput || true