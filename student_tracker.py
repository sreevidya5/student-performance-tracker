from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)
CORS(app)

# ---------------- HOME ROUTE ----------------
@app.route('/')
def home():
    return "✅ Student Tracker API is running"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS students
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  roll TEXT,
                  math INTEGER,
                  science INTEGER,
                  english INTEGER,
                  prediction TEXT)''')

    conn.commit()
    conn.close()

init_db()

# ---------------- ML MODEL ----------------
X = [[80, 85, 90], [30, 40, 35], [60, 65, 70], [20, 25, 30]]
y = ["Pass", "Fail", "Pass", "Fail"]

model = LogisticRegression()
model.fit(X, y)

def predict_result(marks):
    return model.predict([marks])[0]

# ---------------- CREATE ----------------
@app.route('/students', methods=['POST'])
def add_student():
    try:
        data = request.json

        math = int(data['math'])
        science = int(data['science'])
        english = int(data['english'])

        prediction = predict_result([math, science, english])

        conn = sqlite3.connect('students.db')
        c = conn.cursor()

        c.execute(
            "INSERT INTO students (name, roll, math, science, english, prediction) VALUES (?, ?, ?, ?, ?, ?)",
            (data['name'], data['roll'], math, science, english, prediction)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "✅ Student added successfully"})

    except Exception as e:
        return jsonify({"error": str(e)})

# ---------------- READ ----------------
@app.route('/students', methods=['GET'])
def get_students():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()

    c.execute("SELECT * FROM students")
    rows = c.fetchall()
    conn.close()

    students = []
    for row in rows:
        students.append({
            "id": row[0],
            "name": row[1],
            "roll": row[2],
            "math": row[3],
            "science": row[4],
            "english": row[5],
            "prediction": row[6]
        })

    return jsonify(students)

# ---------------- UPDATE ----------------
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    try:
        data = request.json

        math = int(data['math'])
        science = int(data['science'])
        english = int(data['english'])

        prediction = predict_result([math, science, english])

        conn = sqlite3.connect('students.db')
        c = conn.cursor()

        c.execute("""
            UPDATE students
            SET name=?, roll=?, math=?, science=?, english=?, prediction=?
            WHERE id=?
        """, (data['name'], data['roll'], math, science, english, prediction, id))

        conn.commit()
        conn.close()

        return jsonify({"message": "✏️ Student updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)})

# ---------------- DELETE ----------------
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    try:
        conn = sqlite3.connect('students.db')
        c = conn.cursor()

        c.execute("DELETE FROM students WHERE id=?", (id,))

        conn.commit()
        conn.close()

        return jsonify({"message": "🗑️ Student deleted successfully"})

    except Exception as e:
        return jsonify({"error": str(e)})

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)