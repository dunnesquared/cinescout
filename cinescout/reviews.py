"""Classes to handle api queries to external sources for movie reviews."""

import os
import time
from datetime import datetime

import requests                  # API calls
from fuzzywuzzy import fuzz      # For determining how similar two movie titles are.

from cinescout.movies import TmdbMovie 


class MovieReview:
    """Class representing a movie review.

    Attributes:
        title: String representing the title of movie reviewed.
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

    @classmethod
    def get_movie_review(cls, movie):
        """Returns movie review based on information in Movie object"""
        pass

    def __str__(self):
        return f"'{self.title}' ({self.year}): {self.text}"


class NytMovieReview(MovieReview):
    """Class representing a movie review from the New York Times.

    Class Attributes:
        api_key: String representing API key required to access NYT's API.
        delay: Integer representing delay before calling NYT api.
        threshold: Integer of [0, 100] representing the Levenshtein distance
                   ratio as a result of fuzzy string comparison.
        max_year_gap: Integer representing the max number of years between
                      the release of a movie and it being reviewed.
        exceptions: Dictionary containing titles (string) and years (int) of
                    movies who need cannot be queried the usual way.

    Attributes:
        title: String representing the title of movie reviewed.
        year: Integer representing the release year of the movie.
        text: String containing summary of movie review.
        publication_date: String representing date review was published.
        critics_pick: Boolean representing whether movie is NYT critic's pick.
    """

    # Class Attributes

    # New York Times API movie review key
    api_key = os.getenv('NYT_API_KEY')

    # Number of seconds to wait before making next call to NYT api
    delay = 3

    # Percentage the likelihood that two strings match per Levenshtein distance
    # ratio. An arbitrary value that seems reasnoable.
    threshold = 80

    # Max number of years between when a movie was released and its review
    # published.
    max_year_gap = 5

    # Movies that cannot be queried the usual way, probably because two movies
    # of the same title came out the same year.
    exceptions = { "Black Rain": 1989, "Nineteen Eighty-Four": 1984}

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

        # Remove Unicode characters from review text that are not rendered,
        # but presented as is. Replace them with appropriate characters.
        temp_text = temp_text.replace('&quot;', '"')  # straight quotes
        temp_text = temp_text.replace('&#151;', '—')  # em dash
        temp_text = temp_text.replace('&#8220;', '"')  # left quote
        temp_text = temp_text.replace('&#8221;', '"')  # right quote
        temp_text = temp_text.replace('&#8217;', '\'')  # apostrophe

        cleaned_text = temp_text
        return cleaned_text

    @classmethod
    def delay_next(cls):
        """Delays execution of next line of code by passed number of seconds"""
        time.sleep(cls.delay)

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
        # Check arguments.
        if not extdb_title or not nyt_title:
            raise ValueError("Titles cannot be blank or None type.")

        # Calculate Levenshtein similarity ratios.
        ratio = fuzz.ratio(extdb_title.strip().lower(),
                           nyt_title.strip().lower())

        partial_ratio = fuzz.partial_ratio(extdb_title.strip().lower(),
                           nyt_title.strip().lower())

        print(f"Levenshtein similarity ratio, full = {ratio}")
        print(f"Levenshtein similarity ratio, partial = {partial_ratio}")

        # Are the two title similar enough to be confident they refer to same
        # movie?
        if ratio >= cls.threshold or (ratio >= 50 and partial_ratio >= cls.threshold):
            return True
        else:
            return False

    @classmethod
    def get_movie_review_for_exception(cls, movie):
        """Processes special cases where film review exists but is otherwise
        impossible to find given current algorithms.

        Args:
            movie: Movie object

        Raises:
            ValueError: if processing a film that is not an exception.

        Returns:
            Dictionary: Two fields
                'status_code': Integer representing Http response code.
                'review': Review object. None if no review is to be found.
         """
        print("Processing exceptions...")

        # Black Rain, 1989
        # The Japanese film's original title is in Japanese.
        if movie.title.lower().strip() == 'black rain' and movie.release_year == 1989:

            # The Michael Douglas movie has same main and original title.
            if movie.title != movie.original_title:
                print(f"{movie.title}, {movie.release_year} => Japanese version!")
                print("Review does exist in NYT database.")
                return {'status_code': 200, 'review': None}
            else:
                print(f"{movie.title}, {movie.release_year} => Michael Douglas version!")
                print("Getting review for film!")

                # The dates on which a movie is released and reviewed likely differ.
                # Most movies will have been reviewed in the same year they were
                # released, however.
                opening_date_start = f"{movie.release_year}-01-01"
                opening_date_end = f"{movie.release_year}-12-31"

                print("Making initial request to NYT Movie Review API...", end="")
                res = requests.get("https://api.nytimes.com/svc/movies/v2/reviews/search.json",
                                        params={"api-key": cls.api_key,
                                                "opening-date": f"{opening_date_start}:{opening_date_end}",
                                                "query": movie.title.strip()})

                # Request to NYT failed...
                if res.status_code != 200:
                    print(f"FAILED! Http response status code = {res.status_code}")
                    return {'status_code': res.status_code, 'review': None}

                print("SUCCESS!")

                # All good. Extract data.
                nyt_data = res.json()

                # Build review object.
                review = cls(title=movie.title, year=movie.release_year,
                             text=cls.clean_review_text(nyt_data['results'][0].get('summary_short')),
                             publication_date=nyt_data['results'][0].get('publication_date'),
                             critics_pick=nyt_data['results'][0].get('critics_pick'))

                return {'status_code': res.status_code, 'review': review}

            # '1984', 1984
            # Written ad 'Nineteen Eighty-Four' in tmdb.
        elif movie.title.lower().strip() == 'nineteen eighty-four' and movie.release_year == 1984:

                print(f"'1984', {movie.release_year} => John Hurt version!")
                print("Getting review for film!")

                # Film reviewed in US in 1985
                opening_date_start = f"1985-01-01"
                opening_date_end = f"1985-12-31"

                print("Making initial request to NYT Movie Review API...", end="")
                res = requests.get("https://api.nytimes.com/svc/movies/v2/reviews/search.json",
                                        params={"api-key": cls.api_key,
                                                "opening-date": f"{opening_date_start}:{opening_date_end}",
                                                "query": '1984'})

                # Request to NYT failed...
                if res.status_code != 200:
                    print(f"FAILED! Http response status code = {res.status_code}")
                    return {'status_code': res.status_code, 'review': None}

                print("SUCCESS!")

                # All good. Extract data.
                nyt_data = res.json()

                # Build review object.
                review = cls(title='1984', year=movie.release_year,
                             text=cls.clean_review_text(nyt_data['results'][0].get('summary_short')),
                             publication_date=nyt_data['results'][0].get('publication_date'),
                             critics_pick=nyt_data['results'][0].get('critics_pick'))

                return {'status_code': res.status_code, 'review': review}
        else:
            raise ValueError("Film that is not a special case being processed as one!")

    @classmethod
    def get_movie_review(cls, movie, first_try=True):
        """Attempts to return NYT movie review based on movie data.

        Args:
            movie: Movie object representing movie searched for.

        Raises:
            ValueError: if pertinent movie data needed to query NYT's api
                        is missing.

        Returns:
            result: A dictionary with the following fields
                success: True or False, depending on wheter movie found.
                status_code: Integer repr. status code of Http response.
                message: String repr. description of status.
                review: Review object containing salient data. None if
                        no review could be found.
                bullseye: A boolean indicating whether review found is
                          is considered to a be a 'bullseye' exact match,
                          or a best-that-could-be found one.
                future_release: A boolean indicating whether movie has yet
                                to be realeased.


        """
        # ==================== INNER FUNCTIONS ==============================
        def get_result(success=None, status_code=None, message=None,
                        review=None, bullseye=None, future_release=None):
            """Returns result object. See outerfunction doctstring
            for more details."""
            result = {
                      'success': success,
                      'status_code': status_code,
                      'message': message,
                      'review': review,
                      'bullseye': bullseye,
                      'future_release': future_release
                    }
            return result

        def error_result(message, status_code=None):
            """Returns particular result object when review cannot be found
            due to an error (http error, missing movie information, etc.)"""
            return get_result(success=False,
                              status_code=status_code,
                              message=message)

        def nyt_api_title_query(title):
            """Queries for NYT review based on title."""
            url = "https://api.nytimes.com/svc/movies/v2/reviews/search.json"
            res = requests.get(url, params={"api-key": cls.api_key,
                                            "query": title.strip()})
            return res

        def nyt_api_title_release_year_query(title, release_year):
            """First query made to NYT api to find movie review.
            Results in ascending ordred per review publication year.

            Args:
                title: String representing film's title.
                release_year: Integer representing film's release year.

            Returns:
                res: JSON response object from NYT server.
            """

            # Look from beginning of year. The film's release date may differ
            # from that of the NYT. For the NYT, it may have been released
            # earlier, so reviewed earlier. Accept results within several years of review year.
            start = f"{release_year}-01-01"
            end = f"{release_year + cls.max_year_gap}-12-31"
           
            url = "https://api.nytimes.com/svc/movies/v2/reviews/search.json"

            res = requests.get(url, params={"api-key": cls.api_key,
                                            "publication-date": f"{start}:{end}",
                                            "order": "by-publication-date",
                                            "query": title.strip()})
            return res

        def nyt_api_title_release_date_query(title, release_date):
            """Second query made to NYT api to find movie review.
            Results in ascending ordred per opening date.

            Args:
                title: String representing film's title.
                release_date: String representing film's release date.

            Returns:
                res: JSON response object from NYT server.
            """
            url = "https://api.nytimes.com/svc/movies/v2/reviews/search.json"

            # End-date for query should be however many years after
            # a film has opened that the programmer has decided for it to be
            # 'acceptable' consider reviews.
            date_parts = release_date.split('-', 1)
            end_year = int(date_parts[0]) + cls.max_year_gap
            end_date = f"{end_year}-{date_parts[1]}"

            # Date to send with API request.
            opening_date = f"{release_date}:{end_date}"

            res = requests.get(url, params={"api-key": cls.api_key,
                                            "opening-date": opening_date,
                                            "order": "by-opening-date",
                                            "query": title.strip()})

            return res

        def build_NYTReview_object(movie, nyt_data_result):
            """Returns NYTReview object based on NYT api response data for a
            single review and a Movie object.

            Args:
                movie: Movie object representing movie searched for.
                nyt_data_result: Dictionary containing data from NYT api for
                                 a single review.
            Returns:
                review: An NYTMovieReview object.
            """

            # Extract info from NYT api result.
            nyt_critics_pick = nyt_data_result['critics_pick']
            nyt_summary_short = nyt_data_result['summary_short']

            if nyt_summary_short is not None:
                if nyt_summary_short.strip() == "":
                    nyt_summary_short = "No summary review provided."

            review = cls(title=movie.title, year=movie.release_year,
                         text=cls.clean_review_text(nyt_summary_short),
                         critics_pick=nyt_critics_pick,
                         publication_date=nyt_data_result.get('publication_date'))

            return review

        # +++++++ SINGLE RESULT ++++++++
        def get_publication_year(nyt_data_result):
            """Extracts publication year of review.

            Args:
                nyt_data_result: Dictionary containing data from NYT api for
                                 a single review.

            Returns:
                nyt_pub_year: String representing publication date.
            """
            nyt_pub_date = nyt_data_result.get('publication_date')
            nyt_pub_year = int(nyt_pub_date.split('-')[0].strip())
            return nyt_pub_year

        def film_reviewed_in_last_X_years(release_year, nyt_pub_year,
                                          acceptable_range):
            """Determines whether film was reviewed within X years of being
            released.

            Args:
                release_year: Integer representing release year of film.
                nyt_pub_year: Integer representing year review was published.
                acceptable_range: Integer representing the max number of years
                                  a review could be published for a film.
            """
            # Film review is too old.
            if (nyt_pub_year - release_year) > acceptable_range:
                return False

            # No, it isn't.
            return True

        def verify_result(nyt_data_result, original_title_used=False):
            """Checks whether single NYT api review result can be reliably
            trusted. Verification checks two aspects of the returned review:
            when it was published, and the title of movie it reviews.

            Args:
                nyt_data_result: Dictionary containing data from NYT api for
                                 a single review.
                original_title_used: Boolean indicating whether film's
                                    original title was used to query the api.
            Returns:
                result: A dictionary containing the final result data
                        after analysis.
            """

            # Ensure that all reviews have a publication date.
            # Don't trust them otherwise.
            if not nyt_data_result.get('publication_date'):
                message = "Unable to verify review: it has no publication date."
                print(f"{message}: {movie.title}, ({movie.release_year})")
                result = get_result(success=False,
                                  status_code=response.status_code,
                                  message=message)
                return result

            # Get publication year from publication date
            nyt_pub_year = get_publication_year(nyt_data_result)

            # Film review cannot have been published before a film's realease.
            if nyt_pub_year != movie.release_year:
                if nyt_pub_year < movie.release_year:
                    message = "Review no good: A review cannot be published before a film's release."
                    print(f"{message}: {movie.title}, ({movie.release_year})")
                    result = get_result(success=False,
                                      status_code=response.status_code,
                                      message=message)
                    return result

                # Film reviews that are published 'too late' are not trustworthy.
                if not film_reviewed_in_last_X_years(release_year=movie.release_year,
                                                nyt_pub_year=nyt_pub_year,
                                                acceptable_range=cls.max_year_gap):

                    message = "Review unlikely: review published too many years after film release."
                    print(f"{message}: {movie.title}")
                    result = get_result(success=False,
                                      status_code=response.status_code,
                                      message=message)
                    return result

            # See whether film's title is highly similar to title used in
            # NYT review.
            # NYT may have used original movie title instead of
            # more widely-known, often Anglicized, movie title.
            if original_title_used:
                searched_title = movie.original_title.strip().lower()
            else:
                searched_title = movie.title.strip().lower()

            # Clean NYT title for movie so differences in case and spacing
            # doesn't give us false negatives.
            nyt_movie_title = nyt_data_result.get('display_title').strip().lower()

            # Check whether TMDB movie title and move title in NYT review
            # are similar.
            similar_titles = cls.good_enough_match(searched_title,
                                                    nyt_movie_title)

            if not similar_titles:
                message = "Not a close enough match: Film title does not match title of film in review."
                print(f"{message}: {movie.title}, ({movie.release_year})")
                result = get_result(success=False,
                                  status_code=response.status_code,
                                  message=message)
                return result

            # All good. Build a review object.
            print("Best review possible found. Building review object...")
            review = build_NYTReview_object(movie, nyt_data_result)

            # Let caller know whehter review is an exact match or not.
            if nyt_pub_year != movie.release_year or not similar_titles:
                print("Some risk that this is the wrong review.")
                bullseye = False
            else:
                print("Zero or low risk that this is the wrong review.")
                bullseye = True

            result = get_result(success=True,
                                status_code=response.status_code,
                                review=review,
                                bullseye=bullseye)

            return result

        # +++++++ MUTLIPLE RESULTS ++++++++
        def nyt_review_year(nytreview):
            """Returns year a NYT review was published; should that not exist,
            then the year the movie opened.

            Args:
                nytreview: An element from NYT api 'results' list.

            Returns:
                review_year: Integer representing desired year.
            """
            if nytreview['publication_date']:
                nyt_date = nytreview['publication_date']
            else:
                nyt_date = nytreview['opening_date']

            review_year = int(nyt_date.split('-')[0].strip())

            return review_year

        def exact_match(movie, nytreviews):
            """Attempts to find NYT review that has exactly the same title
            and year as the passed Movie object.

            Args:
                movie: Movie object containing salient movie data.
                nytreviews: List of dictionaries containing review data from
                            NYT api response.

            Returns:
                nytreview: An element from said list if an exact match found.
                None: A None type object should an exact match not be found.
            """
            # Matches should be capitalization and space-neutral
            movie_obj_title = movie.title.strip().lower()

            for nytreview in nytreviews:
                # Idem reason.
                review_movietitle = nytreview['display_title'].strip().lower()

                # Compare titles.
                if movie_obj_title == review_movietitle:

                    # Compare release years.
                    if movie.release_year == nyt_review_year(nytreview):
                        return nytreview

            # No match.
            return None

        def filter_year(release_year, nytreviews, grace_period):
            """Builds and returns list of NYT reviews that were written
            after a movie's release_year and within a grace period

            Args:
                release_year: Integer representing movie release year.
                nytreviews: List of dictionaries containing review data from
                            NYT api response.
                grace_period: Integer representing number of years after
                              a film's release for a review to be 'valid'.

            Returns:
                filtered_list: A list of NYT reviews that pass the filter
                               tests; list can be empty.
            """
            filtered_reviews = []

            for nytreview in nytreviews:
                review_year = nyt_review_year(nytreview)

                if review_year >= release_year:
                    if (review_year - release_year) <= grace_period:
                        filtered_reviews.append(nytreview)

            return filtered_reviews

        def filter_title(movie_title, nytreviews):
            """Filters NYT data api response for titles that are
            good-enough matches.

            Args:
                movie_title: String representing movie title.
                nytreviews: List of dictionaries containing review data from
                            NYT api response.

            Returns:
                filtered_list: A list of NYT reviews that pass the filter
                               tests; list can be empty.
            """
            filtered_list = []

            for nytreview in nytreviews:
                nyt_movie_title = nytreview.get('display_title').lower().strip()

                if cls.good_enough_match(movie_title, nyt_movie_title):
                    filtered_list.append(nytreview)

            return filtered_list

        def highest_levenshtein(searched_title, nyt_data_results):
            """Returns NYT movie review that has the highest Levenshtein score."""

            # An exact match should be worth more than a partial one.
            weight_full = 2
            weight_partial = 1

            # Calculate score of first title. Let it be the max.
            full_ratio = fuzz.ratio(searched_title,
                                    nyt_data_results[0]['display_title'].strip().lower())
            partial_ratio = fuzz.partial_ratio(searched_title,
                                    nyt_data_results[0]['display_title'].strip().lower())

            score_max = weight_full * full_ratio + weight_full + partial_ratio * weight_partial
            index = 0 # index of review with best score

            # We need to be sure that the result we're returning is the only
            # result with the highest score.
            two_results_same_score = False

            for i in range(1, len(nyt_data_results)):
                # Calculate score for each film.
                full_ratio = fuzz.ratio(searched_title,
                                        nyt_data_results[i]['display_title'].strip().lower())
                partial_ratio = fuzz.partial_ratio(searched_title,
                                        nyt_data_results[i]['display_title'].strip().lower())

                score_i = weight_full * full_ratio + weight_full + partial_ratio * weight_partial

                # Update accordingly if new max found or tie.
                if score_i > score_max:
                    score_max = score_i
                    index = i
                    two_results_same_score = False
                elif score_i == score_max:
                    two_results_same_score = True

            # No ties allowed.
            if two_results_same_score:
                return None

            # All is well: one result found.
            return nyt_data_results[index]

        # =========================== ALGORITHM =============================

        # 1. Ensure that movie title, release year and release date all exist
        #    before proceeeding.
        # 2. Check whether movie is a future release. If so, there's no review,
        #    so return right away.
        # 3. Check whether film is a special 'exception': a film in which the
        #    algorithm will not find becuase of its unique 'situation.'
        # 4. Query NYT api. Selecting the right one whether its the first or
        #    second call to this method to fetch a review.
        # 5. Check the api's response. Return if something's gone wrong.
        # 6. Unpack the response object.
        # 7. Process response if no results are returned.
        # 8. Process response if one result is returned.
        # 9. Process response if multiple results are returned.

        #                               ***


        # 1. Ensure that movie title, release year and release date all exist
        #    before proceeeding.

        # Guard code: need the title of a movie to find a review at a minimum.
        if not movie.title or not movie.release_year or not movie.release_date:
            message = "Title, release year or date can't be None or empty."
            raise ValueError(message)

        # 2. Check whether movie is a future release. If so, there's no review,
        #    so return right away.

        # It's highly unlikely a review exists for a future release. The only
        # exception might be if a film is reviewed at a festival,
        # and given a general release at a later date. The release date though
        # tends to be this festival date though, so there is probably
        # little chance of missing a review.
        today = datetime.today()
        release_dt = datetime.strptime(movie.release_date, '%Y-%m-%d')

        if release_dt > today:
            message = "No review: film has yet to be released."
            print(message)
            return get_result(success=False,
                              message=message,
                              future_release=True)

        # 3. Check whether film is a special 'exception': a film in which the
        #    algorithm will not find becuase of its unique 'situation.'

        # An exception movie must have the same title and release year as a
        # a movie on the exception list.
        if cls.exceptions.get(movie.title) == movie.release_year:
            # Get the movie review directly.
            review_result = cls.get_movie_review_for_exception(movie)

            # No review found for some inexplicable reason...
            if not review_result['review']:
                message = "Error: processing exceptions failed."
                result = error_result(message=message,
                                      status_code=review_result['status_code'])
            else:
                # All good.
                result = get_result(success=True,
                                    status_code=review_result['status_code'],
                                    review=review_result['review'])

            return result

        # 4. Query NYT api. Selecting the right one whether its the first or
        #    second call to this method to fetch a review.
        if first_try:
            response = nyt_api_title_release_year_query(movie.title,
                                                        movie.release_year)
        else:
            response = nyt_api_title_release_date_query(movie.title,
                                                        movie.release_date)

        # 5. Check the api's response. Return if something's gone wrong.
        if response.status_code != 200:
            err_data = response.json()
            message = f"{err_data.get('message', None)}"
            result = error_result(message=message, 
                                  status_code=response.status_code)
            return result

        # 6. Unpack the response object.
        nyt_data = response.json()

        # Flag for check later on to make sure the right titles are
        # compared.
        original_title_used = False

        # 7. Process response if no results are returned.
        if nyt_data["num_results"] == 0:
            print("No reviews found.")

            # Foreign films may be in their original titles.
            if movie.original_title != movie.title:

                # Delay request, so as not to timeout NYT api.
                print(f"Checking original title: {movie.original_title}...")
                print(f"Waiting {cls.delay} seconds...")
                cls.delay_next()

                if first_try:
                    response = nyt_api_title_release_year_query(movie.original_title,
                                                                movie.release_year)
                else:
                    response = nyt_api_title_release_date_query(movie.original_title,
                                                                movie.release_date)


                if response.status_code != 200:
                    message = "Error: Http response status code = {res.status_code}"
                    result = error_result(message=message,
                                          status_code=response.status_code)
                    return result

                # Update response data.
                nyt_data = response.json()

                # Found at least one review with original title; important to
                # know for later.
                original_title_used = True

            # Still no luck with foreign title.
            if nyt_data["num_results"] == 0:
                message = "No review found for this movie."
                print(f"{message}: {movie.title}")
                result = get_result(success=False,
                                  status_code=response.status_code,
                                  message=message)
                return result

        # 8. Process response if one result is returned.
        if nyt_data["num_results"] == 1:
            print("One review found.")

            # Single result. Naturally going to be first item.
            nyt_data_result = nyt_data['results'][0]

            # Just because one result returned doesn't mean it's right!
            result = verify_result(nyt_data_result, original_title_used)

            return result

        # 9. Process response if multiple results are returned.
        if nyt_data["num_results"] > 1:
            print("Multiple reviews found.")

            nytreviews = nyt_data['results']

            # Try to find exact match first.
            nytreview = exact_match(movie, nytreviews)

            # Success!
            if nytreview:
                print("Exact match found!")
                review_obj = build_NYTReview_object(movie, nytreview)
                result = get_result(success=True,
                                    status_code=response.status_code,
                                    review=review_obj,
                                    bullseye=True)
                return result

            # No exact match. Maybe review was written a later year than
            # its release.
            print("Filtering by release year...")
            filtered_reviews = filter_year(release_year=movie.release_year,
                                           nytreviews=nytreviews,
                                           grace_period=cls.max_year_gap)

            # All the reviews were written 'way' later than film was released.
            # None were thus trustworthy, so none were returned.
            if not filtered_reviews:
                message = "Multiple reviews: No review found within grace period."
                print(f"{message}: {movie.title}")
                result = get_result(success=False,
                                  status_code=response.status_code,
                                  message=message)
                return result

            # With the shortlist of filtered movies above, let's try to find
            # ones with the closest-matching movie title.
            print("Filtering by title....")

            # Make sure to pass the right title before filtering the results!
            # NYT may have used original movie title instead of
            # more widely-known, often Anglicized, movie title.
            if original_title_used:
                movie_title = movie.original_title.strip().lower()
            else:
                movie_title = movie.title.strip().lower()

            filtered_reviews = filter_title(movie_title, filtered_reviews)

            # None of the filtered reviews had titles that matched closely
            # enough.
            if not filtered_reviews:
                message = "Multiple reviews: none passed title filtering."
                print(f"{message}: {movie.title}")
                result = get_result(success=False,
                                  status_code=response.status_code,
                                  message=message)
                return result

            # If there's only one review, we can assume that it's likely a
            # a good match.
            if len(filtered_reviews) == 1:
                print("Review found! Hopefully it's the right one.")
                review_obj = build_NYTReview_object(movie, filtered_reviews[0])
                result = get_result(success=True,
                                    status_code=response.status_code,
                                    review=review_obj,
                                    bullseye=False)
                return result

            # Still more than one review that could be the right one.
            # Title that matches the closest to one searched for will be the
            # deciding factor.
            if len(filtered_reviews) > 1:
                print("Choosing review with highest Levenshtein score...")
                nytreview = highest_levenshtein(movie_title, filtered_reviews)

            # Out of tricks. Time to give up.
            if not nytreview:
                message = "No luck: Multiple reviews with same Levenshtein score."
                print(f"{message}: {movie.title}")
                result = get_result(success=False,
                                  status_code=response.status_code,
                                  message=message)
                return result

            # Success!
            else:
                print("Review with highest Levenshtein score selected!")
                print("Hopefully it's the right one.")
                review_obj = build_NYTReview_object(movie, nytreview)
                result = get_result(success=True,
                                    status_code=response.status_code,
                                    review=review_obj,
                                    bullseye=False)
                return result