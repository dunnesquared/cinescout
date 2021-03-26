"""API to fetch NYT film review films."""

from flask import jsonify, request
from flask_login import current_user, login_user, logout_user, login_required

from cinescout.movies import Movie
from cinescout.reviews import NytMovieReview
from cinescout.api import bp

@bp.route("/nyt-movie-review/<string:title>")
def get_nyt_movie_review(title):
    """Fetches movei review from NYT api

    Returns:
        JSON object with the following fields:
        In case of errors:
            'success': Boolean set to False.
            'err_message': String containing error message.
        Otherwise:
            'success': Boolean set to True.
            'review_text': String respresenting NYT movie review for given movie.
            'critics_pick': Boolean whether film is a NYT Critic's Pick.
            'review_warning': Boolean indicating whether warning message should be displayed
                              indicating that fetched film review may not be the correct one.
            
    """
    data = request.get_json()
    original_title = data.get("original_title")
    release_year = data.get("release_year")
    release_date = data.get("release_date")
    
    print("Fetching movie review:")
    print(f"Title: '{title}'")
    print(f"Original Title: {original_title}")
    print(f"Release Year: {release_year}")
    print(f"Release Date: {release_date}")
    
    # Fetch movie review data (stub data for now)
    review_text = f"'{title}' was interesting...Five bags of popcorn!"
    critics_pick = True
    review_warning = False
    
    # Error.
    if not review_text: 
        err_message = "Unable to get movie review."
        return {'success': False, 'err_message': err_message}, 404
        
    # All good.
    result = {
                'success': True, 
                'review_text': review_text, 
                'critics_pick': critics_pick,
                'review_warning': review_warning
                }

    return jsonify(result)

