// app/static/js/script.js
document.addEventListener("DOMContentLoaded", function () {
  const patientForm = document.getElementById("patient-form");

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
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Success:", data);
        // Handle the response data here
        // For example, display the results on the page
      })
      .catch((error) => {
        console.error("Error:", error);
        // Handle any errors here
      });
  });
});
