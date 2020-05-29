from cinescout import app # Get app object defined in __init__.py

print("Executing routes.py...")

@app.route('/')
@app.route('/index')
def index():
	return "Welcome to Cinescout"
  
