import os
import time
import json
import requests


from flask import render_template, request, redirect, url_for, abort, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required

from cinescout import app, db # Get app, db object defined in __init__.py
from cinescout.models import User, Film, CriterionFilm, PersonalFilm, FilmListItem
from cinescout.forms import LoginForm, RegistrationForm, SearchByTitleForm
from cinescout.movies import TmdbMovie, NytMovieReview

NYT_API_KEY = app.config['NYT_API_KEY']
TMDB_API_KEY = app.config['TMDB_API_KEY']

# N.B. These may change every few days!!!
TMDB_BASE_IMG_URL = "http://image.tmdb.org/t/p/"
POSTER_SIZE = "w300"

# Recommended sleep times in seconds between calls as per Terms of Service
# Read https://developer.nytimes.com/faq#a11
NYT_API_DELAY = 3 # Six seconds recommneded

print("Executing views.py...")

@app.route('/')
@app.route('/index')
def index():
	message = "This is placeholder content"
	return render_template("index.html", message=message)


@app.route('/register', methods=['GET', 'POST'])
def register():
	"""Allows non-logged in users to register for account."""

	# Logged in users shouldn't be allowed to register.
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = RegistrationForm()

	# Ensure user-entered data is good. If so, register and take to login page!
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash(f'Welcome to cinescout, {form.username.data}! Now login to get started.', 'success')
		return redirect(url_for('login'))

	# When users GET the register page
	return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log-in user with valid credentials. Reject otherwise."""

	# Logged-in users don't get to log-in before logging out again.
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))

		# Remember user id in case session ended and user then re-enters app,
		# e.g. closing tab while still logged-in.
        login_user(user, remember=form.remember_me.data)
        flash('You have been logged in!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'success')
    return redirect(url_for('index'))


@app.route('/movie-list')
@login_required
def movie_list():
    """Displays list of movies user has added."""

    films = FilmListItem.query.filter_by(user_id=current_user.id).all()

    return render_template("list.html", films=films)


@app.route('/add-to-list', methods=['POST'])
@login_required
def add_to_list():
    """Adds movies to user's list"""
    print("Request received to add film to list...")
    tmdb_id = int(request.form.get("tmdb_id"))
    title = request.form.get("title")
    year = int(request.form.get("year"))

    # See whether movie is in user list
    film = FilmListItem.query.filter_by(user_id=current_user.id, tmdb_id=tmdb_id).first()


    if not film:

        # Add film to list
        new_film = FilmListItem(user_id=current_user.id,
                                title=title,
                                year=year,
                                tmdb_id=tmdb_id)

        db.session.add(new_film)
        db.session.commit()

        return jsonify({"success": True})

    else:
        return jsonify({"success": False})


@app.route('/remove-from-list', methods=["POST"])
@login_required
def remove_from_list():
    #Check that film is on list
    print("REMOVE METHOD ACCESSED!!!")
    tmdb_id = int(request.form.get('tmdb_id'))
    print(tmdb_id)

    film = FilmListItem.query.filter_by(tmdb_id=tmdb_id, user_id=current_user.id).first()
    print(film)

    if film:
        db.session.delete(film)
        db.session.commit()
        return jsonify({"success": True})

    else:
        return jsonify({"success": False})



@app.route("/browse")
def browse():
    """Display list of critically-acclaimed movies."""
    all_films = Film.query.all()

    criterion_films = db.session.query(Film).join(CriterionFilm).all()
    personal_films = db.session.query(Film).join(PersonalFilm).all()

    return render_template("browse.html",
                            films=all_films,
                            criterion_films=criterion_films,
                            personal_films=personal_films)


@app.route("/search")
def search():
    """Renders search forms"""
    title_form = SearchByTitleForm()
    return render_template("search.html", title_form=title_form)


# @app.route("/search")
# def search():
#     return render_template("search.html")

@app.route("/results", methods=["POST"])
def search_results_title():
    """Gets movie results from the TMDB based on title supplied."""

    form = SearchByTitleForm()

    if form.validate_on_submit():
        movies = TmdbMovie.get_movie_list_by_title(form.title.data.strip())
        return render_template("results.html", movies=movies)




