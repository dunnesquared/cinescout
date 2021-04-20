"""Handling functions of users' requests that represent app's features."""
from flask import render_template, request, redirect, url_for, abort, flash
from flask_login import current_user, login_required

from cinescout import app, db # Get app, db object defined in __init__.py
from cinescout.models import User, Film, CriterionFilm, FilmListItem
from cinescout.main.forms import  SearchByTitleForm, SearchByPersonForm
from cinescout.movies import TmdbMovie
from cinescout.reviews import NytMovieReview

from cinescout.main import bp

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

@bp.route('/')
@bp.route('/index')
def index():
    """Home page."""
    return render_template("index.html")


@bp.route('/user-movie-list')       # GET /user-movie-list
@login_required
def get_user_movie_list():
    """Displays list of movies user has added."""
    films = FilmListItem.query.filter_by(user_id=current_user.id).all()
    return render_template("list.html", films=films)


@bp.route("/browse")
def browse():
    """Displays list of critically-acclaimed movies."""
    # Ensure that film query works alright before trying to render anything on the template.
    if db.session.query(Film).join(CriterionFilm).all():
        return render_template("browse.html", criterion_films_exist=True)
    else:
        err_message = f"Unable to load Criterion films: error fetching results from database."
        print("ERROR! " + err_message)
        return render_template("errors/misc-error.html", err_message=err_message)


@bp.route("/search")
def search():
    """Renders search forms."""
    title_form = SearchByTitleForm()
    person_form = SearchByPersonForm()
    return render_template("search.html",
                            title_form=title_form,
                            person_form=person_form)


@bp.route("/title-search-results", methods=["GET", "POST"])
def search_results_title():
    """Validates form data from movie search form."""

    form = SearchByTitleForm()

    if form.validate_on_submit():
        # Gets list of movies based on given title.
        movie_title = form.title.data.strip()

        # Redirect rather than render so user can book the results page
        # and refresh the results page without resubmittting the form.
        # As per Post-Get-Redirect pattern.
        return redirect(url_for('main.display_movie_search_results',
                        movie_title=movie_title))

    # In case users GET this route, or the form data is invalid.
    return render_template("search.html",
                           title_form=form,
                           person_form=SearchByPersonForm())


@bp.route("/movie-search-results", methods=["GET"])
def display_movie_search_results():
    """Renders list of movies from the external movie API based on
    title supplied. Allows users to see list of possible movies
    via GET http request and so do things like bookmark the page.
    """

    # Get the movie title passed in URl; hopefully it exists.
    movie_title = request.args.get('movie_title')

    # Clever users have messed around with the query parameters in the URL
    # by not giving a value to movie_title a value
    # No point in wasting TMDB's time if that's the case. Abort immediately.
    if not movie_title:
        abort(422)

    # Search external database for given title.
    result = TmdbMovie.get_movie_list_by_title(movie_title.strip())

    # Something went wrong...
    if not result['success']:
        # Bad HTTP response from API call or...
        if result['status_code'] != 200:
            abort(result['status_code'])
        else:
            # No movies found for given title.
            return render_template("movies.html", movies=None,
                                    form_title=movie_title)

    return render_template("movies.html", movies=result['movies'],
                            form_title=movie_title)


@bp.route("/person-search-results", methods=["GET", "POST"])
def search_results_person():
    """Validates data from person search form."""

    form = SearchByPersonForm()

    # Sent via POST
    if form.validate_on_submit():
        name = form.name.data.strip()
        known_for = form.known_for.data

        return redirect(url_for('main.search_results_person_get',
                        name=name, known_for=known_for))

    # In case users GET this route, or the form data is invalid.
    return render_template("search.html",
                            person_form=form,
                            title_form=SearchByTitleForm())


@bp.route("/person-search", methods=["GET"])
def search_results_person_get():
    """Renders list of people in their associated fields in the movie
    industry, via GET request."""

    name = request.args.get('name')
    known_for = request.args.get('known_for')

    # Query parameters should not be valueless. Don't bother TMDB otherwise.
    if not name or known_for == "":
        abort(422)

    # If not specified in GET query, assume it's 'All'
    if known_for is None:
        known_for = 'All'

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


@bp.route("/person/<int:person_id>", methods=["GET"])
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

    # Double checking whether person queried is actually who we're looking
    # for.
    tmdb_person_name = bio_data['name']

    # Possibility name erased from url. In that case, just set it to the
    # name from the query.

    print("Double-checking whether person name in url goes with data fetched...")
    if tmdb_person_name:
        if name is None:
            print("Name not specified in URL; assuming TMDB name is correct.")
            name = tmdb_person_name
        elif name.lower().strip() != tmdb_person_name.lower().strip():
            # Some other error, e.g. 429: too many request.
            err_message = f"URL person name and TMDB person name do not match: '{name}' vs. '{tmdb_person_name}'."
            print(err_message)
            return render_template("errors/misc-error.html",
                                    err_message=err_message)


    return render_template("filmography.html",
                             cast=filmography_data.get('cast'),
                             crew=filmography_data.get('crew'),
                             no_films=False,
                             name=name,
                             person_image_url=bio_data.get('image_url'))


