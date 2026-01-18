
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const tabs = document.querySelectorAll(".tab");

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault(); //stops page refresh
      login();
    });
  }
});

function showLogin() {
  
  window.location.href ="/login";
}

function showRegister() {
  loginForm.classList.add("hidden");
  registerForm.classList.remove("hidden");
  tabs[1].classList.add("active");
  tabs[0].classList.remove("active");
}


  async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.success) {
            // Redirect to the Flask dashboard route
            window.location.href = "/dashboard";
        } else {
            alert(data.error);
        }
    } catch (error) {
        console.error("Login Error:", error);
        alert("Server error. Please try again later.");
    }
}


 function register() {
  const fullName = document.querySelector("#registerForm input[type='text']").value;
  const email = document.querySelector("#registerForm input[type='email']").value;
  const password = document.querySelector("#registerForm input[type='password']").value;

  if (!fullName || !email || !password) {
    alert("Please fill in all fields");
    return;
  }

  fetch("/api/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fullName: fullName,
      email: email,
      password: password
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert("Account created. Please login.");
      window.location.href = "/login";
    } else {
      alert(data.error);
    }
  })
  .catch(() => alert("Server error"));
}


// Scroll Reveal Animation
const revealElements = document.querySelectorAll(".reveal");

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("active");
        observer.unobserve(entry.target); // animate only once
      }
    });
  },
  {
    threshold: 0.15
  }
);

revealElements.forEach(el => observer.observe(el));

function goToAdminLogin() {
    // Redirect to the Flask route URL
    window.location.href = "/admin";
}

async function handleRegister(event) {
  event.preventDefault();
  
  const fullName = document.getElementById('reg-fullname').value;
  const email = document.getElementById('reg-email').value;
  const password = document.getElementById('reg-password').value;

  const response = await fetch('/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fullName, email, password })
  });

  const result = await response.json();
  if (result.success) {
    alert("Registration successful! Please login.");
    window.location.href = "/login";
  } else {
    alert(result.error);
  }
}

async function registerUser() {
    const userData = {
        fullName: document.getElementById("reg-name").value,
        username: document.getElementById("reg-username").value, // Required by your DB
        email: document.getElementById("reg-email").value,
        password: document.getElementById("reg-password").value
    };

    const response = await fetch("/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData)
    });

    const result = await response.json();
    if (result.success) {
        alert("Registration Successful!");
        window.location.href = "/login";
    } else {
        alert("Error: " + result.error);
    }
}