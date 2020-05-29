print("Executing app.py")

from cinescout import app # Get app object from __init__.py
print("Importing app object from cinescout package: __init.py__...")

from cinescout import db
from cinescout.models import User
print("Importing db and models to configure 'flask shell' context...")

@app.shell_context_processor
def make_shell_context():
    """Makes it so 'flask shell' already has db and models imported 
    (i.e. no need to reimport every time you open the shell. """
    print("Adding db and models to flask shell...")
    return {'db':db, 'User': User}

