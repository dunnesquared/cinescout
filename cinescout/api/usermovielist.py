"""API to add or remove a film from a user's movie list."""

from flask import request, jsonify
from flask_login import current_user, login_required

from cinescout import db # Get db object defined in __init__.py
from cinescout.models import Film, FilmListItem

from cinescout.api import bp

@bp.route('/user-movie-list/item', methods=['POST'])     # POST /user-movie-list/item
@login_required
def create_user_movie_item():
    """Adds movie to user's list."""
    try:
        print("Request received to add film to list...")
        print("Retrieving POST data...", end="")

        # Get minimum data. An exception should be thrown if there's a problem
        # and the program should fail gracefully.
        tmdb_id = int(request.form.get("tmdb_id"))
        title = request.form.get("title").strip()

        # Get non-essential data. Appropriate placeholders should be
        # used if data values are blank.

        # Film release year.
        # TypeError if None, ValueError if string: ''
        try:
            year = int(request.form.get("year"))
        except (TypeError, ValueError):
            print("POST value 'year' not an integer. Setting year to zero.")
            year = 0

        # Film release date.
        date = request.form.get("date")

        if date is None:
            date = ''

        # Original title
        original_title = request.form.get("original_title")

        if original_title:
            original_title = original_title.strip()

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
        return jsonify({"success": False, "err_message": err_message}), 500

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
        return jsonify({"success": True}), 201
    else:
        # Film is on list. Send error message.
        err_message = ("Film already on list! Film likely added elsewhere on " \
                        "site. Try refreshing page movie list or movie page.")
        print(err_message)
        # Send 409 response code ('Conflict') b/c film cannot be added if already on list!
        return jsonify({"success": False, "err_message": err_message}), 409


@bp.route('/user-movie-list/item', methods=["DELETE"])       # DELETE /user-movie-list/item
@login_required
def delete_user_movie_item():
    """Removes film from user's list."""
    print("Request received to remove film...")

    try:
        # Get id of film to be removed.
        print("Retrieving DELETE data...", end="")
        tmdb_id = int(request.form.get('tmdb_id'))

        # Check for bad values.
        if tmdb_id < 1:
            raise ValueError("tmdb_id must be positive.")

    except (ValueError, TypeError) as err:
        # Bad id value or NoneType passed.
        err_message = "Fatal Error: {0}".format(err)
        print(err_message)
        return jsonify({"success": False, "err_message": err_message}), 500

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
        return jsonify({"success": False, "err_message": err_message}), 409
