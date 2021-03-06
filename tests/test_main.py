"""Performs unit test on functions in `views.py`."""

import os
import unittest

# Add this line to whatever test script you write
from context import app, db, basedir, User, Film, CriterionFilm


class RouteTests(unittest.TestCase):

    def setUp(self):
        # """Executes before each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tests/test.db')
        self.app = app.test_client()
        db.create_all()

        # See whether Alex in db. If not add him. 
        default_user = User.query.filter_by(username="Alex").first()
        if not default_user:
            print("Creating default user 'Alex'...")
            self.create_user(name="Alex", email="alex@test.com", password="123")

        # Placeholder variables to make testing easier
        self.dummy_pw = "12345678"


    def tearDown(self):
        """Executes after each test."""
        # print("TEST DB dropped!")
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
        return self.app.post('/api/user-movie-list/item',
                   data=dict(tmdb_id=tmdb_id, title=title,
                           year=year, date=date,
                           original_title=original_title),
                           follow_redirects=True)

    def remove_film_from_list(self, tmdb_id=None):
        return self.app.delete('/api/user-movie-list/item',
              data=dict(tmdb_id=tmdb_id),
                      follow_redirects=True)

    # +++++++++++++++++++++++++++++++ TESTS +++++++++++++++++++++++++++++++++

    # *** INDEX ***
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # *** LOGIN ***
    def test_valid_login(self):
        response = self.login(username="Alex", password="123")
        self.assertIn(b'You have been logged in!', response.data)

    def test_invalid_login_bad_password(self):
        # Bad password.
        # self.create_user(name='xyz', email="alex@test.com", password="123")
        response = self.login(username="Alex", password="789")
        self.assertIn(b'Invalid username or password', response.data)
    
    def test_invalid_login_user_dne(self):
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


    # # *** REGISTER ***
    # ==============  TESTS OBSOLETE AS OF v1.1.0 =====================
    # def test_register_page_anonymous(self):
    #     response = self.app.get('/register', follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Register', response.data)

    # def test_register_page_authenticated(self):
    #     response = self.login(username="Alex", password="123")
    #     response = self.app.get('/register', follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Welcome', response.data)

    # def test_register_valid_data(self):
    #     username = "borat"
    #     email = "borat@borat.com"
    #     password = self.dummy_pw
    #     password2 = self.dummy_pw
    #     response = self.app.post(
    #         '/register',
    #         data=dict(username=username, email=email, password=password, password2=password2),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Welcome to Cinescout, borat! Now login to get started.', response.data)

    # def test_register_blank_fields(self):
    #     # Empty string: ""
    #     username = ""
    #     email = ""
    #     password = ""
    #     password2 = ""
    #     response = self.app.post(
    #         '/register',
    #         data=dict(username=username, email=email, password=password, password2=password2),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'This field is required.', response.data)

    #     # Whitespace strings: "     "
    #     # Empty string: ""
    #     username = "\n\t\r"
    #     email = "    "
    #     password = "    "
    #     password2 = "     "
    #     response = self.app.post(
    #         '/register',
    #         data=dict(username=username, email=email, password=password, password2=password2),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'This field is required.', response.data)

    #     # No data passed
    #     response = self.app.post(
    #         '/register',
    #         data=dict(username=None, email=None, password=None, password2=None),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'This field is required.', response.data)

    # def test_taken_username_email(self):
    #     # Taken username
    #     response = self.app.post(
    #         '/register',
    #         data=dict(username="Alex", email="a@a.com", password=123, password2=123),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Username already taken.', response.data)

    #     # Taken email
    #     response = self.app.post(
    #         '/register',
    #         data=dict(username="Random", email="alex@test.com", password=123, password2=123),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'An account already exists with this email address.', response.data)

    # def test_bad_input(self):
    #     # Non alphanumeric characters in username
    #     response = self.app.post(
    #         '/register',
    #         data=dict(username="Sheryl?Lee", email="shery@lee.com",
    #         password=123, password2=123),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Username must contain only alphanumeric or underscore characters.', response.data)

    #     # Bad email
    #     response = self.app.post(
    #         '/register',
    #         data=dict(username="SherylLee", email="shery?lee.com",
    #         password=123, password2=123),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Invalid email address.', response.data)

    # def test_different_passwords(self):
    #     response = self.app.post(
    #         '/register',
    #         data=dict(username="SherylLee", email="shery@lee.com",
    #         password=123, password2=456),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Passwords do not match.', response.data)

    # def test_password_length(self):
    #     response = self.app.post(
    #         '/register',
    #         data=dict(username="SherylLee", email="shery@lee.com",
    #         password=123, password2=123),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Password must be at least 8 characters long.', response.data)


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

    def test_search_title_GET(self):
        title="Mulholland Drive"
        response = self.app.get(f'movie-search-results?movie_title={title}')
        self.assertIn(b'2001-06-06', response.data)

    def test_search_title_GET_not_exist(self):
        title="eiwr43t984h3tkjdnfg,df.gmdf.glkto"
        response = self.app.get(f'movie-search-results?movie_title={title}')
        self.assertIn(b'There are no movies matching that title.',
                        response.data)

    def test_search_title_GET_blank(self):
        title=""
        response = self.app.get(f'movie-search-results?movie_title={title}')
        self.assertIn(b'422', response.data)

    def test_search_title_GET_None(self):
        response = self.app.get(f'movie-search-results?')
        self.assertIn(b'422', response.data)


    # *** SEARCH - Person Search ***
    def test_search_page_person(self):
        response = self.app.get('/search', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'By person', response.data)

    def test_search_person_exists(self):
        response = self.app.post(
            '/person-search-results',
            data=dict(name="Gabriel Byrne", known_for="Acting"),
                    follow_redirects=True)
        self.assertIn(b'Gabriel Byrne', response.data)

    def test_search_person_not_exist(self):
        response = self.app.post(
            '/person-search-results',
            data=dict(name="433u5h6krbtrbhtertkejb56k5363", known_for="All"),
                     follow_redirects=True)
        self.assertIn(b'No persons matching description found.', response.data)

    def test_search_person_blank(self):
        response = self.app.post(
            '/person-search-results',
            data=dict(name="\t\n\r    ", known_for="All"),
                     follow_redirects=True)
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
        self.assertIn(b'Internal Server Error', response.data)

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

    def test_search_person_GET(self):
        name = "Paul Newman"
        known_for = "All"
        response = self.app.get(f'person-search?name={name}&known_for={known_for}')
        self.assertIn(b'Harry Paul Newman', response.data)

    def test_search_person_GET_name_not_exist(self):
        known_for = "All"
        response = self.app.get(f'person-search?name=&known_for={known_for}')
        self.assertIn(b'422', response.data)

    def test_search_person_GET_known_for_not_exist(self):
        name = "Paul Newman"
        response = self.app.get(f'person-search?name={name}&known_for=')
        self.assertIn(b'422', response.data)

    def test_search_person_GET_name_exists_not_known_for(self):
        name = "Paul Newman"
        response = self.app.get(f'person-search?name={name}')
        self.assertIn(b'Harry Paul Newman', response.data)

    def test_search_person_GET_no_values(self):
        response = self.app.get(f'person-search?')
        self.assertIn(b'422', response.data)

    # *** FILMOGRAPHY ***

    def test_filmography_good_parameters(self):
        firstname = "Ingmar"
        lastname = "Bergman"
        id = 6648
        response = self.app.get(f'/person/{id}?name={firstname}+{lastname}')
        self.assertIn(b'Winter Light', response.data)

    def test_filmography_blank_name(self):
        firstname = ""
        lastname = ""
        id = 6648
        response = self.app.get(f'/person/{id}?name={firstname}+{lastname}')
        self.assertIn(b'URL person name and TMDB person name do not match',
                        response.data)

    def test_filmography_no_name(self):
        id = 6648
        response = self.app.get(f'/person/{id}')
        self.assertIn(b'Winter Light', response.data)

    def test_filmography_wrong_name(self):
        firstname = "Miranda"
        lastname = "Otto"
        id = 6648
        response = self.app.get(f'/person/{id}?name={firstname}+{lastname}')
        self.assertIn(b'URL person name and TMDB person name do not match',
                        response.data)



    # *** MOVIE PAGE ***
    # All major headings there
    def test_movie_page_good(self):
        movie_id = "1018" # Mulholland Drive (2001)
        response = self.app.get(f'/movie/{movie_id}')
        self.assertIn(b'Release Date', response.data)
        self.assertIn(b'Overview', response.data)
        self.assertIn(b'Runtime', response.data)
        self.assertIn(b'TMDB Link', response.data)
        self.assertIn(b'IMDB Link', response.data)
        self.assertIn(b'Cast', response.data)
        self.assertIn(b'Crew', response.data)
        self.assertIn(b'Learn More', response.data)
        self.assertIn(b'Google', response.data)
        self.assertIn(b'DuckDuckGo', response.data)
        self.assertIn(b'Where to Watch', response.data)

        # v1.1+: User must be logged-in to see reviews.
        # self.assertIn(b'Movie Review', response.data 
        # self.assertIn(b'Critic\'s Pick', response.data)

    # Where to watch
    def test_moviepage_wheretowatch_ok(self):
        movie_id = '11'
        response = self.app.get(f'/movie/{movie_id}')
        self.assertIn(b'Star Wars', response.data)
        self.assertIn(b'Stream', response.data)
        self.assertIn(b'Disney', response.data)
        self.assertIn(b'Rent', response.data)
        self.assertIn(b'Apple', response.data)
    
    def test_moviepage_wheretowatch_nodata(self):
        movie_id = '502057'
        response = self.app.get(f'/movie/{movie_id}')
        self.assertIn(b'Dark Streets', response.data)   # A lost film 
        self.assertIn(b'No provider data available', response.data)

    # Credits
    def test_moviepage_creditsok(self):
        movie_id = "1018"
        response = self.app.get(f'/movie/{movie_id}')
        self.assertIn(b'Adam Kesher', response.data)
    
    def test_moviepage_credits_nocastcrew(self):
        movie_id = "669330" # Retour à Mulholland Drive
        response = self.app.get(f'/movie/{movie_id}')
        self.assertIn(b'No data available.', response.data)
    
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

    # USER LIST
    # Tests:
    # Try to access list without being logged in.
    def test_user_list_not_logged_in(self):
        response = self.app.get('/user-movie-list')
        self.assertIn(b'Access Denied', response.data)

    # Try to access list while logged in.
    def test_user_list_logged_in(self):
        self.login("Alex", "123")
        response = self.app.get('/user-movie-list')
        self.assertIn(b'Alex\'s List', response.data)

    # Remove regular remove
    def test_user_list_remove_ok(self):
    	# Login and add a film.
        self.login("Alex", "123")
        self.add_film_to_list(tmdb_id="1018", title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive")

        self.remove_film_from_list(tmdb_id="1018")

        response = self.app.get('/user-movie-list')
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

        response = self.app.get('/user-movie-list')
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

        response = self.app.get('/user-movie-list')
        self.assertIn(b'Mulholland Drive', response.data)

    # Remove with blank data.
    def test_user_list_remove_blank__None_data(self):
    	# Login and add a film.
        self.login("Alex", "123")
        self.add_film_to_list(tmdb_id="1018", title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive")

        self.remove_film_from_list(tmdb_id="\n \t")
        response = self.app.get('/user-movie-list')
        self.assertIn(b'Mulholland Drive', response.data)

        self.remove_film_from_list(tmdb_id=None)
        response = self.app.get('/user-movie-list')
        self.assertIn(b'Mulholland Drive', response.data)

    # Remove with bad data
    def test_user_list_remove_bad_data(self):
    	# Login and add a film.
        self.login("Alex", "123")
        self.add_film_to_list(tmdb_id="1018", title="Mulholland Drive",
                            year="2001", date="2001-09-08",
                            original_title="Mulholland Drive")

        self.remove_film_from_list(tmdb_id="ewr43%#$^^")
        response = self.app.get('/user-movie-list')
        self.assertIn(b'Mulholland Drive', response.data)

    # See whether film release date flagged as 'Unknown' if no release info
    # provided
    def test_user_list_release_date_unknown(self):
    	# Login and add a film.
        self.login("Alex", "123")
        self.add_film_to_list(tmdb_id="1018", title="Mulholland Drive",
                            year=None, date=None,
                            original_title="Mulholland Drive")

        response = self.app.get('/user-movie-list')
        self.assertIn(b'Unknown', response.data)

    # BROWSE
    # Check if Criterion film page loaded properly.
    def test_browse_not_logged_in(self):
        title = "Mulholland Dr."
        release_year = 2001
        tmdb_id = 1018
        director = "David Lynch"
        self.create_film(title=title, year=release_year, tmdb_id=tmdb_id, director=director,
                         criterionfilm=True)
        response = self.app.get('/browse')
        self.assertIn(b'Criterion Collection', response.data)

    # Get Browse page when logged in; see if it loaded correctly.
    def test_browse_logged_in(self):
        title = "Mulholland Dr."
        release_year = 2001
        tmdb_id = 1018
        director = "David Lynch"
        self.create_film(title=title, year=release_year, tmdb_id=tmdb_id, director=director,
                         criterionfilm=True)
        self.login("Alex", "123")
        response = self.app.get('/browse')
        self.assertIn(b'Criterion Collection', response.data)

    # Check for error message if no Criterion films in database, so page cannot be loaded. 
    def test_browse_list_empty(self):
        response = self.app.get('/browse')
        self.assertIn(b'Unable to load Criterion films', response.data)

    # ABOUT
    def test_about_menubar_anonymous(self):
        response = self.app.get('/')
        self.assertIn(b'About', response.data)
    
    def test_about_menubar_loggedin(self):
        self.login("Alex", "123")
        response = self.app.get('/')
        self.assertIn(b'About', response.data)

    def test_about_page_exists_anonymous(self):
        response = self.app.get('/about')
        self.assertIn(b'version', response.data)
    
    def test_about_page_exists_loggedin(self):
        self.login("Alex", "123")
        response = self.app.get('/about')
        self.assertIn(b'version', response.data)


if __name__ == "__main__":
    unittest.main()
