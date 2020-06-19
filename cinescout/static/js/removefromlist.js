/**
 * @file Removes movie from user list
 */

document.addEventListener('DOMContentLoaded', () => {

  console.log('removefromlist.js');

  buttons = document.querySelectorAll('.trash-button')

  if (buttons.length !== 0){
    document.querySelector("#empty-list-message").style.visibility = "hidden";
  }

  // if document.querySelectorAll('.trash-button') === null {
  //   console.log("No buttons!")
  // }



  buttons.forEach(button => {

    // Add event lister for each button
    button.onclick =  () => {

        console.log(`button value = ${button.value}`);

        // Get id of film you want to delete
        const tmdbId = button.value;

        const request = new XMLHttpRequest();
        request.open('POST', '/remove-from-list');

        request.onload = function() {
          // Extract JSON data
          const data = JSON.parse(request.responseText);


          if (data.success){
            console.log("Film removed from your list!!");
            // console.log(button.parentElement);
            // console.log(button.parentElement.parentElement);

            // Removes row from table.
            button.parentElement.parentElement.remove();

            console.log(document.querySelectorAll('.trash-button').length);

            if (document.querySelectorAll('.trash-button').length === 0) {
                console.log("Setting to visible!");
                document.querySelector("#empty-list-message").style.visibility = "visible";
            }
            else document.querySelector("#empty-list-message").style.visibility = "hidden";

            // button.previousElementSibling.remove();
            // button.remove();
          }else{
            // Film could not be removed for some reason...
            console.error(`Error: ${data.err_message}`);
            alert(`Error: Remove Film failed.\n${data.err_message}`);
          }

        };


        const data = new FormData();
        data.append('tmdb_id', tmdbId);

        // Send request
        request.send(data);
        return false;

    };


  });




  //
  // form = document.querySelector('#list-form')
  //
  // form.addEventListener('submit', () => {
  //
  //   alert(this.id);
  //
  //
  //   // Initialize new request
  //   const filmId = document.querySelector("button[name='remove']").value;
  //   console.log(filmId);
  //   alert("Item removed!")
  //
  //   // const request = new XMLHttpRequest();
  //   //
  //   //
  //   // request.open('POST', '/remove-item');
  //   //
  //   //
  //   // // Send form data with request
  //   // const data = new FormData();
  //   // data.append()
  //
  // });



});
