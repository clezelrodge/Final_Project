/* ================================================================
   FileTrack - Document Management System
   Frontend JavaScript
   ================================================================ */

/* ================= VIEW CONTROL ================= */
const views = document.querySelectorAll(".view");

function showView(viewId) {
    views.forEach(function(view) {
        view.classList.remove("active-view");
    });

    const selectedView = document.getElementById(viewId);

    if (selectedView) {
        selectedView.classList.add("active-view");
        window.scrollTo(0, 0);
    }
}

/* ================= MOBILE NAVIGATION ================= */
const menuBtn = document.getElementById("menuBtn");
const navLinks = document.getElementById("navLinks");

if (menuBtn && navLinks) {
    menuBtn.addEventListener("click", function() {
        navLinks.classList.toggle("active");
    });
}

/* ================= SMOOTH SCROLLING ================= */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href && href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                // Close mobile menu if open
                if (navLinks) {
                    navLinks.classList.remove('active');
                }
            }
        }
    });
});

/* ================= CLOSE MOBILE MENU ON OUTSIDE CLICK ================= */
document.addEventListener('click', function(event) {
    if (menuBtn && navLinks) {
        if (!menuBtn.contains(event.target) && !navLinks.contains(event.target)) {
            navLinks.classList.remove('active');
        }
    }
});

/* ================= TARGET USERS CAROUSEL ================= */
const targetCarousel = document.getElementById('targetCarousel');
const targetPrevButton = document.querySelector('.target-arrow-left');
const targetNextButton = document.querySelector('.target-arrow-right');
const targetDots = document.querySelectorAll('.target-dot');

function getTargetCardStep() {
    if (!targetCarousel) return 0;
    const card = targetCarousel.querySelector('.target-card');
    if (!card) return 0;

    const style = window.getComputedStyle(targetCarousel);
    const gap = parseFloat(style.columnGap || style.gap || 0);
    return card.getBoundingClientRect().width + gap;
}

function updateTargetDots() {
    if (!targetCarousel || !targetDots.length) return;

    const step = getTargetCardStep();
    if (!step) return;

    const activeIndex = Math.min(
        targetDots.length - 1,
        Math.round(targetCarousel.scrollLeft / step)
    );

    targetDots.forEach(function(dot, index) {
        dot.classList.toggle('active', index === activeIndex);
    });
}

if (targetCarousel) {
    if (targetPrevButton) {
        targetPrevButton.addEventListener('click', function() {
            targetCarousel.scrollBy({ left: -getTargetCardStep(), behavior: 'smooth' });
        });
    }

    if (targetNextButton) {
        targetNextButton.addEventListener('click', function() {
            targetCarousel.scrollBy({ left: getTargetCardStep(), behavior: 'smooth' });
        });
    }

    targetDots.forEach(function(dot, index) {
        dot.addEventListener('click', function() {
            targetCarousel.scrollTo({ left: getTargetCardStep() * index, behavior: 'smooth' });
        });
    });

    targetCarousel.addEventListener('scroll', function() {
        window.requestAnimationFrame(updateTargetDots);
    });

    window.addEventListener('resize', updateTargetDots);
    updateTargetDots();
}

/* ================= FLASH MESSAGE AUTO-HIDE ================= */
window.addEventListener("load", function() {
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        const flashMessages = document.querySelector('.flash-messages');
        if (flashMessages) {
            flashMessages.style.transition = 'opacity 0.5s ease';
            flashMessages.style.opacity = '0';
            setTimeout(function() {
                if (flashMessages) {
                    flashMessages.style.display = 'none';
                }
            }, 500);
        }
    }, 5000);
});

/* ================= LOGIN FORM PASSWORD TOGGLE ================= */
function togglePassword(inputId, toggleElement) {
    const input = document.getElementById(inputId);
    
    if (input.type === "password") {
        input.type = "text";
        if (toggleElement) {
            toggleElement.textContent = "HIDE";
        }
    } else {
        input.type = "password";
        if (toggleElement) {
            toggleElement.textContent = "SHOW";
        }
    }
}

/* ================= LOGIN MODE SWITCHING ================= */
function switchMode(mode) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const loginBtn = document.getElementById('loginModeBtn');
    const registerBtn = document.getElementById('registerModeBtn');

    if (mode === 'login') {
        if (loginForm) loginForm.classList.add('active');
        if (registerForm) registerForm.classList.remove('active');
        if (loginBtn) loginBtn.classList.add('active');
        if (registerBtn) registerBtn.classList.remove('active');
    } else {
        if (loginForm) loginForm.classList.remove('active');
        if (registerForm) registerForm.classList.add('active');
        if (loginBtn) loginBtn.classList.remove('active');
        if (registerBtn) registerBtn.classList.add('active');
    }
}

/* ================= ROLE SELECTION ================= */
function selectRole(role, element) {
    const parent = element.parentElement;
    const options = parent.querySelectorAll('.role-option');
    const hiddenInput = parent.querySelector('input[type="hidden"]');
    
    options.forEach(function(opt) {
        opt.classList.remove('selected');
    });
    
    element.classList.add('selected');
    
    if (hiddenInput) {
        hiddenInput.value = role;
    }
}

