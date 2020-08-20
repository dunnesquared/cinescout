# Script to setup project environment variables.
# To run type the following on the console: "source setup.sh"
echo "Setting up Flask environment variables..."
export FLASK_ENV=development
export FLASK_APP=app.py
export FLASK_DEBUG=True
printf "FLASK_ENV=%s\n" $FLASK_ENV
printf "FLASK_APP=%s\n" $FLASK_APP
printf "FLASK_DEBUG=%s\n" $FLASK_DEBUG

# Setup database.
echo "Setting up database..."

# app.db exists.
if [ -f app.db ]; then
  echo -n "File 'app.db' detected in current directory. Would you like to continue using this file? [y/n] "
  read ans

  if [[ $ans == 'y' || $ans == 'Y' || $ans == 'yes' || $ans == 'Yes' ]]; then
    echo "Okay."

  elif [[ $ans == 'n' || $ans == 'N' || $ans == 'no' || $ans == 'No' ]]; then
    if [ -z "${DATABASE_URL}" ]; then
        echo "DATABASE_URL does not exist."

        echo -n "Please specify database for DATABASE_URL: "
        read ans

        if [ -z "${ans}" ]; then
          echo "DATABASE_URL cannot be empty."
          echo "Bad input. Quitting setup.sh."
          kill -INT $$
        else
          echo "Setting DATABASE_URL..."
          export DATABASE_URL="${ans}"
        fi

    else
      echo "Env variable DATABASE_URL exists."
      echo -n "Would you like to continue using DATABASE_URL="${DATABASE_URL}"? [y/n] "
      read ans

      if [[ $ans == 'y' || $ans == 'Y' || $ans == 'yes' || $ans == 'Yes' ]]; then
        echo "Okay."

      elif [[ $ans == 'n' || $ans == 'N' || $ans == 'no' || $ans == 'No' ]]; then
        echo -n "Please specify database for DATABASE_URL: "
        read ans

        if [ -z "${ans}" ]; then
          echo "DATABASE_URL cannot be empty."
          echo "Bad input. Quitting setup.sh."
          kill -INT $$
        else
          echo "Saving former DATABASE_URL value under DATABASE_URL_PREV..."
          export DATABASE_URL_PREV="${DATABASE_URL}"

          echo "Setting DATABASE_URL..."
          export DATABASE_URL="${ans}"
        fi

      else
        echo "Bad input. Quitting setup.sh."
        kill -INT $$
      fi
    fi

  else
    echo "Bad input. Quitting setup.sh."
    kill -INT $$
  fi

# app.db not detected
else

  echo "File 'app.db' not detected in current directory."
  echo -n "Would you like to create an SQLite database in the current directory? [y/n] "
  read ans

  if [[ $ans == 'y' || $ans == 'Y' || $ans == 'yes' || $ans == 'Yes' ]]; then
    if [ ! -z "${DATABASE_URL}" ]; then
        echo "DATABASE_URL exists."

        echo "Saving former DATABASE_URL value under DATABASE_URL_PREV..."
        export DATABASE_URL_PREV="${DATABASE_URL}"

        echo "Unsetting DATABASE_URL..."
        unset DATABASE_URL
    fi

    echo "Creating 'app.db' file in current directory..."
    touch app.db

  elif [[ $ans == 'n' || $ans == 'N' || $ans == 'no' || $ans == 'No' ]]; then
    if [ -z "${DATABASE_URL}" ]; then
        echo "DATABASE_URL does not exist."

        echo -n "Please specify database for DATABASE_URL: "
        read ans

        if [ -z "${ans}" ]; then
          echo "DATABASE_URL cannot be empty."
          echo "Bad input. Quitting setup.sh."
          kill -INT $$
        else
          echo "Setting DATABASE_URL..."
          export DATABASE_URL="${ans}"
        fi

    else
      echo "Env variable DATABASE_URL exists."
      echo -n "Would you like to continue using DATABASE_URL="${DATABASE_URL}"? [y/n] "
      read ans

      if [[ $ans == 'y' || $ans == 'Y' || $ans == 'yes' || $ans == 'Yes' ]]; then
        echo "Okay."

      elif [[ $ans == 'n' || $ans == 'N' || $ans == 'no' || $ans == 'No' ]]; then
        echo -n "Please specify database for DATABASE_URL: "
        read ans

        if [ -z "${ans}" ]; then
          echo "DATABASE_URL cannot be empty."
          echo "Bad input. Quitting setup.sh."
          kill -INT $$
        else
          echo "Saving former DATABASE_URL value under DATABASE_URL_PREV..."
          export DATABASE_URL_PREV="${DATABASE_URL}"

          echo "Setting DATABASE_URL..."
          export DATABASE_URL="${ans}"
        fi

      else
        echo "Bad input. Quitting setup.sh."
        kill -INT $$
      fi
    fi

  else
    echo "Bad input. Quitting setup.sh."
    kill -INT $$
  fi

fi

echo "Database setup complete!"
echo "Don't forget to populate the database by running './scripts/film_data.py."


echo "Don't forget to set your API and secret keys!"
echo -n "Would you like to enter them now? [y/n]: "
read ans
if [[ $ans == 'y' ]]; then
  echo "Hint: For your secret key, try using Python's secret.token_bytes."

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
