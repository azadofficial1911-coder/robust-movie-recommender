"""Safer production settings for future deployment.

This file is intentionally not used by Week 1 `runserver`. A hosting platform
should set DJANGO_SETTINGS_MODULE=config.settings.production and provide the
required environment variables.
"""
from django.core.exceptions import ImproperlyConfigured
from .base import *  # noqa: F403,F401

DEBUG = False

if SECRET_KEY.startswith("django-insecure-"):  # noqa: F405
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY before using production settings.")

if not ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured("Set DJANGO_ALLOWED_HOSTS before using production settings.")

SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
