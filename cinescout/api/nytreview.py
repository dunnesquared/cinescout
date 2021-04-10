"""API to fetch NYT film review films."""

from typing import Dict

from datetime import datetime

from flask import jsonify, request
from flask_login import current_user, login_user, logout_user, login_required

from cinescout.movies import Movie
from cinescout.reviews import NytMovieReview
from cinescout.api import bp


def _nyt_response_error(response : Dict) -> Dict:
     """Private function to handle errors returned from NYT api."""
     print("Error retrieving NYT review.")
     status_code = response['status_code']
     if status_code == 429:
        err_message = ("Too many requests in a row. Please wait 30–60 seconds "
                "before your next query.")
     else:
        err_message = f"NYT API query failed ({status_code}): {response['message']}"
    
     print(err_message)
     return {'success': False, 'err_message': err_message}, status_code


@bp.route("/nyt-movie-review/")
def get_nyt_movie_review():
    """Fetches movie review from NYT API.

    Returns:
        JSON object with the following fields:
        In case NYT api returns an error:
            'success': Boolean set to False.
            'err_message': String containing error message.
        In case a review cannot be found despite all attempts:
            'success': Boolean set to False.
            'message': String containing message describing that fim could not be found.
        In case review is found:
            'success': Boolean set to True.
            'review_text': String respresenting NYT movie review for given movie.
            'critics_pick': Boolean whether film is a NYT Critic's Pick.
            'review_warning': Boolean indicating whether warning message should be displayed
                              indicating that fetched film review may not be the correct one.
            
    """
    data = request.get_json()
    title = data.get('title')
    original_title = data.get("original_title")
    release_year = data.get("release_year")
    release_date = data.get("release_date")
    
    print("Fetching movie review:")
    print(f"Title: '{title}'")
    print(f"Original Title: {original_title}")
    print(f"Release Year: {release_year}")
    print(f"Release Date: {release_date}")

    # No point in searching for review if release year DNE.
    if not release_year:
        err_message = "Unable to fetch review: No review year specified in payload."
        return {'success': False, 'err_message': err_message}, 400

    # No point in searching for review if movie has yet to come out.
    today = datetime.today()
    release_dt = datetime.strptime(release_date, '%Y-%m-%d')
    if release_dt > today:
        message = "No review to display: this film has yet to be released."
        return {'success': False, 'message': message}
        
    # Create Movie object.
    movie = Movie(title=title, release_year=release_year, release_date=release_date,
                  original_title=original_title)
    
    # Fetch movie review. Try main title first.
    print(f"Fetching NYT movie review for '{movie.title}' ({movie.release_year})...")
    print("Making first attempt...")
    response = NytMovieReview.get_movie_review(movie)
    print(response)

    # Handle error.
    if response['status_code'] != 200:
        return _nyt_response_error(response)

    # See if there's a review to print.
    review = response.get('review', None)
    
    # Make second attempt. NytMovieReview will try using a different method this time.
    if not review:
        print("Making second attempt...")
        NytMovieReview.delay_next()
        response = NytMovieReview.get_movie_review(movie, first_try=False)
    
    # Handle error.
    if response['status_code'] != 200:
        return _nyt_response_error(response)

    # No review found for specified movie despite all attempts to find one.
    if not review: 
        message = "No review found for this movie."
        return {'success': False, 'message': message}
        
    # All good. Extract data.
    review_text = review.text
    critics_pick = bool(review.critics_pick)
    review_warning = not response.get('bullseye', None)
    result = {
                'success': True, 
                'review_text': review_text, 
                'critics_pick': critics_pick,
                'review_warning': review_warning
             }
    return jsonify(result)

