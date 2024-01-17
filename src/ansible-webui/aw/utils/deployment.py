from os import environ

from aw.config.hardcoded import ENV_KEY_DEPLOYMENT


def deployment_dev() -> bool:
    return ENV_KEY_DEPLOYMENT in environ and environ[ENV_KEY_DEPLOYMENT] == 'dev'


def deployment_staging() -> bool:
    return ENV_KEY_DEPLOYMENT in environ and environ[ENV_KEY_DEPLOYMENT] == 'dev'


def deployment_prod() -> bool:
    return not deployment_dev() and not deployment_staging()
