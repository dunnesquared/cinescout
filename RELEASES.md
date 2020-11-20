# Cinescout🎞: Releases

### 1.4
- Display hyperlink on Movie page that queries Google for more information on respective movie 

### 1.3
- Display cast and crew credits for a searched film
- Minor bug fixes


### 1.2
- New 'About' page
- Version number accessible across templates
- Minor changes

### 1.1.2
- Minor bug fix to ensure deletion of records in parent tables also deletes records in child tables

### 1.1.1
- Minor bug fix to ensure unittest script `test_views.py` runs correctly

### 1.1.0
- Addition of admin panel to view/modify database via Flask-Admin
- Forms for easy user registration and password change from admin panel
- Removal of view that allowed users to register for Cinescout; now exclusive domain of admin
- No longer displaying NYT movie reviews to anonymous users; now only for registered users

### 1.0.1
- Fixed Cross-Origin-Request errors blocking JS scripts in Safari in live demo
- Disabled movie-link spinners until back-forward cache issue resolved
- Updated README: clearer setup instructions for Windows users
- Minor bug fixes and aesthetic changes

### 1.0
- Redesign and unit-test of NYT review-fetching algorithm for faster retrievals
- Redesign of 'Browse' feature to support sorting and searching of movie list  
- AJAX requests secured against potential CSRF attacks when adding/removing film from personal list
- Refactored setup script to be more flexible and robust to user input
- Users now able to query movie and person results via an HTTP GET request
- Photo of cast or crew member on Filmography page now displayed
- UI improvements: highlighted menu buttons, spinners, and streamlined-look for forms
- Minor bug fixes
