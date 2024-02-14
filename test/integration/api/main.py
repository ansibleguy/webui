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
        return api.post(url=url, data=data)

    if method == 'delete':
        return api.post(url)

    print('ERROR: - got unsupported method!')
    sys_exit(1)


def _api_request_ok(location: str, method: str = None, data: dict = None) -> bool:
    response = _api_request(location, method, data)
    if not response.ok:
        print(f"GOT ERROR: {response.content}")
        sys_exit(1)

    return response.ok


def test_add_locations(location_data_list: list[dict]):
    for loc_data in location_data_list:
        assert _api_request_ok(loc_data['l'], 'post', loc_data['d'])


def test_get_locations(locations: list):
    for location in locations:
        assert _api_request_ok(location)


def test_add():
    test_add_locations([
        {'l': 'credentials', 'd': {'name': 'cred1', 'become_user': 'guy', 'become_pass': 'sePwd', 'vault_id': 'myID'}},
        {'l': 'job', 'd': {
            'name': 'job1', 'playbook_file': 'play1.yml', 'inventory_file': 'inv/hosts.yml', 'tags': 'svc1',
            'limit': 'srv1',
        }},
        {'l': 'key', 'd': None},
        {'l': 'permission', 'd': {'name': 'perm1', 'jobs': 1}},
    ])


def test_list():
    test_get_locations([
        'credentials', 'job', 'job_exec', 'key', 'permission',
    ])


def main():
    test_add()
    test_list()


if __name__ == '__main__':
    main()
