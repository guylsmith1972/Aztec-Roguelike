import json

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
        json.dump({}, file)
    _config = {}

def get(key, default_value=None):
    if _config is None:
        _load_or_create()
    
    parts = key.split(".")
    curr_dict = _config
    for part in parts:
        if part not in curr_dict:
            if default_value is not None:
                set(key, default_value)
            return default_value
        curr_dict = curr_dict[part]
    return curr_dict

def set(key, value):
    if _config is None:
        _load_or_create()
    
    parts = key.split(".")
    curr_dict = _config
    for part in parts[:-1]:
        if part not in curr_dict:
            curr_dict[part] = {}
        curr_dict = curr_dict[part]
    curr_dict[parts[-1]] = value

    with open(_config_filename, 'w') as file:
        json.dump(_config, file, indent=2, sort_keys=True)

