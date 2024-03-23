let currentContent = {};

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.content) {
        console.log('Received content from the content script');
        // Store the scraped content
        currentContent = request.content;
        // You can process it with an LLM here
    } else if (request.action === "getSummary") {
        // Send the stored content to the popup
        sendResponse({ summary: currentContent.html }); // For example, sending the HTML directly
    }
});
