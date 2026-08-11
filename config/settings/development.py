"""Local settings used by `python manage.py ...`."""
from .base import *  # noqa: F403,F401

DEBUG = True

# Local hosts are always valid in development; environment values can add more.
ALLOWED_HOSTS = list(dict.fromkeys([*ALLOWED_HOSTS, "127.0.0.1", "localhost"]))  # noqa: F405
