import os
from simple_events.config import configs


def get_app_settings():
    return os.getenv(
        'APP_SETTINGS',
        'simple_events.config.DevelopmentConfig'
    )


def get_config():
    app_settings = get_app_settings()
    config_name = app_settings.split('.')[-1]
    return configs[config_name]
