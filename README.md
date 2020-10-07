# Cinescout🎞 (v1.1.1)

`Cinescout` is a Flask-based, mobile-responsive, web tool that allows you to learn
more about almost any film or person in the world of cinema.

With `Cinescout` you can:
- Read a brief synopsis of a film from [The Movie Database](https://www.themoviedb.org/), as well as a review summary from [The New York Times](https://nytimes.com).
- Discover the filmography of your favourite cast or crew member.
- Add movies to a personal list for later reference.
- Browse through a list of critically-acclaimed films from [The Criterion Collection](https://www.criterion.com/).

## Short History
`Cinescout`  came to be as my final project submission for Harvard
University's online cont-ed course, 'CS50W: Web Programming with Python and JavaScript.' As a movie buff, I wanted to create a tool that would help me find great movies.
I also liked working with APIs. Extracting data and functionality from
external systems excited me.

Although I received a passing grade for my project submission, `Cinescout, v0.1`,  I wanted to seriously improve the app before pushing its code to `github`.
So, I worked on it for a few more more weeks, and, eventually, `version 1.x` was
born.

## Demo and Video
You can try out `Cinescout` in its current state [here](https://dunnesquared.pythonanywhere.com).
You'll be able to search for films and crew members, but won't be able to create an account, maintain a movie list
or see NYT movie reviews. For security and maintainability reasons, I've made myself the gatekeeper and limited these features to registered users. See [README-LIVE](https://github.com/dunnesquared/cinescout/blob/master/README-LIVE.md) if you're curious to know more.

That said, you can get some idea of what these features look like by watching my Razzie-winning [screencast of `Cinescout v1.0`](https://vimeo.com/450192710). It's a bit out of date UI-wise, but you'll get the picture. 
I hear watching the video works wonders for insomnia :-p.

## APIs
`Cinescout` retrieves all movie data from two places: *The New York Times* (NYT)
and the *The Movie Database* (TMDB). Movie reviews are retrieved from the former;
general movie vitals from the latter.

API keys are required to access these resources. For security reasons
no keys are provided with this app: go to each website and get your
own.

## Python version
I wrote `Cinescout` using `Python 3.6.1`. Any version higher than that
until `Python 3.8.5` (the latest version from which `Cinescout` was run)
should be fine (I hope).

## External dependencies
This project depends on several external packages. Using these extensions
seemed like the best way to speed up development with well-tested, secure
code. Notable dependencies include

- `Bootstrap` for the styling the user-interface.
- `Flask-Login` to help users login/logout securely and manage session data.
- `Flask-Migrate` to help migrate changes to database models.
- `Flask-SqlAlchemy` to help create and manage the app's database.
- `Flask-WTF` to write secure web forms quickly.
- `Flask-Admin` to create a UI to administer the user logins, passwords and other database tasks.
- `requests` to interact the external APIs.
- `fuzzywuzzy` to determine how similar two movie titles are to each other.

## Running `Cinescout` on macOS, 'nix
1. Download or clone this project from `github`.
2. Create accounts and API keys at https://developer.nytimes.com and https://developers.themoviedb.org.
3. Containerize and activate the app in a virtual environment. `virtualenv` is good.
4. Download all external Python dependencies: `pip install -r requirements.txt`.
5. Create a secret key. Several Python packages depend on it. It's highly recommended you use a strong random key. See https://docs.python.org/3/library/secrets.html for more info on how to do this.
6. Ensure your console is in the project's root folder, i.e  the same level as `app.py`.
7.  Run `source setup.sh`. This script will save your keys as environment variables, as well as some Flask config settings. You'll also be prompted as to whether you want to create a local database file or use the one specified in DATABASE_URL, should it exist. If the latter, it's assumed you're setup to connect an external database (e.g. Postgres database on Heroku). Otherwise, a default `SQLite` database will be used.[^1]
8. Populate the database by running `python scripts/film_data.py`. The script creates two demo users: 'Alex' and 'Yoda'. The script prompts you to enter passwords for them.
9. Make sure you are **connected** to the Internet.
10. Type `flask run` into your Terminal and hit Enter.
11. Open a web browser and go to `http://127.0.0.1:5000/` to start using `Cinescout`!


## Running `Cinescout` on Windows
You can do all of the above, except, I suspect, running `setup.sh` (Step 7). That's okay: the script just automates a few simple tasks that can be done manually. It's helpful but not really necessary.

All other things being equal, here's what you need to do for the simplest setup on your machine:
1. Create an `app.db` file in the root of the project directory.
2. Enter your keys in whatever environment variable manager Windows uses.
3. Ditto for Flask environment variables. You can find the default values of those at the top of `setup.sh`.

Note that this assumes you're okay using the default SQLite database. I'll leave it up to you
if you want to use something else.
 
## Accessing the admin panel
1. After setting up `Cinescout` per the instructions above, run `flask shell`.
2. Create user `admin` via SQLAlchemy API calls. Please look up how to do this; as an admin you 
should know how. Please choose a strong password if you're making this project public in any way.
3. Go to `http://127.0.0.1:5000/admin` and login. 

## Files of note
To keep things straight, let's look at the contents of each folder in the project, beginning at the project's root.

### `/` (project root)
- `app.py`: Entry module for Flask to launch app.
- `config.py`: Module that ensures data required for app to run properly is there from the start.
- `setup.sh`: Bash script to help setup the project.
- `requirements.txt`: List of external Python modules `pip` downloads and installs.

### `/cinescout`
Project package containing all domain logic code. Files and folders include
- `__init__.py`: Makes parent folder into a Python package; intializes import app objects.   
- `errors.py`: Module that handles http errors and raised exceptions.
- `forms.py`: Module that implements logic to render and validate web forms for `Cinescout` features; uses Flask-WTF.
- `models.py`: Module that implements database table models via SQLAlchemy ORM.
- `movies.py`: Module containing business logic classes of `Cinescout` app: `Person`, `Movie`, `TmdbMovie`, `MovieReview` and `NytMovieReview`. The "heart" of the application, so to speak.
- `views.py`: Module containing functions (routes) representing the app's features and handles users' requests.
- `/static`: Contains CSS and JavaScript files.
  - `css/style.css`: CSS file for extra bits of styling on top of what Bootstrap provides.
  - `js/addremove.js`: JavaScript file that adds and removes films via AJAX requests to the server.
  - `js/removefromlist.js`: Javascript file that removes films from users' lists
- `/templates`: Contains all HTML-Jinja2 template files. All of these are self-explanatory. Please look at the folder's contents for more info.

### `/data`
Folder containing CSV files which in turn contain movie data.
- `criterion.csv`: Contains TMDB data of movies from [The Criterion Collection](https://criterion.com). Input file to `film_data.py` script.
- `films.csv`: Contains data of films from *The Criterion Collection*. Data copied from https://en.wikipedia.org/wiki/List_of_Criterion_Collection_releases and cleaned manually.  Input file to `tmdb_data.py` script.
- `found.csv`: Contains list of movies `tmdb_data.py` found on TMDB with harvested information. Output file of `tmdb_data.py` script. Data from this file manually copied to `criterion.csv`.
- `notfound.csv:`  Contains list of movies `tmdb_data.py` failed to find on TMDB. Output file of `tmdb_data.py` script.

### `/migrations`
Folder containing database migration scripts auto-generated with `Flask-Migrate` extension.

### `/scripts`
Folder containing scripts to scrape data and populate the database. To run successfully,
execute the scripts from the project's root directory.
- `film_data.py`: Script that populates database with data of Criterion Collection movies; sets up two demo users. You will need to enter passwords for these users. Uses `criterion.csv` as input file.
- `tmdb_data.py`: Script that requests movie data from TMDB api. Uses `films.csv` as input; outputs
to `found.csv` and `notfound.csv.` READ WARNING BELOW!

**WARNING!** Do not run `tmdb_data.py` at this moment! If you do, please do not overwrite the contents of `criterion.csv` with `found.csv`. Because some movie titles have commas in them I had to manually use another character to replace the commas so the titles would be accepted by `film_data.py`. If you run the `film_data.py` with an unedited `criterion.csv` as input, `film_data.py` will crash and your database will not be populated. I hope to find an elegant solution to this problem in a future version. In the case you've already gone ahead and run `tmdb_data.py` I've created `criterion_BACKUP.csv` should you need to restore `criterion.csv` to its desired state.

### `/tests`
Unit-testing package. Contains files to run `unittest` framework tests on app.
There are two test files: `test_views.py` and `test_movies.py`; `__init__.py`
and `context.py` make running these tests possible.

- `__init__.py`: Turns parent folder into a Python package.
- `context.py`: Ensures Python can find `Cinescout` modules and objects for test files.
- `test_view.py`: Performs unit test on functions in `views.py`.
- `test_movies.py`: Performs unit test on class methods in `movies.py`.
- `test.db`: SQLite database, mainly used by `test_views.py` script.

To execute the test scripts, run the following on the console:

```sh
python tests/test_views.py
python tests/test_movies.py
```

N.B. The script `test_movies.py` will take around four minutes to run as it
currently stands. Each call to the NYT API has to be delayed by six seconds
to prevent being locked out. Read 'HTTP Error 429: Too Many Requests' below.

## HTTP Error 429: Too Many Requests
If you use this app long enough, you'll eventually get a an HTTP response 429
error, aka Too Many Requests. This is almost certainly because the NYT only allows
for 10 requests per minute (Read https://developer.nytimes.com/faq#a11). As
searching for a review with `Cinescout` requires at least one NYT API call but as many four, it's quite easy to hit this ceiling if you're looking at one movie after another. The NYT recommends setting the delay between calls to six seconds, but I've set it to three, as that is as much as my patience can bear.


## Special Thanks
In addition to CS50W's illuminating lessons and solid instruction from Brian Yu,
I'd like to thank Miguel Gringberg for his helpful [tutorials](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) on how to set up a Flask-based Python project in a more professional manner than I would've otherwise done left to my own devices. A general thank you to all the authors of resources I used and learned from.

Finally, a special thanks to my partner for all her support and patience during the
several weeks it took me put together this app. It took me *way longer* than
I had originally thought.

## Feedback
Any positive or constructive feedback is welcome.