function showScreen(id) {
  document.querySelectorAll('.screen').forEach(div => {
    div.style.display = 'none';
  });
  document.getElementById(id).style.display = 'block';
}

let rfmChartInstance = null;

async function fetchDataAndRender(section) {
  if (section !== 'rfm') return;

  const chartType = document.getElementById("rfmChartType").value;
  const valueKey = document.getElementById("rfmValueKey").value;
  const ctx = document.getElementById("rfmChart").getContext("2d");

  try {
    const response = await fetch("https://crm-based-ecom.onrender.com/rfm");
    const data = await response.json();

    const labels = data.map(item => item.CustomerID);
    const values = data.map(item => item[valueKey]);

    if (rfmChartInstance) rfmChartInstance.destroy(); // Prevent double chart

    rfmChartInstance = new Chart(ctx, {
      type: chartType,
      data: {
        labels,
        datasets: [{
          label: `${valueKey} per Customer`,
          data: values,
          backgroundColor: "rgba(75, 192, 192, 0.5)",
          borderColor: "rgba(75, 192, 192, 1)",
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });
  } catch (err) {
    alert("Failed to fetch RFM data");
    console.error(err);
  }
}

// Optional: open RFM by default
window.onload = () => showScreen('rfm');
