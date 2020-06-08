import os
import unittest

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


	# *** SEARCH ***
	def test_search_page(self):
		response = self.app.get('/search', follow_redirects=True)
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Search', response.data)

	def test_search_title(self):
		response = self.app.post(
			'/title-search-results',
			data=dict(title="Mulholland Drive"), follow_redirects=True)
		self.assertIn(b'Mulholland Drive (Released 2001-09-08)', response.data)

	def test_search_title_blank(self):
		response = self.app.post(
			'/title-search-results',
			data=dict(title="    \n"), follow_redirects=True)
		self.assertIn(b'This field is required.', response.data)

		response = self.app.post(
			'/title-search-results',
			data=dict(title=None), follow_redirects=True)
		self.assertIn(b'This field is required.', response.data)




if __name__ == "__main__":
	unittest.main()
