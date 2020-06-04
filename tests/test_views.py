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


	def tearDown(self):
		"""Executes after each test."""
		db.session.remove()
		db.drop_all()

	# **** HELPER METHODS ****
	def register(self, username, email, password, confirm):
		# https://www.patricksoftwareblog.com/unit-testing-a-flask-application/
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

	# **** TESTS ****
	def test_main_page(self):
		response = self.app.get('/', follow_redirects=True)
		self.assertEqual(response.status_code, 200)

	def test_valid_login(self):
		response = self.login(username="Alex", password="123")
		self.assertIn(b'You have been logged in!', response.data)

	def test_invalid_login(self):
		response = self.login(username="Alex", password="789")
		self.assertIn(b'Invalid username or password', response.data)


if __name__ == "__main__":
	unittest.main()
