"""App package initializer.

Making `app` a package lets you run modules as a package (e.g. `python -m app.main`) and
allow `from app.routers import ...` to work when running from the project root.
"""
__all__ = ["main", "routers", "database", "models", "schemas", "services", "config"]
__version__ = "1.0.0"
