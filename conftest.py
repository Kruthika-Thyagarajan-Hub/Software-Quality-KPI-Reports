import pytest
from requests.auth import HTTPBasicAuth
from os import path
from yaml import safe_load

@pytest.fixture(scope="session")
def config():
    with open(path.join(path.dirname(__file__), "resources.yml")) as config_file:
        return safe_load(config_file)

@pytest.fixture(scope="session")
def jira_auth(config):
    auth = HTTPBasicAuth(config['EMAIL'], config['JIRA_TOKEN'])
    return auth

@pytest.fixture(scope='session')
def testrail_auth(config):
    auth = HTTPBasicAuth(config['EMAIL'], config['TESTRAIL_PASSWORD'])
    return auth

@pytest.fixture(scope='session')
def base_url(config):
    return config['HOST']

@pytest.fixture(scope='session')
def prj_key(config):
    return config['PROJECT_KEY']

@pytest.fixture(scope='session')
def prj_id(config):
    return config['PROJECT_ID']

@pytest.fixture(scope='session')
def testrail_prj_id(config):
    return config['TESTRAIL_PROJECT_ID']

@pytest.fixture(scope='session')
def testrail_suite_id(config):
    return config['TESTRAIL_SUITE_ID']

@pytest.fixture(scope='session')
def previous_release_version(config):
    return config['PREVIOUS_RELEASE_VERSION']

@pytest.fixture(scope='session')
def current_release_version(config):
    return config['CURRENT_RELEASE_VERSION']

