"""Handling functions of users' requests that represent app's features."""

import os
import time
import json
import requests

from flask import render_template, request, redirect, url_for, abort, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required

from cinescout import app, db # Get app, db object defined in __init__.py
from cinescout.models import User, Film, CriterionFilm, PersonalFilm, FilmListItem
from cinescout.forms import LoginForm, RegistrationForm, SearchByTitleForm, SearchByPersonForm
from cinescout.movies import TmdbMovie, NytMovieReview, Person

# Won't be able to access the NYT or The Movie Database without these.
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
    """Home page."""
    return render_template("index.html")


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
        flash(f'Welcome to Cinescout, {form.username.data}! Now login to get started.', 'success')
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
        return redirect(url_for('search'))

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    """Logs out user."""
    logout_user()
    flash('You have been logged out!', 'success')
    return redirect(url_for('login'))


@app.route('/movie-list')
@login_required
def movie_list():
    """Displays list of movies user has added."""
    films = FilmListItem.query.filter_by(user_id=current_user.id).all()
    return render_template("list.html", films=films)


@app.route('/add-to-list', methods=['POST'])
@login_required
def add_to_list():
    """Adds movies to user's list."""

    try:
        print("Request received to add film to list...")
        print("Retrieving POST data...", end="")

        # Get data.
        tmdb_id = int(request.form.get("tmdb_id"))
        title = request.form.get("title").strip()
        year = int(request.form.get("year"))
        date = request.form.get("date").strip()
        original_title = request.form.get("original_title").strip()

        # Check for bad values.
        if year < 0:
            raise ValueError("Year value must be non-negative.")
        if tmdb_id < 1:
            raise ValueError("tmdb_id must be positive.")
        if title.strip() == "":
            raise ValueError("Name cannot be blank.")

    except (ValueError, TypeError) as err:
        # Possible non-integer values passed for id or year; NoneType also.
        print("FAILED!")
        err_message = "Fatal Error: {0}".format(err)
        print(err_message)
        return jsonify({"success": False, "err_message": err_message})

    print("Success!")

    # See whether movie is in user list.
    film = FilmListItem.query.filter_by(user_id=current_user.id,
                                        tmdb_id=tmdb_id).first()

    if not film:
        # Film is not list: add it.
        print(f"Adding film '{title}'...")
        new_film = FilmListItem(user_id=current_user.id,
                                title=title,
                                year=year,
                                tmdb_id=tmdb_id,
                                date=date,
                                original_title=original_title)
        db.session.add(new_film)
        db.session.commit()
        return jsonify({"success": True})
    else:
        # Film is on list. Send error message.
        err_message = ("Film already on list! Film likely added elsewhere on " \
                        "site. Try refreshing page movie list or movie page.")
        print(err_message)
        return jsonify({"success": False, "err_message": err_message})


@app.route('/remove-from-list', methods=["POST"])
@login_required
def remove_from_list():
    """Removes film from user's list."""

    print("Request received to remove film...")

    try:
        # Get id of film to be removed.
        print("Retrieving POST data...", end="")
        tmdb_id = int(request.form.get('tmdb_id'))

        # Check for bad values.
        if tmdb_id < 1:
            raise ValueError("tmdb_id must be positive.")

    except (ValueError, TypeError) as err:
        # Bad id value or NoneType passed.
        err_message = "Fatal Error: {0}".format(err)
        print(err_message)
        return jsonify({"success": False, "err_message": err_message})

    print("Success!")

    # See whether film is on list. Can't be removed otherwise.
    print("Checking to see whether film is on list...")
    film = FilmListItem.query.filter_by(tmdb_id=tmdb_id, user_id=current_user.id).first()

    # Film is on list. Remove it.
    if film:
        print(f"Deleting film '{film.title}' from database...")
        db.session.delete(film)
        db.session.commit()
        return jsonify({"success": True})
    else:
        # Film is not on list. Send error message.
        err_message = ("Film not on list! Film likely removed elsewhere on " \
                       "site. Try refreshing movie list or movie page.")
        print(err_message)
        return jsonify({"success": False, "err_message": err_message})


@app.route("/browse")
def browse():
    """Displays list of critically-acclaimed movies."""
    criterion_films = db.session.query(Film).join(CriterionFilm).all()
    return render_template("browse.html",
                            criterion_films=criterion_films)


@app.route("/browse_new")
def browse_new():
    """Displays list of critically-acclaimed movies."""
    criterion_films = db.session.query(Film).join(CriterionFilm).all()
    return render_template("browse_new.html",
                            criterion_films=criterion_films)

@app.route("/api/criterion-films")
def criterionfilm_api():
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
        })

    num_films = len(criterion_films)

    if num_films == 0:
        return jsonify({
            'success': False,
            'err_message': "Query for Criterion films returned no films."
        })

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


@app.route("/search")
def search():
    """Renders search forms."""
    title_form = SearchByTitleForm()
    person_form = SearchByPersonForm()
    return render_template("search.html",
                            title_form=title_form,
                            person_form=person_form)


