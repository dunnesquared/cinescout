"""Performs unit test on functions in cinescout.api.nytreviewapi."""

import os

# Use in-memory database for testing.
os.environ['DATABASE_URL'] = 'sqlite://'

import time
import unittest

# Add this line to whatever test script you write
from context import app, db, basedir, User


class NytReviewApiTests(unittest.TestCase):
    def setUp(self):
        """Executes before each test."""
        self.app = app

        # Create and push app context before any db transactions
        self.appctx = self.app.app_context()
        self.appctx.push()
        db.create_all()
        
        # Create a client to make HTTP requests.
        self.client = self.app.test_client()

        # Set some config options (not sure these do anything anymore)
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False

        # Add user to test db. See whether Alex exists. If not add him. 
        default_user = User.query.filter_by(username="Alex").first()
        if not default_user:
            print("Creating default user 'Alex'...")
            self.create_user(name="Alex", email="alex@test.com", 
                            password="123")

        # Endpoint to query
        self.end_point = '/api/nyt-movie-review'

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

        # Delete app context, no longer required.
        self.appctx.pop()
        self.app = None
        self.appctx = None
        self.client = None

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
        return self.client.post(
            '/login',
            data=dict(username=username, password=password),
            follow_redirects=True
        )

    def logout(self):
        return self.client.get(
            '/logout',
            follow_redirects=True
        )

    # +++++++++++++++++++++++++++++++ TESTS: nytreview.py +++++++++++++++++++++++++++++++++
    def test_not_logged_in(self):
        response = self.client.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        print(json_data)
        self.assertEqual(response.status_code, 401)
        self.assertFalse(json_data['success'])
        self.assertIn("Current user not authenticated.", json_data['err_message'])

    # Review found.
    def test_review_found(self):
        self.login("Alex", "123")
        response = self.client.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(json_data['success'])
        self.assertIn('Tax inspector obsessed with stripper', json_data['review_text'])
        self.assertFalse(json_data['critics_pick'])
        self.assertFalse(json_data['review_warning'])
    
    # Review not found. Multiple cases.
    # Missing input.
    def test_no_title(self):
        self.login("Alex", "123")
        self.movie_data['title'] = None
        response = self.client.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json_data['success'])
    
    def test_no_original_title(self):
        self.login("Alex", "123")
        self.movie_data['original_title'] = None
        response = self.client.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json_data['success'])
    
    def test_no_release_year(self):
        self.login("Alex", "123")
        self.movie_data['release_year'] = None
        response = self.client.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json_data['success'])
    
    def test_no_release_date(self):
        self.login("Alex", "123")
        self.movie_data['release_date'] = None
        response = self.client.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json_data['success'])

    # Bad input
    def test_bad_title(self):
        self.login("Alex", "123")
        self.movie_data['title'] = ('bad', 'type')
        response = self.client.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json_data['success'])
    
    def test_bad_original_title(self):
        self.login("Alex", "123")
        self.movie_data['original_title'] = ('bad', 'type')
        response = self.client.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json_data['success'])
    
    def test_bad_release_year(self):
        self.login("Alex", "123")
        self.movie_data['release_year'] = ('bad', 'type')
        response = self.client.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json_data['success'])
    
    def test_bad_release_date(self):
        self.login("Alex", "123")
        self.movie_data['release_date'] = ('bad', 'type')
        response = self.client.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(json_data['success'])
    
    # Review does not exist.
    # Non-existent film because of incorrect info.
    def test_no_title(self):
        self.login("Alex", "123")
        self.movie_data['title'] = self.movie_data['original_title'] = 'Mulholland Five'
        response = self.client.post(self.end_point, json=self.movie_data, follow_redirects=True)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(json_data['success'])
        self.assertIn("No review found", json_data['message'])
    
    # Film has yet to be released and so has no review.
    def test_film_not_released(self):
        self.login("Alex", "123")
        future_film = {
                        'title': 'The Future',
                        'original_title': 'The Future',
                        'release_year': 2999,
                        'release_date': '2999-12-31'
                      }
        response = self.client.post(self.end_point, json=future_film, follow_redirects=True)
        json_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(json_data['success'])
        self.assertIn("this film has yet to be released.", json_data['message'])

    # Too many requests, 429
    # Won't write unit test. Manually tested in Postman: works.

            
if __name__ == "__main__":
    unittest.main()
