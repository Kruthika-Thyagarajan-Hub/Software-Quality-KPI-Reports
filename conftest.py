import pytest
from requests.auth import HTTPBasicAuth
from os import path
import yaml

@pytest.fixture(scope="session")
def config():
    with open(path.join(path.dirname(__file__), "resources.yml")) as config_file:
        return yaml.safe_load(config_file)

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

@pytest.fixture(scope='session')
def from_date(config):
    return config['PREVIOUS_RELEASE_DATE']

@pytest.fixture(scope='session')
def to_date(config):
    return config['CURRENT_RELEASE_DATE']

@pytest.fixture(scope='session')
def regression_start_date(config):
    return config['PREVIOUS_REGRESSION_START_DATE']

@pytest.fixture(scope='session')
def regression_end_date(config):
    return config['PREVIOUS_REGRESSION_END_DATE']

@pytest.fixture(scope='session')
def previous_release_date(config):
    return config['PREVIOUS_RELEASE_DATE']

@pytest.fixture(scope='session')
def current_release_date(config):
    return config['CURRENT_RELEASE_DATE']

def update_resources_file():
    EMAIL: input("Enter your email id")
    JIRA_TOKEN: input("Enter your JIRA token")
    TESTRAIL_PASSWORD: input("Enter your Testrail password")
    PREVIOUS_REGRESSION_START_DATE: input("Enter previous regression start date")
    PREVIOUS_REGRESSION_END_DATE: input("Enter previous regression end date")
    PREVIOUS_RELEASE_DATE: input("Enter previous release date")
    PREVIOUS_RELEASE_VERSION: input("Enter previous release version")
    CURRENT_RELEASE_VERSION: input("Enter current release version")
    CURRENT_REGRESSION_START_DATE: input("Enter current regression start date")
    CURRENT_REGRESSION_END_DATE: input("Enter current regression end date")
    CURRENT_RELEASE_DATE: input("Enter current release date")



