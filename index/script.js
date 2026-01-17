alert("Script loaded successfully");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");
const tabs = document.querySelectorAll(".tab");

function showLogin() {
  loginForm.classList.remove("hidden");
  registerForm.classList.add("hidden");
  tabs[0].classList.add("active");
  tabs[1].classList.remove("active");
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

  if (email && password) {
    localStorage.setItem("loggedIn", "true");
    // redirect to dashboard
    window.location.href ="../dashboard/dashboard.html";
  } else {
    alert("Enter email and password");
  }
}

  function register() {
    const fullName = document.querySelector("#registerForm input[type='text']").value;
    const email = document.querySelector("#registerForm input[type='email']").value;
    const password = document.querySelector("#registerForm input[type='password']").value;

    if (fullName && email && password) {
      localStorage.setItem("loggedIn", "true");

      window.location.href ="../dashboard/dashboard.html";
    } else {
      alert("Please fill in all fields");
    }
  }

