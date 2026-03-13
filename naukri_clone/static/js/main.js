// Main JavaScript File

// Document Ready
$(document).ready(function () {
    // Auto-hide alerts after 5 seconds
    setTimeout(function () {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Initialize tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // Password visibility toggle
    $('.toggle-password').click(function () {
        $(this).toggleClass('fa-eye fa-eye-slash');
        var input = $($(this).attr('toggle'));
        if (input.attr('type') == 'password') {
            input.attr('type', 'text');
        } else {
            input.attr('type', 'password');
        }
    });

    // Form validation
    $('form').submit(function () {
        $(this).find(':submit').prop('disabled', true);
        $(this).find(':submit').html('<span class="spinner-border spinner-border-sm"></span> Processing...');
    });

    // Profile completion checker
    checkProfileCompletion();
});

// Check profile completion
function checkProfileCompletion() {
    $('.required-field').each(function () {
        if ($(this).val()) {
            $(this).addClass('is-valid');
        } else {
            $(this).addClass('is-invalid');
        }
    });
}

// Skill input enhancement
function initSkillsInput() {
    $('#key_skills').on('keyup', function () {
        var skills = $(this).val().split(',');
        var html = '';
        skills.forEach(function (skill) {
            if (skill.trim()) {
                html += '<span class="badge bg-primary me-1">' + skill.trim() + '</span>';
            }
        });
        $('#skills-preview').html(html);
    });
}

// File upload preview
function readURL(input, previewId) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#' + previewId).attr('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]);
    }
}

// Password strength checker
function checkPasswordStrength(password) {
    var strength = 0;

    if (password.length >= 6) strength += 1;
    if (password.match(/[a-z]+/)) strength += 1;
    if (password.match(/[A-Z]+/)) strength += 1;
    if (password.match(/[0-9]+/)) strength += 1;
    if (password.match(/[$@#&!]+/)) strength += 1;

    return strength;
}

// AJAX job search
function searchJobs() {
    var keyword = $('#search-keyword').val();
    var location = $('#search-location').val();

    $.ajax({
        url: '/api/search-jobs',
        method: 'GET',
        data: {
            keyword: keyword,
            location: location
        },
        success: function (response) {
            $('#job-results').html(response);
        }
    });
}

// Apply to job with confirmation
function applyToJob(jobId) {
    if (confirm('Are you sure you want to apply for this job?')) {
        $.ajax({
            url: '/apply-job/' + jobId,
            method: 'POST',
            success: function (response) {
                if (response.success) {
                    alert('Application submitted successfully!');
                    location.reload();
                } else {
                    alert('Error: ' + response.message);
                }
            }
        });
    }
}

// Block company confirmation
function blockCompany(companyId) {
    if (confirm('Are you sure you want to block this company? They will not be able to view your profile.')) {
        $.ajax({
            url: '/block-company/' + companyId,
            method: 'POST',
            success: function (response) {
                if (response.success) {
                    alert('Company blocked successfully');
                    location.reload();
                }
            }
        });
    }
}

// Form data validation before submit
function validateForm(formId) {
    var isValid = true;
    $('#' + formId + ' [required]').each(function () {
        if (!$(this).val()) {
            $(this).addClass('is-invalid');
            isValid = false;
        } else {
            $(this).removeClass('is-invalid');
        }
    });
    return isValid;
}

// Initialize on page load
$(document).ready(function () {
    initSkillsInput();

    // Photo upload preview
    $('#photo').change(function () {
        readURL(this, 'photo-preview');
    });

    // Resume upload validation
    $('#resume').change(function () {
        var file = this.files[0];
        var fileSize = file.size / 1024 / 1024; // in MB

        if (fileSize > 2) {
            alert('File size must be less than 2MB');
            $(this).val('');
        }

        var fileType = file.name.split('.').pop().toLowerCase();
        if (!['pdf', 'doc', 'docx', 'rtf'].includes(fileType)) {
            alert('Only PDF, DOC, DOCX, and RTF files are allowed');
            $(this).val('');
        }
    });
});
// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navMenu = document.querySelector('.nav-menu');
    const navButtons = document.querySelector('.nav-buttons');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function () {
            navMenu.classList.toggle('active');
            navButtons.classList.toggle('active');

            // Change icon
            const icon = this.querySelector('i');
            if (icon.classList.contains('fa-bars')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function (event) {
        if (!event.target.closest('.navbar')) {
            if (navMenu && navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                navButtons.classList.remove('active');
                const icon = document.querySelector('.mobile-menu-btn i');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
        }
    });
});