# New movie_info view using redesigned NYTMovieReview algorithm.
@bp.route("/movie/<int:tmdb_id>", methods=["GET"])
def movie_info(tmdb_id):
    """Renders salient movie data and review summary from external APIs."""

    # Get movie info TMDB database.
    print("Fetching movie info based on tmdb id...")
    result = TmdbMovie.get_movie_info_by_id(tmdb_id)

    # TMDB request failed.
    if not result['success']:
        print("Error!")
        # Can't find movie referenced by id.
        if result['status_code'] == 404:
            abort(404)
        else:
            # Some other error, e.g. 429: too many request.
            err_message = f"TMDB API query failed; HTTP response = {result['status_code']}"
            return render_template("errors/misc-error.html",
                                    err_message=err_message)

    # Collect movie object.
    movie = result['movie']

    # To check a user's personal movie list, user must be logged in.
    # Also, limiting the fetching of NYT movie reviews to authenticated users.
    # This will speed up display of movie info for anonymous users as NYT review
    # fetching requires time delays between API requests.

     # See whether movie is already on user's list.
    on_user_list, film_list_item_id = False, None

    # To ref before assignment errors in the case of anonymous users requesting movie info.
    review, review_warning = None, None

    # Get search-engine queries for movie.
    search_engines = {
                        'Google': movie.get_query('google'),
                        'DuckDuckGo': movie.get_query('duckduckgo')
                     }

    if current_user.is_authenticated:

        # CHECK PERSONAL MOVIE LIST!!!
        print(f"Checking whether '{movie.title}' on user list...")
        film = FilmListItem.query.filter_by(tmdb_id=tmdb_id,
                                            user_id=current_user.id).first()
        if film:
            on_user_list = True
            film_list_item_id = film.id

        # on_user_list = True if film else False
        print(f"On user list? {on_user_list}, id: {film_list_item_id}")

        # GET MOVIE REVIEW!!!
        # No point in searching for a movie review if release year is unknown.
        if movie.release_year is not None and movie.release_year != 0:
            # Try this first.
            print(f"Fetching NYT movie review for '{movie.title}' ({movie.release_year})...")
            print("Making first attempt...")
            result = NytMovieReview.get_movie_review(movie)

            # If the above doesn't work, give this a shot.
            # Note that there is no point doing a second attempt for a film
            # that hasn't come out yet.
            if not result['review'] and not result['future_release']:
                print("Making second attempt...")
                print(f"Waiting {NytMovieReview.delay} seconds...")
                NytMovieReview.delay_next()
                result = NytMovieReview.get_movie_review(movie, first_try=False)

        else:
            print("Unable to fetch review: Movie has no review year.")
            return render_template("movie.html",
                                    movie=movie,
                                    review=None,
                                    on_user_list=on_user_list,
                                    search_engines=search_engines)

        # NYT request failed.
        if not result['success'] and result['status_code'] != 200:
            # Too many requests
            if result['status_code'] == 429:
                err_message = ("Too many requests in a row. Please wait 30–60 seconds "
                   "before your next query.")
                print(err_message)
                return render_template("errors/429.html", err_message=err_message), 429
                # Use again once reviews are asynchonously fetched via JS script.
                # abort(429)   
            else:
                # Movie may not have a review yet because it hasn't been released.
                # This is not an error, and so should not be handled as such.
                # Everything else though IS an error, and should be explored.
                if not result['future_release']:
                    print("Error retrieving NYT review.")
                    status_code = result['status_code']
                    description = result['message']
                    err_message = f"NYT API query failed ({status_code}): {description}"
                    print(err_message)
                    return render_template("errors/misc-error.html", err_message=err_message)

        # Looks like a review has been returned. Get it.
        review = result['review']

        # Check whether review has been flagged as being potentially wrong.
        review_warning = None
        if result['bullseye'] is not None:
            review_warning = not result['bullseye']

    return render_template("movie.html",
                            movie=movie,
                            review=review,
                            on_user_list=on_user_list,
                            review_warning=review_warning, 
                            search_engines=search_engines)


@bp.route("/about", methods=['GET'])
def about():
    return render_template("about.html")


### REFACTORED METHODS
# New movie_info view using redesigned NYTMovieReview algorithm.
@bp.route("/movie-redux/<int:tmdb_id>", methods=["GET"])
def movie_info_redux(tmdb_id):
    """Renders salient movie data and review summary from external APIs."""

    # Get movie info TMDB database.
    print("Fetching movie info based on tmdb id...")
    result = TmdbMovie.get_movie_info_by_id(tmdb_id)

    # TMDB request failed.
    if not result['success']:
        print("Error!")
        # Can't find movie referenced by id.
        if result['status_code'] == 404:
            abort(404)
        else:
            # Some other error, e.g. 429: too many request.
            err_message = f"TMDB API query failed; HTTP response = {result['status_code']}"
            return render_template("errors/misc-error.html",
                                    err_message=err_message)

    # Collect movie object.
    movie = result['movie']

    # To check a user's personal movie list, user must be logged in.
    # Also, limiting the fetching of NYT movie reviews to authenticated users.
    # This will speed up display of movie info for anonymous users as NYT review
    # fetching requires time delays between API requests.

     # See whether movie is already on user's list.
    on_user_list, film_list_item_id = False, None

    # To ref before assignment errors in the case of anonymous users requesting movie info.
    review, review_warning = None, None

    # Get search-engine queries for movie.
    search_engines = {
                        'Google': movie.get_query('google'),
                        'DuckDuckGo': movie.get_query('duckduckgo')
                     }

    if current_user.is_authenticated:

        # CHECK PERSONAL MOVIE LIST!!!
        print(f"Checking whether '{movie.title}' on user list...")
        film = FilmListItem.query.filter_by(tmdb_id=tmdb_id,
                                            user_id=current_user.id).first()
        if film:
            on_user_list = True
            film_list_item_id = film.id

        # on_user_list = True if film else False
        print(f"On user list? {on_user_list}, id: {film_list_item_id}")

       

    return render_template("movie-redux.html",
                            movie=movie,
                            on_user_list=on_user_list,
                            review_warning=review_warning, 
                            search_engines=search_engines)