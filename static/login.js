// DOM Elements
const loginForm = document.getElementById('login-form');
const companyNameInput = document.getElementById('company-name');
const companyNameError = document.getElementById('company-name-error');
const loginContent = document.querySelector('.login-content');

// Form submission
loginForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  // Validate company name
  if (validateCompanyName()) {
    // Form is valid, simply submit the form to the login route
    loginForm.submit();
  }
});

// Validate company name on blur and input
companyNameInput.addEventListener('blur', validateCompanyName);
companyNameInput.addEventListener('input', () => {
  if (companyNameInput.value.trim() !== '') {
    validateCompanyName();
  }
});

function validateCompanyName() {
  const value = companyNameInput.value.trim();
  
  if (value === '') {
    companyNameError.textContent = 'Company name is required';
    companyNameInput.classList.add('error');
    return false;
  } else if (value.length < 2) {
    companyNameError.textContent = 'Company name must be at least 2 characters';
    companyNameInput.classList.add('error');
    return false;
  } else {
    companyNameError.textContent = '';
    companyNameInput.classList.remove('error');
    return true;
  }
}

// Optional: Add subtle animation to the login button
document.addEventListener('DOMContentLoaded', () => {
  const loginButton = document.querySelector('.primary-btn');
  setTimeout(() => {
    loginButton.style.animation = 'pulse 2s infinite';
  }, 2000);
});
