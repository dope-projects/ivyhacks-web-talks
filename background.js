chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.content) {
      console.log('Received content from the content script');
      // Here you can send the request.content to the LLM for processing
      // For now, let's just log the content
      console.log(request.content);
  
      // Placeholder response, will eventually hold the LLM response
      sendResponse({ message: 'Content received' });
    }
  });
  