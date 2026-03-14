

function showSection(sectionId, el) {
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
    if (el) {
        el.classList.add('active');
    }
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;
    sidebar.classList.toggle('open');
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
  // hit server to clear session, then navigate home
  fetch('/logout', { method: 'GET' })
    .finally(() => {
      localStorage.removeItem("loggedIn");
      window.location.href = "/";
    });
}

function openSettingsModal() {
  const modal = document.getElementById('settings-modal');
  if (!modal) return;
  modal.style.display = 'flex';
  document.body.classList.add('modal-open');
}

function closeSettingsModal() {
  const modal = document.getElementById('settings-modal');
  if (!modal) return;
  modal.style.display = 'none';
  document.body.classList.remove('modal-open');
}

function saveProfile(event) {
  event.preventDefault();
  const form = document.getElementById('profile-form');
  if (!form) return;

  const formData = new FormData(form);

  fetch('/update-profile', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert('Profile updated successfully');
        closeSettingsModal();
        window.location.reload();
      } else {
        alert(data.error || 'Failed to update profile');
      }
    })
    .catch(err => {
      console.error('Profile update error', err);
      alert('Server error while updating profile.');
    });
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

// --- Star Rating System ---
document.addEventListener('DOMContentLoaded', function() {
    const stars = document.querySelectorAll('.star');
    const ratingInput = document.getElementById('rating-value');
    const ratingText = document.getElementById('rating-text');
    
    if (stars.length > 0) {
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const value = parseInt(this.getAttribute('data-value'));
                ratingInput.value = value;
                updateStars(value);
                ratingText.textContent = getRatingText(value);
            });
            
            star.addEventListener('mouseover', function() {
                const value = parseInt(this.getAttribute('data-value'));
                highlightStars(value);
            });
            
            star.addEventListener('mouseout', function() {
                const currentValue = parseInt(ratingInput.value) || 0;
                updateStars(currentValue);
            });
        });
    }

    const feedbackForm = document.getElementById('feedback-form');
    const supportForm = document.getElementById('support-form');

    if (feedbackForm) {
        feedbackForm.addEventListener('submit', submitFeedback);
    }

    if (supportForm) {
        supportForm.addEventListener('submit', sendSupportMessage);
    }
});

function updateStars(value) {
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        if (index < value) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

function highlightStars(value) {
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        if (index < value) {
            star.style.color = '#ffd700';
        } else {
            star.style.color = '';
        }
    });
}

function getRatingText(value) {
    const texts = ['', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent'];
    return texts[value] || 'Click to rate';
}

// --- NEW: Handle Feedback Submission ---
async function submitFeedback(event) {
    event.preventDefault(); // Stop the page from refreshing
    
    const form = event.target;
    const ratingInput = document.getElementById('rating-value');
    const rating = parseInt(ratingInput.value);
    const comment = form.querySelector('textarea[name="comment"]').value;
    const submitBtn = form.querySelector('.submit-btn');

    // Validate rating
    if (!rating || rating < 1 || rating > 5) {
        alert('Please select a star rating (1-5 stars)');
        return;
    }

    submitBtn.innerText = "Sending...";
    submitBtn.disabled = true;

    try {
        const response = await fetch("/submit-feedback", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                rating: rating,
                comment: comment
            })
        });

        const data = await response.json();

        if (data.success) {
            alert("Thank you for your feedback! " + "⭐".repeat(rating));
            form.reset(); // Clear the form
            // Reset stars
            updateStars(0);
            document.getElementById('rating-text').textContent = 'Click to rate';
        } else {
            alert(data.error || "Failed to send feedback. Please try again.");
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
    const formData = {
        name: form.querySelector('input[name="name"]').value,
        email: form.querySelector('input[name="email"]').value,
        subject: form.querySelector('input[name="subject"]').value,
        message: form.querySelector('textarea[name="message"]').value
    };
    const submitBtn = form.querySelector('.submit-btn');

    submitBtn.innerText = "Sending Message...";
    submitBtn.disabled = true;

    try {
        const response = await fetch("/send-message", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            alert("Message sent! Our team will get back to you at " + formData.email + " soon.");
            form.reset();
        } else {
            alert("Failed to send message: " + (data.error || "Unknown error"));
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Connection error. Please try again.");
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
            newMsg.className = 'message';
            newMsg.innerHTML = `
                <span class="msg-user"><strong>You:</strong></span>
                <span class="msg-content">${content}</span>
                <small class="msg-time">Just now</small>
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

function launchGame(gameName) {
    if (gameName === 'space_invaders') {
        fetch('/launch-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game: 'space_invaders' })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Launching Space Invaders... Enjoy the game!');
            } else {
                alert('Error: ' + (data.error || 'Could not launch game'));
            }
        })
        .catch(error => {
            console.error('Error launching game:', error);
            alert('Error launching game. Please try again.');
        });
    }
}
