from typing import Callable

_registry: dict[str, Callable] = {}

def register(name: str, fn: Callable):
    _registry[name] = fn

def get_synth(name: str) -> Callable:
    return _registry[name]