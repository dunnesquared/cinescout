"""Script to run all test classes.

Adapted from example at 
https://subscription.packtpub.com/book/application_development/9781849514668/1/ch01lvl1sec13/chaining-together-a-suite-of-tests
"""


if __name__ == "__main__":
    import unittest

    # Import all test cases
    from test_api_criterion import *
    from test_api_nytreview import *
    from test_api_usermovielist import *
    from test_auth import *
    from test_main import *
    from test_movies import *
    from test_reviews import *

    # List object makes it easier to add a test case in the future.
    test_cases = [
        CriterionApiTests,
        NytReviewApiTests,
        UserMovieListApiTests,
        AuthTests,
        MainViewsTests,
        MovieTests,
        NytMovieReviewTests,
    ]

    # Load tests, build suite and run.
    tests = [unittest.TestLoader().loadTestsFromTestCase(test_case)
             for test_case in test_cases]
    suite = suite = unittest.TestSuite(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
