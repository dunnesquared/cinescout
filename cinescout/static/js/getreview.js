/**
 * @file Fetches movie review.
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
});