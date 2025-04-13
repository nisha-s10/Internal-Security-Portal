document.addEventListener('DOMContentLoaded', function () {
    let container = document.getElementById('container');
    let alertBox = document.getElementById('custom-alert');

    // Handle sign-in/sign-up toggle
    if (container) {
        window.toggle = function () { // Making toggle accessible globally
            container.classList.toggle('sign-in');
            container.classList.toggle('sign-up');
        };

        setTimeout(() => {
            container.classList.add('sign-in');
        }, 200);
    } else {
        console.error('Container element not found!');
    }

    // Auto dismiss alert after 3 seconds
    if (alertBox) {
        setTimeout(() => dismissAlert(), 3000);
    }
});

// Function to dismiss the alert
function dismissAlert() {
    let alertBox = document.getElementById('custom-alert');
    if (alertBox) {
        alertBox.classList.add('hidden'); // Slide up and fade out
        setTimeout(() => alertBox.remove(), 500);
    }

    if (window.history.replaceState) {
      const url = new URL(window.location);
      url.searchParams.delete('m');
      window.history.replaceState({}, document.title, url.pathname + url.search);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("regemp");
  const passwordInput = document.getElementById("password");
  const confirmPasswordInput = document.getElementById("confirm-password");
  const passToggleBtn = document.getElementById("pass-toggle-btn");
  const confirmPassToggleBtn = document.getElementById("confirm-pass-toggle-btn");

  const fullnameInput = document.getElementById("fullname");
  const emailInput = document.getElementById("email");
  const dateInput = document.getElementById("date");
  const mobileInput = document.getElementById("mobile");
  const aadharInput = document.getElementById("aadhar");

  // --- Password toggle
  if (passToggleBtn && passwordInput) {
    passToggleBtn.addEventListener("click", () => {
      const isPassword = passwordInput.type === "password";
      passwordInput.type = isPassword ? "text" : "password";
      passToggleBtn.className = isPassword ? "fa-solid fa-eye-slash" : "fa-solid fa-eye";
    });
  }

  if (confirmPassToggleBtn && confirmPasswordInput) {
    confirmPassToggleBtn.addEventListener("click", () => {
      const isPassword = confirmPasswordInput.type === "password";
      confirmPasswordInput.type = isPassword ? "text" : "password";
      confirmPassToggleBtn.className = isPassword ? "fa-solid fa-eye-slash" : "fa-solid fa-eye";
    });
  }

  // --- Show error
  const showError = (field, errorText) => {
    field.classList.add("error");

    // Avoid duplicate error messages
    let existingError = field.closest(".form-group").querySelector(".error-text");
    if (existingError) {
      existingError.innerText = errorText;
    } else {
      const errorElement = document.createElement("small");
      errorElement.classList.add("error-text");
      errorElement.innerText = errorText;
      field.closest(".form-group").appendChild(errorElement);
    }
  };

  const clearErrors = () => {
    document.querySelectorAll(".form-group .error").forEach(field => field.classList.remove("error"));
    document.querySelectorAll(".error-text").forEach(errorText => errorText.remove());
  };

  // --- Real-time password match check
  const checkPasswordMatch = () => {
    const password = passwordInput.value.trim();
    const confirmPassword = confirmPasswordInput.value.trim();

    const confirmGroup = confirmPasswordInput.closest(".form-group");

    // Clear previous match error
    const prevError = confirmGroup.querySelector(".error-text");
    if (prevError) prevError.remove();
    confirmPasswordInput.classList.remove("error");

    if (confirmPassword !== "" && password !== confirmPassword) {
      showError(confirmPasswordInput, "Passwords do not match");
    }
  };

  // --- Real-time listener
  confirmPasswordInput.addEventListener("input", checkPasswordMatch);
  passwordInput.addEventListener("input", checkPasswordMatch);

  // --- Form validation on submit
  const handleFormData = (e) => {
    e.preventDefault();
    clearErrors();

    const fullname = fullnameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const confirmPassword = confirmPasswordInput.value.trim();
    const date = dateInput.value;
    const mobile = mobileInput.value.trim();
    const aadhar = aadharInput.value.trim();
    const photoInput = document.getElementById("photo");

    const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;
    let hasError = false;

    if (fullname === "") {
      showError(fullnameInput, "Enter your full name");
      hasError = true;
    }
    if (!emailPattern.test(email)) {
      showError(emailInput, "Enter a valid email address");
      hasError = true;
    }
    if (password === "") {
      showError(passwordInput, "Enter your password");
      hasError = true;
    }
    if (confirmPassword === "") {
      showError(confirmPasswordInput, "Re-enter your password");
      hasError = true;
    } else if (password !== confirmPassword) {
      showError(confirmPasswordInput, "Passwords do not match");
      hasError = true;
    }
    if (date === "") {
      showError(dateInput, "Select your date of birth");
      hasError = true;
    }
    if (mobile.length !== 10 || !/^\d+$/.test(mobile)) {
      showError(mobileInput, "Enter a valid 10-digit mobile number");
      hasError = true;
    }
    if (aadhar.length !== 12 || !/^\d+$/.test(aadhar)) {
      showError(aadharInput, "Enter a valid 12-digit Aadhar number");
      hasError = true;
    }

    // --- Image validation (photo)
    if (photoInput && photoInput.files.length > 0) {
      const file = photoInput.files[0];
      const allowedTypes = ["image/jpeg", "image/png", "image/jpg", "image/webp"];

      if (!allowedTypes.includes(file.type)) {
        showError(photoInput, "Only JPG, JPEG, PNG, or WEBP images are allowed");
        hasError = true;
      }

      const maxSize = 2 * 1024 * 1024; // 2MB
      if (file.size > maxSize) {
        showError(photoInput, "File size should be less than 2MB");
        hasError = true;
      }
    } else {
      showError(photoInput, "Please upload a photo");
      hasError = true;
    }

    if (!hasError) {
      form.submit();
    }
  };

  if (form) {
    form.addEventListener("submit", handleFormData);
  }
});
