"""
Sensor Registry — auto-discovers sensor modules in this package.

To add a new data source:
  1. Create sensors/my_source.py
  2. Implement: fetch() -> dict  (must return a dict with at least "layer" and "source" keys)
  3. That's it — it will be picked up automatically on next run.

Reserved module names (not treated as sensors): __init__, registry
"""
import importlib
import os
from pathlib import Path

_RESERVED = {"__init__", "registry"}
_SENSOR_DIR = Path(__file__).parent


def discover() -> list:
    """Return list of sensor module objects that have a fetch() function."""
    sensors = []
    for path in sorted(_SENSOR_DIR.glob("*.py")):
        name = path.stem
        if name in _RESERVED:
            continue
        try:
            mod = importlib.import_module(f"sensors.{name}")
            if callable(getattr(mod, "fetch", None)):
                sensors.append(mod)
        except Exception as e:
            print(f"[registry] skipping sensors.{name}: {e}")
    return sensors


def list_sources() -> list[dict]:
    """Return metadata about all registered sensors (for the /sources endpoint)."""
    result = []
    for mod in discover():
        result.append({
            "module": mod.__name__,
            "layer": getattr(mod, "LAYER", "unknown"),
            "label": getattr(mod, "LABEL", mod.__name__.split(".")[-1].title()),
            "url": getattr(mod, "SOURCE_URL", None),
            "requires_key": getattr(mod, "REQUIRES_KEY", False),
            "key_env_var": getattr(mod, "KEY_ENV_VAR", None),
        })
    return result
