from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from PyPDF2 import PdfReader

app = Flask(__name__)
app.secret_key = "secret123"

# 👑 FIXED ADMIN
ADMIN_USERNAME = "singhniket99"
ADMIN_PASSWORD = "Singhniket@99"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        candidate_name TEXT,
        score INTEGER,
        role TEXT,
        jd_score INTEGER,
        matched_skills TEXT,
        missing_skills TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- NAME EXTRACTION ----------
def extract_name(text):
    lines = text.split("\n")
    for line in lines[:10]:
        if len(line.strip()) > 2 and len(line.split()) <= 3:
            return line.strip().title()
    return "Unknown Candidate"

# ---------- ROLE SKILLS ----------
ROLE_SKILLS = {
    "software_engineer": ["Python", "Java", "C++", "Data Structures", "Algorithms", "Git"],
    "data_scientist": ["Python", "R", "Machine Learning", "Statistics", "Pandas", "NumPy"],
    "data_analyst": ["SQL", "Excel", "Power BI", "Tableau", "Python", "Data Cleaning"],
    "ml_engineer": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Deployment"],
    "fullstack_developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "SQL"],
    "frontend_developer": ["HTML", "CSS", "JavaScript", "React", "Angular", "UI/UX"],
    "backend_developer": ["Python", "Java", "Node.js", "SQL", "API", "Django", "Flask"],
    "devops_engineer": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux", "Jenkins"],
    "cloud_engineer": ["AWS", "Azure", "GCP", "Networking", "Security", "Virtualization"],
    "cybersecurity_analyst": ["Network Security", "Ethical Hacking", "Cryptography", "Risk Analysis", "Wireshark", "Metasploit"]
}

# ---------- SKILL RESOURCES ----------
SKILL_RESOURCES = {
    "HTML": {"learn": "https://developer.mozilla.org/en-US/docs/Web/HTML","video": "https://www.youtube.com/watch?v=qz0aGYrrlhU"},
    "CSS": {"learn": "https://developer.mozilla.org/en-US/docs/Web/CSS","video": "https://www.youtube.com/watch?v=1Rs2ND1ryYc"},
    "JavaScript": {"learn": "https://developer.mozilla.org/en-US/docs/Web/JavaScript","video": "https://www.youtube.com/watch?v=W6NZfCO5SIk"},
    "React": {"learn": "https://react.dev/learn","video": "https://www.youtube.com/watch?v=bMknfKXIFA8"},
    "Node.js": {"learn": "https://nodejs.org/en/docs","video": "https://www.youtube.com/watch?v=TlB_eWDSMt4"},
    "SQL": {"learn": "https://www.w3schools.com/sql/","video": "https://www.youtube.com/watch?v=HXV3zeQKqGY"},
    "Python": {"learn": "https://docs.python.org/3/tutorial/","video": "https://www.youtube.com/watch?v=rfscVS0vtbw"}
}

# ---------- LOGIN ----------
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_input = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if role == "admin":
            if user_input == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session["user"] = "admin"
                session["role"] = "admin"
                return redirect("/admin")
            else:
                return render_template("login.html", error="Invalid admin credentials")

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE (username=? OR email=?) AND password=?",
                  (user_input, user_input, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = user[1]
            session["role"] = "user"
            return redirect("/home")
        else:
            return render_template("login.html", error="Invalid user credentials")

    return render_template("login.html")

# ---------- REGISTER ----------
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if password != confirm:
            return render_template("register.html", error="Passwords do not match")

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
        existing = c.fetchone()

        if existing:
            conn.close()
            return render_template("register.html", error="User already exists")

        c.execute("INSERT INTO users(username,email,password) VALUES (?,?,?)",
                  (username, email, password))
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

# ---------- HOME ----------
@app.route('/home')
def home():
    if "user" not in session:
        return redirect("/")
    return render_template("index.html")

# ---------- ANALYZE ----------
@app.route('/analyze', methods=['POST'])
def analyze():
    if "user" not in session:
        return redirect("/")

    role = request.form.get("role")
    jd_skills = ROLE_SKILLS.get(role, [])

    file = request.files.get("resume")
    text = ""

    if file:
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)

        if file.filename.endswith(".pdf"):
            reader = PdfReader(filepath)
            text = " ".join([p.extract_text() or "" for p in reader.pages]).lower()
        else:
            with open(filepath, "r", errors="ignore") as f:
                text = f.read().lower()

    candidate_name = extract_name(text)

    def normalize(t):
        return t.lower().replace(" ", "").replace("-", "")

    normalized_text = normalize(text)

    SKILL_MAP = {
        "html": ["html", "html5"],
        "css": ["css"],
        "javascript": ["javascript", "js"],
        "sql": ["sql", "mysql", "sqlite"],
        "react": ["react", "reactjs"],
        "node.js": ["node", "nodejs"],
        "python": ["python"],
        "flask": ["flask"],
    }

    matched, missing = [], []

    for skill in jd_skills:
        variations = SKILL_MAP.get(skill.lower(), [skill.lower()])
        if any(normalize(v) in normalized_text for v in variations):
            matched.append(skill)
        else:
            missing.append(skill)

    score = int((len(matched) / len(jd_skills)) * 100) if jd_skills else 0
    jd_score = max(score - 5, 0)

    breakdown = {
        "skills": score,
        "jd_match": jd_score,
        "projects": min(score + 10, 100),
        "experience": min(score + 5, 100)
    }

    suggestions = []
    for skill in missing:
        resource = SKILL_RESOURCES.get(skill, {
            "learn": f"https://www.google.com/search?q=learn+{skill}",
            "video": f"https://www.youtube.com/results?search_query={skill}+tutorial"
        })
        suggestions.append({
            "skill": skill,
            "learn": resource["learn"],
            "video": resource["video"]
        })

    if score > 80:
        ai = "Excellent resume! 🚀"
    elif score > 50:
        ai = "Good resume, improve few areas."
    else:
        ai = "Needs improvement."

    # ---------- SAVE (SAFE FIX ADDED ONLY) ----------
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT id FROM users WHERE username=?", (session["user"],))
    user_row = c.fetchone()

    if user_row:
        user_id = user_row[0]
    else:
        return redirect("/")

    matched_str = ",".join(matched)
    missing_str = ",".join(missing)

    c.execute("""
    INSERT INTO reports(user_id, candidate_name, score, role, jd_score, matched_skills, missing_skills)
    VALUES (?,?,?,?,?,?,?)
    """, (user_id, candidate_name, score, role, jd_score, matched_str, missing_str))

    conn.commit()
    conn.close()

    return render_template("dashboard.html",
                           score=score,
                           jd_score=jd_score,
                           matched=matched,
                           missing=missing,
                           breakdown=breakdown,
                           suggestions=suggestions,
                           ai=ai,
                           candidate_name=candidate_name)

# ---------- ADMIN ----------
@app.route('/admin')
def admin():
    if session.get("role") != "admin":
        return "❌ Access Denied"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    SELECT users.username, reports.candidate_name, reports.score,
           reports.role, reports.jd_score,
           reports.matched_skills, reports.missing_skills
    FROM reports
    JOIN users ON reports.user_id = users.id
    """)
    reports = c.fetchall()

    conn.close()

    return render_template("admin.html", reports=reports)

# ---------- DELETE USER ----------
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get("role") != "admin":
        return "❌ Access Denied"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return redirect("/admin")

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)