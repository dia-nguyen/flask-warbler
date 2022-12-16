"""Anon View Tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_views.py

import os
from unittest import TestCase

from models import db, Message, User, connect_db

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# This is a bit of hack, but don't use Flask DebugToolbar

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

connect_db(app)

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class AnonViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        m1 = Message(text="test message")

        u1.following.append(u2)
        u2.messages.append(m1)
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.m1_id = m1.id

        self.client = app.test_client()

    def teardown(self):
        db.session.rollback()

    def test_home_page(self):
        """Tests that homepage displays for non logged in user properly"""
        with self.client as c:
            resp = c.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign up', html)

    def test_display_signup_form(self):
        """Tests that sign up form displays for non logged in user properly"""
        with self.client as c:
            resp = c.get("/signup")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign me up!', html)

    def test_display_login_form(self):
        """Tests that login form displays for non logged in user properly"""
        with self.client as c:
            resp = c.get("/login")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome back.', html)

    def test_unauthorized_display_all_users(self):
        """Tests that unlogged in user cannot view all users page."""
        with self.client as c:
            resp = c.get(
                "/users",
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)

    def test_unauthorized_display_specific_users(self):
        """Tests that unlogged in user cannot view a user's page."""
        with self.client as c:
            resp = c.get(
                f"/users/{self.u1_id}",
                follow_redirects=True
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)

    def test_unauthorized_view_followed(self):
        """Tests that non logged in users cannot view a user's followers"""
        with self.client as c:
            resp = c.get(f"/users/{self.u1_id}/followers",
            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)

    def test_unauthorized_view_following(self):
        """Tests that non logged in users cannot view followings"""
        with self.client as c:
            resp = c.get(f"/users/{self.u1_id}/following",
            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)

    def test_unauthorized_follow(self):
        """Tests that an unlogged in user cannot follow someone."""
        with self.client as c:
            resp = c.post(f"/users/follow/{self.u1_id}",
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)

    def test_unauthorized_unfollow(self):
        """Tests that an unlogged in user cannot unfollow someone."""
        with self.client as c:
            resp = c.post(f"/users/stop-following/{self.u1_id}",
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)

    def test_unauthorized_edit_profile(self):
        """Tests that an unlogged in user cannot edit their own profile."""
        with self.client as c:

            resp = c.post("/users/profile",
            data={
                'location': 'California',
                'password': 'password',
            },
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)

    def test_unauthorized_view_message(self):
        """Tests that an unlogged in user cannot view a message."""
        with self.client as c:

            resp = c.get(
                f"/messages/{self.m1_id}",
                follow_redirects=True
                )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)

    def test_unauthorized_view_add_message(self):
        """Tests that non logged in users cannot view add message form"""
        with self.client as c:
            resp = c.get("/messages/new",
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)

    def test_unauthorized_add_message(self):
        """Tests that non logged in users cannot add new message"""
        with self.client as c:
            resp = c.post("/messages/new",
            data={"text": "Hello"},
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)

    def test_unauthorized_like_message(self):
        """Tests that an unlogged in user cannot like a message."""
        with self.client as c:
            resp = c.post(
                f"/messages/{self.m1_id}/like",
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)

    def test_unauthorized_delete_message(self):
        """Tests that non logged in users cannot delete message"""
        with self.client as c:
            resp = c.post(f"/messages/{self.m1_id}/delete",
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)

    def test_unauthorized_delete_user(self):
        """Tests that an unlogged in user cannot delete their own profile."""
        with self.client as c:

            resp = c.post("/users/delete",
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Sign up", html)
