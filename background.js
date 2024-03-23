let scrapedContent = {};

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.content) {
        console.log('Received content from the content script');
        scrapedContent = request.content; // Store the content
        sendResponse({ message: 'Content received' });
    } else if (request.action === "getScrapedContent") {
        sendResponse(scrapedContent); // Send the content to the popup
    }
});

  