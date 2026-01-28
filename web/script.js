// Force Localhost
if (window.location.protocol === 'file:') {
    window.location.href = 'http://localhost:5000/' + window.location.pathname.split('/').pop();
}

const PORT = '5000';
const HOST = window.location.hostname; // e.g. 'localhost' or '127.0.0.1'
// If we are on the backend port, use relative paths. Otherwise point to backend on same host.
const API_BASE = (window.location.port === PORT) ? '' : `http://${HOST}:${PORT}`;

// Global helper to add lounge link (needs to be global for submitAccessCode)
function addLoungeLink() {
    if (document.getElementById('lounge-link')) return;

    const navUl = document.querySelector('nav ul');
    const li = document.createElement('li');
    li.id = 'lounge-link';
    li.innerHTML = '<a href="hub.html" style="color:var(--accent);">The Lounge</a>';
    // Insert before logout/admin/login link (last item)
    navUl.insertBefore(li, navUl.lastElementChild);
}

document.addEventListener('DOMContentLoaded', () => {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
                observer.unobserve(entry.target); // Only animate once
            }
        });
    }, observerOptions);

    // Check Session (Cookie-based)
    checkSession();

    function checkSession() {
        const authLink = document.getElementById('auth-link');
        const scanLink = document.getElementById('scan-qr-link');
        if (!authLink) return;

        fetch(`${API_BASE}/api/current_user`, { credentials: 'include' }) // Send cookies
            .then(res => res.json())
            .then(data => {
                if (data.username) {
                    // Logged In
                    authLink.innerText = `Hi, ${data.username}`;
                    authLink.href = '#';
                    authLink.onclick = (e) => {
                        e.preventDefault();
                        if (data.role === 'admin') {
                            window.location.href = 'admin.html';
                        } else {
                            fetchBookingHistory(data.username);
                        }
                    };

                    // Store for booking form usage (optional helper)
                    window.currentUser = data.username;

                    // Show Scan QR Link (now Enter Code)
                    if (scanLink) {
                        scanLink.style.display = 'block';
                        scanLink.onclick = (e) => {
                            e.preventDefault();
                            if (localStorage.getItem('hubUnlocked') === 'true') {
                                if (confirm("The Lounge is already unlocked. Open it now?")) {
                                    // Try to open
                                    const win = window.open('hub.html', '_blank');
                                    if (win) win.focus();
                                    return;
                                }
                            }
                            openCodeModal();
                        };
                    }

                    // Check for Unlocked Hub
                    if (localStorage.getItem('hubUnlocked') === 'true') {
                        addLoungeLink();
                    }
                } else {
                    // Not Logged In
                    authLink.innerText = 'Login';
                    authLink.href = 'login.html';
                    window.currentUser = null;

                    if (scanLink) scanLink.style.display = 'none';

                    // Remove Lounge Link if present
                    const loungeLink = document.getElementById('lounge-link');
                    if (loungeLink) loungeLink.remove();
                }
            })
            .catch(err => console.error("Session check failed", err));
    }

    const hiddenElements = document.querySelectorAll('.hidden');
    hiddenElements.forEach((el) => observer.observe(el));

    // Navbar scroll effect
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.padding = '1rem 0';
            navbar.style.background = 'rgba(13, 13, 13, 0.98)';
        } else {
            navbar.style.padding = '1.5rem 0';
            navbar.style.background = 'rgba(13, 13, 13, 0.9)';
        }
    });

    // Mobile Menu Toggle
    const mobileBtn = document.querySelector('.mobile-menu-btn');
    const nav = document.querySelector('nav');
    const navLinks = document.querySelectorAll('nav a');

    if (mobileBtn) {
        mobileBtn.addEventListener('click', () => {
            mobileBtn.classList.toggle('active');
            nav.classList.toggle('active');
            document.body.style.overflow = nav.classList.contains('active') ? 'hidden' : 'auto';
        });
    }

    // Close menu when a link is clicked
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (nav.classList.contains('active')) {
                mobileBtn.classList.remove('active');
                nav.classList.remove('active');
                document.body.style.overflow = 'auto';
            }
        });
    });

    // Advanced Text Reveal Animation
    const heroTitle = document.querySelector('.hero h1');
    if (heroTitle) {
        // Wrap words in spans
        const text = heroTitle.innerText; // Get raw text
    }

    const revealElements = document.querySelectorAll('.reveal-text');
    revealElements.forEach(element => {
        const text = element.innerText;
        const words = text.split(/\s+/);
        element.innerHTML = ''; // Clear content

        words.forEach((word, index) => {
            const span = document.createElement('span');
            span.textContent = word;
            span.style.transitionDelay = `${index * 0.1}s`; // Stagger delay
            span.style.marginRight = '0.25em'; // Consistent spacing
            element.appendChild(span);
        });

        // Trigger animation after a slight delay
        setTimeout(() => {
            element.classList.add('visible');
        }, 100);
    });

    // Dynamic Background (Cursor Parallax)
    const heroBg = document.querySelector('.hero-bg');
    if (heroBg) {
        document.addEventListener('mousemove', (e) => {
            const x = (window.innerWidth - e.pageX * 2) / 50; // Sensitivity
            const y = (window.innerHeight - e.pageY * 2) / 50;

            heroBg.style.transform = `scale(1.1) translate(${x}px, ${y}px)`;
        });
    }

    // Booking Form Logic
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = bookingForm.querySelector('button');
            const originalText = submitBtn.innerText;
            submitBtn.innerText = 'Processing...';
            submitBtn.disabled = true;

            const formData = {
                name: document.getElementById('name').value,
                phone: document.getElementById('phone').value,
                service: document.getElementById('service').value,
                date: document.getElementById('date').value,
                time: document.getElementById('time').value,
            };

            try {
                const response = await fetch(`${API_BASE}/api/book`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify(formData)
                });

                const messageDiv = document.getElementById('booking-message');
                const result = await response.json();

                if (response.ok) {
                    messageDiv.style.color = '#4CAF50';
                    messageDiv.innerText = 'Booking Confirmed! Reference ID: ' + result.id;
                    bookingForm.reset();
                    // Clear success message after 5 seconds
                    setTimeout(() => { messageDiv.innerText = ''; }, 5000);
                } else {
                    messageDiv.style.color = '#bf3e3e';
                    messageDiv.innerText = result.error || 'Booking failed.';
                }
            } catch (error) {
                console.error('Error:', error);
                const messageDiv = document.getElementById('booking-message');
                if (messageDiv) {
                    messageDiv.style.color = '#bf3e3e';
                    messageDiv.innerText = 'Failed to connect to the server.';
                } else {
                    alert('Failed to connect to the server.');
                }
            } finally {
                submitBtn.innerText = originalText;
                submitBtn.disabled = false;
            }
        });
    }
});
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('hubUnlocked'); // Lock the hub again
        fetch(`${API_BASE}/api/logout`, { method: 'POST', credentials: 'include' })
            .then(() => window.location.reload());
    }
}

