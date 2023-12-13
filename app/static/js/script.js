// app/static/js/script.js
document.addEventListener("DOMContentLoaded", function () {
  const patientForm = document.getElementById("patient-form");
  const resultsContainer = document.getElementById("results"); // Add an element to display results

  patientForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const fhirId = document.getElementById("FHIR").value;

    fetch("/handle-fhir-id", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ fhirId: fhirId }),
    })
      .then((response) => {
        if (response.status === 401) {
          // Redirect to authentication flow
          window.location.href = "/start_auth";
          return;
        } else if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Success:", data);
        // Display the LLaMa results
        if (data.llama_response) {
          resultsContainer.innerHTML = `<h3>Decision Support:</h3><p>${data.llama_response}</p>`;
        } else {
          resultsContainer.innerHTML = "<p>No results available.</p>";
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        resultsContainer.innerHTML = `<p>Error: ${error.message}</p>`;
      });
  });
});
