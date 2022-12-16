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

#make multiple classes and group test cases by categories
#can have their own setup/tear down or inherit from base testcase
class UserViewTestCase(TestCase):
    def setUp(self):
        """Set up users and messages"""
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        u3 = User.signup("u3", "u3@email.com", "password", None)
        m1 = Message(text="test message")
        db.session.add_all([u1, u2, u3, m1])
        u1.following.append(u2)
        u3.following.append(u1)
        u2.messages.append(m1)

        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u3_id = u3.id
        self.m1_id = m1.id

        self.client = app.test_client()

    def teardown(self):
        db.session.rollback()

    def test_signup(self):
        """Tests that user can sign up properly"""
        with self.client as c:
            resp = c.post("/signup",
            data={
                'username': 'test_user',
                'email': 'test@email.com',
                'password': 'testpassword',
            },
            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@test_user", html)

    #TODO: invalid sign up
    # def test_invalid_sign_up(self):
    #     with self.client as c:
    #         resp = c.post("/signup",
    #         data={
    #             'username': 'u1',
    #             'email': 'test@email.com',
    #             'password': 'testpassword',
    #         },
    #         follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         # check to see if still on sign up form
    #         self.assertIn('Sign me up!', html)
    #         self.assertIn("Username already taken", html)

    # with self.assertRaises(exc.IntegrityError):


    def test_home_logged_in(self):
        """Tests that home page displays as logged in user properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@u1', html)

    def test_login(self):
        """Tests that user can login properly"""
        with self.client as c:
            resp = c.post("/login",
            data={
                'username': 'u1',
                'password': 'password',
            },
            follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Hello, u1!", html)

    def test_logout(self):
        """Tests that user can logout properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("/logout",
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Good bye!", html)

    def test_display_all_users(self):
        """Tests that user can view all users properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get("/users")

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("u1", html)
            self.assertIn("u2", html)
            self.assertIn("u3", html)

    def test_search_user(self):
        """Tests that user can search for users properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get("/users",
            query_string={'q':"u1"})

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("u1", html)
            self.assertNotIn("u2", html)
            self.assertNotIn("u3", html)

    def test_search_invalid_user(self):
        """Tests that invalid user search will show 'No users found' properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get("/users",
            query_string={'q':"idontexist"})

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sorry, no users found", html)

    #this is for search query
    def test_display_user_profile(self):
        """Tests that user can view user profile properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get("/users",
            query_string={'q':"u1"})

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@u1", html)
            self.assertIn("warbler-hero", html)


    def test_display_following(self):
        """Tests that user can view user following properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/following")

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@u2", html)
            self.assertIn("Unfollow", html)

    def test_display_followers(self):
        """Tests that user can view user followers properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/followers")

            html = resp.get_data(as_text=True)
            self.assertIn("@u3", html)

    def test_start_following(self):
        """Tests that following another user works properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f"/users/follow/{self.u3_id}",
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@u3", html)
            #test length of following list

    def test_stop_following(self):
        """Tests that unfollowing another user works properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f"/users/stop-following/{self.u2_id}",
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@u2", html)

    def test_update_profile(self):
        """Tests that user can update their profile properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("/users/profile",
            data={
                'location': 'California',
                'password': 'password',
            },
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Information successfully updated.", html)
            self.assertIn("California", html)

    def test_invalid_update_profile(self):
        """Tests that user cannot update their profile with incorrect password properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("/users/profile",
            data={
                'location': 'California',
                'password': 'drowssap',
            },
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Incorrect password.", html)

    def test_view_likes(self):
        """Tests that user can view likes properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            u1 = User.query.get(self.u1_id)
            m1 = Message.query.get(self.m1_id)
            u1.liked_messages.append(m1)

            resp = c.get(f"/users/{self.u1_id}/likes")

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test message", html)
            self.assertIn("bi-star-fill", html)

    def test_like_message(self):
        """Tests that user can like message properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(
                f"/messages/{self.m1_id}/like",
                follow_redirects=True
            )

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("bi-star-fill", html)

    def test_unlike_message(self):
        """Tests that user can unlike message properly"""
        u1 = User.query.get(self.u1_id)
        m1 = Message.query.get(self.m1_id)
        u1.liked_messages.append(m1)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f"/messages/{self.m1_id}/like",
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('bi-star">', html)

    def test_delete_user(self):
        """Tests that user can delete account properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("/users/delete",
            follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Your account has been deleted.", html)
            self.assertIn("Sign me up", html)

    def test_delete_other_user_message(self):
        """Tests that user cannot delete other user messages properly"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f"/messages/{self.m1_id}/delete",
            follow_redirects=True)

            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("You cannot delete someone else&#39;s message!", html)








