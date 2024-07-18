from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models."""

    def test_create_with_email_successful(self):
        """Test creating a user with email is successful"""
        email = "test1@example.com"
        password = "TestPass123"
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["TEST2@EXAMPLE.com", "TEST2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["teSt4@example.COM", "teSt4@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "pass123")
            self.assertEqual(user.email, expected)

    def test_user_without_raises_error(self):
        """test creating with out a email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "pass123")

    def test_create_superuser(self):
        "test creating a superuser"
        user = get_user_model().objects.create_superuser("admin@example.com", "pass123")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
