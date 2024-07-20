from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_UEL = reverse("user:create")


def create_user(**prams):
    """Create and return new user"""
    return get_user_model().objects.create_user(**prams)


class PublicUserApiTests(TestCase):
    """Test the public futures of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_successful(self):
        """Test creating a user is successful"""
        payload = {
            "email": "test@example.com",
            "password": "TestPass123",
            "name": "Test Name",
        }
        result = self.client.post(CREATE_USER_UEL, payload)
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", result.data)

    def test_user_with_email_exist_error(self):
        """Test error returned if is user is already exist"""
        payload = {
            "email": "test@example.com",
            "password": "TestPass123",
            "name": "Test Name",
        }
        create_user(**payload)
        result = self.client.post(CREATE_USER_UEL, payload)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error will return if password is shorter that 5 char"""
        payload = {
            "email": "test@example.com",
            "password": "pass",
            "name": "Test Name",
        }
        result = self.client.post(CREATE_USER_UEL, payload)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exist)
