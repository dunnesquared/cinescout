"""Performs unit-tests of functions in cinescout.auth package."""

import os

# Use in-memory database for testing.
os.environ['DATABASE_URL'] = 'sqlite://'

import unittest

# Add this line to whatever test script you write
from context import app, db, basedir, User, Film, CriterionFilm


class AuthTests(unittest.TestCase):

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
        # print("TEST DB dropped!")
        db.session.remove()
        db.drop_all()

        # Delete app context, no longer required.
        self.appctx.pop()
        self.app = None
        self.appctx = None
        self.client = None

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

    # +++++++++++++++++++++++++++++++ TESTS +++++++++++++++++++++++++++++++++

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
    #     response = self.client.get('/register', follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Register', response.data)

    # def test_register_page_authenticated(self):
    #     response = self.login(username="Alex", password="123")
    #     response = self.client.get('/register', follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Welcome', response.data)

    # def test_register_valid_data(self):
    #     username = "borat"
    #     email = "borat@borat.com"
    #     password = self.dummy_pw
    #     password2 = self.dummy_pw
    #     response = self.client.post(
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
    #     response = self.client.post(
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
    #     response = self.client.post(
    #         '/register',
    #         data=dict(username=username, email=email, password=password, password2=password2),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'This field is required.', response.data)

    #     # No data passed
    #     response = self.client.post(
    #         '/register',
    #         data=dict(username=None, email=None, password=None, password2=None),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'This field is required.', response.data)

    # def test_taken_username_email(self):
    #     # Taken username
    #     response = self.client.post(
    #         '/register',
    #         data=dict(username="Alex", email="a@a.com", password=123, password2=123),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Username already taken.', response.data)

    #     # Taken email
    #     response = self.client.post(
    #         '/register',
    #         data=dict(username="Random", email="alex@test.com", password=123, password2=123),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'An account already exists with this email address.', response.data)

    # def test_bad_input(self):
    #     # Non alphanumeric characters in username
    #     response = self.client.post(
    #         '/register',
    #         data=dict(username="Sheryl?Lee", email="shery@lee.com",
    #         password=123, password2=123),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Username must contain only alphanumeric or underscore characters.', response.data)

    #     # Bad email
    #     response = self.client.post(
    #         '/register',
    #         data=dict(username="SherylLee", email="shery?lee.com",
    #         password=123, password2=123),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Invalid email address.', response.data)

    # def test_different_passwords(self):
    #     response = self.client.post(
    #         '/register',
    #         data=dict(username="SherylLee", email="shery@lee.com",
    #         password=123, password2=456),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Passwords do not match.', response.data)

    # def test_password_length(self):
    #     response = self.client.post(
    #         '/register',
    #         data=dict(username="SherylLee", email="shery@lee.com",
    #         password=123, password2=123),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Password must be at least 8 characters long.', response.data)


if __name__ == "__main__":
    unittest.main()
