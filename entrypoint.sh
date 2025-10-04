#!/usr/bin/env bash
set -e

# Миграции и сбор статики
python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

# ВАЖНО: замени "config.wsgi" на модуль твоего проекта, если он называется иначе
# SQLite любит одиночный воркер — избежим блокировок базы
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 1 --timeout 120
