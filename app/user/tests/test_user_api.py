from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_UEL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


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

    def test_create_token_for_user(self):
        """Test generate token for valid credentials"""
        user_details = {
            "email": "test@example.com",
            "password": "pass123",
            "name": "Test Name",
        }
        create_user(**user_details)
        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }
        result = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", result.data)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid"""
        create_user(email="Test@example.com", password="pass123")
        payload = {"email": "Test@example.com", "password": "pass321"}
        result = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", result.data)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting an blank password returns an error"""
        payload = {"email": "Test@example.com", "password": ""}
        result = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", result.data)
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorize(self):
        """Test authentication is required for users"""
        result = self.client.get(ME_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUSerApiTests(TestCase):
    """Test api request that required authentication"""

    def setUp(self):
        self.user = create_user(
            email="test@example.com", password="pass123", name="TestName"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile of logged in user"""
        result = self.client.get(ME_URL)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(
            result.data,
            {
                "name": self.user.name,
                "email": self.user.email,
            },
        )

    def test_me_not_allowed(self):
        """Test Post is not allowed in me endpoint"""
        result = self.client.post(ME_URL, {})
        self.assertEqual(result.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated users"""
        payload = {
            "name": "NewName",
            "email": "newTest@example.com",
            "password": "NewPass12345",
        }
        result = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(result.status_code, status.HTTP_200_OK)
