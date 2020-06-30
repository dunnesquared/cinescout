/**
*@file Renders dynamic table of movies from The Criterion Collection.
**/

document.addEventListener('DOMContentLoaded', () => {
  console.log("browse.js");

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

          // Get all directors names.
          let directorsText = "";
          if (film.directors.length > 1){
            directorsText = film.directors.join(' & ')
          }else{
            directorsText = film.directors[0];
          }

          // cellTitle.innerHTML = film.title;
          cellTitle.append(linkTitle);
          cellYear.innerHTML = film.year;
          cellDirectors.innerHTML = directorsText;
          //cellDirectors.innerHTML = film.directors[0];

        });

        console.log(data.num_results);
        console.log(data.results);

      }
      else {
        console.log("Oh no...");
      }
    }

  request.send();

});
