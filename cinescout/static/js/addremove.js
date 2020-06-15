/**
 * @file Adds movie to user list
 */

document.addEventListener('DOMContentLoaded', () => {
  console.log("add.js")


  let remove_button = document.querySelector("#remove-button");
  let add_button = document.querySelector("#add-button");


  // Add or remove button only show up when user is logged in.
  if (add_button === null && remove_button === null){
    return
  }

  // Add film
  if (add_button){
    add_button.onclick = () => {
      add_film_to_list();
      // console.log("Attempting to add film to list...");
      //
      //
      // // Get data values to be sent to route
      // console.log(`tmdb-id: ${document.querySelector("#tmdb-id").value}`);
      // console.log(`title: ${document.querySelector("#title").value}`);
      // console.log(`year: ${document.querySelector("#year").value}`);
      //
      // const tmdbId = document.querySelector("#tmdb-id").value;
      // const title = document.querySelector("#title").value;
      // const year = document.querySelector("#year").value;
      //
      // // Initialize new request
      // const request = new XMLHttpRequest();
      // request.open('POST', '/add-to-list');
      //
      // // Call back function for when request completes
      // request.onload = () => {
      //   const data = JSON.parse(request.responseText);
      //
      //   if (data.success) {
      //     console.log("Film addedd to list!");
      //     alert("Film added to list!")
      //
      //     // Remove add button
      //     console.log("Removing Add button...");
      //     add_button.remove();
      //
      //     // Replace with remove button
      //     let buttonContainer = document.querySelector("#button-container");
      //     const removeButton = document.createElement('button');
      //     removeButton.id = 'remove-button';
      //     removeButton.type = 'submit';
      //     // removeButton.value =
      //     removeButton.innerHTML = '<h2>➖ Remove film from list </h2>';
      //     buttonContainer.append(removeButton);
      //
      //     // Updata remove_button state
      //     remove_button = document.querySelector("#remove-button");
      //
      //     // Remove film
      //     remove_button.onclick = () => {
      //         remove_film_from_list();
      //     }
      //
      //   }else{
      //     console.log("Error: film could not be added to list.");
      //   }
      //
      // };
      //
      // // Add data to send with request
      // const data = new FormData();
      // data.append('tmdb_id', tmdbId);
      // data.append('title', title);
      // data.append('year', year);
      //
      // // Send request
      // request.send(data);
      // return false;
    };
  }

  // Remove film
  if (remove_button){
    console.log("remove button exists.")
    remove_button.onclick = () => {
      remove_film_from_list()
    };
  }


  // Handler AJAX functions
  function add_film_to_list () {
    console.log("FILM ADDED!!");
    console.log("Attempting to add film to list...");


    // Get data values to be sent to route
    console.log(`tmdb-id: ${document.querySelector("#tmdb-id").value}`);
    console.log(`title: ${document.querySelector("#title").value}`);
    console.log(`year: ${document.querySelector("#year").value}`);

    const tmdbId = document.querySelector("#tmdb-id").value;
    const title = document.querySelector("#title").value;
    const year = document.querySelector("#year").value;

    // Initialize new request
    const request = new XMLHttpRequest();
    request.open('POST', '/add-to-list');

    // Call back function for when request completes
    request.onload = () => {
      const data = JSON.parse(request.responseText);

      if (data.success) {
        console.log("Film addedd to list!");
        // alert("Film added to list!")

        // Remove add button
        console.log("Removing Add button...");
        add_button.remove();

        // Replace with remove button
        let buttonContainer = document.querySelector("#button-container");
        const removeButton = document.createElement('button');
        removeButton.id = 'remove-button';
        removeButton.type = 'submit';
        // removeButton.value =
        removeButton.innerHTML = '<h2>➖ Remove film from list </h2>';
        buttonContainer.append(removeButton);

        // Updata remove_button state
        remove_button = document.querySelector("#remove-button");

        // Remove film
        remove_button.onclick = () => {
            remove_film_from_list();
        }

      }else{
        console.log("Error: film could not be added to list.");
        alert("Error: film could not be added to list. This film may already be on your list. Refresh the page and try again.");
      }

    };

    // Add data to send with request
    const data = new FormData();
    data.append('tmdb_id', tmdbId);
    data.append('title', title);
    data.append('year', year);

    // Send request
    request.send(data);
    return false;
  }



  function remove_film_from_list () {
    console.log("Remove button clicked.");
    console.log("Attempting to remove film from list...");

    // Get id of film you want to delete
    const tmdbId = document.querySelector('#tmdb-id').value;
    console.log(`tmdbId = ${tmdbId}`);

    const request = new XMLHttpRequest();
    request.open('POST', '/remove-from-list');

    request.onload = function() {
      // Extract JSON data
      const data = JSON.parse(request.responseText);

      if (data.success){
        // alert("Film removed from your list!!");

        // Delete remove button and replace with add button
        remove_button.remove();

        // Replace with remove button
        let buttonContainer = document.querySelector("#button-container");
        const addButton = document.createElement('button');
        addButton.id = 'add-button';
        addButton.type = 'submit';
        // removeButton.value =
        addButton.innerHTML = '<h2>➕ Add film to list</h2>';
        buttonContainer.append(addButton);

        // Updata remove_button state
        add_button = document.querySelector("#add-button");

        // Remove film
        add_button.onclick = () => {
            add_film_to_list();
        }

      }else{
        console.log("Error: could not remove film from list.");
        alert("Error: could not remove film from list. This film may already be off your list. Refresh the page and try again.");
      }

    };

    const data = new FormData();
    data.append('tmdb_id', tmdbId);

    // Send request
    request.send(data);
    return false;

  }


});
