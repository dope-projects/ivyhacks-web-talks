console.log('contentScript.js loaded');

// Create a clone of the document to work on, to avoid altering the actual page content
const clonedDocument = document.documentElement.cloneNode(true);

// Remove script and style elements from the clone
const elementsToRemove = clonedDocument.querySelectorAll('script, style, link[rel="stylesheet"]');
elementsToRemove.forEach(elem => elem.remove());

// Now, extract the cleaned HTML or text content
const cleanedHTML = clonedDocument.innerHTML;
console.log('Cleaned HTML', cleanedHTML); 

// Send the HTML content to the background script
chrome.runtime.sendMessage({html: cleanedHTML});
// chrome.runtime.sendMessage({text: cleanedText});

