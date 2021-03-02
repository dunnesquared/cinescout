"""Classes to handle api requests to external sources for movie information."""

import os
from datetime import datetime
from typing import Dict

import requests
from urllib import parse
from textwrap import dedent


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
    def __init__(self, id=None, title=None,
                release_year=None, release_date=None, overview=None,
                runtime=None, original_title=None, filmcredits=None):
                 self.id = id
                 self.title = title
                 self.release_year = release_year
                 self.release_date = release_date
                 self.overview = overview
                 self.runtime = runtime
                 self.original_title = original_title
                 self.filmcredits = filmcredits
                 

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

    
    def get_query(self, search_engine: str) -> str:
        """Gets query url that can be used to search for movie info on a given search engine.
        
        Args:
            search_engine: String object that represents different search engines, e.g. 'google'

        Raise: 
            ValueError: if search_engine is None or blank.

        Returns:
            query_url: String object representing the url to query search engine specified for
                       the movie this object models. 
        """
        if not search_engine or not search_engine.strip():
            raise ValueError("Search engine parameter cannot be None or blank.")
        queryfunc = self.querymaker(search_engine)
        return queryfunc()


    def querymaker(self, search_engine: str):
        """Gets function that makes the query per search engine

        Args:
            search_engine: String object that represents different search engines, e.g. 'google'

        Raise: 
            ValueError: if search engine not recognized. 

        Returns:
            queryfunc: Function that builds the desired query for the target search engine. 
        """
        if not search_engine or not search_engine.strip():
            raise ValueError("Search engine parameter cannot be None or blank.")
        search_engine = search_engine.lower()
        if search_engine == 'google':
            queryfunc = self.googlequery
        elif search_engine == 'duckduckgo':
            queryfunc = self.duckduckgoquery
        else:
            raise ValueError(search_engine)
        return queryfunc


    def googlequery(self):
        """Gets URL to learn more about film using Google's search engine
        
        Returns:
            String containing url that will query movie on Google.
        """
        base_url = "https://www.google.com/search?q="
        return self.commonquery(base_url=base_url)
    

    def duckduckgoquery(self):
        """Gets URL to learn more about film using DuckDuckGo's search engine
        

        Returns:
            String containing url that will query movie on DuckDuckGo.
        """
        base_url = "https://duckduckgo.com/?q="
        return self.commonquery(base_url=base_url)


    def commonquery(self, base_url: str) -> str:
        """Builds query based on common build-setup for different search engines. 

        Args:
            base_url: String object that represents the base url required to query a search engine.
        
        Raises:
            ValueError: if base_url is empty.
        Returns:
            query: String containing url that will query movie on search engine.
        """
        if base_url is None or base_url.strip() == "": 
            raise ValueError("Base url cannot be null or empty string.")
        
        # No null titles, no blank titles. 
        if not self.title or not self.title.strip():
            raise ValueError("Query must have title data.")

        # Prefer the original title of foreign films over the English one.
        if self.original_title and self.original_title.strip():
            print("******  original title used!")
            title = self.original_title.strip()
        else:
            title = self.title.strip()

        if self.release_year:
            query = base_url + parse.quote(f"{title} {self.release_year} film", safe=[])
        else:
            query = base_url + parse.quote(f"{title} film", safe=[])

        return query
        
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
        tmdb_base_url: String representing prefix url to access TMDB movie
                       page.

    Attributes:
        id: Integer representing movie in external database.
        title: String representing film's title.
        original_title: String representing film's orginal title, most likely
                        in the case of non-English language film.
        release_year: Integer representing year movie released.
        release_date: String representing date movie released.
        overview: String containing summary of movie's premise.
        runtime: Integer representing runtime of movie in minutes.
        poster_full_url: String representing complete url to access image of
                         a movie's poster should it exist.
        imdb_full_url: String representing complete url to access IMDB movie
                       page, should it exist.
        tmdb_full_url: String representing complete url to access TMDB movie
                       page, should it exist.
        providers: Dictionary containing names of streaming and rental services to 
                   watch the film. 
    """
    # Class attributes
    api_key = os.getenv('TMDB_API_KEY')
    poster_base_url = "https://image.tmdb.org/t/p/"
    poster_size = "w300"
    delay = 1
    imdb_base_url = "https://www.imdb.com/title/"
    tmdb_base_url = "https://www.themoviedb.org/movie/"

    def __init__(self, id=None, title=None,
                 release_year=None, release_date=None, overview=None,
                 runtime=None, original_title=None, filmcredits=None, providers=None, 
                 poster_full_url=None,
                 imdb_full_url=None, tmdb_full_url=None):
        Movie.__init__(self, id, title, release_year, release_date,
                        overview, runtime, original_title, filmcredits)
        self.poster_full_url = poster_full_url
        self.imdb_full_url = imdb_full_url
        self.tmdb_full_url = tmdb_full_url
        self.providers = providers

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
                              original_title=movie.get('original_title'),
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
    def get_bio_data_by_person_id(cls, person_id):
        """Returns details of cast/crew member (limited implementation).

        Args:
            person_id: Integer representing id of person in TMDB database.

        Returns:
            result: A dictionary with four fields fields:
                success: True or False, depending on wheter person found.
                status_code: Status code of Http response of api call.
                name: String representing cast/crew member's 'working' name
                image_url: String representing absolute url for cast/crew
                           member's image. Returns None if you no image foud.
        """

        # Setup return value
        result = {'success': True,
                  'status_code': 200,
                  'name': None,
                  'image_url': None}


        # Make request.
        print(f"Requesting person data from TMDB api with person_id={person_id}...",
                end="")
        res = requests.get(f"https://api.themoviedb.org/3/person/{person_id}",
                            params={"api_key": cls.api_key})


        # Check request.
        if res.status_code != 200:
            print(f"FAILED! status_code={res.status_code}")
            result['success'] = False
            result['status_code'] = res.status_code
            return result

        # Unpack.
        print("SUCCESS!")
        print("Extracting person data from TMDB JSON response....")

        # Deserialize JSON response object
        tmdb_person_data = res.json()

        # Useful to double-check we're getting the data for the person
        # we really want to know about.
        result['name'] = tmdb_person_data['name']

        # See whether relative url or null returned.
        if tmdb_person_data['profile_path'] is None:
            return result

        # Check for empty strings, just in case.
        if tmdb_person_data['profile_path'].strip() == '':
            return result

        # Build image url for person.
        # Use 'w185' size for image (relatively small).
        # See https://developers.themoviedb.org/3/configuration/get-api-configuration
        # for valid image sizes.
        img_full_url = cls.poster_base_url + 'w185' + tmdb_person_data['profile_path']

        result['image_url'] = img_full_url

        # return url or none.
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
                          original_title=movie_credit.get('original_title'),
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
                          original_title=movie_credit.get('original_title'),
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
    def _extract_provider_data(cls, tmdb_movie_data : Dict, country_code: str='CA') -> Dict:
        """Extracts provider data from TMDB JSON response object.

        Args:
            tmdb_movie_data: Dictionary-like object representing a TMDB JSON response for a 
                             reeuested movie.
            country_code: String representing providers' country; default 'CA' for Canada. 
        
        Returns:
            providers: Dictonary object with two keys mapping to lists of streaming and rental
                       services respectively. Any empty dictionary returned in case 
        """        
        providers = { 'stream': [], 'rent': [] }

        try: 
            # Extract watch/providers data
            provider_data = tmdb_movie_data.get('watch/providers', None).get('results', 
                                        None).get(country_code, None)
        except AttributeError:
            # No key-value pair: one of the first two gets above returns None.
            print("Unable to retrieve provider data: tmdb_movie_data entries missing or changed.")
            return providers

        if provider_data:
            # Get names of streaming services.
            stream_data =  provider_data.get('flatrate', None)
            if stream_data: 
                for elem in stream_data:
                    streamer = elem.get('provider_name', None)
                    if stream_data:
                        providers['stream'].append(streamer)
            # Get names of rental services.
            rent_data =  provider_data.get('rent', None)
            if rent_data: 
                for elem in rent_data:
                    renter = elem.get('provider_name', None)
                    if renter:
                        providers['rent'].append(renter)

        return providers

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
                            params={"api_key": cls.api_key, 
                                    "append_to_response": "credits,watch/providers"})

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

            # Get year movie was released. Should a release date no exist,
            # set it to zero: we users to be able to add the movie to
            # their personal lists even if not all the important info is there.
            if tmdb_movie_data.get('release_date'):
                release_year = int(tmdb_movie_data['release_date'].split('-')[0].strip())
            else:
                release_year = 0    # release year unknown

            # Build full url for movie poster.
            poster_full_url = None
            if tmdb_movie_data['poster_path']:
                poster_full_url = cls.poster_base_url + cls.poster_size + tmdb_movie_data['poster_path']

            # Build full url for IMDB
            imdb_full_url = None
            if tmdb_movie_data['imdb_id']:
                imdb_full_url = cls.imdb_base_url + tmdb_movie_data['imdb_id']

            # Build full url for TMDB
            tmdb_full_url = cls.tmdb_base_url + str(id)

            # Extract credits data
            filmcredits = None
            if tmdb_movie_data['credits']:
                # Iterate over response dict to extract essesntial info.
                filmcredits = {'cast': [], 'crew':[]}
                tmdbcredits = tmdb_movie_data['credits']
                # Cast
                for credit in tmdbcredits['cast']:
                    filmcredits['cast'].append({'name':credit.get('name', None), 
                                                'character': credit.get('character', None),
                                                'id': credit.get('id', None)})
                # Crew
                for credit in tmdbcredits['crew']:
                    filmcredits['crew'].append({'name': credit.get('name', None), 
                                                'job': credit.get('job', None),
                                                'id':  credit.get('id', None)})
            
            # Extract watch/providers data
            providers = cls._extract_provider_data(tmdb_movie_data)
            
            print("Building Movie object...")
            movie = cls(id=id, title=tmdb_movie_data['title'],
                        release_year=release_year,
                        release_date=tmdb_movie_data.get('release_date'),
                        overview=tmdb_movie_data['overview'],
                        runtime=tmdb_movie_data['runtime'],
                        original_title=tmdb_movie_data.get('original_title'),
                        poster_full_url=poster_full_url,
                        imdb_full_url=imdb_full_url,
                        tmdb_full_url=tmdb_full_url,
                        filmcredits=filmcredits,
                        providers=providers)

            result['movie'] = movie

        return result