@app.route("/title-search-results", methods=["POST"])
def search_results_title():
    """Renders list of movies from the external movie API based on
    title supplied."""

    form = SearchByTitleForm()

    if form.validate_on_submit():
        # Gets list of movies based on given title.
        form_title = form.title.data.strip()

        result = TmdbMovie.get_movie_list_by_title(form_title)

        # Something went wrong...
        if not result['success']:
            # Bad HTTP response from API call or...
            if result['status_code'] != 200:
                abort(result['status_code'])
            else:
                # No movies found for given title.
                return render_template("results.html", movies=None,
                                        form_title=form_title)

        return render_template("results.html", movies=result['movies'],
                                form_title=form_title)

    # In case users GET this route, or the form data is invalid.
    return render_template("search.html",
                           title_form=form,
                           person_form=SearchByPersonForm())


@app.route("/person-search-results", methods=["POST"])
def search_results_person():
    """Renders list of people in their associated fields in the movie
    industry."""

    form = SearchByPersonForm()

    if form.validate_on_submit():
        name = form.name.data.strip()
        known_for = form.known_for.data
        result = TmdbMovie.get_person_list_by_name_known_for(name=name,
                                                         known_for=known_for)

        if not result['success']:
            # Bad HTTP response from API call or...
            if result['status_code'] != 200:
                abort(result['status_code'])
            else:
                # No people to display.
                return render_template("persons.html",
                                         persons=result['persons'],
                                         name=name)

        return render_template("persons.html",
                                persons=result['persons'],
                                name=name)

    # In case users GET this route, or the form data is invalid.
    return render_template("search.html",
                            person_form=form,
                            title_form=SearchByTitleForm())


@app.route("/person-search", methods=["GET"])
def search_results_person_get():
    """Renders list of people in their associated fields in the movie
    industry, via GET request."""

    name = request.args.get('name')
    known_for = request.args.get('known_for')

    result = TmdbMovie.get_person_list_by_name_known_for(name=name,
                                                     known_for=known_for)

    if not result['success']:
        # Bad HTTP response from API call or...
        if result['status_code'] != 200:
            abort(result['status_code'])
        else:
            # No people to display.
            return render_template("persons.html",
                                     persons=result['persons'],
                                     name=name)

    return render_template("persons.html", persons=result['persons'], name=name)


@app.route("/person/<int:person_id>", methods=["GET"])
def filmography(person_id):
    """Renders movie credits of a person in the movie industry.

    Args:
        person_id: Id in external database of person sought for.
    """

    name = request.args.get("name")

    print(f"Getting filmography data for {name}...")

    filmography_data = TmdbMovie.get_movie_list_by_person_id(person_id)

    if not filmography_data['success']:
        # Bad HTTP response from API call or...
        if filmography_data['status_code'] != 200:
            abort(filmography_data['status_code'])
        else:
            # No films to display.
            return render_template("filmography.html",
                                     cast=None,
                                     crew=None,
                                     no_films=True)


    print(f"Getting person bio data for {name}...")
    bio_data = TmdbMovie.get_bio_data_by_person_id(person_id)

    if not bio_data['success']:
        # Bad HTTP response from API call or...
        if bio_data['status_code'] != 200:
            abort(bio_data['status_code'])

    return render_template("filmography.html",
                             cast=filmography_data.get('cast'),
                             crew=filmography_data.get('crew'),
                             no_films=False,
                             name=name,
                             person_image_url=bio_data.get('image_url'))


@app.route("/movie/<int:tmdb_id>", methods=["GET"])
def movie_info(tmdb_id):
    """Renders salient movie data and review summary from external APIs."""

    # Get movie info TMDB database.
    result = TmdbMovie.get_movie_info_by_id(tmdb_id)

    # TMDB request failed.
    if not result['success']:
        # Can't find movie referenced by id.
        if result['status_code'] == 404:
            abort(404)
        else:
            # Some other error, e.g. 429: too many request.
            err_message = f"TMDB API query failed; HTTP response = {result['status_code']}"
            return render_template("errors/misc-error.html", err_message=err_message)

    # Collect movie object.
    movie = result['movie']

    # Get NYT movie review.
    if movie.release_year is not None:
        # Try first with film's 'main' English language title.
        result = NytMovieReview.get_review_by_title_and_year(title=movie.title,
                                                            year=movie.release_year,
                                                            movie_obj=movie)

        # Review may be under film's original language title.
        if not result['review'] and movie.original_title is not None:
            print("Trying get review with film's original title...")
            result = NytMovieReview.get_review_by_title_and_year(title=movie.original_title,
                                                                year=movie.release_year,
                                                                movie_obj=movie)
    else:
        return render_template("movie.html",
                                movie=movie,
                                review=None,
                                on_user_list=None)

    # NYT request failed.
    if not result['success'] and result['status_code'] != 200:
        # Too many requests
        if result['status_code'] == 429:
            abort(429)
        else:
            err_message = f"NYT API query failed; HTTP response = {result['status_code']}  description={result['message']}"
            return render_template("errors/misc-error.html", err_message=err_message)

    review = result['review']

    # See whether movie is already on user's list.
    on_user_list, film_list_item_id = None, None

    # To check a user's list we need to who were checking, i.e. user must be
    # logged in.
    if current_user.is_authenticated:
        film = FilmListItem.query.filter_by(tmdb_id=tmdb_id, user_id=current_user.id).first()
        on_user_list = True if film else False
        print(f"On user list? {on_user_list}, id: {film_list_item_id}")

    # Check whether review has been flagged as being potentially wrong.
    print(result['message'])
    review_warning = True if result['message'].strip() == 'WARNING' else False

    return render_template("movie.html",
                            movie=movie,
                            review=review,
                            on_user_list=on_user_list,
                            review_warning=review_warning)
