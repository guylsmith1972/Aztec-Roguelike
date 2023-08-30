
import json
import pygame

# Default configuration values
_default_config = {
    "moves_per_second": 10,
    "key_to_movement": {
        pygame.K_KP7: [-1, -1],
        pygame.K_KP8: [0, -1],
        pygame.K_KP9: [1, -1],
        pygame.K_KP4: [-1, 0],
        pygame.K_KP6: [1, 0],
        pygame.K_KP1: [-1, 1],
        pygame.K_KP2: [0, 1],
        pygame.K_KP3: [1, 1]
    },
    "max_invalid_regions": 100,
    "region_size": 16,
    "tile_size": 20
}

_config = None
_config_filename = "config.json"

def _load_or_create():
    global _config
    # Check if the configuration file exists
    try:
        with open(_config_filename, 'r') as file:
            _config = json.load(file)
    except FileNotFoundError:
        create_default_config()

def create_default_config():
    global _config
    with open(_config_filename, 'w') as file:
        json.dump(_default_config, file, indent=4)
    _config = _default_config

def get(key):
    if _config is None:
        _load_or_create()
    return _config.get(key)

def set(key, value):
    if _config is None:
        _load_or_create()
    _config[key] = value
    with open(_config_filename, 'w') as file:
        json.dump(_config, file, indent=4)
