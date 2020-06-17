import os
import time
import json
from datetime import datetime

import requests
from textwrap import dedent

from fuzzywuzzy import fuzz

# Get API key info
# N.B. Use app.config['TMDB_KEY'] to set key below once class has been set up
# from cinescout import app

class Person:
    """Class representing a person in the film industry.

    Attributes:
        id: Integer representing person in external database.
        name: String representing person's name
        known_for: what the person is best known for in the movie industry.
    """
    def __init__(self, id, name, known_for):
        self.id = id
        self.name = name
        self.known_for = known_for

    def __str__(self):
        return f"name: {self.name}, id: {self.id}, known_for: {self.known_for}"


class Movie:
    """Class representing a film.

    Attributes:
        id: Integer representing movie in external database.
        title: String representing film's title.
        release_year: Integer representing year movie released.
        release_date: String representing date movie released.
        overview: String containing summary of movie's premise.
        runtime: Integer representing runtime of movie in minutes.
    """
    def __init__(self, id=None, title=None, release_year=None,
                 release_date=None, overview=None, runtime=None):
                 self.id = id
                 self.title = title
                 self.release_year = release_year
                 self.release_date = release_date
                 self.overview = overview
                 self.runtime = runtime


    @classmethod
    def get_movie_list_by_title(cls, title):
        """Returns data structure containing list of movies and extra
        metadata if needed.
        """
        pass

    @classmethod
    def get_movie_list_by_person_id(cls, person_id):
        """Returns data structure containing list of movies and metadata
        based on id of person in external database.
        """
        pass

    @classmethod
    def get_person_list_by_name_known_for(cls, name, known_for):
        """Returns data structure containing list of people and metadata
        based on person's name and field they have worked in in the movie
        industry.
        """
        pass

    @classmethod
    def get_movie_info_by_id(cls, id):
        """Builds Movie object with id to search external api db."""
        pass

    def __str__(self):
        return dedent(f"""
        api-db id = {self.id}
        title = '{self.title}'
        release year = {self.release_year}
        release date = {self.release_date}
        overview = {self.overview} runtime = {self.runtime} min.""")

    def __repr__(self):
        return dedent(f"""
        api-db id = {self.id}
        title = '{self.title}'
        release year = {self.release_year}
        release date = {self.release_date}
        overview = {self.overview} runtime = {self.runtime} min.""")


