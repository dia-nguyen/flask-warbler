"""Message model tests."""


import os
from unittest import TestCase

from models import db, Message, User, connect_db
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
        User.query.delete()
        Message.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        m1 = Message(text="test")
        m2 = Message(text="test2")
        u1.messages.append(m1)
        u2.messages.append(m2)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id
        self.m1_id = m1.id
        self.m2_id = m2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """Checks if message is created properly and associated with correct user."""
        m1 = Message.query.get(self.m1_id)
        u1 = User.query.get(self.u1_id)

        self.assertEqual(m1.id, self.m1_id)
        self.assertEqual(m1.text, "test")
        # Message should have an associated user
        self.assertIn(m1, u1.messages)

    def test_liked_message(self):
        """Checks if message liking functionality works."""
        m2 = Message.query.get(self.m2_id)
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.liked_messages.append(m2)

        self.assertIn(m2, u1.liked_messages)
        self.assertEqual(len(u1.liked_messages), 1)
        self.assertEqual(len(u2.liked_messages), 0)









