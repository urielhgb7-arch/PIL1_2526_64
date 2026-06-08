// Check authentication
function checkAuth(redirectTo = 'signin.html') {
  const isAuthenticated = localStorage.getItem('isAuthenticated');
  if (!isAuthenticated && window.location.pathname.includes('dashboard')) {
    window.location.href = redirectTo;
  }
}

// Navigate to page
function navigateTo(page) {
  window.location.href = page;
}

// Logout
function logout() {
  localStorage.removeItem('isAuthenticated');
  localStorage.removeItem('userEmail');
  localStorage.removeItem('userData');
  localStorage.removeItem('onboardingCompleted');
  const redirectPath = window.location.pathname.includes('/pages/') ? '../index.html' : 'index.html';
  window.location.href = redirectPath;
}

// Get user data
function getUserData() {
  const userData = localStorage.getItem('userData');
  return userData ? JSON.parse(userData) : null;
}

// Save user data
function saveUserData(data) {
  localStorage.setItem('userData', JSON.stringify(data));
}

// Toggle password visibility
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const iconHide = document.getElementById(`${inputId}-icon-hide`);
  const iconShow = document.getElementById(`${inputId}-icon-show`);
  
  if (input.type === 'password') {
    input.type = 'text';
    iconHide.classList.add('hidden');
    iconShow.classList.remove('hidden');
  } else {
    input.type = 'password';
    iconHide.classList.remove('hidden');
    iconShow.classList.add('hidden');
  }
}

// Format date
function formatDate(date) {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(date).toLocaleDateString('fr-FR', options);
}

// Format time
function formatTime(date) {
  const options = { hour: '2-digit', minute: '2-digit' };
  return new Date(date).toLocaleTimeString('fr-FR', options);
}
