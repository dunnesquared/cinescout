import os
import time
import json
from datetime import datetime

import requests
from textwrap import dedent

# Get API key info
# N.B. Use app.config['TMDB_KEY'] to set key below once class has been set up
# from cinescout import app

class Person:
    """Class representing a person in the film industry

    Attributes:
        id: Integer representing person in external database.
        name: String representing person's name
        known_for: what the person is best known for in the movie industry.
    """

    def __init__(self, id, name, known_for):
        self.id = id
        self.name = name
        self.known_for = known_for

    # def add_known_for(self, known_for):
    #     """Insert known_for person has worked in"""
    #     self.known_fors.append(known_for)
    #     print(self.known_fors)

    def __str__(self):
        return f"name: {self.name}, id: {self.id}, known_for: {self.known_for}"


class Movie:
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
        """Returns list of movies."""
        pass

    @classmethod
    def get_movie_list_by_person_id(cls, person_id):
        """Gets list of movies based on data in person object.

        Args:
            person_id: Integer representing id of person in external databse.

        Returns:
            movie_list: List of items where each item contains movie data.

        """
        pass

    @classmethod
    def get_person_list_by_name_category(cls, name, known_for):
        """Gets list of people based on person's name and known_for they have
        worked in in the movie industry

        Args:
            name: String object representing person's name.
            known_for: String object representing person's occupation.

        Returns:
            person_list: list of Person objects.
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
        """Returns list of movies based on title."""

        # Setup return value
        result = {'success': True, 'status_code': 200, 'movies': None}

        res = requests.get("https://api.themoviedb.org/3/search/movie",
                            params={"api_key": cls.api_key, "query": title.strip()})

        # Check response status
        # Check whether movie found
        if res.status_code != 200:
            result['success'] = False
            result['status_code'] = res.status_code
            result['movies'] = None
            return result

        tmdb_data = res.json()

        if tmdb_data["total_results"] == 0:
            result['success'] = False
            result['movies'] = None
            return result

        if tmdb_data["total_results"] >= 1:
            movies = []

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

            # Ready to send
            result['movies'] = movies
            return result
            

    @classmethod
    def get_person_list_by_name_known_for(cls, name, known_for):
        """Gets list of people based on person's name and known_for they have
        worked in in the movie industry

        Args:
            name: String object representing person's name.
            known_for: String object representing person's occupation.

        Returns:
            result:  A dictionary with three known_fors
                success: True or False, depending on wheter movie found.
                status_code: Status code of Http response
                persons: List of Person objects; None if api call
                returns nothing/could not get data.
        """

        # Setup return value
        result = {'success': True, 'status_code': 200, 'persons':[]}

        # Get persons data from TMDB
        res = requests.get("https://api.themoviedb.org/3/search/person",
                            params={"api_key": cls.api_key,
                                    "query": name.strip()})

        # Check response status
        # Check whether movie found
        if res.status_code != 200:
            result['success'] = False
            result['status_code'] = res.status_code
            result['persons'] = None
            return result

        print("Extracting Person Data from from TMDB JSON response....")

        # Deserialize JSON response object
        tmdb_persons_data = res.json()

        print(f"Number of tmdb person results found: {tmdb_persons_data['total_results']}")

        if tmdb_persons_data["total_results"] == 0:
            print(f"No data found for {name}, known for {known_for}.")
            result['success'] = False
            result['persons'] = None
            return result

        # Load persons data into Person objects and append them to list
        persons = []

        # Create Person object for all TMDB results or just those working
        # in specified field.
        if known_for == 'All':
            for person_data in tmdb_persons_data['results']:
                person = Person(id=person_data['id'],
                                name=person_data['name'],
                                known_for=person_data['known_for_department'])
                persons.append(person)
        else:
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
        # Setup return value
        result = {'success': True, 'status_code': 200, 'cast':[], 'crew':[]}

        # Get persons data from TMDB
        res = requests.get(f"https://api.themoviedb.org/3/person/{person_id}/movie_credits",
                            params={"api_key": cls.api_key})

        # Check response status
        # Check whether movie found
        if res.status_code != 200:
            result['success'] = False
            result['status_code'] = res.status_code
            result['movies'] = None
            return result

        print("Extracting movie credits from from TMDB JSON response....")

        # Deserialize JSON response object
        tmdb_filmography_data = res.json()

        # Get movies where person was in the film
        # count = 0
        cast = []
        for movie_credit in tmdb_filmography_data['cast']:

            release_date = movie_credit.get('release_date')

            if movie_credit.get('release_date') == None or movie_credit.get('release_date') == '':
                release_date = '0001-01-01'

            movie = Movie(id=movie_credit.get('id'),
                          title=movie_credit.get('title'),
                          release_date=release_date)


            character = movie_credit.get('character')
            cast.append({'movie': movie, 'character': character})

            # # Helpful for debugging purposes
            # print(f"\n{count}", end="")
            # print(movie)
            # print(f"Character: {character}")
            # count += 1

        # Sort movies by release date, descending order
        cast.sort(key=lambda x: datetime.strptime(x['movie'].release_date, '%Y-%m-%d'),
                 reverse=True)

        result['cast'] = cast

        # # debug
        # for elem in result['cast']:
        #     print(elem[0])
        #     print(elem[1])


        # Get movies where person was part of the crew

        crew = []
        # count = 0
        for movie_credit in tmdb_filmography_data['crew']:

            release_date = movie_credit.get('release_date')

            if movie_credit.get('release_date') == None or movie_credit.get('release_date') == '':
                release_date = '0001-01-01'

            movie = Movie(id=movie_credit.get('id'),
                          title=movie_credit.get('title'),
                          release_date=release_date)

            job = movie_credit.get('job')
            crew.append({'movie': movie, 'job': job})

            # # Helpful for debugging purposes
            # print(f"\n{count}", end="")
            # print(movie)
            # print(f"Job: {job}")
            # count += 1

        crew.sort(key=lambda x: datetime.strptime(x['movie'].release_date, '%Y-%m-%d'),
                 reverse=True)

        # Eliminate duplicate movies, but combine jobs
        curr = 0
        next = curr + 1

        while curr < len(crew) and next < len(crew):
            # # DEBUG
            # print(f"len={len(crew)}")
            # print(f'curr={curr}')
            # print(f'next={next}')

            # In a sorted list, two movies with the same title are next
            # to each other.
            if crew[curr]['movie'].title != crew[next]['movie'].title:
                curr += 1
                next = curr + 1
            else:
                # print(f"DUPLICATE! {crew[next]['movie'].title}")

                # Add job name from duplicate to original
                crew[curr]['job'] += ", " + crew[next]['job']

                # print(crew[curr].get('job'))

                # Delete the duplicate
                del crew[next]


        result['crew'] = crew

        # # debug
        # for elem in result['crew']:
        #     print(elem[0])
        #     print(elem[1])

        return result



        #return f"TMDB Booyah!! {person_id}"


    @classmethod
    def get_movie_info_by_id(cls, id):
        """Get info from TMDB API to create instance.

        Args:
            id: Integer representing TMDB movie id.

        Returns:
            result: A dictionary with three known_fors
                success: True or False, depending on wheter movie found.
                status_code: Status code of Http response
                movie: Movie object with all salient known_fors filled-in, or None
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
            if tmdb_movie_data.get('release_date'):
                release_year = int(tmdb_movie_data['release_date'].split('-')[0].strip())
            else:
                release_year = None

            # Build full url for movie poster
            poster_full_url = None
            if tmdb_movie_data['poster_path']:
                poster_full_url = cls.poster_base_url + cls.poster_size + tmdb_movie_data['poster_path']

            movie = cls(id=id, title=tmdb_movie_data['title'],
                        release_year=release_year,
                        release_date=tmdb_movie_data.get('release_date'),
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
            nyt_critics_pick = "No review found."
            nyt_summary_short = "No review found."

            # Check case where year in NYT db and TMBD don't match.
            print("Checking to see whether release year in TMDB and NYT don't match....")

            print(f"Delaying next NYT API call by {cls.delay} seconds...")
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

            # Try looking for exact title in results
            for index, movie in enumerate(nyt_data['results']):

                if movie['display_title'].strip().lower() == title.strip().lower():
                    nyt_status = "OK"
                    nyt_critics_pick = nyt_data['results'][index]['critics_pick']
                    nyt_summary_short = nyt_data['results'][index]['summary_short']

                    if nyt_summary_short is not None:
                        if nyt_summary_short.strip() == "":
                            nyt_summary_short = "No summary review provided."

                    nyt_review_already_found = True

                    break

            if not nyt_review_already_found:
                nyt_status = "More than one review found in same year with no exact name match. Unable to choose review."
                nyt_critics_pick = "No review found."
                nyt_summary_short = "No review found."
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
