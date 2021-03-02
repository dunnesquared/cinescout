"""Unit-test script of movies module"""

import unittest

# Add this line to whatever test script you write
from context import app, Movie, TmdbMovie


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

    # duckduckgoquery
    # ---------------
    def testDuckDuckGoQueryNormal(self):
        expected = "https://duckduckgo.com/?q=Tenet%202020%20film"
        result = self.testmovie.duckduckgoquery()
        self.assertEqual(expected, result)
        
    def testDuckDuckGoQueryNoTitles(self):
        self.testmovie.title = None
        self.testmovie.original_title = None
        self.assertRaises(ValueError, self.testmovie.duckduckgoquery)

    def testDuckDuckGoQueryOriginalTitleOnly(self):
        self.testmovie.title = None
        self.testmovie.original_title = 'Tenet'
        self.assertRaises(ValueError, self.testmovie.duckduckgoquery)
    
    def testDuckDuckGoQueryEnglishTitleOnly(self):
        self.testmovie.original_title = None
        expected = "https://duckduckgo.com/?q=Tenet%202020%20film"
        result = self.testmovie.duckduckgoquery()
        self.assertEqual(expected, result)
    
    def testDuckDuckGoQueryBlankSpacesBothTitles(self):
        self.testmovie.title = '    '
        self.testmovie.original_title ='\n\t  '
        self.assertRaises(ValueError, self.testmovie.duckduckgoquery)
    
    def testDuckDuckGoQueryNoReleaseYear(self):
        self.testmovie.release_year = None
        expected = "https://duckduckgo.com/?q=Tenet%20film"
        result = self.testmovie.duckduckgoquery()
        self.assertEqual(expected, result)
    
    def testDuckDuckGoQueryBadReleaseYear(self):
        self.testmovie.release_year = "-128"
        expected = "https://duckduckgo.com/?q=Tenet%20-128%20film"
        result = self.testmovie.duckduckgoquery()
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
    
    # querymaker
    # ----------- 
    def testQueryMakerGoogle(self):
        search_engine = 'google'
        result = self.testmovie.querymaker(search_engine=search_engine)
        expected = self.testmovie.googlequery
        self.assertEqual(expected, result)
    
    def testQueryMakerDuckDuckGo(self):
        search_engine = 'duckduckgo'
        result = self.testmovie.querymaker(search_engine=search_engine)
        expected = self.testmovie.duckduckgoquery
        self.assertEqual(expected, result)
    
    def testQueryMakerDiffCase(self):
        search_engine = 'Duckduckgo'
        result = self.testmovie.querymaker(search_engine=search_engine)
        expected = self.testmovie.duckduckgoquery
        self.assertEqual(expected, result)
    
    def testQueryMakerNone(self):
        search_engine = None
        self.assertRaises(ValueError, self.testmovie.querymaker, search_engine)
    
    def testQueryMakerBlank(self):
        search_engine = "    "
        self.assertRaises(ValueError, self.testmovie.querymaker, search_engine)
    
    def testQueryMakerBadName(self):
        search_engine = "AskJeevus"
        self.assertRaises(ValueError, self.testmovie.querymaker, search_engine)

    # get_query
    # ----------- 
    def testGetQueryGoogle(self):
        search_engine = 'google'
        result = self.testmovie.get_query(search_engine=search_engine)
        expected = "https://www.google.com/search?q=Tenet%202020%20film"
        self.assertEqual(expected, result)
    
    def testGetQueryDuckDuckGo(self):
        search_engine = 'duckduckgo'
        result = self.testmovie.get_query(search_engine=search_engine)
        expected = "https://duckduckgo.com/?q=Tenet%202020%20film"
        self.assertEqual(expected, result)
    
    def testGetQueryDiffCase(self):
        search_engine = 'Duckduckgo'
        result = self.testmovie.get_query(search_engine=search_engine)
        expected = "https://duckduckgo.com/?q=Tenet%202020%20film"
        self.assertEqual(expected, result)
    
    def testGetQueryNone(self):
        search_engine = None
        self.assertRaises(ValueError, self.testmovie.get_query, search_engine)
    
    def testGetQueryBlank(self):
        search_engine = "    "
        self.assertRaises(ValueError, self.testmovie.get_query, search_engine)
    
    def testGetQueryBadName(self):
        search_engine = "AskJeevus"
        self.assertRaises(ValueError, self.testmovie.get_query, search_engine)


if __name__ == "__main__":
    unittest.main()
