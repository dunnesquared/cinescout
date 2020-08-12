import os
import time
from datetime import datetime
import unittest
# import json


# Add this line to whatever test script you write
from context import app, NytMovieReview, Movie, TmdbMovie


class NytMovieReviewTests(unittest.TestCase):

    # Setup/teardown
    def setUp(self):
        # """Executes before each test."""
        print("Setting up NytMovieReviewTests...")

        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()


    def tearDown(self):
        """Executes after each test."""
        print("Tearing down NytMovieReviewTests...")


    def delay_api_call(self, amt=6):
        """Delays executions by amt seconds"""
        print("DELAYING API CALL...")
        time.sleep(amt)

    # Tests
    def test_createReview(self):
        """Create a NytMovieReview object.
        """
        review = NytMovieReview(title="Not a Real Movie", year=2999,
                                text="Five bags of popcorn.",
                                publication_date="2999-10-31",
                                critics_pick=True)

        self.assertEqual(review.title, "Not a Real Movie")
        self.assertEqual(review.year, 2999)
        self.assertEqual(review.text, "Five bags of popcorn.")
        self.assertEqual(review.publication_date, "2999-10-31")
        self.assertTrue(review.critics_pick)

    def test_good_enough_match(self):
        """Tests fuzzy matching."""
        # Practically the same title.
        extdb_title = "Mulholldand Drive"
        nyt_title = "Mulholland Dr."
        result = NytMovieReview.good_enough_match(extdb_title, nyt_title)
        self.assertTrue(result)

        #  Different titles.
        extdb_title = "Maximum Overdrive"
        nyt_title = "Mulholland Drive"
        result = NytMovieReview.good_enough_match(extdb_title, nyt_title)
        self.assertFalse(result)

    def test_get_review_by_title_and_year_OK(self):
        title = "Mulholland Drive"
        release_year = 2001
        result = NytMovieReview.get_review_by_title_and_year(title,
                                                             release_year)

        self.assertTrue(result['success'])
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['message'], 'OK')

        review = result['review']

        extdb_title = "Mulholland Drive"
        review_year = 2001
        text = "David Lynch's epic nightmare of Hollywood"
        publication_date = "2001-10-06"

        self.assertEqual(review.title, title)
        self.assertEqual(review.year, review_year)
        self.assertIn(text, review.text)
        self.assertEqual(review.publication_date, publication_date)
        self.assertTrue(review.critics_pick)

    def test_get_movie_review_future_release(self):
        # Expected for future releases only.
        title = "placeholder title"
        expected = "No review: film has yet to be released."

        # Future release
        movie = Movie(title=title, release_date="2999-12-31", original_title=title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertEqual(expected, result['message'])

        self.delay_api_call()

        # Past release
        movie = Movie(title=title, release_date="1999-12-31", original_title=title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertNotEqual(expected, result['message'])

        self.delay_api_call()

        # Released today
        movie = Movie(title=title,
                      release_date=datetime.today().strftime('%Y-%m-%d'),
                       original_title=title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertNotEqual(expected, result['message'])

    def test_get_movie_review_exception(self):
        # Exception: in exception list, matching year

        self.delay_api_call()

        movie = Movie(title="Black Rain", release_year=1989,
                     original_title="Black Rain")
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("Mechanical police melodrama.", result['review'].text)

        self.delay_api_call()

        # Exception: in exception list, not matching year
        movie = Movie(title="Black Rain", release_year=1900,
                     original_title="Black Rain")
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

        self.delay_api_call()

        # Just one more test
        title = "Nineteen Eighty-Four"
        movie = Movie(title=title, release_year=1984, original_title=title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("Big Brother rewriting history", result['review'].text)

    def test_get_movie_review_bad_title(self):
        # No title
        movie = Movie(title="", release_year=1980)
        self.assertRaises(ValueError, NytMovieReview.get_movie_review,
                                movie)

        self.delay_api_call()

        # Gobbledygook: foreign title
        title = "3254343tertert4564363635465"
        movie = Movie(title=title, release_year=1980, original_title="23523532532")
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])
        self.assertIn('No review found for this movie.', result['message'])

        self.delay_api_call()

        # Gobbledygook: same title
        title = "3254343tertert4564363635465"
        movie = Movie(title=title, release_year=1980, original_title=title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])
        self.assertIn('No review found for this movie.', result['message'])

    def test_get_movie_review_one_result_found(self):
        self.delay_api_call()
        title = "Mulholland Drive"
        release_year = 2001
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])

        self.delay_api_call()
        title = "Lovely & Amazing"
        release_year = 2001 # NYT review written in 2002.
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])

    def test_get_movie_review_multiple_results(self):
        self.delay_api_call()
        title = "Solaris"
        release_year = 2002
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])


        self.delay_api_call()
        title = "Solaris"
        release_year = 2012
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

    # Individual movies

    # # FAILS TEST!
    # # Reason: Too many results come up for kin, none of which are the movie
    # itself. Can remedy by specifying opening year, but then
    # other tests will fail. Trade-off bug.
    def test_get_review_kin_2018(self):
        self.delay_api_call()
        title = "Kin"
        release_year = 2018
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn('fantasy wish fulfillment', result['review'].text)

    def test_get_review_solaris_2002(self):
        self.delay_api_call()
        title = "Solaris"
        release_year = 2002
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn('cerebral science-fiction film', result['review'].text)

    def test_get_review_solaris_1972(self):
        self.delay_api_call()
        title = "Solaris"
        release_year = 1972
        original_title = "Солярис"
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn('Soviet psychologist on strange planet', result['review'].text)

    def test_get_review_sabrina_1994(self):
        self.delay_api_call()
        title = "Sabrina"
        release_year = 1994
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn('Chauffeur\'s daughter loves playboy', result['review'].text)

    def test_get_review_catfight_2006(self):
        self.delay_api_call()
        title = "CatFight"
        release_year = 2006
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

    def test_get_review_catfight_2017(self):
        self.delay_api_call()
        title = "Catfight"
        release_year = 2017
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("jabs at callous privilege", result['review'].text)

    def test_get_review_catfight_2019(self):
        self.delay_api_call()
        title = "Catfight"
        release_year = 2019
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

    def test_get_review_ghostintheshell_1995(self):
        self.delay_api_call()
        title = "Ghost in the Shell"
        release_year = 1995
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

    def test_get_review_ghostintheshell_2017(self):
        self.delay_api_call()
        title = "Ghost in the Shell"
        release_year = 2017
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("thrill-free science fiction thriller", result['review'].text)

    def test_get_review_blueisthewarmestcolor_2013(self):
        self.delay_api_call()
        title = "Blue Is The Warmest Color"
        release_year = 2013
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("blissful attachment to another woman", result['review'].text)

    def test_get_review_dirtydancing_2017(self):
        self.delay_api_call()
        title = "Dirty Dancing"
        release_year = 2017
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

    def test_get_review_dirtydancing_1987(self):
        self.delay_api_call()
        title = "Dirty Dancing"
        release_year = 1987
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("Sweetly seething, like Swayze's samba.",
                        result['review'].text)

    def test_get_review_dirtydancinghavananights_2004(self):
        self.delay_api_call()
        title = "Dirty Dancing: Havana Nights"
        release_year = 2004
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("desperation for a sweaty PG-13 sexiness", result['review'].text)

    def test_get_review_crystalfairy_2013(self):
        self.delay_api_call()
        title = "Crystal Fairy & the Magical Cactus"
        release_year = 2013
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("a coke-and-pot-fueled party", result['review'].text)

    def test_get_review_amelie_2001(self):
        self.delay_api_call()
        title = "Amélie"
        release_year = 2001
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("Jean-Pierre Jeunet", result['review'].text)

    def test_get_review_aubergeespagnole_2002(self):
        self.delay_api_call()
        title = "The Spanish Apartment"
        release_year = 2002
        original_title = "L'Auberge espagnole"
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("the new, borderless Europe", result['review'].text)

    def test_get_review_littlewomen_1917(self):
        self.delay_api_call()
        title = "Little Women"
        release_year = 1917
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

    def test_get_review_littlewomen_1933(self):
        self.delay_api_call()
        title = "Little Women"
        release_year = 1933
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("The Alcott classic, served to perfection" ,
                    result['review'].text)

    def test_get_review_littlewomen_2019(self):
        self.delay_api_call()
        title = "Little Women"
        release_year = 2019
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("Greta Gerwig refreshes a literary classic" ,
                    result['review'].text)








    """
    2) Kin: Couldn't select among multiple reviews:
      SOL'N impose exact title match when picking reviews
    3) Crashes if film is not in database, e.g. Le Shower
      SOL'N: Return None for Movies object instead of warning string.
    4) Catfight" crashes for entry that does not have release date
      SOL'N: Don't display review if release_date does not exist
    5) *** Catfight
      - gives the wrong review for 2006 film "CatFight"
      - gives the wrong review for 2019 film "CatFight"
      *** Ghost in the Shell (1995)
       - gives review for Scar Jo 2017 version
      SOL'N: Better heuristic testing; warning messages
    6) Solaris 1972 review not showing up
      SOL'N: Fix up NytReview Heuristic
    7) *** Dirty Dancing (Released 2017-05-24):
        - ValueError: min() arg is an empty sequence
        SOL'N: Prevent determining review year if all review dated before release
    8)  No review found for "Blue is the Warmest Color" because exact title match
       means if words are capitalized differently there will be no match.
       SOL'N: Force strings into lower case before comparing.
    9) No review show for "Crystal Fairy & the Magical Cactus" because title is
     "Crystal Fairy" in NYT db; No review found "Amélie" because it's 'Amelie' in
     NYT database (accent issue)
      SOL'N: Fuzzy string comparison
    10)  No review for "Auberge Espagnole" because TMDB title searched is in English
     but NYT review has it in the original French: L' Auberge Espagnole
      SOL'N: Query search using original title rather than English translation.
    11) Wrong review for CatFight, 2006 - showing review for 2017 movie
      Little Women (Release date: 1917-07-02) - has review for 1933 version
      even though 1933 version is in NYT db
      SOL'N: Enforce threshold to reject any review that are 10 years older than
      the release date.
    12)   - King Cobra (Review precedes opening date)
     - Tim and Eric's Billion Dollar Movie (get warning even though movie and review dates are the same)
    - Little Women, 2018 (No warnings that review might be wrong!!)
      SOL'N: Append warning for any movie where the release and review years are not the same.
    13) Black Rain: example of movie made in same year with same title!
      SOL'N: Hard code it as an exception.
    14) Sabrina (1995) - Says 2004 is closest review but 1996 is...
        SOLN: Bugs in logic (didn't include case where pub and release years the same)
    15) Handle case where there is no overview text (Sabrina, 2011)
      SOLN: Jinja conditional
    16) 1984: gives link to Apple commercial, not film.
      - Film is "Nineteen Eighty-Four" in tmdb db
      - Sol'n:
        - manually write in correct tmdb id in criterion.csv
        - add 1984 as Criterion movie exception
    17) Rendering all messed up on pages without posters ("Happiest Season")
        Or even with a poster ("The Flavour of Green Tea Over Rice")
        - SOL'N: inappropiately located conditional

    """








if __name__ == "__main__":
    unittest.main()
