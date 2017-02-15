"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

import django
from django.test import TestCase
from django.utils import unittest

# TODO: Configure your database in settings.py and sync before running tests.

class WebUIViewTest(TestCase):
    """Tests for the application views."""

    if django.VERSION[:2] >= (1, 7):
        # Django 1.7 requires an explicit setup() when running tests in PTVS
        @classmethod
        def setUpClass(cls):
            super(WebUIViewTest, cls).setUpClass()
            django.setup()

    def test_home(self):
        """Tests the home page."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        """Tests about page."""
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()