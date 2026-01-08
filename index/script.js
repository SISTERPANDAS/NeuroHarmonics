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

