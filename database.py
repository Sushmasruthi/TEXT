import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def create_connection():
    try:
        conn = sqlite3.connect('education.db')
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            
            # Create students table
            c.execute('''CREATE TABLE IF NOT EXISTS students
                        (id TEXT PRIMARY KEY, 
                         full_name TEXT NOT NULL,
                         department TEXT NOT NULL,
                         password TEXT NOT NULL)''')
            
            # Create teachers table
            c.execute('''CREATE TABLE IF NOT EXISTS teachers
                        (id TEXT PRIMARY KEY,
                         full_name TEXT NOT NULL,
                         department TEXT NOT NULL,
                         specialization TEXT NOT NULL,
                         password TEXT NOT NULL)''')
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()

def check_existing_id(user_id):
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            
            # Check in students table
            c.execute('SELECT id FROM students WHERE id = ?', (user_id,))
            if c.fetchone():
                return True, "Student ID already exists"
            
            # Check in teachers table
            c.execute('SELECT id FROM teachers WHERE id = ?', (user_id,))
            if c.fetchone():
                return True, "Teacher ID already exists"
            
            return False, ""
        finally:
            conn.close()
    return True, "Database error"

def register_student(student_id, full_name, department, password):
    # Check if ID already exists
    exists, message = check_existing_id(student_id)
    if exists:
        return False, message
    
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            hashed_password = generate_password_hash(password)
            c.execute('INSERT INTO students (id, full_name, department, password) VALUES (?, ?, ?, ?)',
                     (student_id, full_name, department, hashed_password))
            conn.commit()
            return True, "Student registration successful!"
        except sqlite3.Error as e:
            return False, f"Registration failed: {str(e)}"
        finally:
            conn.close()
    return False, "Database connection error"

def register_teacher(teacher_id, full_name, department, specialization, password):
    # Check if ID already exists
    exists, message = check_existing_id(teacher_id)
    if exists:
        return False, message
    
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            hashed_password = generate_password_hash(password)
            c.execute('INSERT INTO teachers (id, full_name, department, specialization, password) VALUES (?, ?, ?, ?, ?)',
                     (teacher_id, full_name, department, specialization, hashed_password))
            conn.commit()
            return True, "Teacher registration successful!"
        except sqlite3.Error as e:
            return False, f"Registration failed: {str(e)}"
        finally:
            conn.close()
    return False, "Database connection error"

def verify_student(student_id, password):
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute('SELECT * FROM students WHERE id = ?', (student_id,))
            student = c.fetchone()
            
            if not student:
                return False, "Invalid Student ID"
            
            if check_password_hash(student[3], password):
                return True, {
                    "id": student[0],
                    "full_name": student[1],
                    "department": student[2]
                }
            return False, "Invalid Password"
        finally:
            conn.close()
    return False, "Database connection error"

def verify_teacher(teacher_id, password):
    conn = create_connection()
    if conn:
        try:
            c = conn.cursor()
            c.execute('SELECT * FROM teachers WHERE id = ?', (teacher_id,))
            teacher = c.fetchone()
            
            if not teacher:
                return False, "Invalid Teacher ID"
            
            if check_password_hash(teacher[4], password):
                return True, {
                    "id": teacher[0],
                    "full_name": teacher[1],
                    "department": teacher[2]
                }
            return False, "Invalid Password"
        finally:
            conn.close()
    return False, "Database connection error"

# Initialize the database when the module is imported
init_db() 