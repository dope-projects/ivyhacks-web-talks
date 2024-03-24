console.log('contentScript.js loaded');
// Scrape the HTML content
const pageHTML = document.documentElement.innerHTML;
console.log('pageHTML', pageHTML);
// Send the HTML content to the background script
chrome.runtime.sendMessage({html: pageHTML});


