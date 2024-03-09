document.addEventListener("DOMContentLoaded", function () {
    const labForm = document.getElementById("lab-form");
    const labResultsContainer = document.getElementById("lab-results");
    const loadingGif = document.getElementById('loading-gif');
    let downloadButtonCreated = false;

    labForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const mrn = document.getElementById("lab-MRN").value;

        // Show the loading GIF
        loadingGif.style.display = 'block';
        
        // First, ensure all lab data is processed and updated as necessary
        fetch('/handle-fhir-id', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ mrn: mrn, feature: 'Research Assistant' })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // After processing, fetch all lab data including any updates
            return fetch('/get-all-lab-data');
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(labData => {
            // Process and display fetched lab data
            labResultsContainer.innerHTML = '';
            const columnOrder = ['MRN', 'system', 'code', 'test_name', 'result_value', 'high_value', 'low_value', 'units'];
            const table = document.createElement('table');
            const headerRow = document.createElement('tr');
            columnOrder.forEach(key => {
                const headerCell = document.createElement('th');
                headerCell.textContent = key;
                headerRow.appendChild(headerCell);
            });
            table.appendChild(headerRow);

            labData.forEach(row => {
                const rowElement = document.createElement('tr');
                columnOrder.forEach(key => {
                    const cell = document.createElement('td');
                    cell.textContent = row[key] || 'N/A';
                    rowElement.appendChild(cell);
                });
                table.appendChild(rowElement);
            });

            labResultsContainer.appendChild(table);

            if (!downloadButtonCreated) {
                const downloadButton = document.createElement('button');
                downloadButton.textContent = 'Download CSV';
                downloadButton.classList.add('download-csv');
                downloadButton.addEventListener('click', function() {
                    window.location.href = '/download-lab-data';
                });
                labResultsContainer.after(downloadButton);
                downloadButtonCreated = true;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            labResultsContainer.textContent = 'Error fetching lab data.';
        })
        
        .finally(() => {
            // Hide the loading GIF
            loadingGif.style.display = 'none';
        });
    });
});


/* document.addEventListener("DOMContentLoaded", function () {
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

  
  */