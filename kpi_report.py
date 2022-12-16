import requests
from jinja2 import Environment, FileSystemLoader
from datetime import date
import os, glob
import yaml

for f in glob.glob("KPI_report_*.html"):
    os.remove(f)

class TestKpiReport:
    HEADER = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    def create_report(self):
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('report_template_header.html')
        html = template.render(page_title_text='KPI report')
        with open('KPI_report_'+str(date.today())+'.html', 'a+') as f:
            f.write(html)

    def generate_report(self,metric_name, formula, info1, info2, info3):
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('report_template_body.html')
        html = template.render(title_text=metric_name,
                               formula=formula,
                               info1=info1,
                               info2=info2,
                               info3=info3
                               )
        with open('KPI_report_'+str(date.today())+'.html', 'a+') as f:
            f.write(html)

    def get_filtered_issues(self, url, query, auth):
        response = requests.request(
            "GET",
            url,
            headers=self.HEADER,
            params=query,
            auth=auth
        ).json()
        return response

    def get_release_version_id(self, base_url, prj_key, jira_auth, current_release_version):
        version_id = ""
        url = f"{base_url}rest/api/2/project/{prj_key}/version?expand=issuesstatus&maxResults=25&orderBy=-sequence&startAt=0&status=released%2Cunreleased"
        response = requests.request(
            "GET",
            url,
            headers=self.HEADER,
            auth=jira_auth
        ).json()
        versions = response['values']
        for version in versions:
            for k, v in version.items():
                if v == f'{current_release_version}':
                    version_id = version['id']
        return version_id

    def key_search(self, json_input, lookup_key):
        if isinstance(json_input, dict):
            for k, v in json_input.items():
                if k == lookup_key:
                    yield v
                else:
                    yield from self.key_search(v, lookup_key)
        elif isinstance(json_input, list):
            for item in json_input:
                yield from self.key_search(item, lookup_key)

    def test_update_resource_data(self):
        print("Do you want to update the resources file")
        resp = input("Yes or No \n")
        if resp.lower() == "yes":
            with open(os.path.join(os.path.dirname(__file__), "resources.yml"), 'r')  as data:
                contents = yaml.safe_load(data)
            contents['EMAIL']= input("Enter your email id")
            contents['JIRA_TOKEN']= input("Enter your JIRA token ")
            contents['TESTRAIL_PASSWORD']= input("Enter your Testrail password ")
            contents['PREVIOUS_RELEASE_VERSION']= input("Enter previous release version ")
            contents['CURRENT_RELEASE_VERSION']= input("Enter current release version ")
            with open(os.path.join(os.path.dirname(__file__), "resources.yml"), 'w')  as resource_file:
                yaml.dump(contents, resource_file, sort_keys=False)
        else:
            pass

    def test_calculate_defects_severity_index(self, base_url, prj_key, jira_auth, previous_release_version):
        self.create_report()
        formula = "Escaped Defects Severity Index = (Total no. of defects (weighted density) reported in production / Total no. of defects  (weighted density) found during release) * 100"
        defect_coefficients = {'Critical': 10, 'High': 7, 'Medium': 5, 'Low': 3, 'Very Low': 1}
        leaked_defects = []
        captured_defects = []
        leaked_defect_weightage = 0
        captured_defect_weightage = 0
        url = f'{base_url}rest/api/3/search?maxResults=100'

        query1 = {
            'jql': f'project = {prj_key} AND issuetype = Bug AND affectedVersion = {previous_release_version} AND "Env[Dropdown]" in (Development, Staging) order by created DESC'
        }
        query2 = {
            'jql': f'project = {prj_key} AND type = Bug AND affectedVersion = {previous_release_version} AND "Env[Dropdown]" in (Production) order by created DESC'
        }
        captured_issues = self.get_filtered_issues(url, query1, jira_auth)
        for issue in captured_issues['issues']:
            captured_defects.append(issue['key'])
            defect_priority = issue['fields']['priority']['name']
            captured_defect_weightage = captured_defect_weightage + defect_coefficients[defect_priority]
        leaked_issues = self.get_filtered_issues(url, query2, jira_auth)
        for issue in leaked_issues['issues']:
            leaked_defects.append(issue['key'])
            defect_priority = issue['fields']['priority']['name']
            leaked_defect_weightage = leaked_defect_weightage + defect_coefficients[defect_priority]
        defect_severity_index = (leaked_defect_weightage / captured_defect_weightage) * 100
        self.generate_report(metric_name=f"1. Escaped Defects Severity Index For Release Version {previous_release_version} ", formula=formula, info1=f'Defects found in Prod = {leaked_defects}, \n Total_Prod_Bugs = {len(leaked_defects)}',
                             info2=f'Defects found in Regression = {captured_defects}, \n Total_Regression_Bugs = {len(captured_defects)}',
                             info3=f'Escaped Defects Severity Index = {round(defect_severity_index, 2)} %')

    def test_requirements_coverage_percentage(self, base_url, prj_key, jira_auth, current_release_version, prj_id, testrail_auth, testrail_prj_id):
        formula = "Requirement coverage = (Total number of acceptance criteria mapped to test cases / Total number of acceptance criteria) * 100"
        Jira_FE_Tickets = []
        version_id = self.get_release_version_id(base_url, prj_key, jira_auth, current_release_version)
        url = f'{base_url}/rest/api/2/search?maxResults=100'
        query = {'jql': f'project = {prj_id} AND fixVersion = {version_id} AND summary ~ "FE" AND status != "Will not do" OR project = {prj_id} AND fixVersion = {version_id} AND issuetype = Bug AND status != "Will not do" ORDER BY priority DESC, key ASC'}
        response = requests.request(
            "GET",
            url,
            headers=self.HEADER,
            params=query,
            auth=jira_auth
        ).json()
        for issue in response['issues']:
            Jira_FE_Tickets.append(issue['key'])
        testrail_ref_tickets = []
        url = f"https://relayr102.testrail.net/index.php?api/v2/get_cases/{testrail_prj_id}&suite_id=969"
        results = []
        try:
            while True:
                response = requests.request(
                    "GET",
                    url,
                    headers=self.HEADER,
                    auth=testrail_auth
                ).json()
                results += response['cases']
                if "next" not in response['_links']:
                    break
                next_link = response['_links']['next']
                url = f"https://relayr102.testrail.net/index.php?{next_link}"
        except Exception as e:
            print(e)
        for test in results:
            ref_ids = test['refs']
            if ref_ids != None:
                ids = ref_ids.split(',')
                for id in ids:
                    testrail_ref_tickets.append(id.strip())
        tickets_tested = []
        tickets_not_tested = []
        for tickets in Jira_FE_Tickets:
            if tickets in testrail_ref_tickets:
                tickets_tested.append(tickets)
            else:
                tickets_not_tested.append(tickets)
        requirements_coverage = (len(tickets_tested)/len(Jira_FE_Tickets)*100)
        self.generate_report(metric_name=f"2. Requirements Coverage on Release Version {current_release_version}", formula=formula, info1=f'Total no. of FE and bug tickets included in {current_release_version}  = {len(Jira_FE_Tickets)}',
                             info2=f'Tickets not tested by QA = {tickets_not_tested}', info3=f'Requirements Coverage Percentage = {round(requirements_coverage)} %')

    def test_calculate_valid_bug_percentage(self, base_url, prj_key, jira_auth, current_release_version):
        formula = "Valid bugs percentage = (No. of valid bugs / Total no. of bugs reported) * 100"
        total_issues = []
        valid_issues = []
        url = f'{base_url}rest/api/3/search?maxResults=100'
        query = {'jql': f'project = {prj_key} AND issuetype = Bug AND affectedVersion = {current_release_version} AND "Env[Dropdown]" in (Development, Staging) order by created DESC'}
        captured_issues = self.get_filtered_issues(url, query, jira_auth)
        for issue in captured_issues['issues']:
            total_issues.append(issue['key'])
            issue_status = issue['fields']['status']['name']
            if issue_status != "Will not do":
                valid_issues.append(issue['key'])
        valid_bugs_percentage = (len(valid_issues)/len(total_issues))*100
        self.generate_report(metric_name="3. Valid Bugs Percentage", formula=formula, info1=f'Total no. of valid bugs = {len(valid_issues)}',
                             info2=f'Total no. of invalid bugs = {(len(total_issues)-len(valid_issues))}', info3=f'Valid Bugs Percentage = {round(valid_bugs_percentage)} %')

    def test_get_automated_percentage(self, testrail_prj_id, testrail_suite_id, testrail_auth):
        formula = "Automation Progress = Total no. of actual test cases automated / Total no. of test cases that are " \
                  "automatable. "
        testcase_ids = []
        non_automatable_test_id = []
        automated_test_id = []
        url = f"https://relayr102.testrail.net/index.php?api/v2/get_cases/{testrail_prj_id}&suite_id={testrail_suite_id}"
        total_test = []
        try:
            while True:
                response = requests.request(
                    "GET",
                    url,
                    headers=self.HEADER,
                    auth=testrail_auth
                ).json()
                total_test += response['cases']
                if "next" not in response['_links']:
                    break
                next_link = response['_links']['next']
                url = f"https://relayr102.testrail.net/index.php?{next_link}"
        except Exception as e:
            print(e)
        for test in total_test:
            testcase_ids.append(test['id'])
        for test in total_test:
            if test['custom_automation'] == 4:
                non_automatable_test_id.append(test['id'])
        for test in total_test:
            if test['custom_automation'] == 1:
                automated_test_id.append(test['id'])
        Automatable_tests = [id for id in testcase_ids if id not in non_automatable_test_id]
        Automated_percentage = (len(automated_test_id) / len(Automatable_tests)) * 100
        self.generate_report(metric_name="4. Automated Percentage", formula=formula, info1=f'Total Testcases Automatable = {len(Automatable_tests)}',
                             info2=f'Total Testcases Automated = {len(automated_test_id)}',
                             info3=f'Total Automated Percentage = {round(Automated_percentage, 2)} %')

