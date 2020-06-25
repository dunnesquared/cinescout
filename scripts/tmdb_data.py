"""Scrapes TMDB for tmdb_id given film name and release year."""

import os
import time
import json
import requests
import csv

# So Python can find the data files.
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_API_DELAY = 0.5

# Input file
FILM_FILE = os.path.join(DATA_PATH, "films.csv")

# Output files
FOUND_FILE = os.path.join(DATA_PATH, "found.csv")
NOTFOUND_FILE = os.path.join(DATA_PATH, "notfound.csv")

def main():

    # Films in which a tmdb id is found.
    films = []
    # Films in which a tmdb id cannot be found.
    not_found = []

    try:
        # Import data.
        with open(FILM_FILE, newline='') as csvfile:
            reader = csv.reader(csvfile)

            # Skip the header line.
            next(reader, None)

            # For each line in the csv file...
            for spine_num, title, director, release_year in reader:

                tmdb_id = None

                print(f"Searching for {title}, {release_year}, in TMDB database...",
                        end="")

                # Make API call.
                res = requests.get("https://api.themoviedb.org/3/search/movie",
                                    params={"api_key": TMDB_API_KEY,
                                                "query": title.strip(),
                                                "year": int(release_year)
                                                })

                if res.status_code != 200:
                    return f"TMDB lookup: Something went wrong, Status code {res.status_code}"

                # Unpack JSNO response.
                tmdb_data = res.json()

                # No results for given movie title and year.
                if tmdb_data["total_results"] == 0:
                    print("No luck☹️!")
                    not_found.append({'title': title,
                                  'director': director,
                                  'spine_num': spine_num,
                                  'release_year': release_year,
                                  'tmdb_id': None
                                  })

                # Multiple resulsts for given movie title and year.
                if tmdb_data["total_results"] > 1:
                    # Get results for each movie
                    print("More than one movie found.")
                    print("Attempting to find right movie...", end="")

                    # Best bet: take movie that has exactly the same title.
                    # Might not get the right result even if match
                    # (thus, iffy: True)
                    for result in tmdb_data['results']:
                        if result['title'].lower().strip() == title.lower().strip():
                            tmdb_id = result['id']
                            films.append({'title': title,
                                          'director': director,
                                          'spine_num': spine_num,
                                          'release_year': release_year,
                                          'tmdb_id': tmdb_id,
                                          'iffy': True
                                          })
                            msg = "Found (hopefully the right film🙏🏻)!!"

                    # No match
                    if tmdb_id is None:
                        not_found.append({'title': title,
                                      'director': director,
                                      'spine_num': spine_num,
                                      'release_year': release_year,
                                      'tmdb_id': None
                                      })
                        msg = "No luck☹️!"

                    print(msg)

                # Found exactly one result for given movie and year (ideal)/
                if tmdb_data["total_results"] == 1:
                    print("Found😆!!")
                    film = tmdb_data["results"][0]
                    tmdb_id = film['id']
                    films.append({'title': title,
                                  'director': director,
                                  'spine_num': spine_num,
                                  'release_year': release_year,
                                  'tmdb_id': tmdb_id,
                                  'iffy': False
                                  })

                # So tmdb doesn't block the script.
                print(f"Delaying next TMDB API call by {TMDB_API_DELAY} seconds...")
                time.sleep(TMDB_API_DELAY)

            print("Scraping complete.")

            # Output the results.
            print("Writing films to output files...", end="")

            with open(FOUND_FILE, 'w') as fin:
                fin.write("release_year,title,director,spine_num,tmdb_id,iffy\n")
                for film in films:
                    fin.write(f"{film.get('release_year')},{film.get('title')},{film.get('director')},{film.get('spine_num')},{film.get('tmdb_id')},{film.get('iffy')}\n")

            with open(NOTFOUND_FILE, 'w') as fin:
                fin.write("release_year,title,director,spine_num,tmdb_id\n")
                for film in not_found:
                    fin.write(f"{film.get('release_year')},{film.get('title')},{film.get('director')},{film.get('spine_num')},{film.get('tmdb_id')}\n")

            return "Script complete. No problems."

    except OSError as err:
        print("OSError: {0}".format(err))


# Launch script.
if __name__ == "__main__":
    print("===== Running TMDB_DATA.PY script =====")
    # Print status message.
    print(main())
