const axios = require('axios');
const cheerio = require('cheerio');

function getAmazonSearchURL(query, country) {
  const url = `https://www.amazon.com/s?k=${encodeURIComponent(query)}&ref=nb_sb_noss_2&url=search-alias${country}`;
  return url;
}

async function scrapeAmazonPage(url) {
  try {
    const response = await axios.get(url);
    const $ = cheerio.load(response.data);

    // Extract relevant information from the page
    const title = $('h1.productTitle').text();
    const price = $('span.priceBlockBuyingFormContent').text();

    // Create a payload with the extracted data
    const payload = {
      query: query,
      sourceUrl: url,
      title: title,
      price: price,
    };

    return payload;
  } catch (err) {
    console.error('Error scraping Amazon page:', err);
    return null;
  }
}

function logCustomerData(payload) {
  // API endpoint to send the customer data
  const apiEndpoint = 'https://crm-based-ecom.onrender.com/api/customer-data';

  axios.post(apiEndpoint, payload)
    .then((response) => {
      console.log('Customer data logged successfully:', response.data);
    })
    .catch((error) => {
      console.error('Error logging customer data:', error);
    });
}

function sendMessageToBackground(message) {
  chrome.runtime.sendMessage({ message });
}

// ...

document.getElementById('price-comparison-form').addEventListener('submit', (e) => {
  e.preventDefault(); // Prevent the default form submission behavior

  const query = document.getElementById('query').value;
  const country = document.getElementById('country').value;
  const url = getAmazonSearchURL(query, country);

  scrapeAmazonPage(url).then((payload) => {
    if (payload) {
      logCustomerData(payload);
      sendMessageToBackground({ action: 'analyze_deals', payload });
    }
  });
});

