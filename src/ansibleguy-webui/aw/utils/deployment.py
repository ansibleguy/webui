from aw.config.environment import get_aw_env_var
from aw.config.defaults import inside_docker
from aw.config.main import VERSION


def deployment_dev() -> bool:
    return get_aw_env_var('deployment') == 'dev'


def deployment_staging() -> bool:
    return get_aw_env_var('deployment') == 'staging'


def deployment_prod() -> bool:
    return not deployment_dev() and not deployment_staging()


def deployment_docker() -> bool:
    return inside_docker()


def is_release_version() -> bool:
    return VERSION not in ['dev', 'staging', 'latest', '0.0.0'] and \
            VERSION.find('dev') == -1 and VERSION.find('staging') == -1 and \
            VERSION.find('latest') == -1
