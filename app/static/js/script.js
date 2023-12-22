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
        console.log("Full response data:", data);
        let content = "";

        if (data.patient_data) {
          content += `<h3>Patient Information:</h3>`;
          content += `<div>Age: ${data.patient_data.age || "N/A"}</div>`;
          content += `<div>Gender: ${data.patient_data.gender || "N/A"}</div>`;
          content += `<div>Medications: ${
            data.patient_data.medications || "N/A"
          }</div>`;
          content += `<div>Allergies: ${
            data.patient_data.allergies || "N/A"
          }</div>`;
          content += `<div>Conditions: ${
            data.patient_data.conditions || "N/A"
          }</div>`;
          content += `<div>Social History: ${
            data.patient_data.social_history || "N/A"
          }</div>`;
        }
        if (data.openai_response) {
          let converter = new showdown.Converter();
          let htmlDecisionSupport = converter.makeHtml(data.openai_response);

          // Replace every individual <ol> start tag with a <li> tag, except the very first one
          // Ensure that all list items are in the same <ol></ol> block
          // This regular expression looks for a closing </ol> followed by an opening <ol>
          // and removes these tags, effectively merging separate lists into one.
          htmlDecisionSupport = htmlDecisionSupport.replace(
            /<\/ol>\s*<ol>/g,
            ""
          );

          // Now append this properly formatted HTML to your content
          content += `<div class="decision-support">${htmlDecisionSupport}</div>`;
        } else {
          content += "<p>No decision support available.</p>";
        }

        if (data.articles && data.articles.length > 0) {
          content += `<h3>Relevant Articles:</h3>`;
          data.articles.forEach((article) => {
            content += `<p><strong>Title:</strong> ${article.title}<br><strong>Abstract:</strong> ${article.abstract}</p>`;
          });
        }

        resultsContainer.innerHTML = content;
      })
      .catch((error) => {
        console.error("Error:", error);
        resultsContainer.innerHTML = `<p>Error: ${error.message}</p>`;
      });
  });
});
