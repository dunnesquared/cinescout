# Script to setup project environment variables.
# To run type the following on the console: "source setup.sh"
echo "Setting up Flask environment variables..."
export FLASK_APP=app.py
export FLASK_DEBUG=True
printf "FLASK_APP=%s\n" $FLASK_APP
printf "FLASK_DEBUG=%s\n" $FLASK_DEBUG

# Use this to ensure that database being used is project's app.db
# Comment out this line if you are migrating the app to another db
# (e.g. Postgre) such that you will be setting DATABASE_URL variable to
# whatever resource you're migrating too.
echo -n "Would you like to delete DATABASE_URL and use default SQLlite app.db? [y/n]: "
read ans
if [[ $ans == 'y' ]]; then
  unset DATABASE_URL
  echo "DATABASE_URL deleted."
fi


echo "Don't forget to set your API and secret keys!"
echo -n "Would you like to enter them now? [y/n]: "
read ans
echo "Hint: For your secret key, try using Python's secret.token_bytes."
if [[ $ans == 'y' ]]; then
  unset SECRET_KEY
  unset NYT_API_KEY
  unset TMDB_API_KEY

  echo -n "SECRET_KEY="
  read SECRET_KEY
  echo -n "NYT_API_KEY="
  read NYT_API_KEY
  echo -n "TMDB_API_KEY="
  read TMDB_API_KEY

  echo -n "Are you sure you want to export these keys? [y/n]: "
  read ans
  if [[ $ans == 'y' ]]; then
    printf "Exporting keys..."
    export SECRET_KEY=$SECRET_KEY
    export NYT_API_KEY=$NYT_API_KEY
    export TMDB_API_KEY=$TMDB_API_KEY
    printf "Done!\n"
  fi
fi
