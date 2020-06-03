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
    def get_movie_list_by_title(cls):
        """Returns list of movies."""
        pass

    @classmethod
    def get_movie_info(cls):
        """Builds Movie object."""
        pass


    def __str__(self):
        return dedent(f"""
        api-db id = {self.id}
        title = '{self.title}'
        release year = {self.release_year}
        release date = {self.release_date}
        overview = {self.overview}
        runtime = {self.runtime} min.
        """)



class TmdbMovie(Movie):

    # API info salient to getting data
    api_key = os.getenv('TMDB_API_KEY')
    poster_base_url = "http://image.tmdb.org/t/p/"
    poster_size = "w300"
    delay = 1

    def __init__(self, id=None, title=None, release_year=None,
                 release_date=None, overview=None, runtime=None,
                 poster_rel_url=None):

        Movie.__init__(self, id, title, release_year, release_date,
                        overview, runtime)


        self.poster_rel_url = poster_rel_url


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
    def get_movie_info(cls):
        """Get info from TMDB API  to create instance."""
        pass






# movie_info = {
#     'tmdb_id': tmdb_id,
#     'title': tmdb_movie_data['title'],
#     'opening_date': tmdb_movie_data['release_date'],
#     'year': int(tmdb_movie_data['release_date'].split('-')[0].strip()),
#     'overview': tmdb_movie_data['overview'],
#     'poster_url_full': poster_url_full,
#     'nyt_critics_pick': nyt_critics_pick,
#     'nyt_summary_short': nyt_summary_short,
#     'on_user_list': on_user_list,
# }
#
#
# class MovieReview:
#     pass
#
#
# class NytMovieReview(MovieReview):
#     pass

if __name__ == "__main__":
    movie = TmdbMovie(123, "Cat Game", "1992", "1992-03-07", "Cat chases mouse.",
                    "107", "/csrw/01")
    print(movie)
    print(movie.poster_rel_url)
