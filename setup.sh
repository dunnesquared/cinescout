# Run as "source setup.sh"
export FLASK_APP=app.py
export FLASK_DEBUG=True

# Use this to ensure that database being used is project's app.db
# Comment out this line if you are migrating the app to another db
# (e.g. Postgre) such that you will be setting DATABASE_URL variable to
# whatever resource you're migrating too.
unset DATABASE_URL
