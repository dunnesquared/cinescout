/**
 * @file Adds and removes a movie to user list from movie page.
 */

document.addEventListener('DOMContentLoaded', () => {
  console.log("addremove.js")

  let remove_button = document.querySelector("#remove-button");
  let add_button = document.querySelector("#add-button");

  // Add or remove button only show up when user is logged in.
  if (add_button === null && remove_button === null){
    return
  }

  // Add film.
  if (add_button){
    console.log("Add button exists.")
    add_button.onclick = () => {
      add_film_to_list();
    };
  }

  // Remove film
  if (remove_button){
    console.log("Remove button exists.")
    remove_button.onclick = () => {
      remove_film_from_list()
    };
  }


  // Add-film handler function
  function add_film_to_list () {
    console.log("Add button clicked...")
    console.log("Attempting to add film to list...");

    // Get data values to be sent to backend route.
    console.log(`tmdb-id: ${document.querySelector("#tmdb-id").value}`);
    console.log(`title: ${document.querySelector("#title").value}`);
    console.log(`year: ${document.querySelector("#year").value}`);
    console.log(`date: ${document.querySelector("#date").value}`);
    console.log(`original title: ${document.querySelector("#original-title").value}`);

    const tmdbId = document.querySelector("#tmdb-id").value;
    const title = document.querySelector("#title").value;
    const year = document.querySelector("#year").value;
    const date = document.querySelector("#date").value;
    const originalTitle = document.querySelector("#original-title").value;

    // Initialize new AJAX request.
    const request = new XMLHttpRequest();
    request.open('POST', '/add-to-list');

    // Call-back function for when request completes.
    request.onload = () => {
      const data = JSON.parse(request.responseText);

      if (data.success) {
        console.log("Film addedd to list!");

        // Remove Add button...
        console.log("Removing Add button...");
        add_button.remove();

        //..and replace with Remove button.
        let buttonContainer = document.querySelector("#button-container");
        const removeButton = document.createElement('button');
        removeButton.id = 'remove-button';
        removeButton.type = 'submit';
        removeButton.innerHTML = '<h2>Remove film</h2>';
        removeButton.className = 'btn btn-secondary';
        buttonContainer.append(removeButton);

        // Updata remove_button state.
        remove_button = document.querySelector("#remove-button");

        // Remove film if Remove button clicked.
        remove_button.onclick = () => {
            remove_film_from_list();
        }
      }else{
        // Film could not be added for some reason...
        console.error(`Error: ${data.err_message}`);
        alert(`Error: Add Film failed.\n${data.err_message}`);
      }
    };

    // Add POST data to send with request.
    const data = new FormData();
    data.append('tmdb_id', tmdbId);
    data.append('title', title);
    data.append('year', year);
    data.append('date', date);
    data.append('original_title', originalTitle)

    // Send request.
    request.send(data);
    return false;
  }


  function remove_film_from_list () {
    console.log("Remove button clicked...");
    console.log("Attempting to remove film from list...");

    // Get id of film you want to delete.
    const tmdbId = document.querySelector('#tmdb-id').value;
    console.log(`tmdbId = ${tmdbId}`);

    // Initialize new AJAX request.
    const request = new XMLHttpRequest();
    request.open('POST', '/remove-from-list');

    request.onload = function() {
      // Extract JSON data.
      const data = JSON.parse(request.responseText);

      if (data.success){
        // Delete remove button...
        remove_button.remove();

        // and replace with Add button
        let buttonContainer = document.querySelector("#button-container");
        const addButton = document.createElement('button');
        addButton.id = 'add-button';
        addButton.type = 'submit';
        addButton.innerHTML = '<h2>Add to list</h2>';
        addButton.className ='btn btn-secondary'
        buttonContainer.append(addButton);

        // Updata add_button state
        add_button = document.querySelector("#add-button");

        // Add film if clicked.
        add_button.onclick = () => {
            add_film_to_list();
        }
      }else{
        // Film could not be removed for some reason...
        console.error(`Error: ${data.err_message}`);
        alert(`Error: Remove Film failed.\n${data.err_message}`);
      }
    };

    // Add POST data to send with request.
    const data = new FormData();
    data.append('tmdb_id', tmdbId);

    // Send request
    request.send(data);
    return false;
  }
});
