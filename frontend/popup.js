document.addEventListener("DOMContentLoaded", () => {
  const resultsDiv = document.getElementById("results");

  // Try to get product title from content.js with polling
  let attempts = 0;
  const maxAttempts = 10;
  const interval = 1000; // 1 second

  function pollForProductContext() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(
        tabs[0].id,
        { type: "GET_PRODUCT_CONTEXT" },
        (response) => {
          if (chrome.runtime.lastError) {
            console.warn("Popup: runtime error:", chrome.runtime.lastError.message);
            return;
          }

          if (response && response.title && response.title.trim().length > 0) {
            fetchDeals(response.title);
          } else {
            if (++attempts < maxAttempts) {
              console.log("Polling attempt", attempts);
              setTimeout(pollForProductContext, interval);
            } else {
              resultsDiv.innerText = "Could not extract product details from this page.";
            }
          }
        }
      );
    });
  }

  pollForProductContext();

  async function fetchDeals(query) {
    resultsDiv.innerHTML = `<p>Searching best deals for: <b>${query}</b>...</p>`;
    try {
      const res = await fetch("https://crm-based-ecom.onrender.com/priceapi-proxy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      });
      const deals = await res.json();

      if (!deals || !Array.isArray(deals) || deals.length === 0) {
        resultsDiv.innerHTML = "<p>No deals found.</p>";
        return;
      }

      resultsDiv.innerHTML = deals.map(d => `
        <div style="border-bottom:1px solid #ccc;padding:10px;">
          <a href="${d.url}" target="_blank"><b>${d.name}</b></a><br/>
          Price: ${d.price} | Site: ${d.site}<br/>
          Rating: ${d.rating || 'N/A'} | Reviews: ${d.reviews || 'N/A'}
        </div>
      `).join("");
    } catch (err) {
      resultsDiv.innerHTML = "<p>Error fetching deals: " + err.message + "</p>";
    }
  }
});

