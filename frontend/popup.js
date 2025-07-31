// popup.js
document.addEventListener("DOMContentLoaded", () => {
    const analyzeButton = document.getElementById("analyzeDeals");
    const resultDiv = document.getElementById("result");
    const loadingDiv = document.getElementById("loading");
    let currentTabUrl = '';

    // Function to update the popup UI based on the cached status and result
    function updatePopupUI() {
        if (!currentTabUrl) {
            resultDiv.innerText = "Could not identify the current page URL.";
            return;
        }

        const resultKey = `analysis_result_${currentTabUrl}`;
        const statusKey = `analysis_status_${currentTabUrl}`;

        chrome.storage.local.get([resultKey, statusKey], (data) => {
            const status = data[statusKey];
            const result = data[resultKey];

            loadingDiv.style.display = "none";
            analyzeButton.disabled = false;

            switch (status) {
                case "fetching":
                    loadingDiv.style.display = "block";
                    loadingDiv.innerText = "AI analysis is running in the background...";
                    analyzeButton.disabled = true;
                    resultDiv.innerText = "";
                    break;
                case "complete":
                    resultDiv.innerText = result || "Analysis complete, but no result was saved.";
                    analyzeButton.innerText = "Re-analyze This Page";
                    break;
                case "failed":
                    resultDiv.innerText = result || "Analysis failed. Please try again.";
                    analyzeButton.innerText = "Try to Analyze Again";
                    break;
                default:
                    resultDiv.innerText = "No analysis has been run for this page yet. Click the button to start.";
                    analyzeButton.innerText = "Analyze Deals on This Page";
            }
        });
    }

    // Manual analysis trigger
    analyzeButton.addEventListener("click", () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs.length === 0) {
                resultDiv.innerText = "No active tab found.";
                return;
            }
            loadingDiv.style.display = "block";
            loadingDiv.innerText = "Requesting analysis...";
            analyzeButton.disabled = true;
            resultDiv.innerText = "";
            
            chrome.tabs.sendMessage(tabs[0].id, { type: "start_deal_analysis" }, () => {
                if (chrome.runtime.lastError) {
                    resultDiv.innerText = "Could not communicate with the page. Try reloading it.";
                    loadingDiv.style.display = "none";
                    analyzeButton.disabled = false;
                }
                // The storage listener will handle the UI update once the result is ready.
            });
        });
    });

    // Listen for storage changes to update the UI in real-time
    chrome.storage.onChanged.addListener((changes, namespace) => {
        if (namespace === "local") {
            const statusKey = `analysis_status_${currentTabUrl}`;
            const resultKey = `analysis_result_${currentTabUrl}`;
            if (changes[statusKey] || changes[resultKey]) {
                updatePopupUI();
            }
        }
    });

    // Initial setup: Get current tab's URL and render the initial UI
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0] && tabs[0].url) {
            currentTabUrl = tabs[0].url;
            updatePopupUI();
        } else {
            resultDiv.innerText = "Unable to access tab information.";
            analyzeButton.style.display = "none";
        }
    });
});