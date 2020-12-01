import os
import time
from datetime import datetime
import unittest
# import json


# Add this line to whatever test script you write
from context import app, NytMovieReview, Movie, TmdbMovie

class MovieTests(unittest.TestCase):
     # Setup/teardown
    def setUp(self):
        # """Executes before each test."""
        print("Setting up  MovieTests...")
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.testmovie = Movie(id=577922, title="Tenet", release_year=2020, 
                                release_date='2020-08-22',
                                original_title='Tenet')

    def tearDown(self):
        """Executes after each test."""
        print("Tearing down MovieTests...")
    
    # googlequery
    # -----------
    def testGoogleQueryNormal(self):
        expected = "https://www.google.com/search?q=Tenet%202020%20film"
        result = self.testmovie.googlequery()
        self.assertEqual(expected, result)
        
    def testGoogleQueryNoTitles(self):
        self.testmovie.title = None
        self.testmovie.original_title = None
        self.assertRaises(ValueError, self.testmovie.googlequery)

    def testGoogleQueryOriginalTitleOnly(self):
        self.testmovie.title = None
        self.testmovie.original_title = 'Tenet'
        self.assertRaises(ValueError, self.testmovie.googlequery)
    
    def testGoogleQueryEnglishTitleOnly(self):
        self.testmovie.original_title = None
        expected = "https://www.google.com/search?q=Tenet%202020%20film"
        result = self.testmovie.googlequery()
        self.assertEqual(expected, result)
    
    def testGoogleQueryBlankSpacesBothTitles(self):
        self.testmovie.title = '    '
        self.testmovie.original_title ='\n\t  '
        self.assertRaises(ValueError, self.testmovie.googlequery)
    
    def testGoogleQueryNoReleaseYear(self):
        self.testmovie.release_year = None
        expected = "https://www.google.com/search?q=Tenet%20film"
        result = self.testmovie.googlequery()
        self.assertEqual(expected, result)
    
    def testGoogleQueryBadReleaseYear(self):
        self.testmovie.release_year = "-128"
        expected = "https://www.google.com/search?q=Tenet%20-128%20film"
        result = self.testmovie.googlequery()
        self.assertEqual(expected, result)

    # commonquery
    # ----------- 
    def testCommonQueryBaseURLOK(self):
        base_url = "https://www.google.com/search?q="
        expected = "https://www.google.com/search?q=Tenet%202020%20film"
        result = self.testmovie.commonquery(base_url=base_url)
        self.assertEqual(expected, result)
    
    def testCommonQueryBaseURLNone(self):
        base_url = None
        self.assertRaises(ValueError, self.testmovie.commonquery, base_url)
    
    def testCommonQueryBaseURLBlank(self):
        base_url = "      "
        self.assertRaises(ValueError, self.testmovie.commonquery, base_url)


    # Test Google query feature
    # Normal
    # title = None, original title = None
    # title = None, original title not None
    # title blank spaces = "   ", original title = "   "
    # Unsafe strings: eval('print("hello")')
    # No release year


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

    # Test of old algorithm. No longer relevant.
    # def test_get_review_by_title_and_year_OK(self):
    #     title = "Mulholland Drive"
    #     release_year = 2001
    #     result = NytMovieReview.get_review_by_title_and_year(title,
    #                                                          release_year)
    #
    #     self.assertTrue(result['success'])
    #     self.assertEqual(result['status_code'], 200)
    #     self.assertEqual(result['message'], 'OK')
    #
    #     review = result['review']
    #
    #     extdb_title = "Mulholland Drive"
    #     review_year = 2001
    #     text = "David Lynch's epic nightmare of Hollywood"
    #     publication_date = "2001-10-06"
    #
    #     self.assertEqual(review.title, title)
    #     self.assertEqual(review.year, review_year)
    #     self.assertIn(text, review.text)
    #     self.assertEqual(review.publication_date, publication_date)
    #     self.assertTrue(review.critics_pick)

    def test_get_movie_review_future_release(self):
        # Expected for future releases only.
        title = "placeholder title"
        expected = "No review: film has yet to be released."

        # Future release
        movie = Movie(title=title, release_year=2999,
                      release_date="2999-12-31", original_title=title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertEqual(expected, result['message'])

        self.delay_api_call()

        # Past release
        movie = Movie(title=title, release_year=1999,
                      release_date="1999-12-31", original_title=title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertNotEqual(expected, result['message'])

        self.delay_api_call()

        # Released today
        movie = Movie(title=title,
                     release_year=datetime.today().year,
                      release_date=datetime.today().strftime('%Y-%m-%d'),
                       original_title=title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertNotEqual(expected, result['message'])

    def test_get_movie_review_exception(self):
        # Exception: in exception list, matching year

        self.delay_api_call()

        movie = Movie(title="Black Rain", release_year=1989,
                    release_date="1989-09-22",
                     original_title="Black Rain")
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("Mechanical police melodrama.", result['review'].text)

        self.delay_api_call()

        # Exception: in exception list, not matching year
        movie = Movie(title="Black Rain", release_year=1900,
                     release_date="1900-01-01",
                     original_title="Black Rain")
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

        self.delay_api_call()

        # Just one more test
        title = "Nineteen Eighty-Four"
        release_date = "1984-10-10"
        movie = Movie(title=title, release_year=1984,
                    release_date=release_date, original_title=title)
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
        release_date = "1980-01-01"
        movie = Movie(title=title, release_year=1980,
                     release_date=release_date,
                    original_title="23523532532")
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])
        self.assertIn('No review found for this movie.', result['message'])

        self.delay_api_call()

        # Gobbledygook: same title
        title = "3254343tertert4564363635465"
        release_date = "1980-01-01"
        movie = Movie(title=title, release_year=1980, release_date=release_date,
        original_title=title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])
        self.assertIn('No review found for this movie.', result['message'])

    def test_get_movie_review_one_result_found(self):
        self.delay_api_call()
        title = "Mulholland Drive"
        release_date = "2001-09-08"
        release_year = 2001
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])

        self.delay_api_call()
        title = "Lovely & Amazing"
        release_date = "2001-08-31"
        release_year = 2001 # NYT review written in 2002.
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])

    def test_get_movie_review_solaris_fake(self):
        self.delay_api_call()
        title = "Solaris"
        release_year = 2012
        release_date = "2012-01-01"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

    # Individual movies
    def test_get_review_solaris_2002(self):
            self.delay_api_call()
            title = "Solaris"
            release_year = 2002
            release_date = "2002-11-27"
            original_title = title
            movie = Movie(title=title,
                          release_year=release_year,
                          release_date=release_date,
                          original_title=original_title)
            result = NytMovieReview.get_movie_review(movie)
            self.assertTrue(result['success'])
            self.assertIn('cerebral science-fiction film', result['review'].text)

    def test_get_review_solaris_1972(self):
        self.delay_api_call()
        title = "Solaris"
        release_year = 1972
        release_date = "1972-03-20"
        original_title = "Солярис"
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn('Soviet psychologist on strange planet', result['review'].text)

    def test_get_review_sabrina_1995(self):
        self.delay_api_call()
        title = "Sabrina"
        release_year = 1995
        release_date = "1995-12-15"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn('Chauffeur\'s daughter loves playboy', result['review'].text)

    def test_get_review_catfight_2006(self):
        self.delay_api_call()
        title = "CatFight"
        release_year = 2006
        release_date = "2006-09-11"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

    def test_get_review_catfight_2017(self):
        self.delay_api_call()
        title = "Catfight"
        release_year = 2017
        release_date = "2017-03-03"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("jabs at callous privilege", result['review'].text)

    def test_get_review_catfight_2019(self):
        self.delay_api_call()
        title = "Catfight"
        release_year = 2019
        release_date = "2019-10-26"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

    def test_get_review_ghostintheshell_1995(self):
        self.delay_api_call()
        title = "Ghost in the Shell"
        release_year = 1995
        release_date = "1995-11-18"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

    def test_get_review_ghostintheshell_2017(self):
        self.delay_api_call()
        title = "Ghost in the Shell"
        release_year = 2017
        release_date = "2017-03-29"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("thrill-free science fiction thriller", result['review'].text)

    def test_get_review_blueisthewarmestcolor_2013(self):
        self.delay_api_call()
        title = "Blue Is The Warmest Color"
        release_year = 2013
        release_date = "2013-10-09"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("blissful attachment to another woman", result['review'].text)

    def test_get_review_dirtydancing_2017(self):
        self.delay_api_call()
        title = "Dirty Dancing"
        release_year = 2017
        release_date = "2017-05-24"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

    def test_get_review_dirtydancing_1987(self):
        self.delay_api_call()
        title = "Dirty Dancing"
        release_year = 1987
        release_date = "1987-08-21"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("Sweetly seething, like Swayze's samba.",
                        result['review'].text)

    def test_get_review_dirtydancinghavananights_2004(self):
        self.delay_api_call()
        title = "Dirty Dancing: Havana Nights"
        release_year = 2004
        release_date = "2004-02-27"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("desperation for a sweaty PG-13 sexiness", result['review'].text)

    def test_get_review_crystalfairy_2013(self):
        self.delay_api_call()
        title = "Crystal Fairy & the Magical Cactus"
        release_year = 2013
        release_date = "2013-07-12"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("a coke-and-pot-fueled party", result['review'].text)

    def test_get_review_amelie_2001(self):
        self.delay_api_call()
        title = "Amélie"
        release_year = 2001
        release_date = "2001-04-25"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("Jean-Pierre Jeunet", result['review'].text)

    def test_get_review_aubergeespagnole_2002(self):
        self.delay_api_call()
        title = "The Spanish Apartment"
        release_year = 2002
        release_date = "2002-05-17"
        original_title = "L'Auberge espagnole"
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,

                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("the new, borderless Europe", result['review'].text)

    def test_get_review_littlewomen_1917(self):
        self.delay_api_call()
        title = "Little Women"
        release_year = 1917
        release_date = '1917-07-02'
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,

                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

    def test_get_review_littlewomen_1933(self):
        self.delay_api_call()
        title = "Little Women"
        release_date = "1933-11-24"
        release_year = 1933
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("The Alcott classic, served to perfection" ,
                    result['review'].text)

    def test_get_review_littlewomen_2019(self):
        self.delay_api_call()
        title = "Little Women"
        release_year = 2019
        release_date = "2019-12-25"
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("Greta Gerwig refreshes a literary classic" ,
                    result['review'].text)

    # Testing 'second attempt' query; requires setting release date in Movie
    # object, and setting first_try switch to False.
    def test_get_review_kin_2018(self):
        self.delay_api_call()
        title = "Kin"
        release_year = 2018
        release_date = "2018-08-01"
        original_title = title

        movie = Movie(title=title,
                      release_year=release_year,
                      release_date=release_date,
                      original_title=original_title)

        result = NytMovieReview.get_movie_review(movie, first_try=False)

        self.assertTrue(result['success'])
        self.assertIn('fantasy wish fulfillment', result['review'].text)

    # Final bugs
    def test_get_review_no_release_year(self):
        self.delay_api_call()
        title = "Mulholland Drive"
        release_year = None
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        self.assertRaises(ValueError, NytMovieReview.get_movie_review,
                                movie)

    def test_get_review_no_release_date(self):
        self.delay_api_call()
        title = "Mulholland Drive"
        release_year = 2001
        release_date = None
        original_title = title
        movie = Movie(title=title,
                      release_year=release_year,
                      original_title=original_title)
        self.assertRaises(ValueError, NytMovieReview.get_movie_review,
                                movie)



if __name__ == "__main__":
    unittest.main()
