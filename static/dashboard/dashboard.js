

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

// --- NEW: Handle Feedback Submission ---
async function submitFeedback(event) {
    event.preventDefault(); // Stop the page from refreshing
    
    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('.submit-btn');

    submitBtn.innerText = "Sending...";
    submitBtn.disabled = true;

    try {
        const response = await fetch("/submit-feedback", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            alert("Thank you for your feedback!");
            form.reset(); // Clear the form
        } else {
            alert("Failed to send feedback. Please try again.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Server error. Check your connection.");
    } finally {
        submitBtn.innerText = "Send Feedback";
        submitBtn.disabled = false;
    }
}

// --- NEW: Handle Support Message Submission ---
async function sendSupportMessage(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('.submit-btn');

    submitBtn.innerText = "Sending Message...";
    submitBtn.disabled = true;

    try {
        const response = await fetch("/send-message", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            alert("Message sent! Our team will get back to you soon.");
            form.reset();
        } else {
            alert("Failed to send message.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Connection error.");
    } finally {
        submitBtn.innerText = "Send Message";
        submitBtn.disabled = false;
    }
}

async function postToCommunity() {
    const input = document.getElementById("community-input");
    const chatBox = document.getElementById("chat-box");
    const content = input.value;

    if (!content.trim()) return;

    try {
        const response = await fetch("/post-community", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: content })
        });

        const data = await response.json();

        if (response.ok) {
            // OPTION A: Add the message to the screen immediately without reloading
            const newMsg = document.createElement('div');
            newMsg.className = 'chat-bubble own-message';
            newMsg.innerHTML = `
                <span class="sender-name">You</span>
                <p class="message-text">${content}</p>
                <span class="timestamp">Just now</span>
            `;
            chatBox.appendChild(newMsg);
            
            // Auto-scroll to the bottom
            chatBox.scrollTop = chatBox.scrollHeight;
            
            input.value = ""; // Clear the input field
        }
    } catch (error) {
        console.error("Chat error:", error);
    }
}