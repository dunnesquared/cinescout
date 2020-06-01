"""Scrapes TMDB for tmdb_id given film name and year """

import os
import time
import json
import requests
import csv

# So Python can find the data files
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_API_DELAY = 0.5

FILM_FILE = os.path.join(DATA_PATH, "films.csv")
FOUND_FILE = os.path.join(DATA_PATH, "found.csv")
NOTFOUND_FILE = os.path.join(DATA_PATH, "notfound.csv")

def main():

    films = []
    not_found = []

    try:

        # Import data
        with open(FILM_FILE, newline='') as csvfile:
            reader = csv.reader(csvfile)

            # Skip the header line
            next(reader, None)

            # To inform user of current of record being outputted
            count = 1

            # Insert data into database
            for title, year in reader:

                tmdb_id = None

                print(f"Searching for {title}, {year}, in TMDB database...", end="")

                # Make API call
                res = requests.get("https://api.themoviedb.org/3/search/movie",
                                    params={"api_key": TMDB_API_KEY,
                                                "query": title.strip(),
                                                "year": int(year)
                                                })

                if res.status_code != 200:
                    return f"TMDB lookup: Something went wrong, Status code {res.status_code}"

                tmdb_data = res.json()

                if tmdb_data["total_results"] == 0:
                    print("No luck☹️!")
                    not_found.append((title, year))

                if tmdb_data["total_results"] > 1:
                    # Get results for each movie
                    print("More than one movie found.")
                    print("Attempting to find right movie...", end="")

                    for result in tmdb_data['results']:
                        if result['title'].strip() == title.strip():
                            tmdb_id = result['id']
                            films.append((title, year, tmdb_id))
                            msg = "Found🙏🏻!!"

                    # msg = "No luck☹️" if tmdb_id is None else "Found🙏🏻!!"

                    if tmdb_id is None:
                        not_found.append((title, year))
                        msg = "No luck☹️!"


                    print(msg)


                if tmdb_data["total_results"] == 1:
                    print("Found😆!!")
                    film = tmdb_data["results"][0]
                    tmdb_id = film['id']
                    films.append((title, year, tmdb_id))

                print(f"Delaying next TMDB API call by {TMDB_API_DELAY} seconds...")
                time.sleep(TMDB_API_DELAY)

                count += 1

            print("Scraping complete.")

            # print(f"\nFILMS:")
            # for film in films:
            #     print(film)

            print("Writing films to output files...", end="")

            with open(FOUND_FILE, 'w') as fin:
                fin.write("title,year,tmdb_id\n")
                for film in films:
                    fin.write(f"{film[0]},{film[1]},{film[2]}\n")

            with open(NOTFOUND_FILE, 'w') as fin:
                fin.write("title,year,tmdb_id\n")
                for film in not_found:
                    fin.write(f"{film[0]},{film[1]},{None}\n")


            return "Script complete. No problems."

    except OSError as err:
        print("OSError: {0}".format(err))



if __name__ == "__main__":
    print("===== Running TMDB_DATA.PY script =====")
    print(main())
