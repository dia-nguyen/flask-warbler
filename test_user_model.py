"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, connect_db
from sqlalchemy import exc

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

connect_db(app)

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        """Set up users and messages"""
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        """Tests that user exists"""
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_is_following(self):
        """Tests that is_follow method displays follows properly"""
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.following.append(u2)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))

    def test_is_followed_by(self):
        """Tests that is_followed_by method displays followed by properly"""
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.following.append(u2)
        db.session.commit()

        self.assertTrue(u2.is_followed_by(u1))
        self.assertFalse(u1.is_followed_by(u2))

    def test_successful_user_signup(self):
        """Tests that user can sign up properly"""
        new_user = User.signup("new_user", "new_user@email.com", "password", None)

        db.session.commit()
        self.assertEqual(new_user.username, "new_user")
        self.assertEqual(new_user.email, "new_user@email.com")
        self.assertNotEqual(new_user.password, "password")

    def test_unsuccessful_user_signup(self):
        """Tests that user cannot use existing email or username properly"""
        with self.assertRaises(exc.IntegrityError):
            User.signup("u1", "new_user@email.com", "password", None)
            db.session.commit()

    def test_valid_credentials(self):
        """Tests that valid credentials can log in properly"""
        u1 = User.query.get(self.u1_id)
        valid_credentials = User.authenticate("u1", "password")

        self.assertEqual(valid_credentials, u1)

    def test_invalid_username(self):
        """Tests that invalid username cannot log in, properly"""
        invalid_credentials = User.authenticate("u3", "password")
        self.assertFalse(invalid_credentials)

    def test_invalid_password(self):
        """Tests that invalid password cannot log in, properly"""
        invalid_credentials = User.authenticate("u1", "wrongpassword")
        self.assertFalse(invalid_credentials)










