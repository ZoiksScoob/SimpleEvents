import os


def get_app_settings():
    return os.getenv(
        'APP_SETTINGS',
        'simple_events.config.DevelopmentConfig'
    )
