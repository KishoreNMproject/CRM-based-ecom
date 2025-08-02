const { remote } = require('electron');

function getAmazonSearchURL(query, country) {
    const url = `https://www.amazon.com/s?k=${encodeURIComponent(query)}&ref=nb_sb_noss_2&url=search-alias${country}`;
    return url;
}

function sendMessageToBackground(message) {
    chrome.runtime.sendMessage({ message });
}

function onQuerySubmit(event) {
    const query = event.target.elements.query.value;
    const country = event.target.elements.country.value;
    const url = getAmazonSearchURL(query, country);

    sendMessageToBackground({ action: 'navigate', url });
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('price-comparison-form');
    form.addEventListener('submit', onQuerySubmit);
});
