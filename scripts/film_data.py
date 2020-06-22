"""Script that imports film data from csv file."""

import sys
import os
import csv

print("Building path that will allow python to find to app resources...")
PROJ_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJ_PATH)
print(f"New path inserted into sys.path:\n{PROJ_PATH}")

from cinescout import app, db
from cinescout.models import User, Film, CriterionFilm, PersonalFilm, FilmListItem

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
CRITERION_FILE = os.path.join(DATA_PATH, "criterion.csv")
PERSONAL_FILE = os.path.join(DATA_PATH, "personal.csv")


def in_db(title, year):
    """Checks that film is not already in database.

    Returns:
        True: if list of results has one item or more.
        False: if the list of results is empty.
    """
    result = Film.query.filter(Film.title==title, Film.year==year).all()
    return bool(result)


def update_table(file_name, ModelClass):
    """Updates db table with data from file."""

    try:
        # Import data
        with open(file_name, newline='') as csvfile:
            reader = csv.reader(csvfile)

            # Skip the header line
            next(reader, None)

            # To inform user of current of record being outputted
            count = 1

            # Insert data into database
            for release_year, title, director, spine_num, tmdb_id, iffy in reader:

                # Clean up title. Replace @ symbols with commas.
                title = title.replace('@', ',').strip()

                if not in_db(title, release_year):
                    # Add to main table
                    film = Film(title=title, year=release_year,
                                tmdb_id=tmdb_id, director=director)
                    db.session.add(film)
                    db.session.commit()
                    print(f"#{count}: Inserting record into table '{Film.__tablename__}': {title}, {release_year}, {tmdb_id}")
                else:
                    # Query film id
                    film = Film.query.filter(Film.title==title).first()

                # Add to ModelClass table.
                film_id = film.id
                modelclass_obj = ModelClass(film_id=film_id)
                db.session.add(modelclass_obj)
                db.session.commit()
                print(f"#{count}: Inserting record into table '{ModelClass.__tablename__}': {title}, {release_year}")

                count += 1

            print("Insertion of data from 'criterion.csv' into database complete.")

    except OSError as err:
        print("OSError: {0}".format(err))



if __name__ == "__main__":
    print("===== Running FILM_DATA.PY script =====")

    try:
        # Clear and recreate database before import.
        print("Dropping all tables...")
        print("Creating all tables...")
        db.drop_all()
        db.create_all()

        print("Creating first user 'Alex'....")
        password = input("Please input a password for default user: ")

        print("Adding user to db...")
        u = User(username="Alex", email="alex@alex.com")
        u.set_password(password)
        db.session.add(u)
        db.session.commit()

        print("Creating second user 'Pablo'....")
        password = input("Please input a password for second user: ")

        print("Adding user to db...")
        u = User(username="Pablo", email="pablo@pablo.com")
        u.set_password(password)
        db.session.add(u)
        db.session.commit()

        # Import film data
        update_table(CRITERION_FILE, CriterionFilm)
        # update_table(PERSONAL_FILE, PersonalFilm) # No longer supported.

        # Add movies to personal lists
        print("Adding movies to personal lists...")
        film1 = FilmListItem(user_id=1, title="Wendy and Lucy", year=2008, tmdb_id=8942)
        film2 =  FilmListItem(user_id=2, title="MacGruber", year=2010, tmdb_id=37931)
        db.session.add(film1)
        db.session.add(film2)
        db.session.commit()

        # Display database results
        print("\nDATABASE CONTENTS")
        print("====================")

        print("\n**USERS**")
        for user in User.query.all():
            print(user)

        print("\n**FILMS**")
        for film in Film.query.all():
            print(film)

        print("\n**CRITERION FILMS**")
        for film in CriterionFilm.query.all():
            print(film)

        # No longer supported.
        # print("\n**PERSONAL FILMS**")
        # for film in PersonalFilm.query.all():
        #     print(film)

        print("\n**FILM LIST ITEMS**")
        for film in FilmListItem.query.all():
            print(film)

    except OSError as err:
        print("OSError: {0}".format(err))
