import os
import unittest
import json

# Add this line to whatever test script you write
from context import app, db, basedir, User


class RouteTests(unittest.TestCase):

    def setUp(self):
        # """Executes before each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tests/test.db')
        self.app = app.test_client()
        db.create_all()

        # Create a default user
        u = User(username="Alex", email="alex@test.com")
        u.set_password("123")
        db.session.add(u)
        db.session.commit()

        # Placeholder variables to make testing easier
        self.dummy_pw = "12345678"


    def tearDown(self):
        """Executes after each test."""
        db.session.remove()
        db.drop_all()

    # **** HELPER METHODS ****
    def register(self, username, email, password, confirm):
        # Implement next time...
        pass

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
        return self.app.post('/add-to-list',
                   data=dict(tmdb_id=tmdb_id, title=title,
                           year=year, date=date,
                           original_title=original_title,
                           follow_redirects=True))

    def remove_film_from_list(self, tmdb_id=None):
        return self.app.post('/remove-from-list',
              data=dict(tmdb_id=tmdb_id,
                      follow_redirects=True))

    # +++++++++++++++++++++++++++++++ TESTS +++++++++++++++++++++++++++++++++

    # *** INDEX ***
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # *** LOGIN ***
    def test_valid_login(self):
        response = self.login(username="Alex", password="123")
        self.assertIn(b'You have been logged in!', response.data)

    def test_invalid_login(self):
        # Bad password.
        response = self.login(username="Alex", password="789")
        self.assertIn(b'Invalid username or password', response.data)

        # User does not exist.
        response = self.login(username="AlexO324", password="123")
        self.assertIn(b'Invalid username or password', response.data)

    def test_login_when_loggedin(self):
        response = self.login(username="Alex", password="123")
        self.assertNotIn(b'Login', response.data)
        self.assertIn(b'Logout', response.data)

    def test_login_no_data(self):
        # No data
        response = self.login(username=None, password=None)
        self.assertIn(b'This field is required.', response.data)

        # Whitespace data
        response = self.login(username="   ", password="\n\t\r   ")
        self.assertIn(b'This field is required.', response.data)

    def test_login_remember_me(self):
        # Can't figure out a good way to test this; proabably
        # have to use a higher-level framework like Selenium.
        pass

    # *** LOGOUT ***
    def test_logout_when_logged_in(self):
        response = self.login(username="Alex", password="123")
        response = self.logout()
        self.assertIn(b'Login', response.data)
        self.assertNotIn(b'Logout', response.data)

    def test_logout_when_not_logged_in(self):
        response = self.logout()
        self.assertIn(b'Access Denied', response.data)


    # *** REGISTER ***
    def test_register_page_anonymous(self):
        response = self.app.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_register_page_authenticated(self):
        response = self.login(username="Alex", password="123")
        response = self.app.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Random movie', response.data)

    def test_register_valid_data(self):
        username = "borat"
        email = "borat@borat.com"
        password = self.dummy_pw
        password2 = self.dummy_pw
        response = self.app.post(
            '/register',
            data=dict(username=username, email=email, password=password, password2=password2),
            follow_redirects=True
        )
        self.assertIn(b'Welcome to cinescout, borat! Now login to get started.', response.data)

    def test_register_blank_fields(self):
        # Empty string: ""
        username = ""
        email = ""
        password = ""
        password2 = ""
        response = self.app.post(
            '/register',
            data=dict(username=username, email=email, password=password, password2=password2),
            follow_redirects=True
        )
        self.assertIn(b'This field is required.', response.data)

        # Whitespace strings: "     "
        # Empty string: ""
        username = "\n\t\r"
        email = "    "
        password = "    "
        password2 = "     "
        response = self.app.post(
            '/register',
            data=dict(username=username, email=email, password=password, password2=password2),
            follow_redirects=True
        )
        self.assertIn(b'This field is required.', response.data)

        # No data passed
        response = self.app.post(
            '/register',
            data=dict(username=None, email=None, password=None, password2=None),
            follow_redirects=True
        )
        self.assertIn(b'This field is required.', response.data)

    def test_taken_username_email(self):
        # Taken username
        response = self.app.post(
            '/register',
            data=dict(username="Alex", email="a@a.com", password=123, password2=123),
            follow_redirects=True
        )
        self.assertIn(b'Username already taken.', response.data)

        # Taken email
        response = self.app.post(
            '/register',
            data=dict(username="Random", email="alex@test.com", password=123, password2=123),
            follow_redirects=True
        )
        self.assertIn(b'An account already exists with this email address.', response.data)

    def test_bad_input(self):
        # Non alphanumeric characters in username
        response = self.app.post(
            '/register',
            data=dict(username="Sheryl?Lee", email="shery@lee.com",
            password=123, password2=123),
            follow_redirects=True
        )
        self.assertIn(b'Username must contain only alphanumeric or underscore characters.', response.data)

        # Bad email
        response = self.app.post(
            '/register',
            data=dict(username="SherylLee", email="shery?lee.com",
            password=123, password2=123),
            follow_redirects=True
        )
        self.assertIn(b'Invalid email address.', response.data)

    def test_different_passwords(self):
        response = self.app.post(
            '/register',
            data=dict(username="SherylLee", email="shery@lee.com",
            password=123, password2=456),
            follow_redirects=True
        )
        self.assertIn(b'Passwords do not match.', response.data)

    def test_password_length(self):
        response = self.app.post(
            '/register',
            data=dict(username="SherylLee", email="shery@lee.com",
            password=123, password2=123),
            follow_redirects=True
        )
        self.assertIn(b'Password must be at least 8 characters long.', response.data)


    # *** SEARCH - Title Search ***
    def test_search_page_title(self):
        response = self.app.get('/search', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'By title', response.data)

    def test_search_title_exists(self):
        response = self.app.post(
            '/title-search-results',
            data=dict(title="Mulholland Drive"), follow_redirects=True)
        self.assertIn(b'Mulholland Drive', response.data)

    def test_search_title_not_exist(self):
        response = self.app.post(
            '/title-search-results',
            data=dict(title="43543nkjerhtrehtkreture+rew"), follow_redirects=True)
        self.assertIn(b'There are no movies matching that title.', response.data)

    def test_search_title_blank(self):
        response = self.app.post(
            '/title-search-results',
            data=dict(title="    \n"), follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)

        response = self.app.post(
            '/title-search-results',
            data=dict(title=None), follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)

    # *** SEARCH - Person Search ***
    def test_search_page_person(self):
        response = self.app.get('/search', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'By person', response.data)

    def test_search_person_exists(self):
        response = self.app.post(
            '/person-search-results',
            data=dict(name="Gabriel Byrne", known_for="Acting",
                    follow_redirects=True))
        self.assertIn(b'Gabriel Byrne', response.data)

    def test_search_person_not_exist(self):
        response = self.app.post(
            '/person-search-results',
            data=dict(name="433u5h6krbtrbhtertkejb56k5363", known_for="All",
                     follow_redirects=True))
        self.assertIn(b'No persons matching description found.', response.data)

    def test_search_person_blank(self):
        response = self.app.post(
            '/person-search-results',
            data=dict(name="\t\n\r    ", known_for="All",
                     follow_redirects=True))
        self.assertIn(b'This field is required.', response.data)

    def test_search_person_valid_id(self):
        id = 1 # George Lucas
        response = self.app.get(f'/person/{id}')
        self.assertIn(b'Star Wars', response.data)

    def test_search_person_invalid_id_01(self):
        id = -1
        response = self.app.get(f'/person/{id}')
        self.assertIn(b'404: Page Not Found', response.data)

    def test_search_person_invalid_id_02(self):
        id = 123445465465765767687687980879686787567744566765756
        response = self.app.get(f'/person/{id}')
        self.assertIn(b'404: Page Not Found', response.data)

    def test_search_person_invalid_id_03(self):
        id = "sdjkfdkbgkfdbgkfdsjgb"
        response = self.app.get(f'/person/{id}')
        self.assertIn(b'404: Page Not Found', response.data)

    def test_search_person_no_id(self):
        id = None
        response = self.app.get(f'/person/{id}')
        self.assertIn(b'404: Page Not Found', response.data)

    def test_search_person_blank_id(self):
        id = "\n\t    \r    "
        response = self.app.get(f'/person/{id}')
        self.assertIn(b'404: Page Not Found', response.data)


    # *** MOVIE PAGE ***
    # All major headings there
    def test__movie_page_good(self):
        movie_id = "1018" # Mulholland Drive (2001)
        response = self.app.get(f'/movie/{movie_id}')
        self.assertIn(b'Release Date', response.data)
        self.assertIn(b'Overview', response.data)
        self.assertIn(b'Runtime', response.data)
        self.assertIn(b'Movie Review', response.data)
        self.assertIn(b'TMDB Link', response.data)
        self.assertIn(b'IMDB Link', response.data)
        self.assertIn(b'Critic\'s Pick', response.data)

    # Bad movie id
    def test__movie_page_bad_id(self):
        movie_id = "-1018"
        response = self.app.get(f'/movie/{movie_id}')
        self.assertIn(b'404: Page Not Found', response.data)

    # Blank/no movie id
    # Bad movie id
    def test__movie_page_blank_id(self):
        movie_id = "\n\t   "
        response = self.app.get(f'/movie/{movie_id}')
        self.assertIn(b'404: Page Not Found', response.data)

    # Add movie to list

    # Add when not logged in
    def test_movie_page_add_not_logged_in(self):
        response = self.app.post(
            '/add-to-list',
            data=dict(tmdb_id="1018", title="Mulholland Drive", year="2001",
                    follow_redirects=True))

        self.assertIn(b'Access Denied', response.data)

     # Add ok
    def test_movie_page_add_ok(self):
        self.login("Alex", "123")
        response = self.app.post('/add-to-list',
                data=dict(tmdb_id="1018", title="Mulholland Drive",
                        year="2001", date="2001-09-08",
                        original_title="Mulholland Drive",
 						follow_redirects=True))
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue(data['success'])

     # Add when already on list
    def test_movie_page_add_already_on_list(self):
        self.login("Alex", "123")
        # Add film.
        response = self.app.post('/add-to-list',
                data=dict(tmdb_id="1018", title="Mulholland Drive",
                        year="2001", date="2001-09-08",
                        original_title="Mulholland Drive",
                        follow_redirects=True))
        data = json.loads(response.get_data(as_text=True))
        self.assertTrue(data['success'])

        # Try adding same film again.
        response = self.app.post('/add-to-list',
                   data=dict(tmdb_id="1018", title="Mulholland Drive",
                           year="2001", date="2001-09-08",
                           original_title="Mulholland Drive",
                           follow_redirects=True))
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

     # Add blank
    def test_movie_page_add_blank(self):
        self.login("Alex", "123")

         # White space
        response = self.app.post('/add-to-list',
                 data=dict(tmdb_id="", title=" ",
                         year=" ", date="",
                         original_title="  ",
                         follow_redirects=True))
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

        # None types
        response = self.app.post('/add-to-list',
                data=dict(tmdb_id=None, title=None, year=None,
                        original_title=None, date=None,
                        follow_redirects=True))
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

    # Add movie with bad id or bad year
    def test_movie_page_add_bad_data(self):
        self.login("Alex", "123")
        # Add film: Note that the id for this film is negative
        movie_id = "-1018"
        response = self.app.post('/add-to-list',
                data=dict(tmdb_id=movie_id, title="Mulholland Drive",
                        year="2001", date="2001-09-08",
                        original_title="Mulholland Drive",
                        follow_redirects=True))
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

        # Add film with bad year.
        movie_id = "1018"
        year = "-2001"
        response = self.app.post('/add-to-list',
                data=dict(tmdb_id=movie_id, title="Mulholland Drive",
                        year=year, date="2001-09-08",
                        original_title="Mulholland Drive",
                        follow_redirects=True))
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

    # Remove movie from list
    # Remove when not logged in
    def test_movie_page_remove_not_logged_in(self):
      	response = self.app.post(
          '/remove-from-list',
          data=dict(tmdb_id="1018", follow_redirects=True))

      	self.assertIn(b'Access Denied', response.data)

    # Remove ok
    def test_movie_page_remove_ok(self):
      	self.login("Alex", "123")

      	# Add ok
      	self.app.post('/add-to-list', data=dict(tmdb_id="1018",
      				title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive",
                            follow_redirects=True))

      	response = self.app.post('/remove-from-list',
              data=dict(tmdb_id="1018",
                      follow_redirects=True))

      	data = json.loads(response.get_data(as_text=True))
      	self.assertTrue(data['success'])

    # Remove when not on list
    def test_movie_page_remove_not_on_list(self):
      	self.login("Alex", "123")

        # List is empty.
      	response = self.app.post('/remove-from-list',
              data=dict(tmdb_id="1018",
                      follow_redirects=True))

      	data = json.loads(response.get_data(as_text=True))
      	self.assertFalse(data['success'])

    # Remove blank
    def test_movie_page_remove_blank(self):
        self.login("Alex", "123")

        # Add ok
        self.app.post('/add-to-list', data=dict(tmdb_id="1018",
                    title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive",
                            follow_redirects=True))

        # Blank data
        response = self.app.post('/remove-from-list',
              data=dict(tmdb_id="\n\t ",
                      follow_redirects=True))
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

        # Blank data
        response = self.app.post('/remove-from-list',
              data=dict(tmdb_id=None,
                      follow_redirects=True))
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])

      # Remove movie with bad id
    def test_movie_page_remove_bad_id(self):
        self.login("Alex", "123")

        # Add ok
        self.app.post('/add-to-list', data=dict(tmdb_id="1018",
                    title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive",
                           follow_redirects=True))

        # Bad id
        response = self.app.post('/remove-from-list',
              data=dict(tmdb_id="-1018",
                      follow_redirects=True))
        data = json.loads(response.get_data(as_text=True))
        self.assertFalse(data['success'])


    # USER LIST
    # Tests:
    # Try to access list without being logged in.
    def test_user_list_not_logged_in(self):
        response = self.app.get('/movie-list')
        self.assertIn(b'Access Denied', response.data)

    # Try to access list while logged in.
    def test_user_list_logged_in(self):
        self.login("Alex", "123")
        response = self.app.get('/movie-list')
        self.assertIn(b'Alex\'s List', response.data)

    # Remove regular remove
    def test_user_list_remove_ok(self):
    	# Login and add a film.
        self.login("Alex", "123")
        self.add_film_to_list(tmdb_id="1018", title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive")

        self.remove_film_from_list(tmdb_id="1018")

        response = self.app.get('/movie-list')
        self.assertIn(b'There are no films on your list', response.data)

    # Remove when no films on list
    def test_user_list_remove_no_films_on_list(self):
    	# Login and add a film.
        self.login("Alex", "123")
        self.add_film_to_list(tmdb_id="1018", title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive")

        self.remove_film_from_list(tmdb_id="1018")

        # Try removing it again.
        self.remove_film_from_list(tmdb_id="1018")

        response = self.app.get('/movie-list')
        self.assertIn(b'There are no films on your list', response.data)

    # Try to remove film that is not on list
    def test_user_list_remove_film_not_on_list(self):
    	# Login and add a film.
        self.login("Alex", "123")
        self.add_film_to_list(tmdb_id="1018", title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive")

        # Film 999 not on list
        self.remove_film_from_list(tmdb_id="999")

        response = self.app.get('/movie-list')
        self.assertIn(b'Mulholland Drive', response.data)

    # Remove with blank data.
    def test_user_list_remove_blank__None_data(self):
    	# Login and add a film.
        self.login("Alex", "123")
        self.add_film_to_list(tmdb_id="1018", title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive")

        self.remove_film_from_list(tmdb_id="\n \t")
        response = self.app.get('/movie-list')
        self.assertIn(b'Mulholland Drive', response.data)

        self.remove_film_from_list(tmdb_id=None)
        response = self.app.get('/movie-list')
        self.assertIn(b'Mulholland Drive', response.data)

    # Remove with bad data
    def test_user_list_remove_bad_data(self):
    	# Login and add a film.
        self.login("Alex", "123")
        self.add_film_to_list(tmdb_id="1018", title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive")

        self.remove_film_from_list(tmdb_id="ewr43%#$^^")
        response = self.app.get('/movie-list')
        self.assertIn(b'Mulholland Drive', response.data)




if __name__ == "__main__":
    unittest.main()
