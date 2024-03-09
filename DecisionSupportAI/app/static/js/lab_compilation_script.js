document.addEventListener("DOMContentLoaded", function () {
  const labForm = document.getElementById("lab-form");
  const labResultsContainer = document.getElementById("lab-results");
  let downloadButtonCreated = false; // Flag to check if the download button has been created

  labForm.addEventListener("submit", function (e) {
    e.preventDefault();

    fetch('/get-all-lab-data')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(labData => {
        // Clear previous table results
        labResultsContainer.innerHTML = '';

        // Define the column order based on your requirement
        const columnOrder = ['MRN', 'system', 'code', 'test_name', 'result_value', 'high_value', 'low_value', 'units'];

        // Create table and headers
        const table = document.createElement('table');

        // Create header row based on the column order
        const headerRow = document.createElement('tr');
        columnOrder.forEach(key => {
          const headerCell = document.createElement('th');
          headerCell.textContent = key;
          headerRow.appendChild(headerCell);
        });
        table.appendChild(headerRow);

        // Populate table rows based on the column order
        labData.forEach(row => {
          const rowElement = document.createElement('tr');
          columnOrder.forEach(key => {
            const cell = document.createElement('td');
            cell.textContent = row[key] || ''; // Use empty string if the key doesn't exist
            rowElement.appendChild(cell);
          });
          table.appendChild(rowElement);
        });

        labResultsContainer.appendChild(table);

      // Create the Download CSV button if it hasn't been created yet
      if (!downloadButtonCreated) {
        const downloadButton = document.createElement('button');
        downloadButton.textContent = 'Download CSV';
        downloadButton.addEventListener('click', function() {
          window.location.href = '/download-lab-data';
        });
        labResultsContainer.after(downloadButton); // Place the download button after the results container
        downloadButtonCreated = true; // Set the flag to true
      }
      })
      .catch(error => {
        console.error('Error:', error);
        labResultsContainer.textContent = 'Error fetching lab data.';
      });
  });
});

  
  