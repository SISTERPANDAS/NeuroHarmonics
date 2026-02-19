
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

  const response = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
    body: JSON.stringify({ email, password })
  });

  const data = await response.json();

  if (data.success) {
    window.location.href = "/dashboard";
  } else {
    alert(data.error);
  }
}



 function register() {
  const fullName = document.querySelector("#registerForm input[type='text']").value;
  const email = document.querySelector("#registerForm input[type='email']").value;
  const password = document.querySelector("#registerForm input[type='password']").value;

  if (!fullName || !email || !password) {
    alert("Please fill all fields");
    return;
  }

  fetch("/api/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fullName, email, password })
  })
  .then(async res => {
    const data = await res.json();
    console.log("REGISTER RESPONSE:", data);

    if (data.success) {
      alert("🎉 Registration successful! Please login.");
      window.location.href = "/login";
    } else {
      alert(data.error || "Registration failed");
    }
  })
  .catch(err => {
    console.error("REGISTER ERROR:", err);
    alert("Server error. Check console.");
  });
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