function closeModal() {
    document.getElementById('history-modal').style.display = 'none';
}

async function fetchBookingHistory(username) {
    const modal = document.getElementById('history-modal');
    const list = document.getElementById('history-list');

    modal.style.display = 'flex';
    list.innerHTML = '<p style="text-align:center;">Loading...</p>';

    try {
        const response = await fetch(`${API_BASE}/api/my-bookings`, { credentials: 'include' }); // User inferred from cookie
        const data = await response.json();

        if (data.length === 0) {
            list.innerHTML = '<p style="text-align:center; color:#888;">No booking history found.</p>';
            return;
        }

        list.innerHTML = '';
        data.forEach(appt => {
            const item = `
                <div class="booking-item">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:var(--accent); font-weight:bold;">${appt.service}</span>
                        <span style="font-size:0.8rem; color:#666;">#${appt.id}</span>
                    </div>
                    <p>📅 ${appt.date} at ${appt.time}</p>
                    <p style="font-size:0.8rem; color:${appt.status === 'confirmed' ? '#4CAF50' : (appt.status === 'rejected' ? '#bf3e3e' : '#FFC107')};">
                        ● ${appt.status.charAt(0).toUpperCase() + appt.status.slice(1)}
                    </p>
                </div>
            `;
            list.innerHTML += item;
        });
    } catch (error) {
        console.error(error);
        list.innerHTML = '<p style="text-align:center; color:#bf3e3e;">Failed to load history.</p>';
    }
}

// --- Access Code Logic ---

function openCodeModal() {
    document.getElementById('access-code-modal').style.display = 'flex';
    document.getElementById('access-code-input').value = '';
    document.getElementById('code-error').style.display = 'none';
    const input = document.getElementById('access-code-input');
    if (input) input.focus();
}

function closeCodeModal() {
    document.getElementById('access-code-modal').style.display = 'none';
}

async function submitAccessCode() {
    const code = document.getElementById('access-code-input').value;
    const errorDiv = document.getElementById('code-error');

    if (!code) return;

    try {
        const response = await fetch(`${API_BASE}/api/verify-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code })
        });

        const data = await response.json();

        if (data.success) {
            // Unlock
            localStorage.setItem('hubUnlocked', 'true');
            addLoungeLink();
            closeCodeModal();
            if (confirm("Access Granted! Enter The Lounge now?")) {
                window.open('hub.html', '_blank');
            }
        } else {
            errorDiv.innerText = "Invalid Code. Please try again.";
            errorDiv.style.display = 'block';
        }
    } catch (e) {
        console.error(e);
        errorDiv.innerText = "Connection Error: " + e.message;
        errorDiv.style.display = 'block';
    }
}

// User Hub
function openUserHubModal() {
    document.getElementById('user-hub-modal').style.display = 'flex';
}

function closeUserHubModal() {
    document.getElementById('user-hub-modal').style.display = 'none';
    backToHub(); // Reset view
}

function showSection(sectionId) {
    const grid = document.querySelector('.hub-grid');
    const contentArea = document.getElementById('hub-content-area');
    const gamesContent = document.getElementById('games-content');
    const readsContent = document.getElementById('reads-content');

    grid.style.display = 'none';
    contentArea.style.display = 'block';

    if (sectionId === 'games') {
        gamesContent.style.display = 'block';
        readsContent.style.display = 'none';
    } else if (sectionId === 'reads') {
        gamesContent.style.display = 'none';
        readsContent.style.display = 'block';
    }
}

function backToHub() {
    const grid = document.querySelector('.hub-grid');
    const contentArea = document.getElementById('hub-content-area');
    const gamesContent = document.getElementById('games-content');
    const readsContent = document.getElementById('reads-content');

    grid.style.display = 'grid';
    contentArea.style.display = 'none';
    gamesContent.style.display = 'none';
    readsContent.style.display = 'none';
}
