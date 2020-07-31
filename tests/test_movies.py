import os
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
        expected = "No review: film has yet to be released."

        # Future release
        movie = Movie(release_date="2999-12-31")
        result = NytMovieReview.get_movie_review(movie)
        self.assertEqual(expected, result['message'])

        # Past release
        movie = Movie(release_date="1999-12-31")
        result = NytMovieReview.get_movie_review(movie)
        self.assertNotEqual(expected, result['message'])

        # Released today
        movie = Movie(release_date=datetime.today().strftime('%Y-%m-%d'))
        result = NytMovieReview.get_movie_review(movie)
        self.assertNotEqual(expected, result['message'])

    def test_get_movie_review_exception(self):
        # Exception: in exception list, matching year
        movie = Movie(title="Black Rain", release_year=1989,
                     original_title="Black Rain")
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("Mechanical police melodrama.", result['review'].text)

        # Exception: in exception list, not matching year
        movie = Movie(title="Black Rain", release_year=1900,
                     original_title="Black Rain")
        result = NytMovieReview.get_movie_review(movie)
        self.assertFalse(result['success'])

        # Just one more test
        movie = Movie(title="Nineteen Eighty-Four", release_year=1984)
        result = NytMovieReview.get_movie_review(movie)
        self.assertTrue(result['success'])
        self.assertIn("Big Brother rewriting history", result['review'].text)



if __name__ == "__main__":
    unittest.main()
