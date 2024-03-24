// Initialize chat history
let chatHistory;

// Listen for when the extension is installed
chrome.runtime.onInstalled.addListener(function () {
    // Set default API model
    let defaultModel = "claude-2.1";
    chrome.storage.local.set({ apiModel: defaultModel });

    // Set empty chat history
    chrome.storage.local.set({ chatHistory: [] });

    // Open the options page
    chrome.runtime.openOptionsPage();
});

// Listen for messages from the popup script
chrome.runtime.onMessage.addListener(async function (message, sender, sendResponse) {

    // Get the API key from local storage
    const { apiKey } = await getStorageData(["apiKey"]);
    // Get the model from local storage
    const { apiModel } = await getStorageData(["apiModel"]);
    // get the chat history from local storage
    const result = await getStorageData(["chatHistory"]);

    if (message.html) {
        console.log("Received HTML content from content script:", message.html);

        // Treat the HTML content as a message (either from the user or as a system info, your choice)
        // Here, treating it as a system message for demonstration
        const systemMessage = {
            role: "user", // Or "user" based on your design decision
            content: "Summarize the webpage I am on in simple terms and help me navigate. \
            Here is the scraped HTML Content of the current tab: " + message.html.substring(0,100000)// Showing a preview for brevity
        };

        // Add the system message to the chat history
        chatHistory.push(systemMessage);

        // Optionally, save the updated chat history to local storage
        chrome.storage.local.set({ chatHistory: chatHistory });

        const response = await fetchChatCompletion(chatHistory, apiKey, apiModel);

        if (response) {

            // Get the assistant's response
            const assistantResponse = response.content[0].text;

            // Add the assistant's response to the message array
            chatHistory.push({ role: "assistant", content: assistantResponse });
            // save message array to local storage
            chrome.storage.local.set({ chatHistory: chatHistory });

            // Send the assistant's response to the popup script
            chrome.runtime.sendMessage({ answer: assistantResponse });

            console.log("Sent response to popup:", assistantResponse);
        }
    }

    if (message.userInput) {

        if (!result.chatHistory || result.chatHistory.length === 0) {
            chatHistory = [];
        } else {
            chatHistory = result.chatHistory;
        }

        // save user's message to message array
        chatHistory.push({ role: "user", content: message.userInput });

        // Send the user's message to the OpenAI API
        const response = await fetchChatCompletion(chatHistory, apiKey, apiModel);

        if (response) {

            // Get the assistant's response
            const assistantResponse = response.content[0].text;

            // Add the assistant's response to the message array
            chatHistory.push({ role: "assistant", content: assistantResponse });
            // save message array to local storage
            chrome.storage.local.set({ chatHistory: chatHistory });

            // Send the assistant's response to the popup script
            chrome.runtime.sendMessage({ answer: assistantResponse });

            console.log("Sent response to popup:", assistantResponse);
        }
        return true; // Enable response callback

    }

    return true; // Enable response callback
});

// Fetch data from the OpenAI Chat Completion API
async function fetchChatCompletion(messages, apiKey, apiModel) {
    try {
        const response = await fetch('https://api.anthropic.com/v1/messages', {
            method: 'POST',
            headers: {
                "x-api-key": apiKey,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            },
            body: JSON.stringify({
                "max_tokens": 1024,
                "messages": messages,
                "model": apiModel,
            })
        });

        if (!response.ok) {
            if (response.status === 401) {
                // Unauthorized - Incorrect API key
                throw new Error("Looks like your API key is incorrect. Please check your API key and try again.");
            } else {
                throw new Error(`Failed to fetch. Status code: ${response.status}`);
            }
        }

        return await response.json();
    } catch (error) {
        // Send a response to the popup script
        chrome.runtime.sendMessage({ error: error.message });

        console.error(error);
    }
}

// Get data from local storage
function getStorageData(keys) {
    return new Promise((resolve) => {
        chrome.storage.local.get(keys, (result) => resolve(result));
    });
}
