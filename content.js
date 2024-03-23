console.log("content.js has loaded");

function scrapeAndSendContent() {
    const pageContent = {
      html: document.documentElement.innerHTML,
      url: window.location.href,
      title: document.title
    };
  
    chrome.runtime.sendMessage({ content: pageContent }, function(response) {
      console.log('Content sent to background script.');
    });
  }
  
  // When the DOM is fully loaded, scrape the content.
  document.addEventListener('DOMContentLoaded', scrapeAndSendContent);
  