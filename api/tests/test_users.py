"""from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User


class UserAPITest(TestCase):
    def setUp(self):
        self.cliente = APIClient()

    def test_create_user(self):
        """