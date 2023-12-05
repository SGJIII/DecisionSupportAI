// app/static/js/script.js
document.addEventListener("DOMContentLoaded", function () {
  const patientForm = document.getElementById("patient-form");

  patientForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const patientId = document.getElementById("patient-id").value;

    // Example: Sending patient ID to the server using Fetch API
    fetch("/handle-patient-id", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ patientId: patientId }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Success:", data);
        // Handle response here (e.g., redirecting to another page or displaying a message)
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });
});
