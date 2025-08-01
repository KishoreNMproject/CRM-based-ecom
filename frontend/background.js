// background.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "analyze_deals") {
    const query = request.query;
    const sourceUrl = request.sourceUrl;
    const userId = request.userId; // Not used by the provided proxy, but passed from content.js

    console.log("Background script: Received 'analyze_deals' request.");
    console.log("Background script: Making a call to the Gemini proxy service.");

    // The URL for the backend proxy service, as you specified.
    const priceApiUrl = "http://127.0.0.1:8000/priceapi-proxy";

    // Function to handle fetch with exponential backoff retry logic
    const retryWithExponentialBackoff = async (url, options, retries = 5, delay = 1000) => {
      for (let i = 0; i < retries; i++) {
        try {
          const response = await fetch(url, options);
          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
          }
          return response;
        } catch (err) {
          console.warn(`Attempt ${i + 1} failed: ${err.message}. Retrying in ${delay}ms...`);
          if (i === retries - 1) {
            throw err;
          }
          await new Promise(res => setTimeout(res, delay));
          delay *= 2; // Exponential backoff
        }
      }
    };

    const processRequest = async () => {
      // The payload is structured to match the `Request` object expected by your FastAPI endpoint.
      const payload = {
        query: query,
        sourceUrl: sourceUrl,
      };

      try {
        const response = await retryWithExponentialBackoff(geminiProxyUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await response.json();
        console.log("Background script: Parsed response data from Gemini proxy.");

        let aiResponse = "";
        if (data && data.candidates && data.candidates[0]?.content?.parts[0]?.text) {
          aiResponse = data.candidates[0].content.parts[0].text;
        } else {
          console.error("Background script: Invalid response structure from Gemini proxy:", data);
          aiResponse = `Analysis failed: Invalid response from proxy. Data: ${JSON.stringify(data)}`;
        }
        
        console.log("Background script: Successfully extracted and formatted AI response text.");
        chrome.storage.local.set({ "last_ai_response": aiResponse });
        sendResponse({ success: true, result: aiResponse });
        
      } catch (err) {
        console.error("Background script: Fetch to Gemini proxy failed in catch block:", err);
        const errorMessage = `Analysis failed: ${err.message || "Unknown error during proxy fetch."}`;
        chrome.storage.local.set({ "last_ai_response": errorMessage });
        sendResponse({ success: false, error: errorMessage });
      }
    };
    
    // Call the async function
    processRequest();
    
    return true;
  }
});