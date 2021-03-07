"""Handles http errors and raised exceptions."""

import requests
from flask import render_template

from cinescout.errors import bp


@bp.app_errorhandler(404)
def not_found_error(e):
    """Page not found (e.g. bad movie id)."""
    return render_template("errors/404.html"), 404


@bp.app_errorhandler(401)
def not_authorized(e):
    """Not authorized to see page (e.g. not logged in)."""
    return render_template("errors/401.html"), 401


@bp.app_errorhandler(429)
def too_many_requests_error(e):
    """Too many requests made to API in short period,
    mostly like to NYT movie reviews."""

    err_message = ("Too many requests in a row. Please wait 30–60 seconds "
                   "before your next query.")
    return render_template("errors/429.html", err_message=err_message), 429


@bp.app_errorhandler(422)
def unprocessable_entity(e):
    """Something is likely wrong with one or more query paramaters passed
    in the URL (e.g. movie_title is set not given a value).
    """
    err_message = ("Unprocessable Entity. Check that the values of the query "
                   "parameters in the URL are valid.")
    return render_template("errors/422.html", err_message=err_message), 422


@bp.app_errorhandler(requests.exceptions.ConnectionError)
def connection_error(e):
    """Connection error; mostly likely raised if internet is down."""
    return render_template("errors/connection-error.html")


# THIS CODE WILL SUPERSEDE INTERACTIVE DEBUGGER DURING DEVELOPMENT
# DO NOT ENABLE UNTIL YOU HAVE LOGGING/EMAILING OF ERRORS
# @app.errorhandler(500)
# def internal_error(error):
#     db.session.rollback()
#     return render_template('500.html'), 500
