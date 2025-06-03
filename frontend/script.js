let chart = null;

async function getPrediction() {
  const ticker = document.getElementById('ticker').value.trim();
  const resultDiv = document.getElementById('result');
  const errorDiv = document.getElementById('error');

  resultDiv.classList.add('hidden');
  errorDiv.classList.add('hidden');

  if (!ticker) {
    errorDiv.textContent = 'Please enter a stock ticker symbol.';
    errorDiv.classList.remove('hidden');
    return;
  }

  try {
    const response = await fetch(`http://127.0.0.1:5000/predict?ticker=${ticker}`);
    const data = await response.json();

    if (response.ok) {
      document.getElementById('stock-ticker').textContent = data.ticker;
      document.getElementById('latest-close').textContent = data.latest_close;
      document.getElementById('predicted-close').textContent = data.predicted_close;
      resultDiv.classList.remove('hidden');

      // Render chart
      const ctx = document.getElementById('priceChart').getContext('2d');

      // If chart exists, destroy it before creating new one
      if (chart) {
        chart.destroy();
      }

      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: data.dates,
          datasets: [{
            label: 'Close Price',
            data: data.closes,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            fill: true,
            tension: 0.1,
          }]
        },
        options: {
          scales: {
            x: {
              display: true,
              title: {
                display: true,
                text: 'Date',
              },
              ticks: {
                maxTicksLimit: 6,
              }
            },
            y: {
              display: true,
              title: {
                display: true,
                text: 'Price (USD)',
              },
              beginAtZero: false,
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'top',
            },
          },
          responsive: true,
          maintainAspectRatio: false,
        }
      });

    } else {
      errorDiv.textContent = data.error || 'Error fetching data.';
      errorDiv.classList.remove('hidden');
    }
  } catch (err) {
    errorDiv.textContent = 'Failed to connect to server.';
    errorDiv.classList.remove('hidden');
  }
}
