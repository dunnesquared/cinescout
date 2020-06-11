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
    person_form = SearchByPersonForm()
    return render_template("search.html",
                            title_form=title_form,
                            person_form=person_form)




@app.route("/title-search-results", methods=["POST"])
def search_results_title():
    """Gets movie results from the TMDB based on title supplied."""

    form = SearchByTitleForm()

    if form.validate_on_submit():
        result = TmdbMovie.get_movie_list_by_title(form.title.data.strip())

        if not result['success']:
            if result['status_code'] != 200:
                abort(result['status_code'])
            else:
				# No movies found for given title
                return render_template("results.html", movies=None)


        return render_template("results.html", movies=result['movies'])

    # In case users GET the page, or the data is invalid
    return render_template("search.html",
                           title_form=form,
						   person_form=SearchByPersonForm())


@app.route("/person-search-results", methods=["POST"])
def search_results_person():
    """Renders list of people in their associated fields."""

    form = SearchByPersonForm()

    if form.validate_on_submit():
        name = form.name.data.strip()
        known_for = form.known_for.data
        result = TmdbMovie.get_person_list_by_name_known_for(name=name,
                                                         known_for=known_for)

        if not result['success']:
            if result['status_code'] != 200:
                abort(result['status_code'])
            else:
                # No people to display
                no_persons = True
                return render_template("persons.html",
                                         persons=result['persons'])
        else:
            print("Tmdb person data retrieved :-)!")

        return render_template("persons.html", persons=result['persons'])


    # In case users GET the page, or the data is invalid
    return render_template("search.html",
							person_form=form,
							title_form=SearchByTitleForm())


@app.route("/person/<int:tmdb_person_id>", methods=["GET"])
def filmography(tmdb_person_id):

	filmography_data = TmdbMovie.get_movie_list_by_person_id(tmdb_person_id)

	if not filmography_data['success']:
		if filmography_data['status_code'] != 200:
			abort(filmography_data['status_code'])
		else:
			# No films to display
			return render_template("filmography.html",
									 cast=None,
									 crew=None,
									 no_films=True)
	else:
		print("Tmdb filmography data retrieved :-)!")
		return render_template("filmography.html",
								 cast=filmography_data.get('cast'),
								 crew=filmography_data.get('crew'),
								 no_films=False)


@app.route("/movie/<int:tmdb_id>", methods=["GET"])
def movie_info(tmdb_id):

    # Get movie info TMDB database
    result = TmdbMovie.get_movie_info_by_id(tmdb_id)

    if not result['success']:
        if result['status_code'] == 404:
            abort(404)
        else:
            err_message = f"TMDB API query failed; HTTP response = {result['status_code']}"
            return render_template("errors/misc-error.html", err_message=err_message)
    else:
        print("Tmdb data retrieved :-)!")

    movie = result['movie']

    # Get NYT movie review
    if movie.release_year is not None:
	    result = NytMovieReview.get_review_by_title_and_year(title=movie.title, year=movie.release_year)
    else:
        return render_template("movie.html",
	                            movie=movie,
	                            review=None,
	                            on_user_list=None)

    if not result['success'] and result['status_code'] != 200:
        err_message = f"NYT API query failed; HTTP response = {result['status_code']}  description={result['message']}"
        return render_template("errors/misc-error.html", err_message=err_message)

    print("NYT movie review query completed successfully...")

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
