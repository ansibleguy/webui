from os import environ
from sys import exit as sys_exit

from requests import Session, Response

BASE_URL = 'http://127.0.0.1:8000/api'
API_USER = environ['AW_ADMIN']
API_KEY = environ['AW_API_KEY']

api = Session()
api.headers['X-Api-Key'] = API_KEY
api.headers['accept'] = 'application/json'


def _api_request(location: str, method: str = None, data: dict = None) -> Response:
    url = f'{BASE_URL}/{location}'

    if method is None:
        method = 'get'

    print(f'TESTING API {method} {location}')

    if method == 'get':
        return api.get(url)

    if method == 'post':
        return api.post(url=url, data=data)

    if method == 'put':
        return api.put(url=url, data=data)

    if method == 'delete':
        return api.delete(url)

    print('ERROR: - got unsupported method!')
    sys_exit(1)


def _api_request_ok(location: str, method: str = None, data: dict = None) -> bool:
    response = _api_request(location, method, data)
    if not response.ok:
        print(f"GOT ERROR: {response.content}")
        sys_exit(1)

    return response.ok


def test_modify_locations(location_data_list: list[dict]):
    for loc_data in location_data_list:
        assert _api_request_ok(loc_data['l'], 'put', loc_data['d'])


def test_add_locations(location_data_list: list[dict]):
    for loc_data in location_data_list:
        assert _api_request_ok(loc_data['l'], 'post', loc_data['d'])


def test_delete_locations(location_list: list):
    for loc in location_list:
        assert _api_request_ok(loc, 'delete')


def test_get_locations(locations: list):
    for location in locations:
        assert _api_request_ok(location)


def test_add():
    # NOTE: do not reference entries with ID 1! they should be deleted later on
    test_add_locations([
        {'l': 'key', 'd': None},

        # creds
        {'l': 'credentials', 'd': {'name': 'cred1', 'become_user': 'guy', 'become_pass': 'sePwd', 'vault_id': 'myID'}},
        {'l': 'credentials', 'd': {
            'name': 'c2', 'become_user': 'otherDude', 'become_pass': 'hup', 'vault_pass': 'secUry',
        }},
        {'l': 'credentials', 'd': {
            'name': 'cssh', 'connect_user': 'superGuy',
            'ssh_key': '-----BEGIN OPENSSH PRIVATE KEY----- '
                       'b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW '
                       'QyNTUxOQAAACBqpdUHnkUoKG6khFKIvVWgy5IMXvR0/ktbcxyGKAsmeQAAAJAtbFQeLWxU '
                       'HgAAAAtzc2gtZWQyNTUxOQAAACBqpdUHnkUoKG6khFKIvVWgy5IMXvR0/ktbcxyGKAsmeQ '
                       'AAAEAmjuNJack1cgS1U4AL2p4EOoelebHO3CGo3x/bILwR22ql1QeeRSgobqSEUoi9VaDL '
                       'kgxe9HT+S1tzHIYoCyZ5AAAADXN1cGVyc3Rlc0BzdXA= '
                       '-----END OPENSSH PRIVATE KEY-----'
        }},

        # repos
        {'l': 'repository', 'd': {
            'name': 'gitty1', 'rtype': 2, 'git_origin': 'https://github.com/ansibleguy/webui.git',
            'git_branch': 'latest',
        }},
        {'l': 'repository', 'd': {'name': 'staticy1', 'rtype': 1, 'static_path': '/etc/ansible/repo'}},

        # jobs
        {'l': 'job', 'd': {
            'name': 'job1', 'playbook_file': 'play1.yml', 'inventory_file': 'inv/hosts.yml', 'tags': 'svc1',
            'limit': 'srv1',
        }},
        {'l': 'job', 'd': {
            'name': 'My job2', 'playbook_file': 'PlayBook.yml', 'inventory_file': 'i/h.yml', 'verbosity': 2,
            'tags_skip': 'srv1', 'comment': 'heiHo', 'cmd_args': '--superArg',
        }},
        {'l': 'job', 'd': {
            'name': 'jobby3', 'playbook_file': 'PlayUsBookUs.yml', 'inventory_file': 'hosts.yml', 'enabled': False,
            'repository': 2,
        }},
        {'l': 'job', 'd': {
            'name': 'j4', 'playbook_file': 'nope.yml', 'inventory_file': 'hosts.yml', 'enabled': False,
            'credentials_default': 3, 'mode_diff': True, 'mode_check': True,
        }},
        {'l': 'job', 'd': {
            'name': 'jup5', 'playbook_file': 'nope_nr2.yml', 'inventory_file': 'hosts.yml', 'schedule': '5 4 * * *',
            'environment_vars': 'MY=1,SUPER=2,VARS=3',
        }},

        # perms
        {'l': 'permission', 'd': {'name': 'perm1', 'jobs': 1, 'credentials': 1}},
    ])


def test_modify():
    test_modify_locations([
        {'l': 'config', 'd': {'run_timeout': 6060, 'path_play': '/etc/play', 'path_log': '/var/log'}},

        # jobs
        {'l': 'job/2', 'd': {
            'name': 'My job2.5', 'playbook_file': 'PlayBook_New.yml', 'inventory_file': 'hosts.yml',
            'schedule': '5 4 * * *', 'environment_vars': 'MY=1,SUPER=2,VARS=3', 'tags_skip': 'srv1',
        }},
        {'l': 'job/2', 'd': {
            'name': 'My job2.6', 'playbook_file': 'nope.yml', 'inventory_file': 'hosts.yml', 'enabled': False,
            'credentials_default': 3, 'mode_diff': True, 'mode_check': True,
        }},
        {'l': 'job/2', 'd': {
            'name': 'My job2.7', 'playbook_file': 'PlayUsBookUs.yml', 'inventory_file': 'hosts.yml', 'enabled': False,
            'repository': 2,
        }},

        # perms; todo: fix
        {'l': 'permission/1', 'd': {'name': 'perm1'}},
    ])


def test_list():
    test_get_locations([
        'credentials', 'job', 'job_exec', 'key', 'permission', 'config', 'repository',
        'fs/exists?item=/etc',
    ])


def test_delete():
    test_delete_locations([
        'repository/1',
        'permission/1',
        'job/1',
        'credentials/1',
    ])


def main():
    test_add()
    test_list()
    test_modify()
    test_delete()
    # todo: add should-fail checks
    # todo: add permission checks (multiple api keys)


if __name__ == '__main__':
    main()
