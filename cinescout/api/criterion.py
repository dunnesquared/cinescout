"""API to fetch list of Criterion films."""

from flask import jsonify
from flask_login import current_user, login_user, logout_user, login_required

from cinescout import db # Get db object defined in __init__.py
from cinescout.models import Film, CriterionFilm

from cinescout.api import bp
from cinescout import limiter

# Rate-limit calls to this api route. 
@bp.route("/criterion-films")
@limiter.limit("30 per minute, 2 per second")    
def get_criterion_films():
    """Builds data object required to display a list of critically-acclaimed movies.
    on the client side.

    Returns:
        JSON object with the following fields:
        In case of errors:
            'success': Boolean set to False.
            'err_message': String containing error message.
        Otherwise:
            'success': Boolean set to True.
            'num_results': Integer of indicating number of movies returned.
            'results': List of dictionaries where each represents a film.
                'title': String representing a movie's title.
                'year': String represent movie's release year.
                'directors': A list of strings representing directors' namees.
    """
    criterion_films = db.session.query(Film).join(CriterionFilm).all()

    # Check for error cases.
    if criterion_films is None:
        return jsonify({
            'success': False,
            'err_message': "Query for Criterion films returned NoneType object."
        }), 404

    num_films = len(criterion_films)
    if num_films == 0:
        return jsonify({
            'success': False,
            'err_message': "Query for Criterion films returned no films."
        }), 404

    # All good. Build JSON object.
    movies = {
        'success': True,
        'num_results': len(criterion_films),
        'results': []
    }

    # Extract film info from ORM object.
    for film in criterion_films:
        result = {}
        result['title'] = film.title
        result['year'] = film.year

        directors = film.director.split('&')
        directors = [ director.strip() for director in directors ]
        result['directors'] = directors

        result['tmdb_id'] = film.tmdb_id

        movies['results'].append(result)

    return jsonify(movies)