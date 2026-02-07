// Predefined credentials
const adminCredentials = { username: 'admin', password: 'admin123' };
const defaultStudent = { username: 'student1', password: 'student1' };

// Load student accounts from localStorage or use default
let studentAccounts = JSON.parse(localStorage.getItem('studentAccounts')) || [defaultStudent];

// Ensure default student always exists
if (!studentAccounts.find(student => student.username === 'student1')) {
    studentAccounts.push(defaultStudent);
    localStorage.setItem('studentAccounts', JSON.stringify(studentAccounts));
}

// Save student accounts to localStorage
function saveStudentAccounts() {
    localStorage.setItem('studentAccounts', JSON.stringify(studentAccounts));
}

// Tab switching
function showTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.login-form').forEach(form => form.classList.remove('active'));
    
    if (tabName === 'admin') {
        document.querySelector('.tab-btn:first-child').classList.add('active');
        document.getElementById('adminForm').classList.add('active');
    } else {
        document.querySelector('.tab-btn:last-child').classList.add('active');
        document.getElementById('studentForm').classList.add('active');
    }
    hideMessage();
}

function showCreateAccount() {
    document.querySelectorAll('.login-form').forEach(form => form.classList.remove('active'));
    document.getElementById('createForm').classList.add('active');
    hideMessage();
}

function showForgotPassword() {
    document.querySelectorAll('.login-form').forEach(form => form.classList.remove('active'));
    document.getElementById('forgotForm').classList.add('active');
    hideMessage();
}

function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
}

function hideMessage() {
    document.getElementById('message').style.display = 'none';
}

// Admin login (SAFE version)
const adminForm = document.getElementById('adminForm');

if (adminForm) {
    adminForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const username = document.getElementById('adminUsername').value;
        const password = document.getElementById('adminPassword').value;

        if (username === adminCredentials.username && password === adminCredentials.password) {
            showMessage('Admin login successful!', 'success');
            localStorage.setItem('loginType', 'admin');
            localStorage.setItem('username', 'admin');
            setTimeout(() => window.location.href = 'dashboard.html', 1000);
        } else {
            showMessage('Invalid admin credentials!', 'error');
        }
    });
}


// Student login
const studentForm = document.getElementById('studentForm');

if (studentForm) {
    studentForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const username = document.getElementById('studentUsername').value;
        const password = document.getElementById('studentPassword').value;

        const validStudent = studentAccounts.find(student =>
            student.username === username && student.password === password
        );

        if (validStudent) {
            showMessage('Student login successful!', 'success');
            localStorage.setItem('loginType', 'student');
            localStorage.setItem('username', username);
            setTimeout(() => window.location.href = 'dashboard.html', 1000);
        } else {
            showMessage('Invalid student credentials!', 'error');
        }
    });
}


// Create account
const createForm = document.getElementById('createForm');

if (createForm) {
    createForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const username = document.getElementById('newUsername').value;
        const password = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (password !== confirmPassword) {
            showMessage('Passwords do not match!', 'error');
            return;
        }

        if (studentAccounts.find(student => student.username === username)) {
            showMessage('Username already exists!', 'error');
            return;
        }

        studentAccounts.push({ username, password });
        saveStudentAccounts();
        showMessage('Account created successfully!', 'success');
        setTimeout(() => showTab('student'), 1500);
        createForm.reset();
    });
}


// Forgot password
const forgotForm = document.getElementById('forgotForm');

if (forgotForm) {
    forgotForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const username = document.getElementById('resetUsername').value;
        const student = studentAccounts.find(student => student.username === username);

        if (student) {
            showMessage(`Password reset link sent! Your password is: ${student.password}`, 'success');
        } else {
            showMessage('Username not found!', 'error');
        }
    });
}

// Close hamburger menu on link click (mobile)
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".nav-menu a").forEach(link => {
    link.addEventListener("click", () => {
        const nav = document.getElementById("navMenu");
        if (nav) nav.classList.remove("active");
    });
});
});

// Hamburger menu toggle (for index.html)
function toggleMenu() {
    const nav = document.getElementById("navMenu");
    if (nav) nav.classList.toggle("active");
}