/* ================= PASSWORD STRENGTH CHECKER ================= */
function checkPasswordStrength() {
    const password = document.getElementById('registerPassword');
    const bars = [
        document.getElementById('strengthBar1'),
        document.getElementById('strengthBar2'),
        document.getElementById('strengthBar3'),
        document.getElementById('strengthBar4')
    ];
    const strengthText = document.getElementById('strengthText');

    if (!password || !strengthText) return;

    // Reset all bars
    bars.forEach(function(bar) {
        if (bar) {
            bar.className = 'strength-bar';
        }
    });
    
    strengthText.textContent = '';
    strengthText.className = 'strength-text';

    const value = password.value;
    if (value.length === 0) return;

    let strength = 0;
    
    if (value.length >= 6) strength++;
    if (value.length >= 8) strength++;
    if (/[A-Z]/.test(value)) strength++;
    if (/[0-9]/.test(value)) strength++;
    if (/[!@#$%^&*]/.test(value)) strength++;

    let level, color;
    if (strength <= 2) {
        level = 'weak';
        color = '#ef4444';
        if (bars[0]) bars[0].className = 'strength-bar active weak';
    } else if (strength <= 3) {
        level = 'medium';
        color = '#f59e0b';
        if (bars[0]) bars[0].className = 'strength-bar active medium';
        if (bars[1]) bars[1].className = 'strength-bar active medium';
    } else {
        level = 'strong';
        color = '#10b981';
        bars.forEach(function(bar) {
            if (bar) bar.className = 'strength-bar active strong';
        });
    }

    strengthText.textContent = 'Password strength: ' + level.charAt(0).toUpperCase() + level.slice(1);
    strengthText.className = 'strength-text ' + level;
    strengthText.style.color = color;
}

/* ================= REGISTRATION FORM VALIDATION ================= */
function validateRegisterForm() {
    const username = document.getElementById('registerUsername');
    const password = document.getElementById('registerPassword');
    const confirmPassword = document.getElementById('confirmPassword');

    if (!username || !password || !confirmPassword) {
        return false;
    }

    if (username.value.length < 3) {
        alert('Username must be at least 3 characters');
        return false;
    }

    if (password.value.length < 6) {
        alert('Password must be at least 6 characters');
        return false;
    }

    if (!/[A-Z]/.test(password.value)) {
        alert('Password must contain at least one uppercase letter');
        return false;
    }

    if (!/[0-9]/.test(password.value)) {
        alert('Password must contain at least one number');
        return false;
    }

    if (password.value !== confirmPassword.value) {
        alert('Passwords do not match');
        return false;
    }

    return true;
}

/* ================= FORM SUBMIT LOADING STATE ================= */
function handleSubmit(form) {
    const submitBtn = form.querySelector('.submit-btn');
    if (submitBtn) {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        
        // Store original text
        if (!submitBtn.getAttribute('data-original-text')) {
            submitBtn.setAttribute('data-original-text', submitBtn.textContent);
        }
        
        submitBtn.textContent = 'Processing...';
    }
    
    // Form will submit normally to Flask backend
    return true;
}

/* ================= DASHBOARD SEARCH FUNCTIONALITY ================= */
// This function is used on user dashboard for searching documents
async function searchDocuments(query) {
    if (!query || query.trim() === '') {
        return;
    }

    try {
        const response = await fetch('/search?q=' + encodeURIComponent(query));
        const documents = await response.json();
        
        // Update the search results display
        const resultsContainer = document.getElementById('searchResults');
        if (resultsContainer) {
            if (documents.length === 0) {
                resultsContainer.innerHTML = '<p class="no-results">No documents found</p>';
            } else {
                let html = '';
                documents.forEach(function(doc) {
                    const statusClass = doc.status === 'Available' ? 'status-available' : 'status-borrowed';
                    html += `
                        <div class="document-card">
                            <div class="doc-info">
                                <h4>${doc.title}</h4>
                                <p><strong>RFID:</strong> ${doc.rfid_tag}</p>
                                <p><strong>Location:</strong> ${doc.location || 'Not assigned'}</p>
                                <span class="status-badge ${statusClass}">${doc.status}</span>
                            </div>
                        </div>
                    `;
                });
                resultsContainer.innerHTML = html;
            }
        }
    } catch (error) {
        console.error('Search error:', error);
    }
}

/* ================= DOCUMENT TABLE SEARCH FILTER ================= */
// This function filters document table rows based on search input
function filterDocumentTable() {
    const searchInput = document.getElementById('docSearchInput');
    const tableRows = document.querySelectorAll('.document-table tbody tr');
    
    if (!searchInput || !tableRows.length) return;

    const filter = searchInput.value.toLowerCase();

    tableRows.forEach(function(row) {
        const text = row.textContent.toLowerCase();
        if (text.includes(filter)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/* ================= INITIALIZATION ================= */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any dashboard-specific functionality
    const isAdminDashboard = document.getElementById('adminDashboardView');
    const isUserDashboard = document.getElementById('userDashboardView');
    
    if (isAdminDashboard || isUserDashboard) {
        // Dashboard specific initialization can go here
        console.log('Dashboard initialized');
    }
    
    // Initialize search if on user dashboard
    const searchInput = document.getElementById('docSearchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                searchDocuments(this.value);
            }
        });
    }
});

/* ================= LOGOUT CONFIRMATION ================= */
function confirmLogout() {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/logout';
    }
}

/* ================= ACTIVE NAVIGATION HIGHLIGHT ================= */
// Highlight active navigation link based on scroll position
window.addEventListener('scroll', function() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-links a');
    
    if (!sections.length || !navLinks.length) return;

    let current = '';
    
    sections.forEach(function(section) {
        const sectionTop = section.offsetTop - 100;
        if (window.pageYOffset >= sectionTop) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(function(link) {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + current) {
            link.classList.add('active');
        }
    });
});
