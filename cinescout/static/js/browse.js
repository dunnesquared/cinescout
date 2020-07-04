/**
*@file Renders dynamic table of movies from The Criterion Collection.
**/

// Timeout function's time limit, in milliseconds.
const TIME_MAX = 800;


/**
* Displays Criterion movies list.
*/
document.addEventListener('DOMContentLoaded', () => {
  console.log("browse.js");

  // Don't display the table until timer has eneded.
  document.querySelector("#table-footnote-container").style.visibility = 'hidden';

  /**
  * Show spinner for a few moments before displayin list of Criterion films.
  */
  setTimeout(function () {
    // Once time's up, hide the spinner that's been running since page has loaded.
    hideSpinner();

    // Make AJAX request for table data; display table.
    fetchCriterionTableData();

  }, TIME_MAX);
});


/**
* Hides loading spinner.
*/
function hideSpinner () {
  // Hide spinner
  let spinnerContainer = document.querySelector("#spinner-container");
  spinnerContainer.style.display = 'none';
};


/**
* Makes AJAX request to server api for Criterion movie data.
*/
function fetchCriterionTableData() {

  const url = "api/criterion-films";
  console.log(`Making AJAX request to ${url}...`);

  const request = new XMLHttpRequest();
  request.open('GET', '/api/criterion-films');

  request.onload = () => {

      const data = JSON.parse(request.responseText);

      if (data.success){

        console.log("Horray! Criterion film results returned.");

        const films = data.results;
        populateTable(films);

        // Display table.
        document.querySelector("#table-footnote-container").style.visibility = 'visible';

        console.log(data.num_results);
        console.log(data.results);
      }
      else {
        // Film could not be added for some reason...
        console.error(`Error: ${data.err_message}`);
        alert(`Error: Failed to load CriterionTable data:\n${data.err_message}`);
      }
    }

  // Send data
  request.send();
};


/**
* Populates table rows with data.
*/
function populateTable (films) {

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
    linkTitle.className = 'text-white table-cell';
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
      linkDirector.className = 'text-white table-cell';
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

  // Use DataTables jQuery extension to provide sortable rows and other features.
  $(document).ready( function () {
    // dom => for positioning Search filter box to the left.
    // paging => Don't want pagination feature on.
    // order => Should display movies from oldest to newest
    $('#criterion-table').DataTable( {
        "dom": '<"wrapper"ft>',
        'paging': false,
        'order': [[1, "asc"]],
        'responsive': true
      } );
  } );

}
