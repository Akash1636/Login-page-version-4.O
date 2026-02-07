from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('course_system.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS courses
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, instructor TEXT, 
                  description TEXT, limit_students INTEGER, duration_hours INTEGER, 
                  duration_minutes INTEGER, prerequisites TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS enrollments
                 (id INTEGER PRIMARY KEY, student_id INTEGER, course_id INTEGER, 
                  department TEXT, batch TEXT, enrolled_date TEXT, status TEXT,
                  FOREIGN KEY(student_id) REFERENCES users(id),
                  FOREIGN KEY(course_id) REFERENCES courses(id))''')
    
    conn.commit()
    conn.close()

init_db()

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
        except:
            return jsonify({'message': 'Token invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# User Authentication
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect('course_system.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username=? AND password=?', 
              (username, hashlib.sha256(password.encode()).hexdigest()))
    user = c.fetchone()
    conn.close()
    
    if user:
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token, 'role': user[3]})
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = hashlib.sha256(data.get('password').encode()).hexdigest()
    role = data.get('role', 'student')
    
    try:
        conn = sqlite3.connect('course_system.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                  (username, password, role))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User created successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already exists'}), 400

# Course Management
@app.route('/api/courses', methods=['GET'])
def get_courses():
    conn = sqlite3.connect('course_system.db')
    c = conn.cursor()
    c.execute('SELECT * FROM courses')
    courses = c.fetchall()
    conn.close()
    
    return jsonify([{
        'id': c[0], 'name': c[1], 'category': c[2], 'instructor': c[3],
        'description': c[4], 'limit': c[5], 'duration_hours': c[6],
        'duration_minutes': c[7], 'prerequisites': c[8]
    } for c in courses])

@app.route('/api/courses', methods=['POST'])
@token_required
def create_course(current_user):
    data = request.json
    conn = sqlite3.connect('course_system.db')
    c = conn.cursor()
    c.execute('''INSERT INTO courses (name, category, instructor, description, 
                 limit_students, duration_hours, duration_minutes, prerequisites)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['name'], data['category'], data['instructor'], data['description'],
               data.get('limit', 0), data.get('duration_hours', 0),
               data.get('duration_minutes', 0), data.get('prerequisites', '')))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Course created successfully'})

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
@token_required
def update_course(current_user, course_id):
    data = request.json
    conn = sqlite3.connect('course_system.db')
    c = conn.cursor()
    c.execute('''UPDATE courses SET name=?, category=?, instructor=?, description=?,
                 limit_students=?, duration_hours=?, duration_minutes=?, prerequisites=?
                 WHERE id=?''',
              (data['name'], data['category'], data['instructor'], data['description'],
               data.get('limit', 0), data.get('duration_hours', 0),
               data.get('duration_minutes', 0), data.get('prerequisites', ''), course_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Course updated successfully'})

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
@token_required
def delete_course(current_user, course_id):
    conn = sqlite3.connect('course_system.db')
    c = conn.cursor()
    c.execute('DELETE FROM courses WHERE id=?', (course_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Course deleted successfully'})

# Enrollment Management
@app.route('/api/enroll', methods=['POST'])
@token_required
def enroll_student(current_user):
    data = request.json
    conn = sqlite3.connect('course_system.db')
    c = conn.cursor()
    
    c.execute('SELECT id FROM users WHERE username=?', (current_user,))
    user = c.fetchone()
    
    if user:
        c.execute('''INSERT INTO enrollments (student_id, course_id, department, batch, 
                     enrolled_date, status) VALUES (?, ?, ?, ?, ?, ?)''',
                  (user[0], data['course_id'], data['department'], data['batch'],
                   datetime.datetime.now().isoformat(), 'ongoing'))
        conn.commit()
    
    conn.close()
    return jsonify({'message': 'Enrolled successfully'})

@app.route('/api/enrollments/<username>', methods=['GET'])
def get_enrollments(username):
    conn = sqlite3.connect('course_system.db')
    c = conn.cursor()
    c.execute('''SELECT c.name, e.department, e.batch, e.enrolled_date, e.status
                 FROM enrollments e
                 JOIN users u ON e.student_id = u.id
                 JOIN courses c ON e.course_id = c.id
                 WHERE u.username = ?''', (username,))
    enrollments = c.fetchall()
    conn.close()
    
    return jsonify([{
        'course': e[0], 'department': e[1], 'batch': e[2],
        'enrolled_date': e[3], 'status': e[4]
    } for e in enrollments])

# Statistics
@app.route('/api/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    conn = sqlite3.connect('course_system.db')
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM courses')
    total_courses = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM users WHERE role="student"')
    total_students = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM enrollments')
    total_enrollments = c.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_courses': total_courses,
        'total_students': total_students,
        'total_enrollments': total_enrollments
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