class TmdbMovie(Movie):
    """Class representing a film, with data from tmdb.org.

    Class Attributes:
        api_key: String representing API key required to access tmdb's API.
        poster_base_url: String representing prefix url to access images of
                        movie posters.
        poster_size: String representing size of poster image.
        delay: Integer representing delay before calling tmdb api.
        imdb_base_url: String representing prefix url to access IMDB movie
                       page.

    Attributes:
        id: Integer representing movie in external database.
        title: String representing film's title.
        release_year: Integer representing year movie released.
        release_date: String representing date movie released.
        overview: String containing summary of movie's premise.
        runtime: Integer representing runtime of movie in minutes.
        poster_full_url: String representing complete url to access image of
                         a movie's poster should it exist.
        imdb_full_url: String representing complete url to access IMDB movie
                       page, should it exist.
    """
    # Class attributes
    api_key = os.getenv('TMDB_API_KEY')
    poster_base_url = "http://image.tmdb.org/t/p/"
    poster_size = "w300"
    delay = 1
    imdb_base_url = "https://www.imdb.com/title/"

    def __init__(self, id=None, title=None, release_year=None,
                 release_date=None, overview=None, runtime=None,
                 poster_full_url=None, imdb_full_url=None):
        Movie.__init__(self, id, title, release_year, release_date,
                        overview, runtime)
        self.poster_full_url = poster_full_url
        self.imdb_full_url = imdb_full_url

    @classmethod
    def get_movie_list_by_title(cls, title):
        """Returns dictionary containing list of movies and metadata.

        Args:
            title: String representing movie's title.

        Returns:
            result: Dictionary containing three fields.
                success: Boolean to whether movies found based on given title.
                status code: Http response code of tmdb API call.
                movies: List of Movie objects; None if no API data found.
        """

        # Setup return value
        result = {'success': True, 'status_code': 200, 'movies': None}

        # Make API call
        print(f"Calling tmdb API...", end="")
        res = requests.get("https://api.themoviedb.org/3/search/movie",
                            params={"api_key": cls.api_key,
                                    "query": title.strip()})

        # Check response status; check whether movie found
        if res.status_code != 200:
            print("FAILED!")
            result['success'] = False
            result['status_code'] = res.status_code
            result['movies'] = None
            return result

        print("SUCCESS!")
        tmdb_data = res.json()

        # No dice.
        if tmdb_data["total_results"] == 0:
            print(f"No movies found for movie titled '{title}'😭")
            result['success'] = False
            result['movies'] = None
            return result

        # Movies found!
        if tmdb_data["total_results"] >= 1:
            print("Movies found!")
            movies = []

            # Process tmdb data to create Movie objects. Add them to list.
            for movie in tmdb_data["results"]:
                release_date = movie.get('release_date')

                if movie.get('release_date') == None or movie.get('release_date') == '':
                    release_date = '0001-01-01'

                movie = Movie(id=movie.get('id'),
                              title=movie.get('title'),
                              overview=movie.get('overview'),
                              release_date=release_date)

                movies.append(movie)

            # Sort movies by release date, descending order
            movies.sort(key=lambda x: datetime.strptime(x.release_date, '%Y-%m-%d'),
                     reverse=True)

            # Ready to send!
            result['movies'] = movies
            return result


    @classmethod
    def get_person_list_by_name_known_for(cls, name, known_for):
        """Returns data structure containing list of people and metadata
        based on person's name and field they have worked in in the movie
        industry.

        Args:
            name: String object representing person's name.
            known_for: String object representing person's occupation.

        Returns:
            result: A dictionary with three fields:
                success: True or False, depending on wheter movie found.
                status_code: Status code of Http response of api call.
                persons: List of Person objects; None if api call
                         returns nothing/could not get data.
        """

        # Setup return value
        result = {'success': True, 'status_code': 200, 'persons':[]}

        # Get people data from TMDB
        print(f"Requesting person data from TMDB api for '{name}', '{known_for}'...",
              end="")
        res = requests.get("https://api.themoviedb.org/3/search/person",
                            params={"api_key": cls.api_key,
                                    "query": name.strip()})

        # Check response status
        # Check whether movie found
        if res.status_code != 200:
            print(f"FAILED! status_code={res.status_code}")
            result['success'] = False
            result['status_code'] = res.status_code
            result['persons'] = None
            return result

        print("SUCCESS!")
        print("Extracting person data from from TMDB JSON response....")

        # Deserialize JSON response object
        tmdb_persons_data = res.json()

        print(f"Number of tmdb person results found: {tmdb_persons_data['total_results']}")

        if tmdb_persons_data["total_results"] == 0:
            print(f"No results found for '{name}', '{known_for}'.")
            result['success'] = False
            result['persons'] = None
            return result

        # Load persons data into Person objects and append them to list
        persons = []

        # Create Person object for all TMDB results or just those working
        # in specified field.
        print("Building person list...")
        if known_for == 'All':
            # Add everyone.
            for person_data in tmdb_persons_data['results']:
                person = Person(id=person_data['id'],
                                name=person_data['name'],
                                known_for=person_data['known_for_department'])
                persons.append(person)
        else:
            # Add only those with matching work field.
            for person_data in tmdb_persons_data['results']:
                if person_data['known_for_department'] == known_for:
                    person = Person(id=person_data['id'],
                                    name=person_data['name'],
                                    known_for=person_data['known_for_department'])
                    persons.append(person)

        result['persons'] = persons

        return result


    @classmethod
    def get_movie_list_by_person_id(cls, person_id):
        """Returns data structure containing list of movies and metadata
        based on id of person in external database.

        Args:
            person_id: Integer representing id of person in TMDB database.

        Returns:
            result: A dictionary with four fields fields:
                success: True or False, depending on wheter person found.
                status_code: Status code of Http response of api call.
                cast: List of movies which given person acted in. Each entry
                      is a dictionary referring to Movie object and character
                      name (string). Returns empty list if no roles found.
                crew: List of movies which given person worked in some
                      acting capacity. Each entry is a dictionary referring to
                      Movie object and job title (string).
                      Returns empty list if no such jobs are found.
        """
        # Setup return value
        result = {'success': True, 'status_code': 200, 'cast':[], 'crew':[]}

        # Get person data from TMDB
        print(f"Requesting person data from TMDB api with person_id={person_id}...",
                end="")
        res = requests.get(f"https://api.themoviedb.org/3/person/{person_id}/movie_credits",
                            params={"api_key": cls.api_key})

        # Check response status
        # Check whether movie found
        if res.status_code != 200:
            print(f"FAILED! status_code={res.status_code}")
            result['success'] = False
            result['status_code'] = res.status_code
            result['movies'] = None
            return result

        print("SUCCESS!")
        print("Extracting movie credits for person from TMDB JSON response....")

        # Deserialize JSON response object
        tmdb_filmography_data = res.json()

        # Get movies where person was in the film
        print("Building movie list...")
        cast = []
        for movie_credit in tmdb_filmography_data['cast']:
            release_date = movie_credit.get('release_date')

            # Put in placeholder release date if none found in TMDB data.
            # Useful for sorting later on.
            if movie_credit.get('release_date') == None or movie_credit.get('release_date') == '':
                release_date = '0001-01-01'

            movie = Movie(id=movie_credit.get('id'),
                          title=movie_credit.get('title'),
                          release_date=release_date)

            # Add name of character portrayed in film.
            character = movie_credit.get('character')
            cast.append({'movie': movie, 'character': character})

        # Sort movies by release date, descending order
        cast.sort(key=lambda x: datetime.strptime(x['movie'].release_date, '%Y-%m-%d'),
                 reverse=True)

        result['cast'] = cast

        # Get movies where person was part of the crew.
        crew = []
        for movie_credit in tmdb_filmography_data['crew']:
            release_date = movie_credit.get('release_date')

            # Put in placeholder release date if none found in TMDB data.
            # Useful for sorting later on.
            if movie_credit.get('release_date') == None or movie_credit.get('release_date') == '':
                release_date = '0001-01-01'

            movie = Movie(id=movie_credit.get('id'),
                          title=movie_credit.get('title'),
                          release_date=release_date)

            # Add person's job associated with film.
            job = movie_credit.get('job')
            crew.append({'movie': movie, 'job': job})

        crew.sort(key=lambda x: datetime.strptime(x['movie'].release_date, '%Y-%m-%d'),
                 reverse=True)

        # A person may have had several jobs on a film (e.g. Director/Producer)
        # To avoid having Movie objects for the same film but different jobs,
        # search duplicate movies, combine jobs into single object and
        # delete the duplicates.

        # Index of film in crew list being looked at.
        curr = 0
        # Index of film in crew list that is being compared with film at curr.
        next = curr + 1

        # Carry out search, merge and deletion of duplicate data.
        while curr < len(crew) and next < len(crew):
            # In a sorted list, two movies with the same title are next
            # to each other.
            if crew[curr]['movie'].title != crew[next]['movie'].title:
                curr += 1
                next = curr + 1
            else:
                # Add job name from duplicate to original.
                crew[curr]['job'] += ", " + crew[next]['job']

                # Delete the duplicate.
                del crew[next]

        result['crew'] = crew

        return result

    @classmethod
    def get_movie_info_by_id(cls, id):
        """Returns data structure contiaining Movie object and metadata based
        on movie id.

        Args:
            id: Integer representing a movie in TMDB database.

        Returns:
            result: A dictionary with three fields
                success: True or False, depending on wheter movie found.
                status_code: Status code of Http response.
                movie: Movie object with all salient attributes filled-in;
                      None if api call returns no data.
        """
        # Setup return value
        result = {'success': True, 'status_code': 200, 'movie': None}

        # Get movie info TMDB database
        print(f"Requesting movie data from TMDB api with movie_id={id}...",
                end="")
        res = requests.get(f"https://api.themoviedb.org/3/movie/{id}",
                            params={"api_key": cls.api_key})

        # Check whether movie found
        if res.status_code != 200:
            print(f"FAILED! status_code={res.status_code}")
            result['success'] = False
            result['status_code'] = res.status_code
        else:
            print("SUCCESS!")

            # Deserialize JSON response object
            print("Extracting movie data from TMDB JSON response....")
            tmdb_movie_data = res.json()

            # Get year movie was released.
            if tmdb_movie_data.get('release_date'):
                release_year = int(tmdb_movie_data['release_date'].split('-')[0].strip())
            else:
                release_year = None

            # Build full url for movie poster.
            poster_full_url = None
            if tmdb_movie_data['poster_path']:
                poster_full_url = cls.poster_base_url + cls.poster_size + tmdb_movie_data['poster_path']

            # Build full url for IMDB
            imdb_full_url = None
            if tmdb_movie_data['imdb_id']:
                imdb_full_url = cls.imdb_base_url + tmdb_movie_data['imdb_id']

            print(imdb_full_url)


            print("Building Movie object...")
            movie = cls(id=id, title=tmdb_movie_data['title'],
                        release_year=release_year,
                        release_date=tmdb_movie_data.get('release_date'),
                        overview=tmdb_movie_data['overview'],
                        runtime=tmdb_movie_data['runtime'],
                        poster_full_url=poster_full_url,
                        imdb_full_url=imdb_full_url)

            result['movie'] = movie

        return result