# ***** OLD *****
@app.route("/results", methods=["POST"])
def search_results():
    """Gets results from the TMDB."""

    if request.method == 'POST':

        title = request.form.get("title")

        if title is None:
            return "<em> Unable to get title from form. Please debug. </em>"

        # # Get JSON response from New York Times
        # res = requests.get("https://api.themoviedb.org/3/search/movie",
        #                     params={"api_key": TMDB_API_KEY, "query": title.strip()})
		#
        # tmdb_data = res.json()
		#
        # if tmdb_data["total_results"] == 0:
        #     return "<em> TMDB: No results matching that query. </em>"
		#
        # if tmdb_data["total_results"] >= 1:
        #     # Get results for each movie
        #     movies = tmdb_data["results"]

        movies = TmdbMovie.get_movie_list_by_title(title)
        return render_template("results.html", movies=movies)

@app.route("/movie/<int:tmdb_id>", methods=["GET"])
def movie_info(tmdb_id):

    # Get movie info TMDB database
	result = TmdbMovie.get_movie_info_by_id(tmdb_id)

	if not result['success']:
		if result['status_code'] == 404:
			abort(404)
		else:
			err_message = f"TMDB API query failed; HTTP response = {result['status_code']}"
			return render_template("misc-error.html", err_message=err_message)
	else:
		print("Tmdb data retrieved :-)!")

	movie = result['movie']

    # Get NYT movie review
	result = NytMovieReview.get_review_by_title_and_year(title=movie.title,
	 													 year=movie.release_year)

	if not result['success']:
		err_message = f"NYT API query failed; HTTP response = {result['status_code']}  description={result['message']}"
		return render_template("misc-error.html", err_message=err_message)
	else:
		print("Nyt review data retrieved :-)!")

	review = result['review']

	# Assess whether movie is already on user's list.
	on_user_list, film_list_item_id = None, None
	if current_user.is_authenticated:
	    film = FilmListItem.query.filter_by(tmdb_id=tmdb_id, user_id=current_user.id).first()
	    on_user_list = True if film else False
	    print(f"On user list? {on_user_list}, id: {film_list_item_id}")

	return render_template("movie.html",
							movie=movie,
							review=review,
							on_user_list=on_user_list)


