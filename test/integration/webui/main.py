from os import environ
from time import sleep

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller

BASE_URL = 'http://127.0.0.1:8000'
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-extensions')
options.add_argument('--remote-debugging-port=9222')
chromedriver_autoinstaller.install()
DRIVER = webdriver.Chrome(options=options)


def _response_code(url: str) -> (int, None):
    for request in DRIVER.requests:
        if request.response and request.url == url:
            return request.response.status_code

    return None


def _response_ok(url: str) -> bool:
    return _response_code(url) in [200, 302]


def login(user: str, pwd: str):
    print('TESTING LOGIN')
    login_url = f'{BASE_URL}/a/login/'
    DRIVER.get(login_url)
    DRIVER.find_element(By.ID, 'id_username').send_keys(user)
    DRIVER.find_element(By.ID, 'id_password').send_keys(pwd)
    DRIVER.find_element(By.ID, 'id_password').send_keys(Keys.RETURN)
    assert _response_ok(login_url)

    login_redirect = f'{BASE_URL}/ui/jobs/manage'
    assert DRIVER.current_url == login_redirect
    assert _response_ok(login_redirect)


def test_get_locations(locations: list):
    for location in locations:
        print(f'TESTING GET {location}')
        url = f'{BASE_URL}/{location}'
        sleep(0.1)
        DRIVER.get(url)
        assert _response_ok(url)


def test_main_pages():
    test_get_locations([
        'ui/jobs/manage', 'ui/jobs/log', 'ui/jobs/credentials',
        'ui/settings/api_keys', 'ui/settings/permissions',
        'ui/system/admin/', 'ui/system/api_docs', 'ui/system/environment', 'ui/system/config',
        'a/password_change/',
    ])


def test_actions_views():
    test_get_locations([
        'ui/jobs/manage/job',
        'ui/jobs/credentials/0?global=false', 'ui/jobs/credentials/0?global=true',
        'ui/settings/permissions/0',
    ])


def main():
    try:
        login(user=environ['AW_ADMIN'], pwd=environ['AW_ADMIN_PWD'])
        test_main_pages()
        test_actions_views()
        # todo: add action post variants

    finally:
        DRIVER.quit()


if __name__ == '__main__':
    main()