class MovieReview:
    """Class representing a movie review.

    Attributes:
        title: Striing representing the title of movie reviewed.
        year: Integer representing the release year of the movie.
        text: String containing summary of movie review.
        publication_date: String representing date review was published.
    """


    def __init__(self, title=None, year=None, text=None, publication_date=None):
        self.title = title
        self.year = year
        self.text = text
        self.publication_date=publication_date


    @classmethod
    def get_review_by_title_and_year(cls, title, year):
        """Returns data structure containing review and metadata based on
        title of film and year film was released."""
        pass

    def __str__(self):
        return f"'{self.title}' ({self.year}): {self.text}"



class NytMovieReview(MovieReview):
    """Class representing a movie review from the New York Times.

    Class Attributes:
        api_key: String representing API key required to access NYT's API.
        delay: Integer representing delay before calling NYT api.

    Attributes:
        title: Striing representing the title of movie reviewed.
        year: Integer representing the release year of the movie.
        text: String containing summary of movie review.
        publication_date: String representing date review was published.
        critics_pick: Boolean representing whether movie is NYT critic's pick.
        threshold: Integer of [0, 100] representing the Levenshtein distance
                   ratio as a result of fuzzy string comparison.
    """

    # Class Attributes
    api_key = os.getenv('NYT_API_KEY')

    # Number of seconds to wait before making next call to NYT api
    delay = 3

    # Percentage the likelihood that two strings match per Levenshtein distance
    # ratio. An arbitrary value that seems reasnoable.
    threshold = 80

    def __init__(self, title=None, year=None, text=None, publication_date=None,
                critics_pick=None):
        MovieReview.__init__(self, title, year, text, publication_date)
        self.critics_pick = critics_pick

    @staticmethod
    def clean_review_text(review_text):
        """Removes unwanted characters that may appear in NYT review text

        Args:
            review_text: String representing text of movie review.

        Returns:
            cleaned_text: String representing text with offending characters
                          removed.
        """
        # Use intermediate variable for your cleaning.
        # If string is empty, don't bother doing anything.
        if review_text:
            temp_text = review_text.strip()
        else:
            return None

        # Remove &quot; characters from review text should they exist;
        # replace them with reqular quotes.
        temp_text = temp_text.replace('&quot;', '"')

        cleaned_text = temp_text
        return cleaned_text

    @classmethod
    def good_enough_match(cls, extdb_title, nyt_title):
        """Determines whether the movie titles from the external database and
        NYT review are similar enough to be considered equivalent.

        Args:
            extdb_title: String representing title of movie per external
            database.
            nyt_title: String representing title of movie per NYT movie review.

        Raises:
            ValueError: In the case where an empty string or None object passed.

        Return:
            True: if titles are similar enough to guess they refer to the same
                  film
            False: if title are not similar enough to guess they refer to the
                   same film.
        """
        if not extdb_title or not nyt_title:
            raise ValueError("Titles cannot be blank or None type.")

        ratio = fuzz.ratio(extdb_title.strip().lower(),
                           nyt_title.strip().lower())

        partial_ratio = fuzz.partial_ratio(extdb_title.strip().lower(),
                           nyt_title.strip().lower())

        print(f"Levenshtein similarity ratio, full = {ratio}")
        print(f"Levenshtein similarity ratio, partial = {partial_ratio}")

        if ratio >= cls.threshold or partial_ratio >= cls.threshold:
            return True
        else:
            return False

    @classmethod
    def get_review_by_title_and_year(cls, title, year):
        """Returns data structure containing NYT review summary and metadata
        based on title of film and year film was released."""

        # Setup return value.
        result = {'success': True,
                  'status_code': 200,
                  'message': None,
                  'review': None}

    	# Flag in case NYT review info already found
        nyt_review_already_found = False

        print(f"Starting process to get review for '{title}, {year}' via NYT api...")

        # The dates on which a movie is released and reviewed likely differ.
        # Most movies will have been reviewed in the same year they were
        # released, however.
        opening_date_start = f"{year}-01-01"
        opening_date_end = f"{year}-12-31"

        print("Making request to NYT Movie Review API...", end="")
        res = requests.get("https://api.nytimes.com/svc/movies/v2/reviews/search.json",
                                params={"api-key": cls.api_key,
                                        "opening-date": f"{opening_date_start};{opening_date_end}",
                                        "query": title.strip()})

        if res.status_code != 200:
            print(f"FAILED! Http response status code = {res.status_code}")
            result['success'] = False
            result['status_code'] = res.status_code
            return result

        print("SUCCESS!")

        # Unpack review data
        nyt_data = res.json()

        print("Analyzing NYT review response data...")

        # Check whether a review was written for a movie. Watch out for special cases.
        if nyt_data["num_results"] == 0:

            print("No NYT review found for given movie title and year☹️")

            nyt_status = "No review found."
            nyt_critics_pick = "No review found."
            nyt_summary_short = "No review found."

            # Check case where movie year in NYT db and movie's release year
            # don't match. This happens somewhat frequently as a lot of films
            # shown at festivals before having a general release.
            print("Checking to see whether given release year and NYT year don't match....")

            # You don't want to call the NYT api too fast a second time or the
            # app might get blocked from using it.
            print(f"Delaying next NYT API call by {cls.delay} seconds...")
            time.sleep(cls.delay)

            print("Making second request to NYT API with given release year unspecified...", end="")
            res = requests.get("https://api.nytimes.com/svc/movies/v2/reviews/search.json",
                                    params={"api-key": cls.api_key,
                                            "query": title.strip()})

            if res.status_code != 200:
                print(f"FAILED! Http response status code = {res.status_code}")
                result['success'] = False
                result['status_code'] = res.status_code
                return result

            print("SUCCESS!")
            print("Counting number of reviews returned...")
            nyt_data = res.json()

            # If the title of a movie on its own doesn't return a single
            # result, it probably wasn't reviewed by the NYT.
            if nyt_data["num_results"] == 0:
                print("There are really no reviews for this movie. Sorry😭")
                result['success'] = False
                result['status_code'] = res.status_code
                result['message'] = "No reviews found."
                return result

            # One review found, but is it the one the you want? It could
            # be a title with similar keywords, or a remake of the film.
            if nyt_data["num_results"] == 1:
                print("One review found.")
                print("Beginning verification process...")

                # Test # 1: Look at the movie's release year and publication
                # year. Since it is reasonable to assume that a movie
                # can only have been reviewed after its release, then any
                # review in which the publication year is greater than the
                # release year, can't be the one we want. Conversely, we
                # can only hope that the review is the right one if the review
                # year comes after the publishing year.
                print("Extacting NYT release or publcation year...", end="")

                if nyt_data['results'][0].get('opening_date'):
                    nyt_date = nyt_data['results'][0].get('opening_date')
                else:
                    nyt_date = nyt_data['results'][0].get('publication_date')

                nyt_year = nyt_date.split('-')[0].strip()

                print(nyt_year)

                print(f"Comparing given and NYT release years...{year} vs. {nyt_year}")

                if year > int(nyt_year):
                    print("Film cannot have been reviewed prior to its release.")
                    print("There are really no reviews for this movie. Sorry😭")
                    result['success'] = False
                    result['status_code'] = res.status_code
                    result['message'] = "No review found for this film."
                    return result

                # Title of movie reviewed by NYT.
                nyt_title = nyt_data['results'][0].get('display_title').strip()

                # Test #2: The titles in the review and of the sought movie
                # should either be an exact match or good enough, i.e.
                # meets or surpasses fuzzy search threshold
                print(f"Doing fuzzy string comparison of given title with NYT title: {title} vs {nyt_title}")

                good_enough = cls.good_enough_match(title.strip().lower(),
                                                    nyt_title.strip().lower())

                print(f"Good enough? {good_enough}.")

                if not good_enough:
                    print("Given movie title and NYT movie title do not match.")
                    print("There are really no reviews for this movie. Sorry😭")
                    result['success'] = False
                    result['status_code'] = res.status_code
                    result['message'] = "No review found for this film."
                    return result

                # If both tests passed, accept the review, but add a warning
                # that it might not match the movie sought for.
                print("Heuristic verification complete.")
                print("There is no way to be sure whether this " \
                        "is really the review for the movie.")
                print("Appending warning to review....")

                nyt_status = "WARNING"
                nyt_critics_pick = nyt_data['results'][0]['critics_pick']
                nyt_summary_short = nyt_data['results'][0]['summary_short']

                # In case NYT has the movie in its db, but didn't write
                # a review summary for it.
                if nyt_summary_short is not None:
                    if nyt_summary_short.strip() == "":
                        nyt_summary_short = "No summary review provided."

                print(f"NYT_STATUS: {nyt_status}")

                # Build review object
                review = cls(title=title, year=year,
                             text=cls.clean_review_text(nyt_summary_short),
                             publication_date=nyt_data['results'][0].get('publication_date'),
                             critics_pick=nyt_critics_pick)
                result['message'] = nyt_status
                result['review'] = review

                return result

            # Multiple reviews retrieved. This is likely to happen since
            # searching just by movie title broadens the search considerably.
            if nyt_data["num_results"] > 1:
                print("Multiple reviews found🤔")
                print(f"Qty: {nyt_data['num_results']}")

                # To determine which review of the several might be the right
                # one, pick the review published the soonest after the film
                # was released. No guarantee, but better than nothing.
                print("Using heuristic that the  NYT review  that was " \
                      "closest to the film's release date is likey the review " \
                      "sought after.")
                print("Analyzing NYT review results...")

                # List of years each review was published.
                nyt_years = []

                for movie_result in nyt_data['results']:
                    # Extract year
                    print("Extacting NYT release or publcation year...", end="")
                    nyt_date = movie_result['opening_date'] if movie_result['opening_date'] else movie_result['publication_date']
                    nyt_year = nyt_date.split('-')[0].strip()
                    print(nyt_year)
                    nyt_years.append(nyt_year)

                print("Getting NYT year closest to movie release year...",
                      end="")

                # Some reviews are dated after the movie's release date.
                # These should excluded as viable contenders.
                shortlist = []

                for review_year in nyt_years:
                    diff = int(review_year) - int(year)
                    if diff > 0:
                        shortlist.append(diff)

                # Pick the closest year.
                if shortlist:
                    result_index = shortlist.index(min(shortlist))
                    print(nyt_years[result_index])
                else:
                    print("FAILED!")
                    print("All reviews made prior to release year of film.")
                    print("There are really no reviews for this movie. Sorry😭")
                    result['success'] = False
                    result['status_code'] = res.status_code
                    result['message'] = "No review found for this film."
                    return result

                # There is slight risk that this might not be the right review...
                print("Getting review information. Hopefully right review picked🙏!")

                nyt_critics_pick = nyt_data['results'][result_index]['critics_pick']
                nyt_summary_short = nyt_data['results'][result_index]['summary_short']

                # So we don't overwrite the found review results with the logic below.
                nyt_review_already_found = True

                # In case NYT has the movie in its db, but didn't write
                # a review summary for it.
                if nyt_summary_short is not None:
                    if nyt_summary_short.strip() == "":
                        nyt_summary_short = "No summary review provided."

                # Accept as a valid review. If you want to warn the user that
                # this might be the wrong review, change status to "WARNING".
                nyt_status = "OK"
                print(f"NYT_STATUS: {nyt_status}")

                # Build review object
                review = cls(title=title, year=year,
                             text=cls.clean_review_text(nyt_summary_short),
                             publication_date=nyt_data['results'][result_index].get('publication_date'),
                             critics_pick=nyt_critics_pick)
                result['message'] = nyt_status
                result['review'] = review

                return result


        # More than one movie with same title in the same year!
        # e.g. Black Rain (Japanese film vs Michael Douglas film)
        if nyt_data["num_results"] > 1 and not nyt_review_already_found:

            print("More than one NYT review for found given movie title and year!")

            # Try looking for exact title in results.

            # Try to zero-in on right review by comparing titles.

            print("Comparing title of movie in review with given title...")
            for index, movie in enumerate(nyt_data['results']):

                if movie['display_title'].strip().lower() == title.strip().lower():
                    print("Match found! Extracting review data...")

                    nyt_status = "OK"
                    nyt_critics_pick = nyt_data['results'][index]['critics_pick']
                    nyt_summary_short = nyt_data['results'][index]['summary_short']

                    if nyt_summary_short is not None:
                        if nyt_summary_short.strip() == "":
                            nyt_summary_short = "No summary review provided."

                    nyt_review_already_found = True

                    break

            # Unable to tell which review is the right one.
            if not nyt_review_already_found:
                nyt_status = "More than one review found in same year with no exact name match. Unable to choose review."
                nyt_critics_pick = "No review found."
                nyt_summary_short = "No review found."
                result['success'] = False


        # Exact match with title and release year. Ideal scenario.
        if  nyt_data["num_results"] == 1:
            print("NYT review found for given title and release year on first shot😆")

            nyt_status = "OK"
            nyt_critics_pick = nyt_data['results'][0]['critics_pick']
            nyt_summary_short = nyt_data['results'][0]['summary_short']

            if nyt_summary_short is not None:
                if nyt_summary_short.strip() == "":
                    nyt_summary_short = "No summary review provided."


        print(f"NYT_STATUS: {nyt_status}")

        # Build review object
        review = cls(title=title, year=year,
                     text=cls.clean_review_text(nyt_summary_short),
                     critics_pick=nyt_critics_pick,
                     publication_date=nyt_data['results'][0].get('publication_date'))
        result['message'] = nyt_status
        result['review'] = review

        return result


if __name__ == "__main__":
    # Placeholder main section to play around with classes if desired.
    pass
