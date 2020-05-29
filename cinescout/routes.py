
from flask import render_template

from cinescout import app # Get app object defined in __init__.py

print("Executing routes.py...")

@app.route('/')
@app.route('/index')
def index():
	message = "This is placeholder content" 
	return render_template("index.html", message=message)
  
