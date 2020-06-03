import os
import time
import json
import requests
from textwrap import dedent

# Get API key info
# N.B. Use app.config['TMDB_KEY'] to set key below once class has been set up
# from cinescout import app

class Movie:
    def __init__(self, id=None, title=None, release_year=None,
                 release_date=None, overview=None, runtime=None):
                 self.id = id
                 self.title = title
                 self.year = title
                 self.release_year = release_year
                 self.release_date = release_date
                 self.overview = overview
                 self.runtime = runtime


    @classmethod
    def get_movie_list_by_title(cls, title):
        """Returns list of movies."""
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
        pass


class TmdbMovie(Movie):

    # API info salient to getting data
    api_key = os.getenv('TMDB_API_KEY')
    poster_base_url = "http://image.tmdb.org/t/p/"
    poster_size = "w300"
    delay = 1

    def __init__(self, id=None, title=None, release_year=None,
                 release_date=None, overview=None, runtime=None,
                 poster_full_url=None):

        Movie.__init__(self, id, title, release_year, release_date,
                        overview, runtime)


        self.poster_full_url = poster_full_url


    @classmethod
    def get_movie_list_by_title(cls, title):
        """Returns list of movies."""
        # Get JSON response from New York Times
        res = requests.get("https://api.themoviedb.org/3/search/movie",
                            params={"api_key": cls.api_key, "query": title.strip()})

        tmdb_data = res.json()

        if tmdb_data["total_results"] == 0:
            return "<em> TMDB: No results matching that query. </em>"

        if tmdb_data["total_results"] >= 1:
            # Get results for each movie
            movies = tmdb_data["results"]

        return movies


    @classmethod
    def get_movie_info_by_id(cls, id):
        """Get info from TMDB API to create instance.

        Args:
            id: Integer representing TMDB movie id.

        Returns:
            result: A dictionary with three fields
                success: True or False, depending on wheter movie found.
                status_code: Status code of Http response
                movie: Movie object with all salient fields filled-in, or None
                       if method could not get data.
        """
        # Setup return value
        result = {'success': True, 'status_code': 200, 'movie': None}

        # Get movie info TMDB database
        res = requests.get(f"https://api.themoviedb.org/3/movie/{id}",
                            params={"api_key": cls.api_key})

        # Check whether movie found
        if res.status_code != 200:
            result['success'] = False
            result['status_code'] = res.status_code
        else:
            # Deserialize JSON response object
            tmdb_movie_data = res.json()

            # Get year movie was released
            release_year = int(tmdb_movie_data['release_date'].split('-')[0].strip()) or None

            # Build full url for movie poster
            poster_full_url = None
            if tmdb_movie_data['poster_path']:
                poster_full_url = cls.poster_base_url + cls.poster_size + tmdb_movie_data['poster_path']

            movie = cls(id=id, title=tmdb_movie_data['title'],
                        release_year = release_year,
                        release_date=tmdb_movie_data['release_date'],
                        overview=tmdb_movie_data['overview'],
                        runtime=tmdb_movie_data['runtime'],
                        poster_full_url=poster_full_url)

            result['movie'] = movie


        return result



class MovieReview:

    def __init__(self, title=None, year=None, text=None):
        self.title = title
        self.year = year
        self.text = text


    @classmethod
    def get_review_by_title_and_year(cls, title, year):
        pass

    def __str__(self):
        return f"'{self.title}' ({self.year}): {self.text}"



