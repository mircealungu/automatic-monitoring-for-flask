import requests
import configparser
import time
import datetime
import os
import sys
from unittest import TestLoader

# Abort if config file is not specified.
config = os.getenv('DASHBOARD_CONFIG')
if config is None:
    print('You must specify a config file for the dashboard to be able to use the unit test monitoring functionality.')
    print('Please set an environment variable \'DASHBOARD_CONFIG\' specifying the absolute path to your config file.')
    sys.exit(0)

n = 1
parser = configparser.RawConfigParser()
try:
    parser.read(config)
    if parser.has_option('dashboard', 'N'):
        n = int(parser.get('dashboard', 'N'))
    if parser.has_option('dashboard', 'TEST_DIR'):
        test_dir = parser.get('dashboard', 'TEST_DIR')
    else:
        print('No test directory specified in your config file. Please do so.')
        sys.exit(0)
    if parser.has_option('dashboard', 'SUBMIT_RESULTS_URL'):
        url = parser.get('dashboard', 'SUBMIT_RESULTS_URL')
    else:
        print('No url specified in your config file for submitting test results. Please do so.')
        sys.exit(0)
except configparser.Error:
    raise

data = {'test_runs': []}

if test_dir:
    suites = TestLoader().discover(test_dir, pattern="*test*.py")
    for i in range(n):
        for suite in suites:
            for case in suite:
                for test in case:
                    result = None
                    time1 = time.time()
                    result = test.run(result)
                    time2 = time.time()
                    t = (time2 - time1) * 1000
                    data['test_runs'].append({'name': str(test), 'exec_time': t, 'time': datetime.datetime.now(),
                                              'successful': result.wasSuccessful(), 'iter': i + 1})

print(data)

# Try to send test results to the dashboard
try:
    requests.post(url, json=data)
    print('Sent unit test results to the dashboard.')
except:
    print('Sending unit test results to the dashboard failed.')

# Try and see if there is data in the functionCall table of the database.
try:
    import sqlite3

    conn = sqlite3.connect('flask-dashboard.db')
    print('Let\'s take a look inside the db: functionCalls')
    cursor = conn.execute("SELECT endpoint  FROM functionCalls GROUP BY endpoint")
    for row in cursor:
        print('endpoint = {0}'.format(row[0]))

    print('Let\'s take a look inside the db: monitorRule')
    cursor = conn.execute("SELECT endpoint  FROM rules GROUP BY endpoint")
    for row in cursor:
        print('endpoint = {0}'.format(row[0]))

    print('Let\'s take a look inside the db: tests')
    cursor = conn.execute("SELECT name  FROM tests GROUP BY name")
    for row in cursor:
        print('name = {0}'.format(row[0]))

    conn.close()
except:
    print('Connection to sqlite db failed. No data found.')