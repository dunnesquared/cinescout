/**
*@file Renders a spinner until movie page loads.
**/


console.log("loadspinner.js");

// After X milliseconds, stop showing the spinner. 
const DELAY = 10000;

document.addEventListener('DOMContentLoaded', () => {
  showMovieSpinners(DELAY);
});


/**
* Adds spinners next to movie hyperlinks that are clicked.
* Export function so it can be used in other scripts such as browsw.js.
*/
export function showMovieSpinners (delay) {

  // When any movie link clicked, display spinner for a max of n miliseconds.
  let movieLinks = document.querySelectorAll('.movie-link');

  let previousSpinner = null;
  let spinner = null;

  if (movieLinks.length !== 0){
    // For all movie links...
    movieLinks.forEach(movieLink => {
      // Hide the spinners when the page is initially loaded.
      movieLink.querySelector('span').style.visibility = 'hidden';

      movieLink.onclick = () => {
        console.log("Link clicked; showing spinner...");

        // Unhide spinner associated with clicked link.
        spinner = movieLink.querySelector('span');

        // If use clicks more than one link while another is spinning,
        // turn off first spinner, start the spinner for the most recently
        // clicked link, and remember this last spinner so you can
        // turn it off should a user click another link, and so on...
        if (previousSpinner !== null) {
          if (previousSpinner.style.visibility === 'visible'){
            console.log("Another link clicked; hiding spinner of previously-clicked link.")
            previousSpinner.style.visibility = 'hidden';
          }
        }

        // Show the spinner...
        spinner.style.visibility = 'visible';

        // So we turn off the right spinner if user clicks yet again..
        previousSpinner = spinner;

        // So that spinner doesn't display forever...
        setTimeout(function () {
          console.log("Times up! Hiding spinner...")
          spinner.style.visibility = 'hidden';
        }, delay);
      }
    });
  }

}
