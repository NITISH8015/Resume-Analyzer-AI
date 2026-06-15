
/* ================= PASSWORD TOGGLE ================= */
function togglePassword() {
    const input = document.getElementById("password");
    const icon = document.getElementById("eyeIcon");

    if (input.type === "password") {
        input.type = "text";
        if (icon) icon.innerText = "🙈";
    } else {
        input.type = "password";
        if (icon) icon.innerText = "👁";
    }
}

/* ================= PASSWORD STRENGTH ================= */
function checkStrength() {
    const password = document.getElementById("password").value;
    const bar = document.getElementById("strengthBar");
    const text = document.getElementById("strengthText");

    if (!bar || !text) return;

    let strength = 0;

    if (password.length > 5) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;

    let width = strength * 25;

    bar.innerHTML = `<div style="width:${width}%; background:${getColor(strength)}"></div>`;
    text.innerText = getText(strength);
    text.style.color = getColor(strength);
}

function getColor(strength) {
    return ["#ef4444","#f97316","#eab308","#22c55e"][strength-1] || "#64748b";
}

function getText(strength) {
    return ["Weak","Medium","Strong","Very Strong"][strength-1] || "";
}

/* ================= VALIDATION ================= */
function validateForm() {
    const pass = document.getElementById("password")?.value;
    const confirm = document.getElementById("confirm")?.value;
    const error = document.getElementById("errorMsg");

    if (pass !== confirm) {
        if (error) error.innerText = "Passwords do not match!";
        return false;
    }

    return true;
}

/* ================= LOGIN LOADING ================= */
function showLoader() {
    const btn = document.getElementById("loginBtn");
    if (!btn) return;

    btn.classList.add("loading");
    btn.innerText = "Logging in...";
}

/* ================= SUGGESTION TOGGLE ================= */
function toggleSuggestions() {
    const box = document.getElementById("suggestionBox");
    if (!box) return;

    if (box.style.display === "none" || box.style.display === "") {
        box.style.display = "block";
    } else {
        box.style.display = "none";
    }
}

/* ================= FILE UPLOAD ================= */
const uploadBox = document.getElementById("uploadBox");
const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");

if (uploadBox && fileInput) {

    uploadBox.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            fileName.innerText = "📄 " + fileInput.files[0].name;
        }
    });

    uploadBox.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadBox.style.border = "2px dashed #6366f1";
    });

    uploadBox.addEventListener("dragleave", () => {
        uploadBox.style.border = "2px dashed #555";
    });

    uploadBox.addEventListener("drop", (e) => {
        e.preventDefault();
        fileInput.files = e.dataTransfer.files;
        fileName.innerText = "📄 " + e.dataTransfer.files[0].name;
    });
}

/* ================= CARD HOVER EFFECT ================= */
document.querySelectorAll(".card").forEach(card => {
    card.addEventListener("mouseenter", () => {
        card.style.transform = "translateY(-5px)";
    });

    card.addEventListener("mouseleave", () => {
        card.style.transform = "translateY(0)";
    });
});