class NytMovieReview(MovieReview):

    api_key = os.getenv('NYT_API_KEY')
    delay = 3

    def __init__(self, title=None, year=None, text=None, critics_pick=None):
        MovieReview.__init__(self, title, year, text)
        self.critics_pick = critics_pick


    @classmethod
    def get_review_by_title_and_year(cls, title, year):
        # Setup return value
        result = {'success': True,
                  'status_code': 200,
                  'message': None,
                  'review': None}

        # Get review info from NYT
    	# Flag in case NYT review info already found
        nyt_review_already_found = False

        print(f"RELEASE YEAR = {year}")

        opening_date_start = f"{year}-01-01"
        opening_date_end = f"{year}-12-31"

        res = requests.get("https://api.nytimes.com/svc/movies/v2/reviews/search.json",
                                params={"api-key": cls.api_key,
                                        "opening-date": f"{opening_date_start};{opening_date_end}",
                                        "query": title.strip()})

        if res.status_code != 200:
            result['success'] = False
            result['status_code'] = res.status_code
            return result

        # Unpack review data
        nyt_data = res.json()

        # Check whether a review was written for a movie. Watch out for special cases.
        if nyt_data["num_results"] == 0:
            print("No NYT review found☹️")

            nyt_status = "No review found."
            nyt_critics_pick = "N/A"
            nyt_summary_short = "N/A"

            # Check case where year in NYT db and TMBD don't match.
            print("Checking to see whether release year in TMDB and NYT don't match....")

            print(f"Delaying next NYT API call by {NYT_API_DELAY} seconds...")
            time.sleep(cls.delay)

            print("Making second request to NYT with TMDB release year unspecified...")
            res = requests.get("https://api.nytimes.com/svc/movies/v2/reviews/search.json",
                                    params={"api-key": cls.api_key,
                                            "query": title.strip()})

            if res.status_code != 200:
                result['success'] = False
                result['status_code'] = res.status_code
                return result

            print("Request successful. Counting number of reviews returned...")
            nyt_data = res.json()

            if nyt_data["num_results"] == 0:
                print("There are really no reviews for this movie. Sorry😭")

            if nyt_data["num_results"] == 1:
                print("One review found. Hopefully this is it🙏🏻!")

            if nyt_data["num_results"] > 1:
                print("More than one review found🤔")
                print("Using heuristic that NYT reviewed film at closest date AFTER TMDB's release date....")

                print("Analyzing NYT review results...")

                # Get critics pick data and summary short for review that has years closest to TMDBs
                years = []

                for result in nyt_data['results']:
                    # Extract year
                    print("Extacting NYT release or publcation year...", end="")
                    nyt_date = result['opening_date'] if result['opening_date'] else result['publication_date']
                    nyt_year = nyt_date.split('-')[0].strip()
                    print(nyt_year)

                    years.append(nyt_year)

                print("Getting NYT year closest to TMDB year...", end="")
                shortlist = []

                for year in years:
                    diff = int(year) - int(release_year)
                    if diff > 0:
                        shortlist.append(diff)

                result_index = shortlist.index(min(shortlist))
                print(years[result_index])

                print("Getting review information. Hopefully right review picked🙏!")
                nyt_critics_pick = nyt_data['results'][result_index]['critics_pick']
                nyt_summary_short = nyt_data['results'][result_index]['summary_short']

                # So we don't overwrite the found review results with the logic below
                nyt_review_already_found = True


        if nyt_data["num_results"] > 1 and not nyt_review_already_found:

            nyt_status = "ERROR: More than one review found. Unable to choose."
            nyt_critics_pick = "N/A"
            nyt_summary_short = "N/A"
            result['success'] = False

        if  nyt_data["num_results"] == 1:
            nyt_status = "OK"
            nyt_critics_pick = nyt_data['results'][0]['critics_pick']
            nyt_summary_short = nyt_data['results'][0]['summary_short']

            if nyt_summary_short is not None:
                if nyt_summary_short.strip() == "":
                    nyt_summary_short = "No summary review provided."


        print(f"NYT_STATUS: {nyt_status}")

        # Build review object
        review = cls(title=title, year=year, text=nyt_summary_short, critics_pick=nyt_critics_pick)
        result['message'] = nyt_status
        result['review'] = review

        return result




if __name__ == "__main__":
    # movie = TmdbMovie(123, "Cat Game", "1992", "1992-03-07", "Cat chases mouse.",
    #                 "107", "/csrw/01")
    # print(movie)
    # print(movie.poster_full_url)
    result = TmdbMovie.get_movie_info_by_id(id=88)
    print(result['movie'])

    result = NytMovieReview.get_review_by_title_and_year(title="Dirty Dancing", year="1987")
    print(result['review'])
