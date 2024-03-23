if (document.readyState === "loading") {
    document.addEventListener('DOMContentLoaded', function() {
        chrome.runtime.sendMessage({ action: "getScrapedContent" }, function(response) {
            document.getElementById('content').textContent = JSON.stringify(response, null, 2);
        });
    });
    } else {
        chrome.runtime.sendMessage({ action: "getScrapedContent" }, function(response) {
            document.getElementById('content').textContent = JSON.stringify(response, null, 2);
        });
}