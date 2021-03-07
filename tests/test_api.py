"""Performs unit test on functions in cinescout.api package."""

import os
import unittest
import json


# Add this line to whatever test script you write
from context import app, db, basedir, User, Film, CriterionFilm
# from context import app, basedir, User, Film, CriterionFilm


class ApiTests(unittest.TestCase):

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

        # Placeholder variables to make testing easier.
        self.dummy_pw = "12345678"


    def tearDown(self):
        """Executes after each test."""
        db.session.remove()
        db.drop_all()

    # **** HELPER METHODS ****
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

    def add_film_to_list(self, tmdb_id=None, title=None, year=None,
                         date=None, original_title=None):
        return self.app.post('/api/user-movie-list/item',
                   data=dict(tmdb_id=tmdb_id, title=title,
                           year=year, date=date,
                           original_title=original_title),
                           follow_redirects=True)

    def remove_film_from_list(self, tmdb_id=None):
        return self.app.delete('/api/user-movie-list/item',
              data=dict(tmdb_id=tmdb_id),
                      follow_redirects=True)

    # +++++++++++++++++++++++++++++++ TESTS: usermovielst.py +++++++++++++++++++++++++++++++++
    # ADD MOVIE TO USERLIST
    # Add when not logged in
    def test_movie_page_add_not_logged_in(self):
        response = self.app.post(
            '/api/user-movie-list/item',
            data=dict(tmdb_id="1018", title="Mulholland Drive", year="2001"),
                    follow_redirects=True)

        self.assertIn(b'Access Denied', response.data)

     # Add ok
    def test_movie_page_add_ok(self):
        self.login("Alex", "123")
        response = self.app.post('/api/user-movie-list/item',
                data=dict(tmdb_id="1018", title="Mulholland Drive",
                        year="2001", date="2001-09-08",
                        original_title="Mulholland Drive"),
 						follow_redirects=True)
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue(data['success'])

     # Add when already on list
    def test_movie_page_add_already_on_list(self):
        self.login("Alex", "123")
        # Add film.
        response = self.app.post('/api/user-movie-list/item',
                data=dict(tmdb_id="1018", title="Mulholland Drive",
                        year="2001", date="2001-09-08",
                        original_title="Mulholland Drive"),
                        follow_redirects=True)
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue(data['success'])

        # Try adding same film again.
        response = self.app.post('/api/user-movie-list/item',
                   data=dict(tmdb_id="1018", title="Mulholland Drive",
                           year="2001", date="2001-09-08",
                           original_title="Mulholland Drive"),
                           follow_redirects=True)
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

     # Add blank
    def test_movie_page_add_blank(self):
        self.login("Alex", "123")

         # White space
        response = self.app.post('/api/user-movie-list/item',
                 data=dict(tmdb_id="", title=" ",
                         year=" ", date="",
                         original_title="  "),
                         follow_redirects=True)
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

        # None types
        response = self.app.post('/api/user-movie-list/item',
                data=dict(tmdb_id=None, title=None, year=None,
                        original_title=None, date=None),
                        follow_redirects=True)
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

    # Add movie with bad id or bad year
    def test_movie_page_add_bad_data(self):
        self.login("Alex", "123")
        # Add film: Note that the id for this film is negative
        movie_id = "-1018"
        response = self.app.post('/api/user-movie-list/item',
                data=dict(tmdb_id=movie_id, title="Mulholland Drive",
                        year="2001", date="2001-09-08",
                        original_title="Mulholland Drive"),
                        follow_redirects=True)
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

        # Add film with bad year.
        movie_id = "1018"
        year = "-2001"
        response = self.app.post('/api/user-movie-list/item',
                data=dict(tmdb_id=movie_id, title="Mulholland Drive",
                        year=year, date="2001-09-08",
                        original_title="Mulholland Drive"),
                        follow_redirects=True)
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

    def test_movie_page_add_no_date_year(self):
        self.login("Alex", "123")
        # Add film.
        response = self.app.post('/api/user-movie-list/item',
                data=dict(tmdb_id="1018", title="Mulholland Drive",
                        year="", date=None,
                        original_title="Mulholland Drive"),
                        follow_redirects=True)
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue(data['success'])

    # REMOVE MOVIE FROM USERLIST
    # Remove when not logged in
    def test_movie_page_remove_not_logged_in(self):
      	response = self.app.delete(
          '/api/user-movie-list/item',
          data=dict(tmdb_id="1018"), follow_redirects=True)

      	self.assertIn(b'Access Denied', response.data)

    # Remove ok
    def test_movie_page_remove_ok(self):
      	self.login("Alex", "123")

      	# Add ok
      	self.app.post('/api/user-movie-list/item', data=dict(tmdb_id="1018",
      				title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive"),
                            follow_redirects=True)

      	response = self.app.delete('/api/user-movie-list/item',
              data=dict(tmdb_id="1018"),
                      follow_redirects=True)

      	data = json.loads(response.get_data(as_text=True))
      	self.assertTrue(data['success'])

    # Remove when not on list
    def test_movie_page_remove_not_on_list(self):
      	self.login("Alex", "123")

        # List is empty.
      	response = self.app.delete('/api/user-movie-list/item',
              data=dict(tmdb_id="1018"),
                      follow_redirects=True)

      	data = json.loads(response.get_data(as_text=True))
      	self.assertFalse(data['success'])

    # Remove blank
    def test_movie_page_remove_blank(self):
        self.login("Alex", "123")

        # Add ok
        self.app.post('/api/user-movie-list/item', data=dict(tmdb_id="1018",
                    title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive"),
                            follow_redirects=True)

        # Blank data
        response = self.app.delete('/api/user-movie-list/item',
              data=dict(tmdb_id="\n\t "),
                      follow_redirects=True)
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

        # Blank data
        response = self.app.delete('/api/user-movie-list/item',
              data=dict(tmdb_id=None),
                      follow_redirects=True)
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

    # Remove movie with bad id
    def test_movie_page_remove_bad_id(self):
        self.login("Alex", "123")

        # Add ok
        self.app.post('/api/user-movie-list/item', data=dict(tmdb_id="1018",
                    title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive"),
                           follow_redirects=True)

        # Bad id
        response = self.app.delete('/api/user-movie-list/item',
              data=dict(tmdb_id="-1018"),
                      follow_redirects=True)
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])
    

    # +++++++++++++++++++++++++++++++ TESTS: criterion.py +++++++++++++++++++++++++++++++++
    # No movies in criterion db table
    def test_criterion_api_no_entries(self):
        response = self.app.get('/api/criterion-films', data=dict())
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])
        self.assertIn('no films', data['err_message'])

    # One Criterion movie in db
    def test_criterion_api_ok(self):
        title = "Mulholland Dr."
        release_year = 2001
        tmdb_id = 1018
        director = "David Lynch"
        self.create_film(title=title, year=release_year, tmdb_id=tmdb_id, director=director,
                         criterionfilm=True)
        response = self.app.get('/api/criterion-films', data=dict())
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue(data['success'])
        self.assertEqual(data['num_results'], 1)
        self.assertIn(data['results'][0]['title'], 'Mulholland Dr.')
        self.assertIn(data['results'][0]['directors'][0], 'David Lynch')


if __name__ == "__main__":
    unittest.main()
