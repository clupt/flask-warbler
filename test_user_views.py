"""User View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_user_views.py

import os
from unittest import TestCase
from models import db, Follows, User, Message, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

class UserBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@e.com", "password", None)
        u2 = User.signup("u2", "u2@e.com", "password", None)

        db.session.add_all([u1, u2])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

class UserListTestCase(UserBaseViewTestCase):
    def test_users_list(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id
            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertIn("u1", html)
            self.assertIn("u2", html)
            self.assertNotIn("u3", html)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Testing found in index -->", html)

    def test_users_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"users/{self.u1_id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("u1", html)
            self.assertIn("<!-- Testing found in show -->", html)

    def test_user_delete_profile(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post("users/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<!-- Testing found in signup -->", html)

####################### user not authenticated tests############################
    def test_users_show_not_authenticated(self):
        with self.client as c:

            resp = c.get("/users", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def test_user_delete_profile_not_authenticated(self):
        with self.client as c:
            resp = c.post("users/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("<h4>New to Warbler?</h4>", html)








