// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
  const registerBtn = document.getElementById('register-btn');
  const registrationForm = document.getElementById('registration-form');
  const cancelBtn = document.getElementById('cancel-btn');
  const companyForm = document.getElementById('company-form');
  const companyNameInput = document.getElementById('company-name');
  const companySloganInput = document.getElementById('company-slogan');
  const companyNameError = document.getElementById('company-name-error');
  const emailsContainer = document.getElementById('emails-container');
  const addEmailBtn = document.getElementById('add-email-btn');
  const welcomeContent = document.getElementById('welcome-content');
  const firstEmailInput = document.querySelector('.email-input'); // Select first email input

  firstEmailInput.addEventListener('blur', () => validateEmail(firstEmailInput));
  firstEmailInput.addEventListener('input', () => {
    if (firstEmailInput.value.trim() !== '') {
      validateEmail(firstEmailInput);
    }
  });


  // Show registration form
  registerBtn.addEventListener('click', () => {
    registrationForm.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // Prevent scrolling when modal is open
  });

  // Hide registration form
  cancelBtn.addEventListener('click', () => {
    hideRegistrationForm();
  });

  // Close modal when clicking outside the form
  registrationForm.addEventListener('click', (e) => {
    if (e.target === registrationForm) {
      hideRegistrationForm();
    }
  });

  companyForm.addEventListener('submit', (e) => {
    e.preventDefault();

    // Validate all inputs
    let isValid = validateCompanyName();
    const emailInputs = document.querySelectorAll('.email-input');
    let areEmailsValid = true;

    emailInputs.forEach(input => {
      if (!validateEmail(input)) {
        areEmailsValid = false;
      }
    });

    if (isValid && areEmailsValid) {
      // Form is valid, collect data
      const companyName = companyNameInput.value;
      const companySlogan = companySloganInput.value;
      const emails = Array.from(emailInputs).map(input => input.value);

      // Send form data to backend using fetch
      fetch('/company_registration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          "company-name": companyName,
          "company-slogan": companySlogan,
          "emails": emails
        })
      })
      .then(response => response.json())
      .then(data => {
        // On success, hide the registration form...
        hideRegistrationForm();
        // ... and replace the welcome-content with the success-message div content.
        const successContent = document.getElementById('success-message').innerHTML;
        welcomeContent.innerHTML = successContent;
      })
      .catch(error => {
        console.error('Error:', error);
      });
    }
  });

  // Validate company name
  companyNameInput.addEventListener('blur', validateCompanyName);
  companyNameInput.addEventListener('input', () => {
    if (companyNameInput.value.trim() !== '') {
      validateCompanyName();
    }
  });

  // Function to validate company name
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

  // Function to validate email
  function validateEmail(emailInput) {
    const value = emailInput.value.trim();
    const errorElement = emailInput.nextElementSibling;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (value === '') {
      errorElement.textContent = 'Email is required';
      emailInput.classList.add('error');
      return false;
    } else if (!emailRegex.test(value)) {
      errorElement.textContent = 'Please enter a valid email address';
      emailInput.classList.add('error');
      return false;
    } else {
      errorElement.textContent = '';
      emailInput.classList.remove('error');
      return true;
    }
  }

  // Add new email input
  addEmailBtn.addEventListener('click', () => {
    addEmailInput();
  });

  function addEmailInput() {
    const emailInputGroup = document.createElement('div');
    emailInputGroup.className = 'email-input-group';

    const emailInput = document.createElement('input');
    emailInput.type = 'email';
    emailInput.className = 'email-input';
    emailInput.placeholder = 'example@company.com';
    emailInput.required = true;

    const errorMessage = document.createElement('div');
    errorMessage.className = 'error-message';

    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.className = 'remove-email-btn';
    removeButton.innerHTML = '&times;';
    removeButton.style.position = 'absolute';
    removeButton.style.right = '10px';
    removeButton.style.top = '10px';
    removeButton.style.background = 'transparent';
    removeButton.style.border = 'none';
    removeButton.style.fontSize = '1.2rem';
    removeButton.style.cursor = 'pointer';
    removeButton.style.color = '#666';

    removeButton.addEventListener('click', () => {
      // Add fade-out animation
      emailInputGroup.style.animation = 'fadeOut 0.3s ease-out forwards';

      // Remove after animation completes
      setTimeout(() => {
        emailsContainer.removeChild(emailInputGroup);
      }, 300);
    });

    // Add validation events
    emailInput.addEventListener('blur', () => validateEmail(emailInput));
    emailInput.addEventListener('input', () => {
      if (emailInput.value.trim() !== '') {
        validateEmail(emailInput);
      }
    });

    emailInputGroup.appendChild(emailInput);
    emailInputGroup.appendChild(errorMessage);

    // Only add remove button if there's more than one email input
    if (document.querySelectorAll('.email-input-group').length > 0) {
      emailInputGroup.appendChild(removeButton);
    }

    // Add to container with animation
    emailInputGroup.style.animation = 'fadeInUp 0.3s ease-out forwards';
    emailsContainer.appendChild(emailInputGroup);

    // Focus the new input
    setTimeout(() => {
      emailInput.focus();
    }, 100);
  }

  // Reset form to initial state
  function resetForm() {
    companyForm.reset();
    companyNameError.textContent = '';

    // Remove all email inputs except the first one
    const emailInputGroups = document.querySelectorAll('.email-input-group');
    for (let i = 1; i < emailInputGroups.length; i++) {
      emailsContainer.removeChild(emailInputGroups[i]);
    }

    // Clear error message for the first email input
    const firstEmailError = document.querySelector('.email-input-group .error-message');
    if (firstEmailError) {
      firstEmailError.textContent = '';
    }
  }

  // Function to hide registration form with animation
  function hideRegistrationForm() {
    registrationForm.style.opacity = '0';

    setTimeout(() => {
      registrationForm.classList.add('hidden');
      document.body.style.overflow = ''; // Re-enable scrolling
      resetForm();
      // Reset opacity for next time
      registrationForm.style.opacity = '1';
    }, 300);
  }

  // Add keyframes for animations
  const style = document.createElement('style');
  style.textContent = `
    @keyframes fadeOut {
      from {
        opacity: 1;
      }
      to {
        opacity: 0;
      }
    }

    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  `;
  document.head.appendChild(style);
});
