/**
 * @file Fetches NYT movie review using Cinescout API.
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
    console.log("getreview.js")
    
    const url = '/api/nyt-movie-review'

    // Body data: needs to be fetched from movie page.
    const film = {
        title: document.querySelector("#title").value,
        original_title: document.querySelector("#original-title").value, 
        release_year: parseInt(document.querySelector("#year").value), 
        release_date: document.querySelector("#date").value
    }

    // Request options: Don't forget to include your body data!
    const options = {
        method: 'POST', 
        body: JSON.stringify(film),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrftoken
        }
    }

    // Make API query...
    fetch(url, options)
    .then(response => {
        if(response.ok){
            return response.json()    
        } else {
            errData = response.json()
            throw new Error(`HTTP Error ${response.status}: ${errData.err_message}`);
        }
    })
    .then(reviewData => {
        // Review text or failure message will go here.
        const reviewTextElem = document.querySelector('.review-text');

        // See whether search actually came up with anything.
        if (reviewData.success){
            // Extract data.
            const criticsPick = reviewData.critics_pick;
            const reviewText = reviewData.review_text;
            const publicationDate = reviewData.publication_date;
            const reviewWarning = reviewData.review_warning;

            // Display review.
            reviewTextElem.textContent = reviewText;
            document.querySelector('.review').appendChild(reviewTextElem);

            // Display whether critics pick.
            if (criticsPick) {
                const criticsPickElem = document.createElement('span');
                criticsPickElem.title = "Critic's Pick";
                criticsPickElem.textContent = ' ⭐️';
                document.querySelector('.review').appendChild(criticsPickElem);
            }

            // Display publication info.
            const pubInfoElem = document.createElement('span');
            pubInfoElem.className = 'publication';
            let pubInfo = `New York Times, ${publicationDate}`;
            pubInfoElem.textContent = pubInfo;
            document.querySelector('.review').appendChild(document.createElement('br'));
            document.querySelector('.review').appendChild(pubInfoElem);

            // If needed, display review warning message.
            if (reviewWarning){
                // Create umbrella superscript and attach it to pub info. 
                const supElem1 =  document.createElement('sup');
                supElem1.textContent = ' ☂︎';
                document.querySelector('.publication').appendChild(supElem1);

                // Display warning at end of movie info page.
                const supElem2 =  document.createElement('sup');
                supElem2.textContent = '☂︎ ';
                const warning = "Because the release and review years are different, " +
                           "this movie review might be for another movie of a similar title.";
                warningElem = document.createElement('em');
                warningElem.textContent = warning;
                document.querySelector('#review-warning').appendChild(supElem2);
                document.querySelector('#review-warning').appendChild(warningElem);
            }
        } else {
            // Display message that film could not be found for whatever reason.
            message = reviewData.message;
            reviewTextElem.textContent = message; 
            document.querySelector('.review').appendChild(reviewTextElem);
        }
    })
    .catch(err => {
        const errTextElem = document.querySelector('.review-text');
        console.error(err.message);
        errTextElem.textContent = "An error has occurred. Please open console for more info.";
        document.querySelector('.review').appendChild(errTextElem);
    });
});