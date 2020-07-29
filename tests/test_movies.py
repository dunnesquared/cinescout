import os
import unittest
# import json

# Add this line to whatever test script you write
from context import app, NytMovieReview



class NytMovieReviewTests(unittest.TestCase):
    def setUp(self):
        # """Executes before each test."""
        print("Setting up NytMovieReviewTests...")

        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()


    def tearDown(self):
        """Executes after each test."""
        print("Tearing down NytMovieReviewTests...")

    def test_createReview(self):
        """Create a NytMovieReview object.

            Attributes:
                title: Striing representing the title of movie reviewed.
                year: Integer representing the release year of the movie.
                text: String containing summary of movie review.
                publication_date: String representing date review was published.
                critics_pick: Boolean representing whether movie is NYT critic's pick.
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


if __name__ == "__main__":
    unittest.main()
