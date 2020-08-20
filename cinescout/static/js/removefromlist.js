/**
 * @file Removes movie from user list.
 */

 // Need to prevent possible cross-site-requeest-forgery attacks
 // made using AJAX requests that modify the database.
 var csrftoken = document.querySelector("meta[name=csrf-token]").content;

 // Just in case...
 if (csrftoken)
   console.log("CSRF token loaded.")
 else
   console.error("CSRF token invalid.")


document.addEventListener('DOMContentLoaded', () => {

  console.log('removefromlist.js');

  // Only display empty list message if there are no remove buttons on list.
  // Each time a film is removed, its remove button goes with it.
  buttons = document.querySelectorAll('.trash-button')

  if (buttons.length !== 0){
    document.querySelector("#empty-list-message").style.visibility = "hidden";
  }

  // For all buttons...
  buttons.forEach(button => {
    // Add event listener when button is clicked.
    button.onclick =  () => {
        // Debug purposes.
        console.log(`button value = ${button.value}`);

        // Get id of film you want to delete.
        const tmdbId = button.value;

        // Initialize new AJAX request to remove film.
        const request = new XMLHttpRequest();
        request.open('POST', '/remove-from-list');

        // Add CSRF token to AJAX request (NB: request must be open first before
        // adding token).
        request.setRequestHeader('X-CSRF-Token', csrftoken);

        // Call back function to execute once request completed.
        request.onload = function() {
          // Extract JSON data
          const data = JSON.parse(request.responseText);

          // Film removed from db!
          if (data.success){
            console.log("Film removed from your list!!");

            // Removes row from movie-list table, in essence a movie.
            button.parentElement.parentElement.remove();

            // If there are no buttons on the list, then the list is empty.
            // Make visible the no-films-on-list message.
            console.log("Number of buttons left on list:")
            console.log(document.querySelectorAll('.trash-button').length);

            if (document.querySelectorAll('.trash-button').length === 0) {
                console.log("Setting to visible!");
                document.querySelector("#empty-list-message").style.visibility = "visible";
            }
            else document.querySelector("#empty-list-message").style.visibility = "hidden";

          }else{
            // Film could not be removed for some reason...
            console.error(`Error: ${data.err_message}`);
            alert(`Error: Remove Film failed.\n${data.err_message}`);
          }
        };

        // Pack-up POST data to backend route.
        const data = new FormData();
        data.append('tmdb_id', tmdbId);

        // Send request
        request.send(data);
        return false;
    };
  });
});
