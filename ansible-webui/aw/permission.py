from aw.config.hardcoded import PERMISSIONS


def _group_check(user, permission: str) -> bool:
    if user and user.groups.filter(name=PERMISSIONS[permission]).exists():
        return True

    return False


# def authorized_to_access(user) -> bool:
#     return _group_check(user, 'access')


def authorized_to_exec(user) -> bool:
    return _group_check(user, 'exec')


def authorized_to_write(user) -> bool:
    return _group_check(user, 'write')
