/**
*@file Renders dynamic table of movies from The Criterion Collection.
**/


document.addEventListener('DOMContentLoaded', () => {
  console.log("browse.js");

  document.querySelector("#table-footnote-container").style.visibility = 'hidden';


  // Show spinner for a few moments
  setTimeout(function () {
      // Hide spinner
    let spinnerContainer = document.querySelector("#spinner-container");
    spinnerContainer.style.display = 'none';

    const url = "api/criterion-films";
    console.log(`Making AJAX request to ${url}...`);

    const request = new XMLHttpRequest();
    request.open('GET', '/api/criterion-films');

    request.onload = () => {
        const data = JSON.parse(request.responseText);

        if (data.success){
          console.log("Horray! Criterion film results returned.");
          const films = data.results;

          let criterionTable = document.getElementById("criterion-table").getElementsByTagName('tbody')[0];

          films.forEach(film => {
            console.log(`${film.title}, ${film.year}, ${film.directors}`);

            // Create row.
            let row = criterionTable.insertRow();

            // Create cells in row.
            let cellTitle = row.insertCell(0);
            let cellYear = row.insertCell(1);
            let cellDirectors = row.insertCell(2);

            // Create anchor that will link to movie page of given title.
            const linkTitle = document.createElement('a');
            linkTitle.href = `/movie/${film.tmdb_id}`
            linkTitle.className = 'text-white';
            const textTitle = document.createTextNode(`${film.title}`);
            linkTitle.appendChild(textTitle);
            cellTitle.append(linkTitle);

            // Add year film was released to table.
            cellYear.innerHTML = film.year;

            // Create list of hyperlinks for directors; append & in between.

            // Many of the names in directors are not know specifically for 'Directing'
            // E.g. Charlie Chaplin is better known for 'Acting'
            const known_for = 'All';

            // Go through list of directors...
            for (let i = 0; i < film.directors.length; i++){
              // Create hyperlink for each director.
              const linkDirector = document.createElement('a');
              linkDirector.href = `/person-search?name=${film.directors[i]}&known_for=${known_for}`
              linkDirector.className = 'text-white';
              const textDirector = document.createTextNode(`${film.directors[i]}`);
              linkDirector.appendChild(textDirector);

              // Append that link to the table cell for directors
              cellDirectors.append(linkDirector)

              // Determine whether to add an ampersand or just stop.
              if (i === film.directors.length - 1){
                break;
              } else{
                cellDirectors.append(' & ');
              }
            }
          });

          console.log(data.num_results);
          console.log(data.results);

          document.querySelector("#table-footnote-container").style.visibility = 'visible';
        }
        else {
          console.log("Oh no...");
        }

      }

    // Send data
    request.send();

  }, 800);




});
