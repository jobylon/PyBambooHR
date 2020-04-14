#!/usr/bin/env python
#encoding:utf-8
#author:smeggingsmegger/Scott Blevins
#project:PyBambooHR
#repository:http://github.com/smeggingsmegger/PyBambooHR
#license:agpl-3.0 (http://www.gnu.org/licenses/agpl-3.0.en.html)

"""Unittests for employees api
"""

import httpretty
import json
import os
import sys
import unittest

from json import dumps
from requests import HTTPError

# Force parent directory onto path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyBambooHR import PyBambooHR

class test_employees(unittest.TestCase):
    # Used to store the cached instance of PyBambooHR
    bamboo = None

    # Another instance, using underscore keys
    bamboo_u = None

    def setUp(self):
        if self.bamboo is None:
            self.bamboo = PyBambooHR(subdomain='test', api_key='testingnotrealapikey')

        if self.bamboo_u is None:
            self.bamboo_u = PyBambooHR(subdomain='test', api_key='testingnotrealapikey', underscore_keys=True)

    @httpretty.activate
    def test_get_employee_directory(self):
        body = {"fields": [
            {
                "id": "displayName",
                "type": "text",
                "name": "Display name"
            },
            {
                "id": "firstName",
                "type": "text",
                "name": "First name"
            },
            {
                "id": "lastName",
                "type": "text",
                "name": "Last name"
            },
            {
                "id": "jobTitle",
                "type": "list",
                "name": "Job title"
            },
            {
                "id": "workPhone",
                "type": "text",
                "name": "Work Phone"
            },
            {
                "id": "workPhoneExtension",
                "type": "text",
                "name": "Work Extension"
            },
            {
                "id": "mobilePhone",
                "type": "text",
                "name": "Mobile Phone"
            },
            {
                "id": "workEmail",
                "type": "email",
                "name": "Work Email"
            },
            {
                "id": "department",
                "type": "list",
                "name": "Department"
            },
            {
                "id": "location",
                "type": "list",
                "name": "Location"
            },
            {
                "id": "division",
                "type": "list",
                "name": "Division"
            },
            {
                "id": "photoUploaded",
                "type": "bool",
                "name": "Employee photo exists"
            },
            {
                "id": "photoUrl",
                "type": "url",
                "name": "Employee photo url"
            }],
            "employees": [
                {
                    "id": "123",
                    "displayName": "Test Person",
                    "firstName": "Test",
                    "lastName": "Person",
                    "jobTitle": "Testing Coordinator",
                    "workPhone": "555-555-5555",
                    "workPhoneExtension": "",
                    "mobilePhone": "555-555-5555",
                    "workEmail": "test@testperson.com",
                    "department": "Useless Department",
                    "location": "Testville, US",
                    "division":  None,
                    "photoUploaded":  False,
                    "photoUrl": "https://iws.bamboohr.com/images/photo_placeholder.gif"
                }]
        }
        body = dumps(body)
        httpretty.register_uri(httpretty.GET, "https://api.bamboohr.com/api/gateway.php/test/v1/employees/directory",
                               body=body, content_type="application/json")

        employees = self.bamboo.get_employee_directory()
        self.assertIsNotNone(employees[0])
        self.assertEquals('123', employees[0]['id'])
        self.assertEquals('test@testperson.com', employees[0]['workEmail'])

        employees = self.bamboo_u.get_employee_directory()
        self.assertIsNotNone(employees[0])
        self.assertEquals('123', employees[0]['id'])
        self.assertEquals('test@testperson.com', employees[0]['work_email'])

    @httpretty.activate
    def test_get_employee_specific_fields(self):
        # Request specific fields
        httpretty.register_uri(httpretty.GET, "https://api.bamboohr.com/api/gateway.php/test/v1/employees/123",
                               body='{"workEmail": "user@test.com", "workPhone": "555-555-5555", "id": "123"}',
                               content_type="application/json")

        employee = self.bamboo.get_employee(123, ['workPhone', 'workEmail'])
        self.assertIsNotNone(employee)
        self.assertEquals(employee['workEmail'], 'user@test.com')
        self.assertEquals(employee['workPhone'], '555-555-5555')
        self.assertEquals(employee['id'], '123')

        employee = self.bamboo_u.get_employee(123, ['workPhone', 'workEmail'])
        self.assertIsNotNone(employee)
        self.assertEquals(employee['work_email'], 'user@test.com')
        self.assertEquals(employee['work_phone'], '555-555-5555')

    @httpretty.activate
    def test_get_employee_all_fields(self):
        # Request all fields
        # NOTE: We are mocking this so we aren't getting all fields- we are just adding city.
        httpretty.register_uri(httpretty.GET, "https://api.bamboohr.com/api/gateway.php/test/v1/employees/123",
                               body='{"workEmail": "user@test.com", "workPhone": "555-555-5555", "id": "123", "city": "Testville"}',
                               content_type="application/json")

        employee = self.bamboo.get_employee(123)
        self.assertIsNotNone(employee)
        self.assertEquals(employee['workEmail'], 'user@test.com')
        self.assertEquals(employee['workPhone'], '555-555-5555')
        self.assertEquals(employee['city'], 'Testville')
        self.assertEquals(employee['id'], '123')

    @httpretty.activate
    def test_add_employee(self):
        httpretty.register_uri(httpretty.POST, "https://api.bamboohr.com/api/gateway.php/test/v1/employees/",
                               body='', status='201', adding_headers={'location': 'https://api.bamboohr.com/api/gateway.php/test/v1/employees/333'})
        employee = {
            'firstName': 'Test',
            'lastName': 'Person'
        }
        result = self.bamboo.add_employee(employee)
        self.assertEqual(result['id'], '333')

        # Test adding with underscore keys
        employee = {
            'first_name': 'Test',
            'last_name': 'Person'
        }
        result = self.bamboo.add_employee(employee)
        self.assertEqual(result['id'], '333')

        employee = {
            'firstName': u'Test',
            'lastName': u'Pêrsón'
        }
        result = self.bamboo.add_employee(employee)
        self.assertEqual(result['id'], '333')

    @httpretty.activate
    def test_add_employee_failure(self):
        httpretty.register_uri(httpretty.POST, "https://api.bamboohr.com/api/gateway.php/test/v1/employees/",
                               body='', status='400', adding_headers={'location': 'https://api.bamboohr.com/api/gateway.php/test/v1/employees/333'})
        employee = {}
        self.assertRaises(UserWarning, self.bamboo.add_employee, employee)

    @httpretty.activate
    def test_update_employee(self):
        # Good result
        httpretty.register_uri(httpretty.POST, "https://api.bamboohr.com/api/gateway.php/test/v1/employees/333", body='', status='200')
        employee = {
            'firstName': 'Test',
            'lastName': 'Person'
        }
        result = self.bamboo.update_employee(333, employee)
        self.assertTrue(result)

        # Test updating with underscore keys
        employee = {
            'first_name': 'Test',
            'last_name': 'Person'
        }
        result = self.bamboo.update_employee(333, employee)
        self.assertTrue(result)

    @httpretty.activate
    def test_update_employee_failure(self):
        # Forbidden result
        httpretty.register_uri(httpretty.POST, "https://api.bamboohr.com/api/gateway.php/test/v1/employees/333", body='', status='403')
        employee = {}
        self.assertRaises(HTTPError, self.bamboo.update_employee, 333, employee)

    @httpretty.activate
    def test_get_tabular_data(self):
        resp = [{
            'date': '2010-06-01',
            'location': 'New York Office',
            'divison': 'Sprockets',
            'department': 'Research and Development',
            'jobTitle': 'Machinist',
            'reportsTo': 'John Smith'
        }]
        httpretty.register_uri(httpretty.GET,
                               "https://api.bamboohr.com/api/gateway.php/test/v1/employees/123/tables/customTable",
                               body=json.dumps(resp),
                               content_type="application/json")
        table = self.bamboo.get_tabular_data('customTable', 123)

        self.assertIsNotNone(table)
        self.assertEqual(len(table), 1)
        self.assertEqual(table[0]['location'], 'New York Office')
        self.assertEqual(table[0]['reportsTo'], 'John Smith')

    @httpretty.activate
    def test_get_tabular_data_all_employees(self):
        resp = [{
            'id': '38563',
            'employeeId': '4',
            'date': '2016-04-09',
            'location': 'Lindon, Utah',
            'department': 'Human Resources',
            'division': 'North America',
            'jobTitle': 'Associate HR Administrator',
            'reportsTo': 'Jennifer Caldwell'
        },{
            'id': '38564',
            'employeeId': '5',
            'date': '2018-12-09',
            'location': 'London, UK',
            'department': 'Human Resources',
            'division': 'Europe',
            'jobTitle': 'HR Administrator',
            'reportsTo': 'Jennifer Caldwell'
        }]
        httpretty.register_uri(httpretty.GET,
                               "https://api.bamboohr.com/api/gateway.php/test/v1/employees/all/tables/customTable",
                               body=json.dumps(resp),
                               content_type="application/json")
        table = self.bamboo.get_tabular_data('customTable')

        self.assertIsNotNone(table)
        self.assertEqual(len(table), 2)
        self.assertEqual(table[0]['id'], '38563')
        self.assertEqual(table[1]['id'], '38564')

    @httpretty.activate
    def test_add_row(self):
        httpretty.register_uri(httpretty.POST,
                               "https://api.bamboohr.com/api/gateway.php/test/v1/employees/333/tables/customTable/",
                               body='',
                               status='200')

        row = {'custom_type_a': 'New Value A'}
        result = self.bamboo.add_row('customTable', '333', row)

        self.assertTrue(result)

    @httpretty.activate
    def test_add_row_failure(self):
        # Forbidden result
        httpretty.register_uri(httpretty.POST,
                               "https://api.bamboohr.com/api/gateway.php/test/v1/employees/123/tables/customTable/",
                               body='',
                               status='406')
        row = {'invalid_id': 'New Value A'}

        self.assertRaises(HTTPError, self.bamboo.add_row, 'customTable', '123', row)

    @httpretty.activate
    def test_update_row(self):
        httpretty.register_uri(httpretty.POST,
                               "https://api.bamboohr.com/api/gateway.php/test/v1/employees/333/tables/customTable/321/",
                               body='',
                               status='200')
        row = {'custom_type_a': 'New Value A'}
        result = self.bamboo.update_row('customTable', '333', '321', row)

        self.assertTrue(result)

    @httpretty.activate
    def test_get_employee_files_list(self):
        resp = {
            'employee': {
                'id': 123
            },
            'categories': [
                {
                    'files': [
                        {
                            'canRenameFile': 'yes',
                            'name': 'Company Handbook.pdf',
                            'dateCreated': '2020-01-18T20:45:51+0000',
                            'shareWithEmployee': 'yes',
                            'canDeleteFile': 'yes',
                            'createdBy': 'Charlotte Abbott',
                            'canChangeShareWithEmployeeFieldValue': 'yes',
                            'id': 4,
                            'originalFileName': 'Company Handbook.pdf',
                            'size': 2807480
                        },
                        {
                            'canRenameFile': 'yes',
                            'name': 'I-9 (2017).pdf',
                            'dateCreated': '2020-01-18T21:25:11+0000',
                            'shareWithEmployee': 'yes',
                            'canDeleteFile': 'yes',
                            'createdBy': 'Charlotte Abbott',
                            'canChangeShareWithEmployeeFieldValue': 'yes',
                            'id': 10,
                            'originalFileName': 'I-9 (2017).pdf',
                            'size': 2750869
                        }
                    ],
                    'canDeleteCategory': 'no',
                    'canUploadFiles': 'yes',
                    'name': 'Signed Documents',
                    'canRenameCategory': 'no',
                    'displayIfEmpty': 'yes',
                    'id': 12
                },
                {
                    'files': [],
                    'canDeleteCategory': 'no',
                    'canUploadFiles': 'yes',
                    'name': 'Tasklist Attachments',
                    'canRenameCategory': 'no',
                    'displayIfEmpty': 'yes',
                    'id': 11
                }
            ]
        }
        httpretty.register_uri(httpretty.GET,
                               "https://api.bamboohr.com/api/gateway.php/test/v1/employees/123/files/view",
                               body=json.dumps(resp),
                               status='200')

        data = self.bamboo.get_employee_files_list(123)
        self.assertIsNotNone(data.get('employee'))
        self.assertIsNotNone(data.get('categories'))
        self.assertEqual(len(data['categories']), 2)

    @httpretty.activate
    def test_create_file_category(self):
        httpretty.register_uri(httpretty.POST,
                               "https://api.bamboohr.com/api/gateway.php/test/v1/employees/files/categories/",
                               body='',
                               status='201')
        result = self.bamboo.create_employee_file_category('category_name')
        self.assertTrue(result)
