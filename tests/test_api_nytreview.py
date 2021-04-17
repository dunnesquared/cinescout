"""Performs unit test on functions in cinescout.api.nytreviewapi."""

import os
import time
import unittest

# Add this line to whatever test script you write
from context import app, db, basedir, User


class NytReviewApiTests(unittest.TestCase):
    def setUp(self):
        # """Executes before each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tests/test.db')
        self.app = app.test_client()

        # Need to push app's new test context to ensure that db is created anew.
        with app.app_context():
            db.drop_all()
            db.create_all()

        # See whether default user in db. If not add him. 
        default_user = User.query.filter_by(username="Alex").first()
        if not default_user:
            print("Creating default user 'Alex'...")
            self.create_user(name="Alex", email="alex@test.com", password="123")

        # Endpoint to query
        self.end_point = '/api//nyt-movie-review'

        # Data that can be use to test out api normally or modified for other test
        self.movie_data = {
                            'title': 'Exotica',
                            'original_title': 'Exotica',
                            'release_year': 1994,
                            'release_date': '1994-11-30'
                          }

    def tearDown(self):
        """Executes after each test."""
        db.session.remove()
        db.drop_all()

    # **** HELPER METHODS ****
    def delay_api_call(self, amt=6):
        """Delays executions by amt seconds"""
        print(f"DELAYING API CALL BY {amt} seconds...")
        time.sleep(amt)

    def create_user(self, name, email, password):
        u = User(username=name, email=email)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        return u
    
    def login(self, username, password):
        return self.app.post(
            '/login',
            data=dict(username=username, password=password),
            follow_redirects=True
        )

    def logout(self):
        return self.app.get(
            '/logout',
            follow_redirects=True
        )

    # +++++++++++++++++++++++++++++++ TESTS: nytreview.py +++++++++++++++++++++++++++++++++
    def test_get_review_not_logged_in(self):
        response = self.app.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        print(json_data)
        self.assertEqual(response.status_code, 401)
        self.assertFalse(json_data['success'])
        self.assertIn("Current user not authenticated.", json_data['err_message'])

    def test_get_review_ok(self):
        self.login("Alex", "123")
        response = self.app.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json_data['success'])
        self.assertIn('Tax inspector obsessed with stripper', json_data['review_text'])
        self.assertFalse(json_data['critics_pick'])
        self.assertFalse(json_data['review_warning'])
        
     
if __name__ == "__main__":
    unittest.main()
