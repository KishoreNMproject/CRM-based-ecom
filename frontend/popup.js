document.addEventListener("DOMContentLoaded", () => {
  const resultsDiv = document.getElementById("results");

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'analyze_deals') {
      const { payload } = request;
      fetchDeals(payload.query);
    }
  });

  function fetchDeals(query) {
    resultsDiv.innerHTML = `<p>Searching best deals for: <b>${query}</b>...</p>`;
    chrome.runtime.sendMessage({ action: 'get_amazon_search_url', query, country: '' }, (response) => {
      if (!response) return;

      const { url } = response;
      scrapeAmazonPage(url).then((payload) => {
        if (payload) {
          // Send the payload to the background script
          chrome.runtime.sendMessage({ action: 'analyze_deals', payload });
        }
      });
    });
  }

  function scrapeAmazonPage(url) {
    return new Promise((resolve, reject) => {
      axios.get(url)
        .then(response => {
          const $ = cheerio.load(response.data);
          const title = $('h1.productTitle').text();
          const price = $('span.priceBlockBuyingFormContent').text();

          const payload = {
            query: '',
            sourceUrl: url,
            title,
            price
          };

          resolve(payload);
        })
        .catch(err => reject(err));
    });
  }
});
