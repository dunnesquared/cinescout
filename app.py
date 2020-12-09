"""Entry module for flask to launch app."""

VERSION = "1.4.2"

print(f"\nWelcome to Cinescout, v{VERSION}")
print("============================")
print("***Executing app.py...***")

from cinescout import app # Get app object from __init__.py
print("Importing app object from cinescout package: __init.py__...")

from cinescout import db
from cinescout.models import User, Film, CriterionFilm, PersonalFilm, FilmListItem
print("Importing db and models to configure 'flask shell' context...")

@app.context_processor
def inject_version():
    """Makes version numbers accessible across all templates."""
    return dict(version=VERSION)

@app.shell_context_processor
def make_shell_context():
    """Makes it so 'flask shell' already has db and models imported
    (i.e. no need to reimport every time you open the shell. """
    print("Adding db and models to flask shell...")
    return {'db':db, 'User': User, 'Film': Film,
            'CriterionFilm': CriterionFilm, 'PersonalFilm': PersonalFilm,
            'FilmListItem': FilmListItem}
