

function showSection(sectionId) {
    // 1. Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.style.display = 'none';
    });

    // 2. Show the selected section
    document.getElementById(sectionId).style.display = 'block';

    // 3. Update active button state
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
}



async function analyzeData() {
  const fileInput = document.getElementById("eegFile");
  const resultBox = document.getElementById("result");

  if (!fileInput.files.length) {
    alert("Please upload an EEG file first");
    return;
  }

  const file = fileInput.files[0];

  const formData = new FormData();
  formData.append("eeg", file);

  resultBox.innerText = "Analyzing...";

  try {
    const response = await fetch("http://127.0.0.1:5000/analyze", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (data.error) {
      resultBox.innerText = data.error;
      return;
    }

    resultBox.innerHTML =
      `<b style="color:green">
        ${data.emotion} (${Math.round(data.confidence * 100)}%)
       </b>`;

  } catch (error) {
    console.error(error);
    resultBox.innerText = "Server error";
  }
}


function logout() {
  localStorage.removeItem("loggedIn");
  window.location.href = "/";
}


function handleEEGFile() {
  const input = document.getElementById("eegFile");
  const file = input.files[0];
  const fileNameEl = document.getElementById("file-name");

  if (!file) {
    fileNameEl.innerText = "";
    return;
  }

  const allowedTypes = ["edf", "csv", "txt"];
  const fileExt = file.name.split(".").pop().toLowerCase();

  if (!allowedTypes.includes(fileExt)) {
    alert("Invalid file type! Only .edf, .csv, .txt allowed.");
    input.value = "";
    fileNameEl.innerText = "";
    return;
  }

  fileNameEl.innerText = "Selected: " + file.name;
}