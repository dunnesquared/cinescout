import requests

from flask import render_template
from cinescout import app, db

@app.errorhandler(404)
def not_found_error(e):
	return render_template("errors/404.html"), 404


@app.errorhandler(401)
def not_found_error(e):
	return render_template("errors/401.html"), 401

@app.errorhandler(429)
def not_found_error(e):
    err_message = ("Too many requests in a row. Please wait 30–60 seconds " \
    "before your next query.")
    return render_template("errors/429.html", err_message=err_message), 429

@app.errorhandler(requests.exceptions.ConnectionError)
def connection_error(e):
    return render_template("errors/connection-error.html")



# THIS CODE WILL SUPERSEDE INTERACTIVE DEBUGGER DURING DEVELOPMENT
# DO NOT ENABLE UNTIL YOU HAVE LOGGING/EMAILING OF ERRORS
# @app.errorhandler(500)
# def internal_error(error):
#     db.session.rollback()
#     return render_template('500.html'), 500
