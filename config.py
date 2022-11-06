"""Ensures data required for app to run properly is there from the start."""

import os

# Get absolute directory path of this file (i.e. the project's top-level directory)
basedir = os.path.abspath(os.path.dirname(__file__))
print(f"basedir={basedir}")

class Config(object):
	"""Class that retrieves and stores essential data for app."""

	print("Configuring application...")

	SECRET_KEY = os.getenv('SECRET_KEY')

	if not SECRET_KEY:
		raise ValueError("No SECRET_KEY set for Flask application.")
	else:
		print("SECRET_KEY retrieved!")

	SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'app.db')

	print(f"SQLALCHEMY_DATABASE_URI={SQLALCHEMY_DATABASE_URI}")

	# Don't need to signal the app every time database is about to be modified.
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Get API keys
	NYT_API_KEY = os.getenv('NYT_API_KEY')
	if not NYT_API_KEY:
		raise ValueError("No NYT_API_KEY set for Flask application.")
	else:
		print("NYT_API_KEY retrieved!")

	TMDB_API_KEY = os.getenv('TMDB_API_KEY')
	if not TMDB_API_KEY:
		raise ValueError("No TMDB_API_KEY set for Flask application.")
	else:
		print("TMDB_API_KEY retrieved!")
