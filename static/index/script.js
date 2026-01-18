
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
  
  window.location.href ="../../templates/login/login.html";
}

function showRegister() {
  loginForm.classList.add("hidden");
  registerForm.classList.remove("hidden");
  tabs[1].classList.add("active");
  tabs[0].classList.remove("active");
}


  function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  if (!email || !password) {
    alert("Enter email and password");
    return;
  }

  fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: email,
      password: password
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      window.location.href = "/dashboard";
    } else {
      alert(data.error);
    }
  })
  .catch(() => alert("Server error"));
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
      window.location.href = "../../templates/index/login.html";
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
