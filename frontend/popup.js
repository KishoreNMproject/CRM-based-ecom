// popup.js
document.addEventListener("DOMContentLoaded", () => {
  const analyzeButton = document.getElementById("analyzeDeals");
  const resultDiv = document.getElementById("result");
  const loadingDiv = document.getElementById("loading");

  // Load last saved AI response on popup open
  chrome.storage.local.get("last_ai_response", (data) => {
    if (chrome.runtime.lastError) {
      console.error("Popup script: Storage access error:", chrome.runtime.lastError);
      resultDiv.innerText = "Failed to load previous AI result.";
      return;
    }
    const storedResponse = data.last_ai_response;
    console.log("Popup script: On DOMContentLoaded, last_ai_response from storage:", storedResponse);
    resultDiv.innerText = storedResponse || "No analysis has been run for this page yet. Click the button to start.";
  });

  analyzeButton.addEventListener("click", async () => {
    resultDiv.innerText = ""; // Clear previous result
    loadingDiv.style.display = "block"; // Show loading message
    analyzeButton.disabled = true; // Disable button
    console.log("Popup script: 'Analyze Deals' button clicked. Initiating analysis.");

    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      if (tabs.length === 0) {
        console.error("Popup script: No active tab found.");
        resultDiv.innerText = "No active tab found.";
        loadingDiv.style.display = "none";
        analyzeButton.disabled = false;
        return;
      }

      const activeTabId = tabs[0].id;
      console.log("Popup script: Active tab ID:", activeTabId);

      try {
        // Send a message to the content script and await its response
        console.log("Popup script: Sending 'start_deal_analysis' message to content script.");
        const response = await chrome.tabs.sendMessage(activeTabId, { type: "start_deal_analysis" });

        console.log("Popup script: Received final response from content script:", response);

        if (response && response.success) {
            resultDiv.innerText = response.result;
            console.log("Popup script: Analysis successful, UI updated with result.");
        } else {
            const errorMessage = response.error || "An unknown error occurred during analysis.";
            resultDiv.innerText = `Analysis failed: ${errorMessage}`;
            console.error("Popup script: Analysis failed, UI updated with error:", errorMessage);
        }
      } catch (error) {
        console.error("Popup script: Error during analysis (catch block):", error);
        resultDiv.innerText = `An error occurred: ${error.message || "Please check console for details."}`;
      } finally {
        console.log("Popup script: Analysis process finished. Hiding loading and re-enabling button.");
        loadingDiv.style.display = "none"; // Hide loading message
        analyzeButton.disabled = false; // Re-enable button
      }
    });
  });
});
