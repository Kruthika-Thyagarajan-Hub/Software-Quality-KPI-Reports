# Software-Quality-KPI-Reports

Key performance indicator is a number that shows how a process is performing or progressing towards intended result based on different metrics adapted.

***How to setup***

Checkout the project
cd qa_kpi_report
Install python3
Run python3 -m venv venv/
Run source venv/bin/activate
Run pip install -r requirements.txt
(or alternatively)

Set up isolated python virtual environment by running ./setup.sh
It will install virtualenv library if you don't have it yet and install all python libraries you need to run the tests.
Run source venv/bin/activate

***How to generate report***

Steps:

Go to folder: cd qa_kpi_report

Run pytest kpi_report.py -s

Html report namedKPI_report_jinja.html will be generated or updated in the root folder

Open the html report and click on the browser of your choice from the available options on the right side panel to see the final report
