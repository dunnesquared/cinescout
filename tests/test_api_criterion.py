"""Performs unit test on functions in cinescout.api.criterion."""

import os

# Use in-memory database for testing.
os.environ['DATABASE_URL'] = 'sqlite://'

import time
import unittest
import json


# Add this line to whatever test script you write
from context import app, db, basedir, User, Film, CriterionFilm

CRITERION_API_CALL_DELAY = 30


class CriterionApiTests(unittest.TestCase):
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

        # Placeholder variables to make testing easier
        self.dummy_pw = "12345678"


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
    
    def remove_user(self, user):
        db.session.delete(user)
        db.session.commit()
    
    def create_film(self, title, year, tmdb_id, director, criterionfilm=False):
        film = Film(title=title, year=year, tmdb_id=tmdb_id, director=director)
        db.session.add(film)
        db.session.commit()
        
        if criterionfilm:
            db.session.add(CriterionFilm(film_id=film.id))
            db.session.commit()
        
        return film

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

    def add_film_to_list(self, tmdb_id=None, title=None, year=None,
                         date=None, original_title=None):
        return self.client.post('/api/user-movie-list/item',
                   data=dict(tmdb_id=tmdb_id, title=title,
                           year=year, date=date,
                           original_title=original_title),
                           follow_redirects=True)

    def remove_film_from_list(self, tmdb_id=None):
        return self.client.delete('/api/user-movie-list/item',
              data=dict(tmdb_id=tmdb_id),
                      follow_redirects=True)

    
    # +++++++++++++++++++++++++++++++ TESTS: criterion.py +++++++++++++++++++++++++++++++++
    # No movies in criterion db table
    def test_criterion_api_no_entries(self):
        self.delay_api_call(amt=CRITERION_API_CALL_DELAY)

        response = self.client.get('/api/criterion-films', data=dict())
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])
        self.assertIn('no films', data['err_message'])

    # # One Criterion movie in db
    def test_criterion_api_ok(self):
        self.delay_api_call(amt=CRITERION_API_CALL_DELAY)

        title = "Mulholland Dr."
        release_year = 2001
        tmdb_id = 1018
        director = "David Lynch"
        self.create_film(title=title, year=release_year, tmdb_id=tmdb_id, director=director,
                         criterionfilm=True)
        response = self.client.get('/api/criterion-films', data=dict())
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue(data['success'])
        self.assertEqual(data['num_results'], 1)
        self.assertIn(data['results'][0]['title'], 'Mulholland Dr.')
        self.assertIn(data['results'][0]['directors'][0], 'David Lynch')


    def test_criterion_api_429_2persec(self):
        title = "Mulholland Dr."
        release_year = 2001
        tmdb_id = 1018
        director = "David Lynch"
        self.create_film(title=title, year=release_year, tmdb_id=tmdb_id, director=director,
                         criterionfilm=True)
        
        # Make five rapid calls to api to cause it to violate its 2 request per second policy.
        for i in range(0, 5):
            response = self.client.get('/api/criterion-films', data=dict())

        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])
        self.assertIn('Rate limit exceeded', data['err_message'])
    
    def test_criterion_api_429_30permin(self):
        title = "Mulholland Dr."
        release_year = 2001
        tmdb_id = 1018
        director = "David Lynch"
        self.create_film(title=title, year=release_year, tmdb_id=tmdb_id, director=director,
                         criterionfilm=True)
        
        # Make 40 rapid calls to api to cause it to violate its 30 request per minute policy.
        for i in range(0, 40):
            self.delay_api_call(amt=1)
            response = self.client.get('/api/criterion-films', data=dict())

        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])
        self.assertIn('Rate limit exceeded', data['err_message'])
    
    
if __name__ == "__main__":
    unittest.main()
