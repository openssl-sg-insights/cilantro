import unittest
import json
import os
import datetime
import shutil
import time

from pymongo import MongoClient

from service.run_service import app
from test.service.unit.user.user_utils import get_auth_header, test_user


class JobControllerTest(unittest.TestCase):
    """Test the job controller to validate the parameter payload."""

    test_resource_dir = 'test/resources'
    staging_dir = os.environ['STAGING_DIR']

    def setUp(self):
        """Prepare test setup."""
        self._stage_test_folder('files', 'some_tiffs')
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        """Remove test data from staging dir."""
        shutil.rmtree(os.path.join(self.staging_dir, test_user, 'some_tiffs'),
                      ignore_errors=True)

    def _stage_test_folder(self, folder, path):
        source = os.path.join(self.test_resource_dir, folder, path)
        target = os.path.join(self.staging_dir, test_user, path)
        try:
            if os.path.isdir(source):
                shutil.copytree(source, target)
        except FileExistsError:
            pass

    def test_get_job_type_schema(self):
        """Test if a ingest-journals schema is returned when requested."""
        url = '/job/param_schema/ingest_journals'
        response_text = self.client.get(url).get_data(as_text=True)
        self.assertTrue("{\"$schema\"" in response_text)

    def test_create_ingest_journals_job(self):
        """
        Test listing of jobs.

        The test creates a job and then gets a list of all jobs.
        The job list is checked for existence of a job-id, the test user,
        the correct job type and job name.
        """
        job_params = self._read_test_params()
        self._make_request('/job/ingest_journals',
                           json.dumps(job_params), 202)

    def test_list_jobs(self):
        """
        Test creating and listing jobs.

        It is tested if some parameters show up in the job list response.
        """
        self.test_create_ingest_journals_job()

        response = self.client.get('/job/jobs', headers=get_auth_header())
        last_job_json = response.get_json()[-1]

        self.assertTrue(last_job_json["job_id"])
        self.assertEqual("test_user", last_job_json["user"])
        self.assertEqual("ingest_journals", last_job_json["job_type"])
        self.assertEqual(f'ingest_journals-{last_job_json["job_id"]}',
                         last_job_json["name"])

    def test_create_job_no_payload(self):
        """Job creation has to fail without POST payload."""
        self._make_request('/job/ingest_journals', None, 400,
                           'invalid_job_params', 'No request payload found')

    def test_create_job_invalid_json(self):
        """Test job creation to fail when the POST payload is not JSON."""
        self._make_request('/job/ingest_journals',
                           'jkfj,;', 400, 'bad_request')

    def test_create_job_unknown_param(self):
        """Test job creation to fail when there are unknown params given."""
        job_params = self._read_test_params()
        job_params['bla'] = 'blup'

        self._make_request('/job/ingest_journals', json.dumps(job_params), 400,
                           'invalid_job_params',
                           'Additional properties are not allowed')

    def test_create_job_missing_param(self):
        """Test job creation to fail when there are params missing."""
        job_params = self._read_test_params()
        del job_params['targets'][0]['metadata']
        self._make_request('/job/ingest_journals', json.dumps(job_params), 400,
                           'invalid_job_params', 'is a required property')

    def test_create_job_wrong_param_type(self):
        """Test job creation to fail when a param has the wrong type."""
        job_params = self._read_test_params()
        job_params['targets'][0]['metadata']['volume'] = "asdf"
        self._make_request('/job/ingest_journals', json.dumps(job_params), 400,
                           'invalid_job_params', 'is not of type')

    def _make_request(self, job_name, payload, expected_http_code,
                      expected_error_code='', expected_error_message=''):
        response = self.client.post(job_name, data=payload,
                                    headers=get_auth_header())

        self.assertEqual(response.status_code, expected_http_code)
        response_json = response.get_json()
        if str(expected_http_code)[0] == '2':
            self.assertTrue(response_json['success'])
        else:
            self.assertFalse(response_json['success'])
            self.assertEqual(response_json['error']['code'],
                             expected_error_code)
            self.assertTrue(expected_error_message in
                            response_json['error']['message'])

        return response

    def _read_test_params(self):
        test_params_path = os.path.join(self.test_resource_dir, 'params',
                                        'journal.json')

        with open(test_params_path, 'r') as params_file:
            job_params = json.loads(params_file.read())

        return job_params
