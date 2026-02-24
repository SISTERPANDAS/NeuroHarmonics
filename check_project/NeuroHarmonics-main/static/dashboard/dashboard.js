// --- Video Recommendation Cards Data ---
const videoRecommendations = [
  {
    file: 'body_movements.mp4',
    topic: 'Body Movements',
    quote: 'Movement is a medicine for creating change in a person’s physical, emotional, and mental states.',
    theme: 'Physical Wellness'
  },
  {
    file: 'Create_a_new_morning_routine.mp4',
    topic: 'Morning Routine',
    quote: 'Win the morning, win the day.',
    theme: 'Mindful Start'
  },
  {
    file: 'finding_goal.mp4',
    topic: 'Finding Your Goal',
    quote: 'The secret of getting ahead is getting started.',
    theme: 'Purpose & Growth'
  },
  {
    file: 'happy_activities.mp4',
    topic: 'Happy Activities',
    quote: 'Happiness is not something ready made. It comes from your own actions.',
    theme: 'Joyful Living'
  },
  {
    file: 'promise_to_a_friend.mp4',
    topic: 'Promise to a Friend',
    quote: 'A real friend is one who walks in when the rest of the world walks out.',
    theme: 'Social Connection'
  },
  {
    file: 'relaxed_time.mp4',
    topic: 'Relaxed Time',
    quote: 'Sometimes the most productive thing you can do is relax.',
    theme: 'Calm & Balance'
  },
  {
    file: 'spending_time_happily.mp4',
    topic: 'Spending Time Happily',
    quote: 'Enjoy the little things, for one day you may look back and realize they were the big things.',
    theme: 'Gratitude'
  }
];

function getRandomCards(arr, n) {
  const shuffled = arr.slice().sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

function createVideoCard(card) {
  const cardDiv = document.createElement('div');
  cardDiv.className = 'video-card glass';
  cardDiv.innerHTML = `
    <div style="position:relative;">
      <img class="card-thumb" src="/static/dashboard/video_thumbs/${card.file.replace('.mp4','.jpg')}" alt="${card.topic}">
      <video class="video-hover-preview" src="/images/${card.file}" loop muted playsinline></video>
    </div>
    <div class="card-title">${card.topic}</div>
    <div class="card-theme">${card.theme}</div>
    <div class="card-quote">“${card.quote}”</div>
  `;
  // Hover video logic
  cardDiv.addEventListener('mouseenter', function() {
    const video = cardDiv.querySelector('.video-hover-preview');
    video.currentTime = 0;
    video.play();
  });
  cardDiv.addEventListener('mouseleave', function() {
    const video = cardDiv.querySelector('.video-hover-preview');
    video.pause();
    video.currentTime = 0;
  });
  return cardDiv;
}

function renderVideoRecommendations() {
  const container = document.querySelector('.video-recommendations-container');
  if (!container) return;
  container.innerHTML = '';
  const cards = getRandomCards(videoRecommendations, 4);
  cards.forEach(card => {
    container.appendChild(createVideoCard(card));
  });
}

// Render on recommendations section show
document.addEventListener('DOMContentLoaded', function() {
  // If recommendations section is visible by default, render immediately
  if (document.getElementById('recommendations').style.display !== 'none') {
    renderVideoRecommendations();
  }
  // Otherwise, render when nav is clicked
  const navBtns = document.querySelectorAll('.nav-item');
  navBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      if (btn.textContent.includes('Recommendations')) {
        setTimeout(renderVideoRecommendations, 200);
      }
    });
  });
});


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



// --- Face scan: camera + capture + send to /api/face/analyze ---
let faceStream = null;

function startFaceScan() {
  const video = document.getElementById("face-video");
  const placeholder = document.getElementById("face-placeholder");
  const btnStart = document.getElementById("btn-start-scan");
  const btnCapture = document.getElementById("btn-capture");
  const btnStop = document.getElementById("btn-stop-scan");

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Camera not supported in this browser.");
    return;
  }

  navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
    .then(function (stream) {
      faceStream = stream;
      video.srcObject = stream;
      video.style.display = "block";
      placeholder.style.display = "none";
      btnStart.style.display = "none";
      btnCapture.style.display = "inline-block";
      btnStop.style.display = "inline-block";
    })
    .catch(function (err) {
      console.error(err);
      alert("Could not access camera: " + (err.message || "Permission denied"));
    });
}

function stopFaceScan() {
  if (faceStream) {
    faceStream.getTracks().forEach(function (t) { t.stop(); });
    faceStream = null;
  }
  const video = document.getElementById("face-video");
  const placeholder = document.getElementById("face-placeholder");
  const btnStart = document.getElementById("btn-start-scan");
  const btnCapture = document.getElementById("btn-capture");
  const btnStop = document.getElementById("btn-stop-scan");
  video.srcObject = null;
  video.style.display = "none";
  placeholder.style.display = "flex";
  btnStart.style.display = "inline-block";
  btnCapture.style.display = "none";
  btnStop.style.display = "none";
}

function captureAndAnalyze() {
  const video = document.getElementById("face-video");
  const canvas = document.getElementById("face-canvas");
  const resultEl = document.getElementById("face-result");

  if (!video.srcObject || !faceStream) {
    alert("Start the camera first.");
    return;
  }

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0);
  const dataUrl = canvas.toDataURL("image/jpeg", 0.85);
  const base64 = dataUrl.split(",")[1] || dataUrl;

  resultEl.style.display = "block";
  resultEl.innerHTML = "Analyzing...";

  fetch("/api/face/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: dataUrl })
  })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.error) {
        resultEl.innerHTML = "<span style='color:#e66'>" + data.error + "</span>";
        return;
      }
      const pct = Math.round((data.confidenceScore || 0) * 100);
      resultEl.innerHTML =
        "<b style='color:#9d4edd'>" + (data.dominantEmotion || "—") + "</b> " +
        " <span style='color:#a0a0c0'>(" + pct + "% confidence)</span>";
    })
    .catch(function (err) {
      console.error(err);
      resultEl.innerHTML = "<span style='color:#e66'>Request failed. Is the ML service running on port 8000?</span>";
    });
}

async function loadRecommendations() {
  const container = document.getElementById("rec-content");
  const quoteEl = document.getElementById("rec-quote");
  const authorEl = document.getElementById("rec-author");
  const harmonicEl = document.getElementById("rec-harmonic");
  const tipEl = document.getElementById("rec-tip");

  container.style.display = "none";
  try {
    const r = await fetch("/api/recommendations");
    const data = await r.json();
    if (!r.ok) {
      quoteEl.textContent = data.error || "Failed to load.";
      container.style.display = "block";
      return;
    }
    const q = data.motivational_quote || {};
    quoteEl.textContent = q.quote || "—";
    authorEl.textContent = "— " + (q.author || "");
    harmonicEl.textContent = data.harmonic_suggestion || "—";
    tipEl.textContent = data.calming_tip || "—";
    container.style.display = "block";
  } catch (e) {
    quoteEl.textContent = "Could not load recommendations.";
    container.style.display = "block";
  }
}


function logout() {
  localStorage.removeItem("loggedIn");
  window.location.href = "/";
}


// Legacy EEG file handler removed; face analysis used instead.

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