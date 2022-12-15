"""Message View tests."""

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

from app import app, CURR_USER_KEY

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

class UserViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)

        db.session.add(u1)
        db.session.commit()

        self.u1_id = u1.id

        self.client = app.test_client()

    def test_display_sign_up(self):
        with app.test_client() as client:
            resp = client.get("/signup")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign me up!', html)

    def test_sign_up(self):
        with app.test_client() as client:
            resp = client.post("/signup",
            data={
                'username': 'test_user',
                'email': 'test@email.com',
                'password': 'testpassword',
            },
            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@test_user", html)

    def test_invalid_sign_up(self):
        with app.test_client() as client:
            resp = client.post("/signup",
            data={
                'username': 'u1',
                'email': 'test@email.com',
                'password': 'testpassword',
            },
            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # check to see if still on sign up form
            self.assertIn('Sign me up!', html)
            self.assertIn("Username already taken", html)



