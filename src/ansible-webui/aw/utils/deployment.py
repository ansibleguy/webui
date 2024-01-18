from aw.config.environment import get_aw_env_var


def deployment_dev() -> bool:
    return get_aw_env_var('deployment') == 'dev'


def deployment_staging() -> bool:
    return get_aw_env_var('deployment') == 'staging'


def deployment_prod() -> bool:
    return not deployment_dev() and not deployment_staging()
