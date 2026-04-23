import json
import os
import copy
import tempfile

CONFIG_PATH = "bot_settings/config.json"

DEFAULT_CONFIG = {
    "vhd-universal-account": {
        "platform": "",
        "access_token": "",
        "proxy": "",
        "requests_timeout": 30
    },
    "telegram": {
        "token": "",
        "admin_id": 0,
        "proxy": ""
    },
    "language": "ru",
    "auto_response": {
        "enabled": False,
        "commands": {}
    },
    "tg_logging": {
        "enabled": True,
        "events": {
            "new_message": True,
            "new_order": True
        }
    }
}


def _deep_merge(base: dict, override: dict) -> dict:
    result = copy.deepcopy(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return copy.deepcopy(DEFAULT_CONFIG)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return _deep_merge(DEFAULT_CONFIG, data)


def save_config(config: dict) -> None:
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    tmp = CONFIG_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    os.replace(tmp, CONFIG_PATH)