#
# @app.route("/movie/<int:tmdb_id>", methods=["GET"])
# def movie_info(tmdb_id):
#
#     # Get movie info TMDB database
#     res = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}",
#                         params={"api_key": TMDB_API_KEY})
#
#     if res.status_code == 404:
#         abort(404)
#
#     if res.status_code != 200:
#         return f"TMDB Movie Id lookup: Something went wrong, Status code {res.status_code}"
#
#     tmdb_movie_data = res.json()
#
# 	# Build poster/still urls
#     poster_url_full = None
#     if tmdb_movie_data['poster_path']:
#         poster_url_full = TMDB_BASE_IMG_URL + POSTER_SIZE + tmdb_movie_data['poster_path']
#         print(f"FULL POSTER URL: {poster_url_full}")
#
#
#     # Get review info from NYT
# 	# Flag in case NYT review info already found
#     nyt_review_already_found = False
#
#     # Release year helps to narrow down movie if there are multiple hits
#     if tmdb_movie_data['release_date']:
#         release_year = tmdb_movie_data['release_date'].split('-')[0].strip()
#
#     print(f"RELEASE YEAR = {release_year}")
#
#     opening_date_start = f"{release_year}-01-01"
#     opening_date_end = f"{release_year}-12-31"
#
#     res = requests.get("https://api.nytimes.com/svc/movies/v2/reviews/search.json",
#                             params={"api-key": NYT_API_KEY,
#                                     "opening-date": f"{opening_date_start};{opening_date_end}",
#                                     "query": tmdb_movie_data['title'].strip()})
#
#     if res.status_code == 404:
#         abort(404)
#
#     if res.status_code != 200:
#         return f"NYT movie review lookup: Something went wrong, Status code {res.status_code}"
#
#     nyt_data = res.json()
#
#     # Check whether a review was written for a movie. Watch out for special cases.
#     if nyt_data["num_results"] == 0:
#         print("No NYT review found☹️")
#
#         nyt_status = "No review found."
#         nyt_critics_pick = "N/A"
#         nyt_summary_short = "N/A"
#
#         # Check case where year in NYT db and TMBD don't match.
#         print("Checking to see whether release year in TMDB and NYT don't match....")
#
#         print(f"Delaying next NYT API call by {NYT_API_DELAY} seconds...")
#         time.sleep(NYT_API_DELAY)
#
#         print("Making second request to NYT with TMDB release year unspecified...")
#         res = requests.get("https://api.nytimes.com/svc/movies/v2/reviews/search.json",
#                                 params={"api-key": NYT_API_KEY,
#                                         "query": tmdb_movie_data['title'].strip()})
#
#         if res.status_code == 404:
#             abort(404)
#         if res.status_code != 200:
#             return f"NYT movie review lookup: Something went wrong, Status code {res.status_code}"
#
#         print("Request successful. Counting number of reviews returned...")
#         nyt_data = res.json()
#
#         if nyt_data["num_results"] == 0:
#             print("There are really no reviews for this movie. Sorry😭")
#
#         if nyt_data["num_results"] == 1:
#             print("One review found. Hopefully this is it🙏🏻!")
#
#
#         if nyt_data["num_results"] > 1:
#             print("More than one review found🤔")
#             print("Using heuristic that NYT reviewed film at closest date AFTER TMDB's release date....")
#
#             print("Analyzing NYT review results...")
#
#             # Get critics pick data and summary short for review that has years closest to TMDBs
#             years = []
#
#             for result in nyt_data['results']:
#                 # Extract year
#                 print("Extacting NYT release or publcation year...", end="")
#                 nyt_date = result['opening_date'] if result['opening_date'] else result['publication_date']
#                 nyt_year = nyt_date.split('-')[0].strip()
#                 print(nyt_year)
#
#                 years.append(nyt_year)
#
#             print("Getting NYT year closest to TMDB year...", end="")
#             shortlist = []
#
#             for year in years:
#                 diff = int(year) - int(release_year)
#                 if diff > 0:
#                     shortlist.append(diff)
#             result_index = shortlist.index(min(shortlist))
#             print(years[result_index])
#
#             print("Getting review information. Hopefully right review picked🙏!")
#             nyt_critics_pick = nyt_data['results'][result_index]['critics_pick']
#             nyt_summary_short = nyt_data['results'][result_index]['summary_short']
#
#             # So we don't overwrite the found review results with the logic below
#             nyt_review_already_found = True
#
#
#     if nyt_data["num_results"] > 1 and not nyt_review_already_found:
#
#         nyt_status = "ERROR: More than one review found. Unable to choose."
#         nyt_critics_pick = "N/A"
#         nyt_summary_short = "N/A"
#
#     if  nyt_data["num_results"] == 1:
#         nyt_status = "OK"
#         nyt_critics_pick = nyt_data['results'][0]['critics_pick']
#         nyt_summary_short = nyt_data['results'][0]['summary_short']
#
#         if nyt_summary_short is not None:
#             if nyt_summary_short.strip() == "":
#                 nyt_summary_short = "No summary review provided."
#
#
#     print(f"NYT_STATUS: {nyt_status}")
#
#
#
#
#     # Assess whether movie is already on user's list.
#     on_user_list, film_list_item_id = None, None
#     if current_user.is_authenticated:
#         film = FilmListItem.query.filter_by(tmdb_id=tmdb_id, user_id=current_user.id).first()
#         on_user_list = True if film else False
#         print(f"On user list? {on_user_list}, id: {film_list_item_id}")
#
#
#     movie_info = {
#         'tmdb_id': tmdb_id,
#         'title': tmdb_movie_data['title'],
#         'opening_date': tmdb_movie_data['release_date'],
#         'year': int(tmdb_movie_data['release_date'].split('-')[0].strip()),
#         'overview': tmdb_movie_data['overview'],
#         'poster_url_full': poster_url_full,
#         'nyt_critics_pick': nyt_critics_pick,
#         'nyt_summary_short': nyt_summary_short,
#         'on_user_list': on_user_list,
#     }
#
#
#     return render_template("movie.html", movie_info=movie_info)
