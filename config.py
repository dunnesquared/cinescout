import os

# Get absolute directory path of this file (i.e. the project's top-level directory) 
basedir = os.path.abspath(os.path.dirname(__file__))
print(f"basedir={basedir}")

class Config(object):
	SECRET_KEY=os.getenv('SECRET_KEY')
	print("SECRET_KEY=Can't say — it's a secret ;-)")	

	SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'app.db')
	
	print(f"SQLALCHEMY_DATABASE_URI={SQLALCHEMY_DATABASE_URI}")
	
	# Don't need to signal the app every time database is about to be modified.  
	SQLALCHEMY_TRACK_MODIFICATIONS = False 
