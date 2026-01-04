from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json

app = Flask(__name__)

def get_db():
    return sqlite3.connect("students.db")

# ---------------- DB SETUP ----------------
with get_db() as con:
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        subjects TEXT,
        marks TEXT,
        grades TEXT,
        cgpa REAL
    )
    """)
    con.commit()

# ---------------- UTILS ----------------
def calculate_grade(mark):
    if mark >= 90: return "A+"
    elif mark >= 80: return "A"
    elif mark >= 70: return "B"
    elif mark >= 60: return "C"
    elif mark >= 50: return "D"
    else: return "F"

def calculate_cgpa(marks):
    return round(sum(marks) / len(marks) / 10, 2)

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/add", methods=["GET", "POST"])
def add_result():
    if request.method == "POST":
        name = request.form["name"]
        subjects = request.form.getlist("subject[]")
        marks = list(map(int, request.form.getlist("mark[]")))

        grades = [calculate_grade(m) for m in marks]
        cgpa = calculate_cgpa(marks)

        with get_db() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO results VALUES (NULL, ?, ?, ?, ?, ?)",
                (
                    name,
                    json.dumps(subjects),
                    json.dumps(marks),
                    json.dumps(grades),
                    cgpa,
                ),
            )
            con.commit()

        return redirect("/records")

    return render_template("add_result.html")

@app.route("/records")
def records():
    with get_db() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM results")
        data = cur.fetchall()

    results = []
    for r in data:
        results.append({
            "id": r[0],
            "name": r[1],
            "subjects": json.loads(r[2]),
            "marks": json.loads(r[3]),
            "grades": json.loads(r[4]),
            "cgpa": r[5],
        })

    return render_template("records.html", results=results)

@app.route("/chart/<int:id>")
def chart(id):
    with get_db() as con:
        cur = con.cursor()
        cur.execute("SELECT subjects, marks, student_name FROM results WHERE id=?", (id,))
        r = cur.fetchone()

    return render_template(
        "chart.html",
        subjects=json.loads(r[0]),
        marks=json.loads(r[1]),
        name=r[2],
    )

@app.route("/delete/<int:id>")
def delete(id):
    with get_db() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM results WHERE id=?", (id,))
        con.commit()
    return redirect("/records")

if __name__ == "__main__":
    app.run(debug=True)
