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
  
if (document.readyState === "loading") {
    document.addEventListener('DOMContentLoaded', scrapeAndSendContent);
    } else {
        scrapeAndSendContent(); // If the content script runs after the DOM is complete
}
  